# coding=utf-8
import unittest
from app import create_app, db
from app.models import User, Role, Operation,  RawCourse, Course, _Class


class CourseModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        rc = RawCourse(name=u"邓小平理论与三个代表重要思想")
        u = User(username=u"我是老师")
        c = Course(u, rc)
        db.session.add(rc)
        db.session.add(u)
        db.session.add(c)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_a_new_course(self):
        rc = RawCourse.query.filter_by(name=u"邓小平理论与三个代表重要思想").first()
        self.assertTrue(rc is not None)

        c = rc.courses.first()
        # rc = RawCourse(name=u"邓小平理论与三个代表重要思想")
        # u = User(username=u"我是老师")
        # c = Course(u, rc)
        # c.raw_course = rc
        self.assertTrue(c in rc.courses)

    def test_operate_classes_in_course(self):
        rc = RawCourse.query.filter_by(name=u"邓小平理论与三个代表重要思想").first()
        self.assertTrue(rc is not None)

        c = rc.courses.first()
        c1 = _Class(name=u'14计本1')
        c2 = _Class(name=u'14计本2')
        c3 = _Class(name=u'15计本1')
        c.operate_classes(Operation.ADD, [c1, c2])
        self.assertTrue(c1 in c.classes)
        self.assertTrue(c in c2.courses)
        self.assertFalse(c3 in c.classes)

        c.operate_classes(Operation.REMOVE, [c1])
        self.assertFalse(c in c1.courses)
        self.assertTrue(c2 in c.classes)
        self.assertTrue(c2.id in c.to_json().get('classes'))
        self.assertFalse(c3.id in c.to_json().get('classes'))

    def test_appoint_substitute_teacher(self):
        rc = RawCourse.query.filter_by(name=u"邓小平理论与三个代表重要思想").first()
        self.assertTrue(rc is not None)

        u = User(name=u"巧了我也是老师")
        u2 = User(name=u"我是路过的老师")

        c = rc.courses.first()
        c.appoint_substitute_teacher(Operation.ADD, [u, u2])
        self.assertTrue(u in c.substitute_teachers)
        self.assertTrue(c in u2.guest_courses)

        c.appoint_substitute_teacher(Operation.REMOVE, [u2])
        self.assertTrue(u in c.substitute_teachers)
        self.assertFalse(u2 in c.substitute_teachers)
