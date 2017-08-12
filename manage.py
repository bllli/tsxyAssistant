#!/usr/bin/env python
# coding=utf-8
"""服务器脚本

开启、调试、部署, 并便于启用测试环境。

Examples:
    进行单元测试::

        $ python manage.py test

    部署/初始化::

        $ python manage.py deploy

    进入shell调试::

        $ python manage.py shell

    启用服务器::

        $ python manage.py runserver
"""
from __future__ import absolute_import, unicode_literals
import six

if six.PY2:
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')

import os

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell

from app import create_app, db
from app.models import User, Role, Permission, School, Department, Specialty, \
    _Class, Temp, RawCourse, Course, CheckIn

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    """为Flask-Script的shell功能导入model类"""
    return dict(app=app, db=db, User=User, Role=Role, Temp=Temp, CheckIn=CheckIn,
                Permission=Permission, School=School, Department=Department,
                Specialty=Specialty, _Class=_Class, RawCourse=RawCourse, Course=Course)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test(coverage=False):
    """执行单元测试."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


@manager.command
def deploy():
    """部署服务器 初始化数据库"""
    from flask_migrate import upgrade
    from app.models import Role

    # migrate database to latest revision
    upgrade()

    # create user roles
    Role.insert_roles()
    School.insert_school_structure()


if __name__ == '__main__':
    manager.run()
