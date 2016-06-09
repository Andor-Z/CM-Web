from flask import render_template, redirect, url_for, request, flash, abort, current_app, make_response
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
from . import main
from .forms import CostForm, LoginForm, AddEmployeeFrom, EditEmployeeFrom, LabelForm, ChangePasswordForm
from .. import db
from ..models import Cost, Department, Employee, Role, Permission, Label
from ..decorator import permission_required, admin_required


@main.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('main.costs_list')))
    resp.set_cookie('show_dept', '0', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/costs_list')
@login_required
def costs_list():
    page = request.args.get('page', 1, type=int)
    if current_user.can(Permission.CHECKDEPT):
        cost_pagination = Cost.query.filter_by(dept_id=current_user.dept_id).order_by(Cost.event_time.desc()).paginate(page, per_page=current_app.config['NUM_PER_PAGE'], error_out=False)
    else:
        cost_pagination = Cost.query.filter_by(party_employee_id=current_user.id).order_by(Cost.event_time.desc()).paginate(page, per_page=current_app.config['NUM_PER_PAGE'], error_out=False)
    costs = cost_pagination.items
    return render_template('costs_list.html', costs=costs, pagination=cost_pagination)


@main.route('/costs_list_admin/<int:dept_id>', methods=['GET', 'POST'])
@permission_required(Permission.CHECKALL)
@login_required
def costs_list_admin(dept_id):
    depts = Department.query.order_by(Department.dept_id.desc()).all()
    page = request.args.get('page', 1, type=int)
    if dept_id == 0:
        cost_pagination = Cost.query.order_by(Cost.event_time.desc()).paginate(page, per_page=current_app.config['NUM_PER_PAGE'], error_out=False)
    else:
        cost_pagination = Cost.query.filter_by(dept_id=dept_id).order_by(Cost.event_time.desc()).paginate(page, per_page=current_app.config['NUM_PER_PAGE'], error_out=False)
    form = CostForm()
    if form.validate_on_submit():
        c = Cost(
            record_time=form.event_time.data,
            label_id=Label.query.get(form.label_name.data),
            cost_detail=form.cost_detail.data,
            cost_money=form.cost_money.data,
            dept=Department.query.get(form.dept_name.data),
            employee=Employee.query.get(form.party_employee.data))
        db.session.add(c)
        return redirect(url_for('main.costs_list'))
    form.event_time.data = datetime.utcnow()
    costs = cost_pagination.items
    # e =url_for('main.costs_list_admin', dept_id=dept_id)
    return render_template('costs_list_admin.html', form=form, depts=depts, dept_id=dept_id, costs=costs, pagination=cost_pagination)


@main.route('/edit_cost/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_cost(id):
    cost = Cost.query.get_or_404(id)
    form = CostForm()
    if form.validate_on_submit():
        cost.record_time = form.event_time.data
        cost.cost_detail = form.cost_detail.data
        cost.cost_money = form.cost_money.data
        cost.dept = Department.query.get(form.dept_name.data)
        cost.employee = Employee.query.get(form.party_employee.data)
        cost.label = Label.query.get(form.label_name.data)
        db.session.add(cost)
        return redirect(url_for('main.costs_list'))
    form.event_time.data = cost.record_time
    form.label_name.data = cost.label_id
    form.cost_detail.data = cost.cost_detail
    form.cost_money.data = cost.cost_money
    form.dept_name.data = cost.dept_id
    form.party_employee.data = cost.party_employee_id
    return render_template('edit_cost.html', cost=cost, form=form)


@main.route('/del_cost/<int:id>')
@login_required
@admin_required
def del_cost(id):
    cost = Cost.query.get_or_404(id)
    db.session.delete(cost)
    flash(cost.event_time + cost.dept + cost.employee + '的费用记录已经被删除！')
    return redirect(url_for('main.costs_list'))


@main.route('/employee/<employee_name>')
@login_required
def employee(employee_name):
    employee = Employee.query.filter_by(employee_name=employee_name).first()
    if employee is None:
        abort(404)
    return render_template('employee.html', employee=employee)


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        employee = Employee.query.filter_by(login_name=form.login_name.data).first()
        if employee is not None and employee.verify_password(form.password.data):
            login_user(employee, form.remember_me.data)
            # 用户访问未授权的 URL 时会显示登录表单，Flask-Login会把原地址保存在查询字符串的 next 参数中
            # 这个参数可从 request.args 字典中读取。如果查询字符串中没有 next 参数，则重定向到首页。
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('无效的用户名或密码')
    return render_template('login.html', form=form)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已经退出。')
    return redirect(url_for('main.index'))


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_profile(id):
    employee = Employee.query.get_or_404(id)
    if current_user == employee or current_user.is_administrator():
        form = EditEmployeeFrom(employee)
        if form.validate_on_submit():
            employee.login_name = form.login_name.data
            employee.employee_name = form.employee_name.data
            employee.role = Role.query.get(form.role_name.data)
            employee.dept = Department.query.get(form.dept_name.data)
            db.session.add(employee)
            flash('员工信息修改成功！')
            if current_user.is_administrator():
                return redirect(url_for('main.employee_list'))
            else:
                return redirect(url_for('main.employee', employee_name=current_user.employee_name))
        form.login_name.data = employee.login_name
        form.employee_name.data = employee.employee_name
        form.role_name.data = employee.role_id
        form.dept_name.data = employee.dept_id
        return render_template('edit_profile.html', form=form, employee=employee)
    else:
        abort(403)


@main.route('/employee_list')
@login_required
def employee_list():
    page = request.args.get('page', 1, type=int)
    empl_pagination = Employee.query.order_by(Employee.id).paginate(page, per_page=current_app.config['NUM_PER_PAGE'], error_out=False)
    employees = empl_pagination.items
    return render_template('employee_list.html', employees=employees, pagination=empl_pagination)


@main.route('/admin/add_employee', methods=['GET', 'POST'])
@login_required
@admin_required
def add_employee():
    form = AddEmployeeFrom()
    if form.validate_on_submit():
        employee = Employee(login_name=form.login_name.data,
                            employee_name=form.employee_name.data,
                            password=form.password.data,
                            role=Role.query.get(form.role_name.data),
                            dept=Department.query.get(form.dept_name.data))
        db.session.add(employee)
        flash('已经添加一名员工。')
        return redirect(url_for('.index'))
    return render_template('add_employee.html', form=form)


@main.route('/del_employee/<int:id>')
@login_required
@admin_required
def del_employee(id):
    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    flash(employee.employee_name + '已经被删除了！')
    return redirect(url_for('main.employee_list'))


@main.route('/label_list', methods=['GET', 'POST'])
@login_required
@admin_required
def label_list():
    form = LabelForm()
    if form.validate_on_submit():
        label = Label(label_name=form.label_name.data)
        db.session.add(label)
        flash('已经添加一个新标签。')
        return redirect(url_for('main.label_list'))
    labels = Label.query.order_by(Label.label_name).all()
    return render_template('label_list.html', form=form, labels=labels)


@main.route('/del_label/<int:id>')
@login_required
@admin_required
def del_label(id):
    label = Label.query.get_or_404(id)
    db.session.delete(label)
    flash(label.label_name + '已经被删除了！')
    return redirect(url_for('main.label_list'))


@main.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('你的密码已经修改。')
            return redirect(url_for('main.index'))
        else:
            flash('无效的密码')
    return render_template('change_password.html', form=form)
