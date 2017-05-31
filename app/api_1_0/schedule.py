# -*- coding: utf-8 -*-
from flask import jsonify, request, current_app, url_for, g
from . import api
from .. import db
from ..models import User, ScheduleCacheForStuID, localtime
from .authentication import auth
from .errors import unauthorized
from tsxypy.ScheduleCatcherFromStuId import ScheduleCatcherFromStuId
from tsxypy.Exception import NoneScheduleException, NetException
from datetime import date, datetime

sc = ScheduleCatcherFromStuId()


def school_year():
    today = date.today()
    return today.year if today.month >= 9 else today.year - 1


def semester():
    """
    钦定一年的9月前未下半学期, 9月后为上半学期
    :return: '1':下学期, '0':上学期
    """
    today = date.today()
    return '1' if today.month < 9 else '0'


@api.route('/schedule/get-schedule')
def get_schedule():
    use_cache = True if not request.args.get('use_cache') else False
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
        cache = ScheduleCacheForStuID.query.filter_by(stu_id=school_code).first()
        if cache:
            delta = datetime.utcnow() - cache.date
            if delta.days < 2:
                cache_dict = eval(cache.content)
                cache_dict['cache'] = True
                cache_dict['cache-date'] = localtime(cache.date)
                return jsonify(cache_dict)
    try:
        d = sc.get_schedule(school_code, school_year(), semester())
        c = ScheduleCacheForStuID(content=str(d), stu_id=school_code)
        db.session.add(c)
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
