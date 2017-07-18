# coding=utf-8
from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission


def permission_required(permission):
    """权限检测修饰器 如果没有该权限，报403错误

    :param permission: 检测是否拥有该权限
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """权限检测修饰器 检测是否拥有管理员权限"""
    return permission_required(Permission.ADMINISTER)(f)
