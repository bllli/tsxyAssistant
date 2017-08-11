# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from flask import render_template
from . import main


@main.route('/', methods=['GET'])
def index():
    return render_template("index.html")
