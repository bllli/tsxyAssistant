用户接口
=================

通过用户id获取用户信息
------------------------

请求地址::

    v1.0/users/<user-id>

接口描述

  获取用户信息 , 注意`<user-id>`代表需要填写的用户id

请求类型

  HTTP GET

请求参数

    +---------+------+------+--------+--------+--------+
    | 参数名  | 类型 | 必填 | 描述   | 默认值 | 参考值 |
    +=========+======+======+========+========+========+
    | user-id | 数字 | Y    | 用户id | -      | 1      |
    +---------+------+------+--------+--------+--------+

    注意, url中的`<user-id>`应替换为user-id参数的值

正确返回Json

  用户Json :ref:`user_json`

获取本人的用户信息
-------------------------

请求地址::

    v1.0/users/myself

接口描述

  通过 HTTP Basic Auth 获取当前登录用户的用户信息

请求类型

  HTTP GET

请求参数

  无

正确返回json

  操作正确即返回 :ref:`user_json`

错误返回json示例

  see :ref:`error_json`

  未通过 http basic auth 认证::

      {
        "error": "unauthorized",
        "message": "Invalid credentials"
      }

  账号密码有效， 但未通过认证::

      {
        "error": "forbidden",
        "message": "Unconfirmed account"
      }
