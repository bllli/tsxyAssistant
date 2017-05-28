from flask import jsonify, request, current_app, url_for, g

from . import api
from ..models import User
from .authentication import auth
from .errors import unauthorized


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
