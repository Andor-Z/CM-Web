from config import config
from flask import Flask
# from flask import render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_login import LoginManager
# from flask.ext.bootstrap import Bootstrap
# from flask.ext.sqlalchemy import SQLAlchemy
# from flask.ext.moment import Moment


bootstrap = Bootstrap()
db = SQLAlchemy()
moment = Moment()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
# LoginManager 对象的 session_protection 属性可以设为 None、 'basic' 或 'strong'
# 设为 'strong' 时， Flask-Login 会记录客户端 IP地址和浏览器的用户代理信息， 如果发现异动就登出用户。
login_manager.login_view = 'main.login'
# login_view 属性设置登录页面的端点。若登录路由在蓝本中定义，要在前面加上蓝本的名字。


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # config[config_name].init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
