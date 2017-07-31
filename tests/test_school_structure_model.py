# coding=utf-8
import unittest
from app import create_app, db
from app.models import School, Department, Specialty, _Class, User, Role, Course, RawCourse


class SchoolStructureModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_department_in_school(self):
        s = School(name='tsxy')
        db.session.add(s)
        db.session.commit()
        d = Department(name='cs')
        d.school = s
        db.session.add(d)
        db.session.commit()
        self.assertTrue(d in s.departments)

    def test_specialty_in_department(self):
        d = Department(name='cs')
        db.session.add(d)
        db.session.commit()
        s = Specialty(name='cs')
        s.department = d
        db.session.add(s)
        db.session.commit()
        self.assertTrue(s in d.specialties)

    def test_class_in_specialty(self):
        s = Specialty(name='cs')
        db.session.add(s)
        db.session.commit()
        c = _Class(name='14CS1')
        c.specialty = s
        db.session.add(c)
        db.session.commit()
        self.assertTrue(c in s.classes)

    def test_student_in_class(self):
        c = _Class(name='14CS1')
        db.session.add(c)
        db.session.commit()
        u = User(name='bllli')
        u._class = c
        db.session.add(c)
        db.session.commit()
        self.assertTrue(u in c.students)

    def test_course_with_class(self):
        # + 原课程
        raw_course = RawCourse(name=u'Java')
        db.session.add(raw_course)
        db.session.commit()
        # + 从原课程指定实际课程
        course = Course(User(name=u"老师"), RawCourse(name=u"没课"))
        # course.raw_course_id = raw_course.id
        course.raw_course = raw_course
        db.session.add(course)
        db.session.commit()
        # + 两个班级
        c = _Class(name=u'14计本1')
        c2 = _Class(name=u'14计本2')
        # 将班级与课程关联起来
        c.courses.append(course)
        # c2.courses.append(course)
        course.classes.append(c2)
        db.session.add(c)
        db.session.add(c2)
        db.session.commit()

        # 判断
        self.assertTrue(course in c.courses)
        self.assertTrue(c in course.classes)
        self.assertTrue(course in c2.courses)
        self.assertTrue(c2 in course.classes)
        course.classes.remove(c)
        db.session.add(course)
        db.session.commit()
        self.assertFalse(course in c.courses)
        self.assertFalse(c in course.classes)
