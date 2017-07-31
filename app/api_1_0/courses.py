# -*- coding: utf-8 -*-
"""courses.py

课程接口
"""

from flask import jsonify, request, g

from . import api
from ..models import Course

prefix = '/courses/'


@api.route(prefix + 'all', methods=['GET'])
def all_courses():
    l = Course.query.all()
    return


@api.route(prefix + 'in-charge', methods=['GET'])
def in_charge():
    """教师调用时，显示教师教授的课程；课代表调用时，显示负责点名的课程

    :return:
    """
    name = g.current_user.role.name
    if name is 'teacher':
        pass
    elif name is 'student':
        pass
    return
