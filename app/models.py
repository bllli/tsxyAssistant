# -*- coding:utf-8 -*-
"""models.py

用于定义ORM中用到的类、关系及某些表中的初始数据及工具函数。

新建数据库时应该依次调用::

    Role.insert_roles()
    School.insert_school_structure()

Attributes:

"""
from datetime import datetime

import tsxypy
from flask import current_app, url_for
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash

from . import db, login_manager


class Permission:
    """权限类 用于规定权限的二进制数值"""
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    """角色类
    每个用户的身份信息、 权限
    """
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        """向角色表插入角色数据
        :return: N/A
        """
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class School(db.Model):
    __tablename__ = 'schools'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    school_code = db.Column(db.String(16))

    departments = db.relationship('Department', backref='school', lazy='dynamic')

    def __repr__(self):
        return '<School %r>' % self.name

    @staticmethod
    def insert_school_structure():
        """使用抓取到的学校院系部结构生成表结构
        :return: N/A
        """
        import os
        base_dir = os.getcwd()
        tmp_dir = os.path.join(base_dir, 'tmp')
        school_file_dir = os.path.join(tmp_dir, 'school_dict')
        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)
        if os.path.exists(school_file_dir):
            with open(school_file_dir) as f:
                import pickle
                school_dict = pickle.load(f)
        else:
            sc = tsxypy.ScheduleCatcher()
            school_dict = sc.get_school_json()
            with open(school_file_dir, 'w') as f:
                import pickle
                pickle.dump(school_dict, f)
        for school_year in school_dict['school_years']:
            print(school_year['year'])
            for department in school_year['departments']:
                print("Dict: code:%s, name:%s in" % (department['code'], department['name']))
                d = Department.query.filter_by(department_code=department['code']).first()
                if not d:
                    d = Department(name=department['name'], department_code=department['code'])
                    db.session.add(d)
                    db.session.commit()
                else:
                    print("DB: already in db code:%s, name:%s" % (d.department_code, d.name))
                for specialty in department['specialties']:
                    print("Dict: code:%s, name:%s in" % (specialty['code'], specialty['name']))
                    s = Specialty.query.filter_by(specialty_code=specialty['code']).first()
                    if not s:
                        s = Specialty(name=specialty['name'], specialty_code=specialty['code'])
                        s.department = d
                        db.session.add(s)
                        db.session.commit()
                    else:
                        print("DB: already in db code:%s, name:%s" % (s.specialty_code, s.name))
                    for _class in specialty['classes']:
                        print("Dict: code:%s, name:%s in" % (_class['code'], _class['name']))
                        c = _Class.query.filter_by(class_code=_class['code']).first()
                        if not c:
                            c = _Class(name=_class['name'], class_code=_class['code'])
                            c.specialty = s
                            db.session.add(c)
                            db.session.commit()
                        else:
                            print("DB: already in db code:%s, name:%s" % (c.class_code, c.name))


class Department(db.Model):
    """学院/系别/部门"""
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    department_code = db.Column(db.String(16))

    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'))
    specialties = db.relationship('Specialty', backref='department', lazy='dynamic')

    def __repr__(self):
        return '<Department %r>' % self.name


class Specialty(db.Model):
    """专业"""
    __tablename__ = 'specialties'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    specialty_code = db.Column(db.String(16))

    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    classes = db.relationship('_Class', backref='specialty', lazy='dynamic')

    def __repr__(self):
        return '<Specialty %r>' % self.name


registrations = db.Table('registrations',
                         db.Column('course_id', db.Integer, db.ForeignKey('courses.id')),
                         db.Column('class_id', db.Integer, db.ForeignKey('classes.id'))
                         )


class _Class(db.Model):
    """班级"""
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    class_code = db.Column(db.String(16))

    specialty_id = db.Column(db.Integer, db.ForeignKey('specialties.id'))
    students = db.relationship('User', backref='_class', lazy='dynamic')

    courses = db.relationship('Course',
                              secondary=registrations,
                              backref=db.backref('classes', lazy='dynamic'),
                              lazy='dynamic')

    def __repr__(self):
        return '<_Class %r>' % self.name


class Temp(db.Model):
    """缓存表 缓存字符串"""
    __tablename__ = 'temp'
    id = db.Column(db.Integer, primary_key=True)
    mark = db.Column(db.String)
    identify = db.Column(db.String)
    content = db.Column(db.Text)
    date = db.Column(db.DateTime(), default=datetime.utcnow)

    @staticmethod
    def set_temp(mark, identify, content):
        """放置缓存

        :param string mark: 标记 声明缓存的用途
        :param string identify: 用户标识 用于区分不同用户的缓存记录
        :param content: 内容 多为dict
        :return: None
        """
        temps = Temp.query.filter_by(mark=mark, identify=identify).all()
        for t in temps:
            db.session.delete(t)
        t = Temp(mark=mark, identify=identify, content=str(content))
        db.session.add(t)

    @staticmethod
    def get_temp(mark, identify):
        """取出缓存

        :param mark: 标记 声明缓存的用途
        :param identify: 指定用户标示
        :return: 之前缓存的对象 (default:None)
        """
        t = Temp.query.filter_by(mark=mark, identify=identify).first()
        if not t:
            return None
        delta = datetime.utcnow() - t.date
        if delta.days < 2:
            content = eval(t.content)
            if isinstance(content, type({})):
                content['cache'] = True
                content['cache-date'] = localtime(t.date)
            return content
        else:
            return None

    @staticmethod
    def set_schedule_cache_for_stu_id(stu_id, schedule):
        """缓存学号对应的课程表

        :param string stu_id: 学生学号
        :param dict schedule: 课程表词典
        :return: None
        """
        Temp.set_temp(mark='schedule_stu_id', identify=stu_id, content=schedule)

    @staticmethod
    def get_schedule_cache_for_stu_id(stu_id):
        """通过学号获取缓存的课程表

        :param string stu_id: 学生学号
        :return: 课程表dict 无缓存或缓存过期则返回None
        """
        return Temp.get_temp(mark='schedule_stu_id', identify=stu_id)

    @staticmethod
    def set_school_structure(school_structure):
        Temp.set_temp(mark='school_structure', identify=None, content=school_structure)

    @staticmethod
    def get_school_structure():
        return Temp.get_temp(mark='school_structure', identify=None)


class Course(db.Model):
    """课程

    Args:
        id (int): 课程编号.

    :argument id:
    """
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    course_code = db.Column(db.String(16))

    when_code = db.Column(db.String(32))
    worth = db.Column(db.String(2))
    week = db.Column(db.String(32))
    parity = db.Column(db.String(32))
    which_room = db.Column(db.String(32))
    where = db.Column(db.String(32))

    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class User(UserMixin, db.Model):
    """用户model"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    school_code = db.Column(db.String(16), unique=True, index=True)  # 学号
    user_code = db.Column(db.String(16), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64))
    about_me = db.Column(db.Text())

    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)

    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))

    courses = db.relationship('Course', backref='teacher', lazy='dynamic')

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def to_json(self):
        """将本对象转换为json

        ============ ============= ==== ====
        字段名       字段说明      类型 备注
        ============ ============= ==== ====
        id           用户id        int
        username     用户昵称       str  允许为空
        url          用户信息url    str
        school_code  学号          str  10位数字
        member_since 注册时间       str
        last_seen    上次访问时间    str
        ============ ============= ==== ====

        :return: 用户信息json
        """
        json_user = {
            'id': self.id,
            'url': url_for('api.get_user', id=self.id, _external=True),
            'school_code': self.school_code,
            'username': self.username,
            'member_since': localtime(self.member_since),
            'last_seen': localtime(self.last_seen),
        }
        return json_user

    def generate_auth_token(self, expiration):
        """生成认证token

        :param expiration: 生存期 单位为秒
        :return:
        """
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        """验证认证token

        :param token: 之前获取的token
        :return: 如通过验证，返回登录用户的对象
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    """陌生人

    没有任何权限
    """
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def localtime(utc_time):
    """获取utc时间转换为的亚洲时间

    :param utc_time: utc时间
    :return: 亚洲时间
    """
    if not isinstance(utc_time, type(datetime.utcnow())):
        return None
    from pytz import timezone
    local_time = utc_time.replace(tzinfo=timezone('UTC')).astimezone(timezone('Asia/Chongqing'))
    return local_time.strftime('%Y-%m-%d %H:%M:%S %Z')
