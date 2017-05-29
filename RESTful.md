# RESTful API文档

# 数据
## 错误
### 错误信息Json
发生错误时, 返回Json示例如下:
```json
{
  "error": "错误类型",
  "message": "错误信息"
}
```
### 错误列表
错误名称|http状态码|错误类型
---|---|---
无法识别的请求|400|bad_request
未认证|401|unauthorized
权限不足|403|forbidden
找不到页面|404|not found

## 用户信息
### 用户信息Json
```json
{
  "id": 1,
  "last_seen": "2017-05-26 17:14:42 CST",
  "member_since": "2017-05-26 17:14:42 CST",
  "school_code": "4140200000",
  "url": "http://127.0.0.1:5000/api/v1.0/users/1",
  "username": null
}
```

字段解释

字段名|字段说明|类型|备注
---|---|---|---
id|用户id|int|
username|用户昵称|string|可能为空
url|用户信息url|string|
school_code|学号|string|十位纯数字
member_since|注册时间|string|
last_seen|上次访问时间|string|

时间格式化字符串为`%Y-%m-%d %H:%M:%S %Z`  
意为:年-月-日 24进制小时-分钟-秒数 时区代号

# API
## 通过用户id获取用户信息
### 请求地址 
`v1.0/users/<user-id>`
### 接口描述
获取用户信息 , 注意`<user-id>`代表需要填写的用户id
### 请求类型
HTTP GET
### 请求参数
参数名|类型|必填|描述|默认值|参考值
---|---|---|---|---|---
user-id|数字|Y|用户id|-|1

注意, url中的`<user-id>`应替换为user-id参数的值
### 正确返回Json
用户Json

## 通过登录信息获取用户信息
### 请求地址
`v1.0/users/myself`
### 接口描述
通过 HTTP Basic Auth 获取当前登录用户的用户信息
### 请求类型
HTTP GET
### 请求参数
无
### 正确返回json
操作正确即返回[用户json](#用户信息json)
### 错误返回json示例
see: [错误列表](#错误列表)

未通过 http basic auth 认证
```json
{
  "error": "unauthorized", 
  "message": "Invalid credentials"
}
```

账号密码有效， 但未通过认证
```json
{
  "error": "forbidden",
  "message": "Unconfirmed account"
}
```
