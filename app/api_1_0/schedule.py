# -*- coding: utf-8 -*-
from flask import jsonify, request, current_app, url_for, g
from . import api
from ..models import User
from .authentication import auth
from .errors import unauthorized
from tsxypy.ScheduleCatcherFromStuId import ScheduleCatcherFromStuId
from datetime import date

sc = ScheduleCatcherFromStuId()


@api.route('/schedule/get-schedule')
def get_schedule():
    def school_year():
        today = date.today()
        return today.year if today.month >= 9 else today.year-1

    def semester():
        """
        钦定一年的9月前未下半学期, 9月后为上半学期
        :return: '1':下学期, '0':上学期
        """
        today = date.today()
        return '1' if today.month < 9 else '0'
    if g.current_user.is_anonymous:
        return unauthorized('Invalid credentials')
    d = sc.get_schedule(g.current_user.school_code, school_year(), semester())
    return jsonify(d)
