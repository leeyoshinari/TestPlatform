#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: leeyoshinari

import json
import requests


class Request(object):
	def __init__(self):
		self.session = requests.Session()

	def get(self, url, headers, timeout):
		"""get请求"""
		res = self.session.get(url=url, headers=headers, timeout=timeout)
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
			if headers:
				headers = json.loads(headers)
			else:
				headers = None

			if method == 'get':
				res = self.get(url, headers, timeout)
			elif method == 'post':
				res = self.post(url, data, headers, timeout, files)
			else:
				raise Exception('暂不支持其他请求方式')

			return res

		except:
			raise

	def __del__(self):
		pass


def get(url):
	try:
		res = requests.get(url=url)
		return json.loads(res.content.decode())
	except:
		return {'code': 1, 'msg': '测试计划执行失败', 'data': None}
