#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import time
import datetime


def time_strftime():
	return time.strftime('%Y-%m-%d %H:%M:%S')


def datetime_strftime():
	return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
