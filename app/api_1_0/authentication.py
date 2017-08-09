# -*- coding: utf-8 -*-
"""认证

确认登入用户的身份
"""
import tsxypy
from flask import g, jsonify, abort
from flask_httpauth import HTTPBasicAuth
from tsxypy.Exception import TsxyException

from . import api
from .errors import unauthorized, forbidden
from .. import db
from ..models import User, AnonymousUser, Role

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(user_identity, password):
    """确认用户密码的正确性
    
    :param str user_identity: 用户标识码
    :param str password: 用户输入的密码
    :return bool: 是否通过密码验证(是->True;->False)
    """
    if user_identity == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(user_identity)
        g.token_used = True
        return g.current_user is not None
    if len(user_identity) == 10 or user_identity[0] in ['t', 'T']:
        user = User.query.filter_by(school_code=user_identity).first()
    else:
        user = User.query.filter_by(username=unicode(user_identity)).first()
    if not user:  #: 尝试登录
        try:
            if len(user_identity) == 10:
                user_code = tsxypy.is_tsxy_stu(user_identity, password)
                role = Role.query.filter_by(name='Student').first()
            elif user_identity[0] in ['t', 'T']:
                user_code = tsxypy.is_tsxy_teacher(user_identity, password)
                role = Role.query.filter_by(name='Teacher_V').first()
            if user_code:
                user = User(school_code=user_identity, password=password, user_code=user_code)
                user.confirmed = True
                user.role = role
                db.session.add(user)
                db.session.commit()
            else:
                return False
        except TsxyException as e:
            abort(401)
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


# @auth.error_handler
# def auth_error():
#     """登陆错误时会被调用
#
#     :return: 未认证异常Json
#     """
#     return unauthorized('Invalid credentials')

@api.before_request
@auth.login_required
def before_request():
    """请求前会调用

    过滤掉未经确认的账户

    :return: 未经确认error Json
    """
    if g.current_user.is_anonymous:
        return unauthorized('Invalid credentials')
    elif not g.current_user.confirmed:
        return forbidden('Unconfirmed account')


@api.route('/token')
def get_token():
    """获取本用户的认证token

    以*账号密码*成功登陆的用户才能获取token。即不允许通过token获取新token以延长token的生存时间。

    :return:
    """
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(
        expiration=3600), 'expiration': 3600})
