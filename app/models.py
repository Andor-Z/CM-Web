from . import db, login_manager
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class Department(db.Model):
    __tablename__ = 'info_department'
    dept_id = db.Column(db.Integer, primary_key=True)
    dept_name = db.Column(db.String(64), unique=True)
    employee = db.relationship('Employee', backref='dept', lazy='dynamic')
    cost = db.relationship('Cost', backref='dept', lazy='dynamic')


class Permission:

    CHECKSELF = 0x01  # 查看和自己有关的费用条目
    CHECKDEPT = 0x02  # 查看本部门的费用条目
    CHECKALL = 0x04   # 查看所有的费用条目
    ADMINISTER = 0x80

class Role(db.Model):
    # 一共4个用户角色
    # admin可以添加删除修改费用条目，可以添加修改员工信息
    # president可以查看所有的费用条目
    # manager可以查看本部门的费用条目
    # employee仅可以查看和自己有关的费用条目
    __tablename__ = 'info_role'
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(64), unique=True)
    permission = db.Column(db.Integer)
    default = db.Column(db.Boolean, default=False, index=True)
    employee = db.relationship('Employee', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {'普通员工': (Permission.CHECKSELF, True),
                 '部门经理': (Permission.CHECKDEPT, False),
                 '总经理': (Permission.CHECKALL, False),
                 '管理员': (0xff, False)}
        for r in roles:
            role = Role.query.filter_by(role_name=r).first()
            if role is None:
                role = Role(role_name=r)
                role.permission = roles[r][0]
                role.default = roles[r][1]
                db.session.add(role)
        db.session.commit()


class Employee(UserMixin, db.Model):
    # UserMixin 解决登陆的一些问题。
    __tablename__ = 'info_employee'
    id = db.Column(db.Integer, primary_key=True)
    login_name = db.Column(db.String(64), unique=True, index=True)
    employee_name = db.Column(db.String(64), unique=True, index=True)
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('info_role.role_id'))
    dept_id = db.Column(db.Integer, db.ForeignKey('info_department.dept_id'))
    cost = db.relationship('Cost', backref='employee', lazy='dynamic')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.role is None:
            # 每个员工实例创建的时候都会运行此函数，
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @staticmethod
    def create_admin():
        admin_name = current_app.config['ADMIN_NAME']
        admin_password = current_app.config["ADMIN_PASSWORD"]
        e = Employee.query.filter_by(login_name='admin').first()
        if e is None:
            admin = Employee(login_name=admin_name,employee_name='admin', password=admin_password,
                             role=Role.query.filter_by(permission=0xff).first())
            db.session.add(admin)
            db.session.commit()

    @property
    def password(self):
        # @property 将方法变成属性
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can(self, permission):
        return self.role is not None and (self.role.permission & permission) == permission

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)


class AnonymousUer(AnonymousUserMixin):
    def can(self, permission):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUer


@login_manager.user_loader
def load_user(empl_id):
    # login_manager的回调函数，主要用于用户方法的get_id()
    # 回调函数接收以 Unicode 字符串形式表示的用户标识符。如果能找到用户，这个函数必须返回用户对象；否则应该返回 None。
    # get_id()返回用户的唯一标识符，使用 Unicode 编码字符串
    return Employee.query.get(int(empl_id))


class Label(db.Model):
    __tablename__ = 'cost_label'
    label_id = db.Column(db.Integer, primary_key=True)
    label_name = db.Column(db.String(64))
    cost = db.relationship('Cost', backref='label', lazy='dynamic')


class Cost(db.Model):
    __tablename__ = 'thing_cost'
    cost_id = db.Column(db.Integer, primary_key=True)
    event_time = db.Column(db.DateTime(), default=datetime.utcnow)
    record_time = db.Column(db.DateTime(), default=datetime.utcnow)
    label_id = db.Column(db.Integer, db.ForeignKey('cost_label.label_id'))      # 后期准备键一个cost标签表
    cost_detail = db.Column(db.Text)
    cost_money = db.Column(db.Float)
    dept_id = db.Column(db.Integer, db.ForeignKey('info_department.dept_id'))
    party_employee_id = db.Column(db.Integer, db.ForeignKey('info_employee.id'))


    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     empl = Employee.query.filter_by(id=self.party_employee_id).first()
    #     dept = self.dept
    #     if dept.dept_id != empl.dept_id:
    #         raise ValueError('员工与部门不匹配。')
