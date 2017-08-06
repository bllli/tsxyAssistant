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
from flask import current_app, url_for, abort
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash

from app.exceptions import ValidationError
from . import db, login_manager


class Operation:
    ADD = 0x01
    REMOVE = 0x02


class Permission:
    """权限类 用于规定权限的二进制数值"""
    VIEW_SCHEDULE = 0x01  #: 查看课程表
    VIEW_SCORE = 0x02  #: 查看成绩
    VIEW_ALL_SCHEDULE = 0x04  #: 查看所有人的课程表
    VIEW_ALL_SCORE = 0x08  #: 查看所有人的成绩
    MODIFY = 0x0f  #: 编辑权限
    ADMINISTER = 0x80  #: 管理员权限

    student = VIEW_SCHEDULE | VIEW_SCORE
    teacher = VIEW_ALL_SCHEDULE | VIEW_ALL_SCORE
    teacher_v = VIEW_ALL_SCHEDULE | VIEW_ALL_SCORE | MODIFY
    administrator = 0xff

    @staticmethod
    def to_json():
        json_permission = {}
        for member in dir(Permission):
            value = eval('Permission.' + member)
            if isinstance(value, int):
                json_permission[member] = value
        return json_permission


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
            'Student': (Permission.student, True),
            'Teacher': (Permission.teacher, False),
            'Teacher_V': (Permission.teacher_v, False),
            'Administrator': (Permission.administrator, False),
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

    @staticmethod
    def to_json():
        """角色json"""
        return {
            'roles': [{
                'name': role.name,
                'permissions': role.permissions
            } for role in Role.query.all()]
        }


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


enrollments = db.Table('enrollments',
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
                              secondary=enrollments,
                              backref=db.backref('classes', lazy='dynamic'),
                              lazy='dynamic')
    """班级与课程的多对多关系定义"""

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
        # type: (str, str, object ) -> None
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


class RawCourse(db.Model):
    """原课程

    抽象的课程概念。如不同年级、不同专业、不同教师所教授的“毛概”都是毛概课
    """
    __tablename__ = 'raw_courses'
    id = db.Column(db.Integer, primary_key=True)  #: 原课程id
    name = db.Column(db.String(128))  #: 课程名
    nickname = db.Column(db.String(128))  #: 课程昵称 如“毛泽东思想与中国特色社会主义理论体系概论”昵称为“毛概”
    course_code = db.Column(db.String(16))  #: 课程代号

    worth = db.Column(db.String(2))  #: 学分

    courses = db.relationship('Course', backref='raw_course', lazy='dynamic')

    def to_json(self):
        raw_course_json = {
            'id': self.id,
            'name': self.name,
            'nickname': self.nickname,
            'course_code': self.course_code,
            'worth': self.worth,
            'url': url_for('api.get_raw_courses_by_id', id=self.id, _external=True),
        }
        return raw_course_json

    @staticmethod
    def from_json(json_post):
        name = json_post.get('name')
        nickname = json_post.get('nickname')
        course_code = json_post.get('course_code')
        worth = json_post.get('worth')
        if name is None or name == '' or course_code is None or course_code == '':
            raise ValidationError('Must have name and course_code')
        return RawCourse(name=name, nickname=nickname, course_code=course_code, worth=worth)


substitutes = db.Table('substitutes',
                       db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                       db.Column('course_id', db.Integer, db.ForeignKey('courses.id')),
                       )


class Course(db.Model):
    """课程

    具体的课程，包含上课时间地点周次、哪位老师负责、上课涉及班级等具体信息
    """
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)  #: 课程id
    when_code = db.Column(db.String(32))  #: 上课时间代号
    week = db.Column(db.String(64))  #: 上课周次
    week_raw = db.Column(db.String(32))  #: 未解析的上课周次
    parity = db.Column(db.String(32))  #: 单双周属性
    which_room = db.Column(db.String(32))  #: 上课教室
    where = db.Column(db.String(32))  #: 上课校区

    raw_course_id = db.Column(db.Integer, db.ForeignKey('raw_courses.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    substitute_teachers = db.relationship('User',
                                          secondary=substitutes,
                                          backref=db.backref('guest_courses', lazy='dynamic'),
                                          lazy='dynamic')

    def __init__(self, teacher, raw_course, **kwargs):
        super(Course, self).__init__(**kwargs)
        self.teacher = teacher
        self.raw_course = raw_course

    @staticmethod
    def is_safety(string):
        # type: (str) -> bool
        allow_chr = [' ', ',', '[', ']', ',', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        try:
            for each in string:
                if each not in allow_chr:
                    raise ValueError("含有非安全字符")
            return True
        except ValueError:
            return False

    def to_json(self):
        if self.week is not None and Course.is_safety(self.week):
            week = eval(self.week)
        else:
            week = None
        course_json = {
            'id': self.id,
            'when_code': self.when_code,
            'week': week,
            'week_raw': self.week_raw,
            'parity': self.parity,
            'which_room': self.which_room,
            'where': self.where,
            'raw_course_id': self.raw_course.id,
            'name': self.raw_course.name,
            'nickname': self.raw_course.nickname,
            'teacher_id': self.teacher_id,
            'teacher': self.teacher.name,
            'url': url_for('api.get_courses_by_id', id=self.id, _external=True),
        }
        return course_json

    @staticmethod
    def from_json(post_json):
        when_code = post_json.get('when_code')
        week = post_json.get('week')
        if when_code is None or week is None:
            raise ValidationError("必须含有上课时间(when_code)、上课周次(week)")
        week_str = str(week)
        if week_str is not None and Course.is_safety(week_str):
            week = week_str
        else:
            abort(400, u"week字段中有错误")
        week_raw = post_json.get('week_raw')
        parity = post_json.get('parity')
        which_room = post_json.get('which_room')
        where = post_json.get('where')
        raw_course_id = post_json.get('raw_course_id')
        teacher_id = post_json.get('teacher_id')

        raw_course = RawCourse.query.get_or_404(raw_course_id)
        teacher = User.query.get_or_404(teacher_id)

        return Course(teacher, raw_course, when_code=when_code, week=week, week_raw=week_raw,
                      parity=parity, which_room=which_room, where=where)

    def operate_classes(self, operation, _classes):
        # type: (int, list) -> None
        """为课程添加/删除上课班级

        :param operation: 执行的操作 应为Operation类中的类变量
        :param list _classes: _Class 班级对象 列表
        """
        for each in _classes:
            if operation is Operation.ADD:  # 向课程中新增班级
                self.classes.append(each)
            elif operation is Operation.REMOVE:  # 从课程中删除班级
                self.classes.remove(each)
        db.session.add(self)
        db.session.commit()

    def appoint_substitute_teacher(self, operation, users):
        # type: (int, list) -> None
        """指定代课教师

        课程负责教师、代本课的教师、教务处管理教师 能指定代课教师
        """
        for each in users:
            if operation is Operation.ADD:
                self.substitute_teachers.append(each)
            elif operation is Operation.REMOVE:
                self.substitute_teachers.remove(each)
        db.session.add(self)
        db.session.commit()


class User(UserMixin, db.Model):
    """用户model"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    school_code = db.Column(db.String(16), unique=True, index=True)  #: 学号
    user_code = db.Column(db.String(16), unique=True, index=True)  #: 教务系统用户代号
    username = db.Column(db.String(64), unique=True, index=True)  #: 用户名(自拟)
    name = db.Column(db.UnicodeText(64))  #: 姓名
    about_me = db.Column(db.Text())  #: 个人简介

    password_hash = db.Column(db.String(128))  #: (加密过的)密码
    confirmed = db.Column(db.Boolean, default=False)  #: 通过确认

    member_since = db.Column(db.DateTime(), default=datetime.utcnow)  #: 账号注册时间
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)  #: 最后登录时间

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))  #: 所属角色
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))  #: 所属班级

    courses = db.relationship('Course', backref='teacher', lazy='dynamic')  #: 教师负责的课程

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

        :return: 用户信息json
        """
        role = self.role
        json_user = {
            'id': self.id,
            'url': url_for('api.get_user', id=self.id, _external=True),
            'school_code': self.school_code,
            'username': self.username,
            'member_since': localtime(self.member_since),
            'last_seen': localtime(self.last_seen),
            'role': role.name,
            'permissions': role.permissions,
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
