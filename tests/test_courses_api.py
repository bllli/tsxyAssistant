# -*- coding:utf-8 -*-
import unittest
import json
from base64 import b64encode
from flask import current_app, url_for

from app import create_app, db
from app.models import Role, User, RawCourse, Course


class CoursesAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

        # 新建教师 赋予加V角色 新建原课程/课程
        r = Role.query.filter_by(name='Teacher_V').first()
        if r is None:
            raise Exception('没有教师角色???')
        self.teacher = User(username=u'桃李满园关不住', name=u'这是老师', password='cat', confirmed=True, role=r)
        self.raw_course = RawCourse(name=u'出装、意识与走位', course_code='12345', worth='100')
        self.course = Course(self.teacher, self.raw_course)

        db.session.add(self.teacher)
        db.session.add(self.raw_course)
        db.session.add(self.course)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, username, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

    def test_no_auth(self):
        response = self.client.get(url_for('api.get_raw_courses'),
                                   content_type='application/json')
        self.assertTrue(response.status_code == 401)

    def test_raw_courses(self):
        # 测试新建原课程功能
        response = self.client.post(url_for('api.new_raw_courses'),
                                    headers=self.get_api_headers(self.teacher.username, 'cat'),
                                    data=json.dumps({
                                        'name': '意识与走位',
                                        'course_code': '10086',
                                        'worth': '100'}))
        self.assertTrue(response.status_code == 201)
        url = response.headers.get('Location')
        self.assertIsNotNone(url)

        # 获取刚刚新建的原课程
        response = self.client.get(url,
                                   headers=self.get_api_headers(self.teacher.username, 'cat'))
        self.assertTrue(response.status_code == 200)
        response_json = json.loads(response.data.decode('utf-8'))
        # print(json.dumps(response_json))
        self.assertTrue(response_json['url'] == url)
        self.assertTrue(response_json['name'] == "意识与走位")
        self.assertTrue(response_json['course_code'] == '10086')
        self.assertTrue(response_json['worth'] == '100')

    def test_courses(self):
        # 新建详细课程
        response = self.client.post(url_for('api.new_courses'),
                                    headers=self.get_api_headers(self.teacher.username, 'cat'),
                                    data=json.dumps({
                                        'raw_course_id': self.raw_course.id,
                                        'teacher_id': self.teacher.id,
                                        'when_code': '011',  # 周一第一节
                                        'week': '1',
                                    }))
        self.assertTrue(response.status_code == 201)
        url = response.headers.get('Location')
        self.assertIsNotNone(url)

        # 查询刚才新建的详细课程
        response = self.client.get(url,
                                   headers=self.get_api_headers(self.teacher.username, 'cat'))
        self.assertTrue(response.status_code == 200)
        response_json = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response_json.get('url') == url)
        self.assertTrue(response_json.get('name') == self.raw_course.name)
        self.assertTrue(response_json.get('teacher') == self.teacher.name)
        self.assertTrue(response_json.get('when_code') == '011')

    def test_get_all_raw_courses(self):
        response = self.client.get(url_for('api.get_raw_courses'),
                                   headers=self.get_api_headers(self.teacher.username, 'cat'))

        self.assertTrue(response.status_code == 200)
        response_json = json.loads(response.data.decode('utf-8'))
        self.assertTrue(self.raw_course.name in
                        [raw_courses.get('name') for raw_courses in response_json.get('raw_courses')])

    def test_get_all_courses(self):
        response = self.client.get(url_for('api.get_courses'),
                                   headers=self.get_api_headers(self.teacher.username, 'cat'))
        self.assertTrue(response.status_code == 200)
        response_json = json.loads(response.data.decode('utf-8'))
        self.assertTrue(self.teacher.name in
                        [courses.get('teacher') for courses in response_json.get('courses')])
        self.assertTrue(self.raw_course.id in
                        [courses.get('raw_course_id') for courses in response_json.get('courses')])
