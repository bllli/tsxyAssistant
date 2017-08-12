# coding=utf-8
from __future__ import absolute_import, unicode_literals
import unittest
from app import create_app, db
from app.models import User, Role, Operation,  RawCourse, Course, _Class, CheckIn


class CheckInModelTestCase(unittest.TestCase):
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

    def test_new_check_in(self):
        # 假数据
        c1 = _Class(name=u'14LOL本1')
        c2 = _Class(name=u'14LOL本2')
        rc = RawCourse(name=u'套路心理学-如何反野')
        course = Course(self.teacher, rc)
        course.classes.append(c2)
        student1 = User(username=u'大学森', _class=c1)
        student2 = User(username=u'中学森', _class=c2)
        check = CheckIn(name="某次签到", sponsor=self.teacher, check_in_type=CheckIn.CheckInType.classes)
        check.classes.append(c1)
        check.users.append(student1)

        db.session.add(c1)
        db.session.add(c2)
        db.session.add(student1)
        db.session.add(student2)
        db.session.add(check)
        db.session.commit()
        # 测试班级与签到表的兼容性
        self.assertTrue(check in c1.check_in)
        self.assertTrue(check in student1._class.check_in)
        self.assertTrue(check not in student2._class.check_in)
        # 测试签到能通过教师对象查询到
        self.assertTrue(check in self.teacher.init_check_in)
        # 测试to_json
        check_json = check.to_json()
        self.assertTrue(check_json.get('sponsor_id') == self.teacher.id)
        self.assertTrue(check_json.get('type') == CheckIn.CheckInType.classes.value)

        check = CheckIn(name="又一次签到", sponsor=self.teacher, check_in_type=CheckIn.CheckInType.course)
        check.course = course
        # 签到 -> 课程 -> 班级 班级如何直接获取签到信息？
        for course in student2._class.courses:
            if course.check_in:
                self.assertTrue(check in course.check_in)
        self.assertTrue(check in student2._class.courses[0].check_in)
        student2.check_in.append(check)
        self.assertTrue(student2 in check.users)

        check_json = check.to_json()
        self.assertTrue(check_json.get('sponsor_id') == self.teacher.id)
        self.assertTrue(check_json.get('type') == CheckIn.CheckInType.course.value)

