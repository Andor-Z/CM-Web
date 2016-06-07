from flask_wtf import Form
from wtforms import StringField, DateTimeField, SubmitField, BooleanField, SelectField, TextAreaField, DecimalField,PasswordField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Length, EqualTo
from ..models import Department, Employee, Role, Label


class CostForm(Form):
    event_time = DateTimeField('发生时间', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    dept_name = SelectField('部门', coerce=int)
    label_name = SelectField('分类', coerce=int)
    cost_detail = TextAreaField('备注')
    cost_money = DecimalField('金额', places=2)
    party_employee = SelectField('当事人', coerce=int)
    submit = SubmitField('添加')

    def __init__(self):
        super(CostForm, self).__init__()
        self.dept_name.choices = [(dept.dept_id, dept.dept_name) for dept in Department.query.order_by(Department.dept_name).all()]
        self.party_employee.choices = [(emp.id, emp.employee_name) for emp in Employee.query.order_by(Employee.employee_name).all()]
        self.label_name.choices = [(label.label_id, label.label_name) for label in Label.query.order_by(Label.label_name).all()]


class LoginForm(Form):
    login_name = StringField('登录名', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('保持登陆')
    submit = SubmitField('登录')


class LabelForm(Form):
    label_name = StringField('费用分类', validators=[DataRequired(), Length(1, 64)])
    submit = SubmitField('添加')


class AddEmployeeFrom(Form):
    login_name = StringField('登录名', validators=[DataRequired(), Length(1, 64)])
    employee_name = StringField('员工名', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('密码', validators=[DataRequired(), EqualTo('password2', message='2次密码不一致')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    dept_name = SelectField('部门', coerce=int, validators=[DataRequired()])
    role_name = SelectField('职位', coerce=int, validators=[DataRequired()])
    submit = SubmitField('确认')

    def __init__(self):
        super(AddEmployeeFrom, self).__init__()
        self.dept_name.choices = [(dept.dept_id, dept.dept_name) for dept in Department.query.order_by(Department.dept_name).all()]
        self.role_name.choices = [(role.role_id, role.role_name) for role in Role.query.order_by(Role.role_id).all()]

    def validate_login_name(self, filed):
        # 如果表单类中定义了以validate_ 开头且后面跟着字段名的方法，这个方法就和常规的验证函数一起调用。
        if Employee.query.filter_by(login_name=filed.data).first():
            raise ValidationError('此登录名已存在。')

    def validate_employee_name(self, filed):
        if Employee.query.filter_by(employee_name=filed.data).first():
            raise ValidationError('此姓名已经存在。')


class EditEmployeeFrom(Form):
    login_name = StringField('登录名', validators=[DataRequired(), Length(1, 64)])
    employee_name = StringField('员工名', validators=[DataRequired(), Length(1, 64)])
    dept_name = SelectField('部门', coerce=int)
    role_name = SelectField('职位', coerce=int)
    submit = SubmitField('确认')


    def __init__(self, employee):
        super(EditEmployeeFrom, self).__init__()
        self.dept_name.choices = [(dept.dept_id, dept.dept_name) for dept in Department.query.order_by(Department.dept_name).all()]
        self.role_name.choices = [(role.role_id, role.role_name) for role in Role.query.order_by(Role.role_id).all()]
        self.employee = employee

    def validate_login_name(self, filed):
        # 如果表单类中定义了以validate_ 开头且后面跟着字段名的方法，这个方法就和常规的验证函数一起调用。
        if filed.data != self.employee.login_name and Employee.query.filter_by(login_name=filed.data).first():
            raise ValidationError('此登录名已存在。')

    def validate_employee_name(self, filed):
        if filed.data != self.employee.employee_name and Employee.query.filter_by(employee_name=filed.data).first():
            raise ValidationError('此姓名已经存在。')


class ChangePasswordForm(Form):
    old_password = PasswordField('旧密码', validators = [DataRequired()])
    password = PasswordField('新密码', validators = [DataRequired(), EqualTo('password2', message = '两次密码输入不一致')])
    password2 = PasswordField('确认新密码', validators = [DataRequired()])
    submit = SubmitField('提交')