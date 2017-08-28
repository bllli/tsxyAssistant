Api
===

采用RESTful API进行后端与安卓端、前端的交互。

.. toctree::
    api/system.rst
    api/user.rst
    api/course.rst
    api/score.rst
    api/school.rst
    api/schedule.rst
    api/check_in.rst

需要注意的是前端与后端使用mvvm框架交互时，可能会遇到CORS跨域资源共享问题，将

app/api_1_0/__init__.py::

    # CORS(api, origins=['http://bllli.cn'], supports_credentials=True)
    # 改为
    CORS(api, origins=['http://your_domain.com'], supports_credentials=True)
    # 或
    CORS(api, origins=['*'], supports_credentials=True)

