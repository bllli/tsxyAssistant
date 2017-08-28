# coding=utf-8
"""courses.py

课程接口
"""

from __future__ import absolute_import, unicode_literals
from flask import jsonify, request, g, url_for, abort

from . import api
from .. import db
from .decorators import permission_required
from ..models import Course, RawCourse, Permission, CheckIn, User, _Class


@api.route('/check-in/', methods=['POST'])
@permission_required(Permission.NEW_CHECK_IN)
def new_check_in():
    # TODO:  增加权限验证
    check_in = CheckIn.from_json(request.json)
    db.session.add(check_in)
    db.session.commit()
    return jsonify(check_in.to_json())


@api.route('/check-in/')
@permission_required(Permission.STUDENT_BASE)
def my_check_in():
    """查看学生涉及的签到

    其中描述学生对签到的状态(已完成 / 未完成(过期) / 未完成(正在签到))
    0.是a否涉及本用户  1.是否过期  2.是否已签到
    """
    query_type = request.args.get('type')
    current_user = g.current_user
    current_class = current_user._class
    if not current_class:
        abort(404, '该生没有班级信息')
    class_check_in_list = [check.to_simple_json() for check in current_class.check_in]


@api.route('/all-check-in')
@permission_required(Permission.VIEW)
def all_check_in():
    """检查所有签到记录

    请求类型  类型代号

    涉及用户所在班级的  class
    涉及某节课程的  course
    某位用户(教师/课代表/班干部)发起的  user
    """
    query_type = request.args.get('type')
    if query_type == 'class':
        _class = _Class.query.get_or_404(request.args.get('class_id'))
        _class.find_check_in()
        pass
    elif query_type == 'course':
        course = User.query.get_or_404(request.args.get('course_id'))
        pass
    elif query_type == 'user':
        user = User.query.get_or_404(request.args.get('user_id'))
        pass
    pass
