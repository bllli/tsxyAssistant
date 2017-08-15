from __future__ import absolute_import, unicode_literals
from flask import Blueprint
from flask_cors import CORS

api = Blueprint('api', __name__)
CORS(api, origins=['http://bllli.cn'], supports_credentials=True)

from . import authentication, users, errors, schedule, school, score, courses, system, check_in
