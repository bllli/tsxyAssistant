# -*- coding: utf-8 -*-
from flask import g, jsonify, abort
from flask_httpauth import HTTPBasicAuth
from ..models import User, AnonymousUser
from . import api
from .errors import unauthorized, forbidden
from .. import db
import tsxypy
from tsxypy.Exception import TsxyException


auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(user_identity, password):
    """
    
    :param user_identity: 可能时
    :param password: 
    :return: 
    """
    if user_identity == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(user_identity)
        g.token_used = True
        return g.current_user is not None
    if len(user_identity) == 10:
        user = User.query.filter_by(school_code=user_identity).first()
    else:
        user = User.query.filter_by(username=user_identity).first()
    if not user:
        try:
            user_code = tsxypy.is_tsxy_stu(user_identity, password)
            if len(user_identity) == 10 and user_code:
                user = User(school_code=user_identity, password=password, user_code=user_code)
                user.confirmed = True
                db.session.add(user)
                db.session.commit()
            else:
                return False
        except TsxyException as e:
            abort(401)
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and \
            not g.current_user.confirmed:
        return forbidden('Unconfirmed account')


@api.route('/token')
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(
        expiration=3600), 'expiration': 3600})
