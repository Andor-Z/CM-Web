import os
from app import create_app, db
from app.models import Department, Employee
from init_db import init_db
from flask_script import Manager, Shell


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(app=app, db=db, Department=Department, Employee=Employee)

manager.add_command('shell', Shell(make_context=make_shell_context))
# manager.add_command('db', )


@manager.command
def create_db():
    init_db()


if __name__ == '__main__':
    manager.run()
