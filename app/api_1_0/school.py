# -*- coding: utf-8 -*-
from flask import jsonify, request
from tsxypy.ScheduleCatcher import ScheduleCatcher

from . import api
from .schedule import this_semester, this_school_year
from ..models import Temp


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


@api.route('/school/semester')
def get_semester():
    return jsonify({
        'school_year': str(this_school_year()),
        'semester': this_semester(),
    })
