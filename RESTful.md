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


## 学校结构
### 学校结构json
json实例:[文件过大, 请点击链接查看](example/Structure.json)

```json
{
  "cache": true,
  "cache-date": "2017-06-01 10:45:39 CST",
  "school_years": [
    {
      "year": "2013",
      "departments": [
        {
          "code": "31",
          "name": "机电工程系",
          "specialties": [
            {
              "code": "0105",
              "name": "机械设计制造及其自动化",
              "classes": [
                {
                  "code": "2013010501",
                  "name": "13机本1"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

> 按现在抓取的数据分析来看, 各个年级的院系部代码和专业代码都是不变的.  
> 但为稳妥起见(以防抽风改成不一致), 仍按照教务系统原有的从年份开始设计json.  
> 学校-年份-系别(院系部)-专业-班级.  
> classes = {'name': '14计本1', 'code': '2014020601'}  
> specialty = {'name': '计算机专业与技术', 'code': '4001', 'classes': [c1, c2...]}  
> department = {'name': '计算机专业与技术系', 'code': '40', 'specialties': [s1, s2...]}  
> school_year = {'year': '2014', 'departments': [department1, department2...]}  
> school = {'school_years': [school_year1, school_year2...]}

### 字段解释
#### json主体
字段名|字段说明|类型|备注
---|---|---|---
*cache*|是否使用了缓存|布尔|true/false
*cache-date*|缓存时间|string|
school_years|学年|列表|

#### 学年json
字段名|字段说明|类型|备注
---|---|---|---
year|学年|string|四位年
departments|该学年的系|列表|目前每个学年的系都一样

#### 系别json
字段名|字段说明|类型|备注
---|---|---|---
code|系别代号|string|貌似都是两位数字
name|系名称|string|
specialties|该系的专业|列表|

#### 专业json
字段名|字段说明|类型|备注
---|---|---|---
code|专业代号|string|貌似都是四位数字
name|专业名称|string|
classes|该专业下的班级|列表|

#### 班级json
字段名|字段说明|类型|备注
---|---|---|---
code|班级代号|string|貌似都是十位数字
name|班级名称|string|

## 学年学期信息
### 学年学期json
```json
{
  "school_year": "2016",
  "semester": "1"
}
```
### 字段解释
字段名|字段说明|类型|备注
---|---|---|---
school_year|学年|string|"2016" 意为：“2016-2017学年”
semester|学期|string|"1" 意为下半学期; "0" 意为上半学期

## 成绩数据
### 成绩数据json
成绩数据json实例: [文件过大，请点击链接查看](example/Score.json)
```json
{
  "department": "计算机科学与技术系",
  "major": "14计本1",
  "stu_id": "4140206139",
  "user_code": "201400000407"
  "score_tables": [
    {
      "semester": "2014-2015学年第一学期",
      "scores": [
        {
          "exam_method": "考试",
          "get_method": "初修取得",
          "id": "1",
          "name": "大学英语A（一）",
          "ps": "",
          "quale": "初修",
          "score": "70.0",
          "type": "公共课/必修课",
          "worth": "4.0"
        },
        ...
      ]
    },
    ...
  ],
}

### 字段解释
#### json主体
字段名|字段说明|类型|备注
---|---|---|---
department|系别|string|
major|班级代号（年级专业班级一体）|string|
stu_id|学号|string|
user_code|用户编号|string|
score_tables|成绩表|列表|按学期分隔的成绩表

#### 成绩表json
字段名|字段说明|类型|备注
---|---|---|---
semester|学期|string|当前成绩表的学期
scores|分数|列表|

#### 分数json
字段名|字段说明|类型|备注
---|---|---|---
id|在成绩表中的编号|string|没啥用，可以不解析
name|课程名|string|
worth|学分|string|
type|课程类别|string|公共课、必修课
quale|修读性质|string|初修/重修
exam_method|考核方式|string|考试/考察
get_method|取得方式|string|初修取得
score|成绩|string|分数/合格
ps|备注|string|一般都是空

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
### 请求类型
HTTP GET
### 请求参数
参数名(key)|说明|value示例|备注
---|---|---|---
use_cache|是否使用缓存|False 或 True|当值为False时, 不使用服务端缓存.不填写或其他任意值均为使用缓存
stu_id|学号|学生学号|

如需不使用缓存, 直接获取新课程表, url加上参数 "use_cache=False" 如 `v1.0/schedule/get-schedule?use_cache=False`  
如需指定查询学号的课表, 在url上加参数 "stu_id=学号" 如 `api/v1.0/schedule/get-schedule?stu_id=0000000000`
### 正确返回json
操作正确即返回[课程json](#课程表json)

## 获取学校结构
这是一大坨数据, 100K左右, 请注意缓存使用
### 请求地址 
`v1.0/school/get-structure`
### 接口描述
获取学校结构Json
### 请求类型
HTTP GET
### 请求参数
如需不使用服务端缓存, 请在url后加上参数 "?use_cache=False"

参数名(key)|说明|value示例|备注
---|---|---|---
use_cache|是否使用缓存|False|当值为False时, 不使用服务端缓存.不填写或其他任意值均为使用缓存
### 正确返回json
[学校结构json](#学校结构json)

## 获取学期学年信息
### 请求地址
`v1.0/school/get-semester`
### 接口描述
获取当前学年、学期Json
### 请求类型
HTTP GET
### 请求参数
无
### 正确返回json
[学年学期json](#学年学期json)

## 通过登录信息获取当前用户的成绩信息
### 请求地址
`v1.0/score`
### 接口描述
通过 HTTP Basic Auth 获取该用户的成绩信息
### 请求类型
HTTP GET
### 请求参数
参数名(key)|说明|value示例|备注
---|---|---|---
score_type|分数类型|all new|all 表示全部成绩， new 表示最新成绩

### 正确返回json
[成绩数据json](#成绩数据json)

### 异常返回json
该用户没有用户代号 http相应码404
以现在登录方式来说， 这是一个不应该出现的错误
```json
{
    "error": "该用户没有用户代号"
}
```

教务系统出现网络问题 http响应吗502
```json
{
    "error": "教务系统出现网络问题"
}
```
