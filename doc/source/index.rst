.. tsxyAssistant documentation master file, created by
   sphinx-quickstart on Thu Jul 27 13:43:44 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

欢迎查看《唐小二》文档
======================

《唐小二》，做唐院师生的好帮手。

.. toctree::
     usage.rst
     api.rst
     data.rst

E-R图

.. uml::
   
  @startuml
   
  'style options 
  skinparam monochrome true
  skinparam circledCharacterRadius 9
  skinparam circledCharacterFontSize 8
  skinparam classAttributeIconSize 0
  hide empty members

  entity Role < 角色 > << Entity >>{
   + id  自增id
   + name  角色名
   + default  是否为账号创建时默认角色
   + permissions  权限表
  }

  entity User < 用户 > << Entity >>{
    + id  自增id
    + school_code  学号(十位数字)
    + user_code  教务处查询代码
    + username  用户名
    + name  真实姓名
    + about_me  个人简介
  }
  
  Role "1" -- "*" User : 属于

  entity Course < 课程 > << Entity >>{
    + id  自增id
    + when_code  上课时间代码
    + week  上课周次
    + parity  单双周属性
    + which_room  上课教室
    + where  上课位置
  }

  User "1" -- "*" Course : 一位教师可负责多个课程\n一节课程只能由一位教师负责
  User "n" -- "m" Course : 代课

  entity RawCourse < 原课程 > << Entity >>{
    + id  自增id
    + name  原课程名
    + nickname  课程名昵称
    + course_code  课程代码
    + worth  学分
  }

  RawCourse "1" -- "*" Course : 一个原课程\n可具体化为多个课程

  entity School < 学校 > << Entity >>{
    + id  自增id
    + name  校名
    + school_code  学校代号
  }

  entity Department < 院系部 > << Entity >>{
    + id  自增id
    + name  部门名称
    + department_code  院系部代码
  }

  School "1" -- "*" Department : 属于

  entity Specialty < 专业 > << Entity >>{
    + id  自增id
    + name  专业名
    + specialty_code  专业代码
  }

  Department "1" -- "*" Specialty: 属于

  entity _Class < 班级 > << Entity >>{
    + id  自增id
    + name  班级名
    + class_code  班级代码
  }

  _Class "*" -- "1" Specialty : 属于
  _Class "*" -- "1" User : 在
  _Class "n" -- "m" Course : 注册

  @enduml

Indices and tables
==================

* :ref:`search`
