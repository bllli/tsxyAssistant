# coding=utf-8
"""courses.py

课程接口
"""

from __future__ import absolute_import, unicode_literals
from flask import jsonify, request, g, url_for

from . import api
from .. import db
from .decorators import permission_required
from ..models import Course, RawCourse, Permission, CheckIn


@api.route('/check-in/', methods=['POST'])
@permission_required(Permission.NEW_CHECK_IN)
def new_check_in():
    # TODO:  增加权限验证
    check_in = CheckIn.from_json(request.json)
    db.session.add(check_in)
    db.session.commit()
    return jsonify(check_in.to_json())


@api.route('/check-in/')
def my_check_in():
    """学生访问 查看所属班级的"""
    current_user = g.current_user
    if 'Student' in current_user.role.name:
        if current_user._class:
            current_user._class.find_check_in()
        else:
            return
    else:
        return
