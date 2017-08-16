# coding=utf-8
from __future__ import absolute_import, unicode_literals
import unittest
from app import create_app, db
from app.models import User, Role, Operation,  RawCourse, Course, _Class, CheckIn


class ClassModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.teacher = User(username=u"某用户")
        db.session.add(self.teacher)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_class_find_check_in(self):
        # 新建假数据
        cl = _Class(name=u"14计本1")
        rc = RawCourse(name=u"打野入门")
        rc2 = RawCourse(name=u"打野进阶")
        course = Course(self.teacher, rc)
        course2 = Course(self.teacher, rc2)
        course.classes.append(cl)
        course2.classes.append(cl)

        check_in = CheckIn(check_in_type=CheckIn.CheckInType.course)
        check_in.appoint_course(course)

        db.session.add(cl)
        db.session.add(rc)
        db.session.add(course)
        db.session.add(course2)
        db.session.add(check_in)
        db.session.commit()
        # 判断假数据是否生效
        self.assertTrue(course in cl.courses)
        self.assertTrue(course2 in cl.courses)
        self.assertTrue(check_in in course.check_in)
        #
        check_in_id_list = cl.find_check_in()
        self.assertTrue(check_in.id in [c.get('id') for c in check_in_id_list.get('classes_check_in')])
