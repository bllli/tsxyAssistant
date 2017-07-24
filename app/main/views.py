# -*- coding: utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from flask import render_template
from . import main


@main.route('/', methods=['GET'])
def index():
    return render_template("index.html")
