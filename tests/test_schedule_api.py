# coding=utf-8
from __future__ import absolute_import, unicode_literals
import unittest
import json
from base64 import b64encode
from flask import current_app, url_for

from app import create_app, db
from app.models import Role, User, RawCourse, Course

student_id = '4140206139'
other_student_id = '4140206109'

old_student_id = '4120206101'


def get_api_headers(username, password):
    return {
        'Authorization': 'Basic ' + b64encode(
            (username + ':' + password).encode('utf-8')).decode('utf-8'),
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }


class CoursesAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

        # 新建教师 赋予加V角色 新建原课程/课程
        role_student = Role.query.filter_by(name='Student').first()
        role_teacher = Role.query.filter_by(name='Teacher_V').first()
        if role_teacher is None and role_student is None:
            raise Exception('缺少角色')
        self.student = User(username=u'小明', name=u'这是学生', password='cat', confirmed=True,
                            role=role_student, school_code=student_id)
        self.teacher = User(username=u'桃李满园关不住', name=u'这是老师', password='cat',
                            confirmed=True, role=role_teacher, school_code='t0861')

        db.session.add(self.student)
        db.session.add(self.teacher)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_no_auth(self):
        response = self.client.get(url_for('api.get_schedule'))
        self.assertTrue(response.status_code == 401)

    def test_student_get(self):
        # 获取自己的
        response = self.client.get(url_for('api.get_schedule'),
                                   headers=get_api_headers(student_id, 'cat'))
        self.assertTrue(response.status_code == 200)
        response_json = json.loads(response.data.decode('utf-8'))
        self.assertIsNotNone(response_json.get('class_name'))
        # 无权获取他人的课表
        response = self.client.get(url_for('api.get_schedule', stu_id=other_student_id),
                                   headers=get_api_headers(student_id, 'cat'))
        self.assertTrue(response.status_code == 403)

    def test_teacher_get(self):
        # 可以获取指定学号学生的课表
        response = self.client.get(url_for('api.get_schedule', stu_id=other_student_id),
                                   headers=get_api_headers('t0861', 'cat'))
        self.assertTrue(response.status_code == 200)
        response_json = json.loads(response.data.decode('utf-8'))
        self.assertIsNotNone(response_json.get('class_name'))

        response = self.client.get(url_for('api.get_schedule', stu_id=old_student_id),
                                   headers=get_api_headers('t0861', 'cat'))

        self.assertTrue(response.status_code == 404)
        response_json = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response_json.get('message'), '该用户没有最新课表!')

    def test_use_cache(self):
        response = self.client.get(url_for('api.get_schedule', use_cache=False),
                                   headers=get_api_headers(student_id, 'cat'))
        self.assertTrue(response.status_code == 200)
        response = self.client.get(url_for('api.get_schedule'),
                                   headers=get_api_headers(student_id, 'cat'))
        self.assertTrue(response.status_code == 200)
        response_json = json.loads(response.data.decode('utf-8'))
        class_name = response_json.get('class_name')
        self.assertIsNotNone(class_name)

        response_json = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response_json.get('cache') is True)
        self.assertEquals(class_name, response_json.get('class_name'))

    def test_no_student_code(self):
        self.student = User(username=u'大明', name=u'这也是学生', password='cat', confirmed=True)
        response = self.client.get(url_for('api.get_schedule'),
                                   headers=get_api_headers(u'大明', 'cat'))
        self.assertTrue(response.status_code == 404)
        response_json = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response_json.get('message'), '该用户未设定学号')
