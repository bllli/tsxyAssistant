# coding=utf-8
"""courses.py

课程接口
"""

from __future__ import absolute_import, unicode_literals
from flask import jsonify, request, g, url_for

from . import api
from .. import db
from .authentication import auth
from .decorators import permission_required
from ..models import Course, RawCourse, Permission


@api.route('/raw_courses/')
@auth.login_required
def get_raw_courses():
    """获取所有原课程"""
    raw_courses = RawCourse.query.all()
    return jsonify({'raw_courses': [rc.to_json() for rc in raw_courses]})


@api.route('/raw_courses/<int:id>')
def get_raw_courses_by_id(id):
    """获取指定id原课程"""
    rc = RawCourse.query.get_or_404(id)
    return jsonify(rc.to_json())


@api.route('/raw_courses/', methods=['POST'])
@permission_required(Permission.MODIFY)
def new_raw_courses():
    """新增原课程"""
    rc = RawCourse.from_json(request.json)
    db.session.add(rc)
    db.session.commit()
    return jsonify(rc.to_json()), 201, \
           {'Location': url_for('api.get_raw_courses_by_id', id=rc.id, _external=True)}


@api.route('/courses/', methods=['POST'])
@permission_required(Permission.MODIFY)
def new_courses():
    """新增详细课程"""
    c = Course.from_json(request.json)
    db.session.add(c)
    db.session.commit()
    return jsonify(c.to_json()), 201, \
           {'Location': url_for('api.get_courses_by_id', id=c.id, _external=True)}


@api.route('/courses/<int:id>')
def get_courses_by_id(id):
    """查询单个详细课程"""
    c = Course.query.get_or_404(id)
    return jsonify(c.to_json())


@api.route('/courses/')
def get_courses():
    """查看所有课程"""
    courses = Course.query.all()
    return jsonify({'courses': [c.to_json() for c in courses]})


@api.route('/courses/in-charge', methods=['GET'])
def in_charge():
    """查询自己负责的课程

    教师调用时，显示教师教授的课程；课代表调用时，显示负责点名的课程
    """
    name = g.current_user.role.name
    if name is 'teacher':
        pass
    elif name is 'student':
        pass
    return
