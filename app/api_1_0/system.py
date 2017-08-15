# coding=utf-8
"""system.py

系统接口
"""
from __future__ import absolute_import, unicode_literals
from flask import jsonify
from flask_cors import cross_origin

from . import api
from ..models import Permission, Role, Version


@api.route('/system/roles')
def get_roles():
    return jsonify(Role.to_json())


@api.route('/system/permissions')
def get_permissions():
    return jsonify(Permission.to_json())


@api.route('/system/new_version')
@cross_origin(supports_credentials=True)
def get_new_version():
    version = Version.query.filter_by(new=True).first()
    return jsonify(version.to_json())
