import os
import unittest

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app.main import create_app, db
from app.main.util.commands.create_admin import start_admin_account

from app import blueprint


app = create_app('prod')
app.register_blueprint(blueprint)

app.app_context().push()

manager = Manager(app)

migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)


@manager.option('-n', '--name', dest='name', help='Admin first name')
@manager.option('-sn', '--second_name', dest='second_name', help='Admin second name')
@manager.option('-un', '--username', dest='username', help='Admin username')
@manager.option('-e', '--email', dest='email', help='Admin email')
@manager.option('-p', '--password', dest='password', help='Admin password')
@manager.option('-bd', '--birthday', dest='birthday', help='Admin date of birth')
def create_admin(
    name, 
    second_name,
    username,
    email,
    password,
    birthday
    ):
    start_admin_account(
        name,
        second_name,
        username,
        email,
        password,
        birthday
    )


@manager.command
def run():
    app.run()


@manager.command
def test():
    """Runs the unit tests."""
    tests = unittest.TestLoader().discover('app/test', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


if __name__ == '__main__':
    manager.run()
