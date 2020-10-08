#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: leeyoshinari

import json
import requests


class Request(object):
	def __init__(self):
		self.session = requests.Session()

	def get(self, url, timeout):
		"""get请求"""
		res = self.session.get(url=url, timeout=timeout)
		return res

	def post(self, url, data, headers, timeout, files):
		"""post请求"""
		try:
			res = self.session.post(url=url, data=data, headers=headers, files=files, timeout=timeout)
		except ValueError as err:
			res = self.session.post(url=url, data=json.loads(data), headers=headers, files=files, timeout=timeout)
		return res

	def request(self, url, method, data, headers, timeout, files=None):
		"""请求入口，目前仅支持get和post请求，其他请求可自行添加"""
		try:
			if method == 'get':
				res = self.get(url, timeout)
			elif method == 'post':
				res = self.post(url, data, headers, timeout, files)
			else:
				raise Exception('暂不支持其他请求方式')

			return res

		except:
			raise

	def __del__(self):
		pass
