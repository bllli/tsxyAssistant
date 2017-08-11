from __future__ import absolute_import, unicode_literals
from flask import jsonify, g

from . import api
from .authentication import auth
from .errors import unauthorized
from ..models import User


@api.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())


@auth.login_required
@api.route('/users/myself')
def myself():
    if not g.current_user.is_anonymous:
        return jsonify(g.current_user.to_json())
    return unauthorized('Invalid credentials')
