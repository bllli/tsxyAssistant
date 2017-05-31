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

## 课程表
### 课程表json
json实例: [文件过大, 请点击此链接查看](example/Schedule.json)

```json
{
  "class_code": null,
  "class_name": "14计本1",
  "department": null, 
  "grade": null, 
  "major": null, 
  "school_year": "2016", 
  "semester": "1",
  "courses": [
    {
      "name": "C#程序设计A", 
      "nickname": null, 
      "parity": null, 
      "teacher": "张铁军", 
      "week": [], 
      "week_raw": "1-7", 
      "when_code": "044", 
      "where": null, 
      "which_room": "A305", 
      "worth": null
    }, 
    ...
  ]
  
}
```

### 字段解释
#### json主体
字段名|字段说明|类型|备注
---|---|---|---
*cache*|是否使用了缓存|布尔|true/false
*cache-date*|缓存时间|string|
class_code|班级代码|string|
class_name|班级名|string|
department|院/系|string|
grade|||
major|专业|string|
school_year|学年|string|2016代表2016-2017学年
semester|学期|string|'0':上学期 '1'下学期
courses|课程|列表|
#### 课程json
字段名|字段说明|类型|备注
---|---|---|---
name|课程名称|string|
nickname|课程昵称|string|如"毛泽东思想和中国特色社会主义理论体系概论"的昵称为"毛概"
parity|单双周|string|"单周" "双周" 或null
teacher|教师姓名|string|
week|解析后的上课周次信息|列表|列表内为数字
week_raw|未解析的上课周次信息|string|如1-7代表1到7周, 
when_code|上课时间信息|string|三位数字,第一位为0, 第二位星期几, 第三位第几节 如044代表周四第四节 
where|上课位置|string|
which_room|上课教室|string|如:A305 
worth|学分|string|

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

## 通过登录信息获取课程表
### 请求地址 
`v1.0/schedule/get-schedule`
### 接口描述
通过 HTTP Basic Auth 获取课程表

课程表缓存:当两天内相同用户的课程表将不会从教务系统获取新的, 而是返回缓存的课程表.

如需直接获取新课程表, 请讲url换为 `v1.0/schedule/get-schedule-without-cache`
### 请求类型
HTTP GET
### 请求参数
无
### 正确返回json
操作正确即返回[课程json](#课程表json)
