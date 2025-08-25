#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: idp_backend celeryconfig
# CREATE_TIME: 2024/3/26 10:38
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note:
task_routes = {
    'tasks.hello': 'low-priority',
}