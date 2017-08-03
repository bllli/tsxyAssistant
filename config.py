# -*- coding:utf-8 -*-
"""配置文件

保存了项目需要的配置信息、密码及管理员邮箱等信息。

不要填写明文数据，应设置环境变量。
"""
import os

#: 本文件的绝对路径。 用于决定SQLite2数据库文件存储位置
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """设置类

    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'  #: 加密字符串
    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    # """sqlalchemy配置 """
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.googlemail.com'  #: 邮件配置 邮件服务器(str)
    MAIL_PORT = 587  #: 邮件配置 邮件服务器端口
    MAIL_USE_TLS = True  #: 邮件配置
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  #: 邮件配置 邮件用户名
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  #: 邮件配置
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'  #: 主题前缀
    FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'  #: 发送人签名
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')  #: 管理员邮箱
    FLASKY_POSTS_PER_PAGE = 20  #: 每页推文数
    FLASKY_FOLLOWERS_PER_PAGE = 50  #: 每页粉丝数
    FLASKY_COMMENTS_PER_PAGE = 30  #: 每页评论数

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True  #: 开启调试模式
    #: 数据库URI
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True  #: 开启测试模式
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    WTF_CSRF_ENABLED = False
    #: 数据库URI
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    #: 数据库URI
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
