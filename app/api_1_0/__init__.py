from __future__ import absolute_import, unicode_literals
from flask import Blueprint

api = Blueprint('api', __name__)

from . import authentication, users, errors, schedule, school, score, courses, system
