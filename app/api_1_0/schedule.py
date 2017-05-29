# -*- coding: utf-8 -*-
from flask import jsonify, request, current_app, url_for, g
from . import api
from ..models import User
from .authentication import auth
from .errors import unauthorized


@api.route('/schedule/get-schedule')
def get_schedule():
    return
