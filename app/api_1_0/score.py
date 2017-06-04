# -*- coding: utf-8 -*-
from flask import jsonify, request, g
from tsxypy import ScoreCatcher
from tsxypy.Exception import ScoreException, NetException

from app.api_1_0.errors import unauthorized
from . import api


@api.route('/score')
def get_score():
    score_type = request.args.get('score_type')
    if g.current_user.is_anonymous:
        return unauthorized('Invalid credentials')
    user_code = g.current_user.user_code
    if user_code is None:
        response = jsonify({'error': '该用户没有用户代号'})
        response.status_code = 404
        return response
    try:
        sc = ScoreCatcher()
        score = sc.get_score(g.current_user.school_code, user_code, score_type=score_type)
    except ScoreException as e:
        response = jsonify({'error': str(e)})
        response.status_code = 404
        return response
    except NetException:
        response = jsonify({'error': '教务系统出现网络问题'})
        response.status_code = 502
        return response
    return jsonify(score)
