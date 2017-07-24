# coding=utf-8
"""html to jinja2首席挖洞官

将本目录/子目录下的html文件中使用到的 *静态文件* 的URL改为使用jinja2 + flask url_for渲染

href="css/base.css" -> href="{{ url_for("static", filename="css/base.css") }}"

挖洞前会在文件同目录做一个.bak后缀名的备份文件。

Usage:
    $ cd my_project
    $ python2 translate.py

"""
from __future__ import print_function

import re
import os
import shutil

types = ['css', 'html']


# href="css/base.css"
# src="img/a39-1.png"


def bak(filename):
    """备份

    数据无价 谨慎操作

    :type filename: str 文件名
    """
    if os.path.exists(filename + ".bak"):
        return  # 如果已有备份文件 则不再重复生成备份文件
    if os.path.isfile(filename):
        shutil.copy(filename, filename + ".bak")


def rollback():
    """回滚

    暂时用不到 先不写了
    """
    pass


def translate(filename):
    with open(filename, 'r+') as f:
        replaced = re.sub(r'(href|src)="(css|img|font|js)/(.*?)"',
                          r'\g<1>="{{ url_for("static", filename="\g<2>/\g<3>") }}"', f.read())
        f.seek(0)
        f.write(replaced)


if __name__ == '__main__':
    for paths, subs, files in os.walk(os.getcwd()):
        # 遍历本路径下文件
        for filename in files:
            if filename.split('.')[-1] not in types:
                # 后缀名不在翻译后缀名列表中的，不进行翻译
                continue
            fullname = os.path.join(paths, filename)
            print("translating " + fullname)
            bak(fullname)
            translate(fullname)
