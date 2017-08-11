# coding=utf-8
"""
error.py
====
错误处理
"""
from __future__ import absolute_import, unicode_literals
from flask import jsonify
from app.exceptions import ValidationError
from . import api


def bad_request(message):
    """错误的请求

    :param message:提示信息
    :return:包含提示信息及响应码的响应
    """
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):
    """未通过认证

    :param message:提示信息
    :return:包含提示信息及响应码的响应
    """
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response


def forbidden(message):
    """权限不足 或 被禁止的操作

    :param message:提示信息
    :return:包含提示信息及响应码的响应
    """
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


def bad_gateway(message):
    response = jsonify({'error': 'bad_gateway', 'message': message})
    response.status_code = 502
    return response


@api.errorhandler(ValidationError)
def validation_error(e):
    """出现访问错误时，Flask将自动调用该函数"""
    return bad_request(e.args[0])


@api.app_errorhandler(404)
def page_not_found(e):
    """调用abort(404)，即页面未找到错误时，将会自动执行该函数"""
    response = jsonify({'error': 'not found', 'message': e.description or 'not found'})
    response.status_code = 404
    return response


@api.app_errorhandler(401)
def unauthorized_handler(e):
    """调用abort(401)，即未认证错误时，将将自动执行该函数"""
    return unauthorized(e.description or "Invalid credentials")


@api.app_errorhandler(400)
def bad_request_handler(e):
    return bad_request(e.description or 'bad request')


@api.app_errorhandler(403)
def forbidden_handler(e):
    return forbidden(e.description or 'forbidden')


@api.app_errorhandler(502)
def bad_gateway_handler(e):
    return bad_gateway(e.description or 'bad gateway')
