# -*- coding: utf-8 -*-
"""
schedule.py
====
课程表相关接口
"""
from datetime import date

from flask import jsonify, request, g
from tsxypy.Exception import NoneScheduleException, NetException
from tsxypy.ScheduleCatcherFromStuId import ScheduleCatcherFromStuId

from . import api
from .errors import unauthorized
from ..models import Temp


def this_school_year():
    """判断当前学年

    :return: 当前学年
    """
    today = date.today()
    return today.year if today.month >= 9 else today.year - 1


def this_semester():
    """判断本学期

    钦定一年9~2月为上半学期, 3~8月为下半学期
    :return: '1':下学期; '0':上学期
    """
    today = date.today()
    return '1' if 3 < today.month < 9 else '0'


@api.route('/schedule/get-schedule')
def get_schedule():
    """获取课程表"""
    use_cache = False if request.args.get('use_cache') == "False" else True
    school_code = request.args.get('stu_id')

    if g.current_user.is_anonymous:
        return unauthorized('Invalid credentials')
    if not school_code:
        school_code = g.current_user.school_code
    if school_code is None:
        response = jsonify({'error': '该用户未设定学号'})
        response.status_code = 404
        return response
    if use_cache:
        schedule = Temp.get_schedule_cache_for_stu_id(school_code)
        if schedule:
            return jsonify(schedule)
    try:
        sc = ScheduleCatcherFromStuId()
        d = sc.get_schedule(school_code, this_school_year(), this_semester())
        Temp.set_schedule_cache_for_stu_id(school_code, d)
        d['cache'] = False
        d['cache-date'] = None
    except NoneScheduleException as e:
        print(e)
        response = jsonify({'error': '该用户没有最新课表!'})
        response.status_code = 404
        return response
    except NetException:
        response = jsonify({'error': '教务系统出现网络问题'})
        response.status_code = 502
        return response
    return jsonify(d)
