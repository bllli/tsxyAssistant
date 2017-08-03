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
        # 新建教师 赋予加V角色
        r = Role.query.filter_by(name='Teacher_V').first()
        self.assertIsNotNone(r)
        teacher = User(username=u'老师', password='dog', confirmed=True, role=r)

        db.session.add(teacher)
        db.session.commit()

        # 测试新建原课程功能
        response = self.client.post(url_for('api.new_raw_courses'),
                                    headers=self.get_api_headers(u'老师', 'dog'),
                                    data=json.dumps({
                                        'name': '意识与走位',
                                        'course_code': '10086',
                                        'worth': '100'}))
        self.assertTrue(response.status_code == 201)
        url = response.headers.get('Location')
        self.assertIsNotNone(url)

        # 获取刚刚新建的原课程
        response = self.client.get(url,
                                   headers=self.get_api_headers(u'老师', 'dog'))
        self.assertTrue(response.status_code == 200)
        response_json = json.loads(response.data.decode('utf-8'))
        # print(json.dumps(response_json))
        self.assertTrue(response_json['url'] == url)
        self.assertTrue(response_json['name'] == "意识与走位")
        self.assertTrue(response_json['course_code'] == '10086')
        self.assertTrue(response_json['worth'] == '100')

    def test_courses(self):
        # 新建教师 赋予加V角色 新建原课程
        r = Role.query.filter_by(name='Teacher_V').first()
        self.assertIsNotNone(r)
        teacher = User(username=u'巧了我也是老师', password='cat', confirmed=True, role=r)
        raw_course = RawCourse(name=u'马原', course_code='12345', worth='100')

        db.session.add(teacher)
        db.session.add(raw_course)
        db.session.commit()

        # 新建详细课程
        response = self.client.post(url_for('api.new_courses'),
                                    headers=self.get_api_headers(u'巧了我也是老师', 'cat'),
                                    data=json.dumps({
                                        'raw_course_id': raw_course.id,
                                        'teacher_id': teacher.id,
                                        'when_code': '011',  # 周一第一节
                                        'week': '1',
                                    }))
        self.assertTrue(response.status_code == 201)
        url = response.headers.get('Location')
        self.assertIsNotNone(url)

        # 查询刚才新建的详细课程
        response = self.client.get(url,
                                   headers=self.get_api_headers(u'巧了我也是老师', 'cat'))
        self.assertTrue(response.status_code == 200)
        response_json = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response_json.get('url') == url)
        self.assertTrue(response_json.get('name') == raw_course.name)
        self.assertTrue(response_json.get('teacher') == teacher.name)
        self.assertTrue(response_json.get('when_code') == '011')
