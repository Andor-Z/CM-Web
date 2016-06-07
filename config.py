import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cost manage key'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    # 每次 request 自动提交 db.session.commit()
    ADMIN_NAME = 'admin'
    ADMIN_PASSWORD = 'admin'
    WEB_TITLE = 'Cost Management'
    NUM_PER_PAGE = 15

    # @staticmethod
    # def init_app(app):
    #     # 参数为程序实例。在这个方法中，可以执行对当前环境的配置初始化。
    #     # init_app函数的函数体为空只是预留一个方法，方便调用
    #     pass


class DevelopmentConfig(Config):
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://*:*@localhost/cm_web_dev'
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class Testing(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'test.sqlite')


class Production(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data.sqlite')


# config 中设定了默认的配置类
config = {
    'default': DevelopmentConfig,
    'development': DevelopmentConfig,
    'production': Production,
    'test': Testing
}
