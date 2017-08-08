# coding=utf-8
from __future__ import absolute_import, unicode_literals
import unittest
import json
from flask import url_for
from base64 import b64encode

from app import create_app, db
from app.models import Role, Permission, Version, User


def get_api_headers(username, password):
    return {
        'Authorization': 'Basic ' + b64encode(
            (username + ':' + password).encode('utf-8')).decode('utf-8'),
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }


class SystemApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=True)
        db.create_all()
        Role.insert_roles()
        u = User(username=u'bllli', password='cat', confirmed=True)
        db.session.add(u)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_permission(self):
        response = self.client.get(url_for('api.get_permissions'),
                                   headers=get_api_headers('bllli', 'cat'))
        self.assertTrue(response.status_code == 200)
        response_json = json.loads(response.data.decode('utf-8'))
        self.assertIsNotNone(response_json)
        self.assertIsNotNone(response_json.get('permissions'))
        self.assertTrue({'permission': 'ADMINISTER',
                         'value': 0x80,
                         } in response_json.get('permissions'))

    def test_get_roles(self):
        response = self.client.get(url_for('api.get_roles'),
                                   headers=get_api_headers('bllli', 'cat'))
        self.assertTrue(response.status_code == 200)
        response_json = json.loads(response.data.decode('utf-8'))
        self.assertIsNotNone(response_json)
        self.assertIsNotNone(response_json.get('roles'))
        for role in response_json.get('roles'):
            self.assertIsNotNone(role.get('name'))
            self.assertIsNotNone(role.get('permissions'))

    def test_get_version(self):
        Version.new_version('0.0.1', 'https://bllli.cn:2345/download', u'项目正式开启内测 欢迎使用测试')
        Version.new_version('0.0.2', 'https://bllli.cn:2345/download', u'新增教师登录功能')
        response = self.client.get(url_for('api.get_new_version'),
                                   headers=get_api_headers('bllli', 'cat'))
        self.assertTrue(response.status_code == 200)
        response_json = json.loads(response.data.decode('utf-8'))
        self.assertIsNotNone(response_json)
        self.assertEqual(response_json.get('download_android'), 'https://bllli.cn:2345/download')
        self.assertEqual(response_json.get('download_qr_url'),
                         'http://qr.topscan.com/api.php?'
                         'text=%s&logo=http://otl5stjju.bkt.clouddn.com/logo.png' % 'https://bllli.cn:2345/download')
        self.assertEqual(response_json.get('version'), '0.0.2')
        self.assertEqual(response_json.get('whatsnew'), '新增教师登录功能')
