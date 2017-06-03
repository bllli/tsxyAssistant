# -*- coding: utf-8 -*-
from flask import jsonify, request, current_app, url_for, g
from . import api
from ..models import User, localtime, Temp
from .authentication import auth
from .errors import unauthorized
from tsxypy.ScheduleCatcher import ScheduleCatcher
from tsxypy.ScheduleCatcherFromStuId import ScheduleCatcherFromStuId
from tsxypy.Exception import NoneScheduleException, NetException
from datetime import date, datetime


@api.route('/school/get-structure')
def get_structure():
    use_cache = False if request.args.get('use_cache') == "False" else True
    if use_cache:
        t = Temp.get_school_structure()
        if t:
            return jsonify(t)
    sc = ScheduleCatcher()
    school_json = sc.get_school_json()
    Temp.set_school_structure(school_json)
    return jsonify(school_json)
