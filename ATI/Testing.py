#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: leeyoshinari

import os
import re
import json
import time
import logging
import traceback
from ATI.request import Request
from ATI.readCase import read_scene, read_variable, read_setting
from ATI.HtmlController import HtmlController
from user.models import Results
from common.EmailController import sendMsg
from common.config import getConfig
from common.compare import compare


logger = logging.getLogger('django')

class Testing(object):
	def __init__(self, args):
		self.request = Request()
		self.html = HtmlController()
		self.global_variable = read_variable(args[1])
		self.scenes = read_scene(args[1])
		self.plan_setting = read_setting(args[1])

		self.is_send_email = getConfig('isSendEmail')

		self.test_result = {}

		self.run(args)

	def run(self, args):
		logger.info('开始测试')
		r = Results.objects.get(id=args[0])
		r.status = 2
		r.start_time = time.strftime('%Y-%m-%d %H:%M:%S')
		r.save()

		start_time = time.time()
		try:
			for case in self.scenes:      # 遍历所有用例
				response_time = 0
				try:
					if case['pre_process']:		#前置处理器
						self.processor(case['pre_process'])

					# 替换变量
					case['url'] = self.compile(case['url'])
					case['param'] = self.compile(case['param'])

					logger.info(f"正在执行用例{case['case_id']}-->{case['case_name']}-->{case['url']}")

					res = self.request.request(url=case['url'], method=case['method'], data=case['param'], headers=case['header'], timeout=case['timeout'])
					logger.debug(f"{case['case_id']}-->{case['url']}-->{res.content.decode()}")

					if res.status_code == 200:      # 如果响应状态码为200
						response = json.loads(res.content.decode())
						response_time = int(res.elapsed.microseconds / 1000)

						if case['assert_result']:        # 如果响应断言不为空
							flag = self.assert_result(case['assert_method'], case['assert_result'], response)

							if flag == 0:   # 断言失败
								result = 'Failure'
								reason = f"Assertion failure: text expected to {case['assert_method']} {case['assert_result']}"
								log_str = reason
							else:
								result = 'Success'
								reason = ''
								log_str = ''

						elif case['expect_result']:     # 如果响应断言为空，期望结果不为空，仅支持json格式
							flag, reason = compare().compare(json.loads(case['expect_result']), response)   # 逐个字段比较响应结果
							if flag == 0:
								result = 'Failure'
								log_str = reason
							else:
								result = 'Success'
								reason = ''
								log_str = ''

						else:       # 如果响应断言为空，且期望结果为空
							flag = 2
							result = 'Unknown'
							reason = 'Warning: Not verify the result'
							log_str = reason

						# 后置处理器，response已经是一个字典或列表了
						if flag > 0 and case['post_process']:
							self.processor(case['post_process'], response)

					else:       # 如果响应状态码不为200
						response = ''
						reason = f'Response status code is {res.status_code}'
						log_str = reason
						result = 'Failure'

				except Exception as err:
					response = ''
					result = 'Failure'
					reason = err
					log_str = traceback.format_exc()
					logger.error(log_str)

				# 拼接测试结果
				case_result = {
					'case_id': case['case_id'],
					'case_name': case['case_name'],
					'url': case['url'],
					'method': case['method'],
					'param': case['param'] if case['method'] == 'post' else '',
					'response': response if result != 'Success' else '',
					'response_time': response_time,
					'result': result,
					'reason': reason,
					'logger': log_str,
				}

				self.html.all_case = case_result    # 将测试结果组装成html

			end_time = time.time()


			logger.info('开始生成测试报告')
			# 读取历史数据
			total_res = {'times':0, 'case_num': 0, 'success_num': 0, 'interval': 0}
			plans = Results.objects.filter(plan_id=args[1])
			for p in plans:
				if p.status == 3:
					total_res['case_num'] += p.total_num
					total_res['success_num'] += p.success_num
					total_res['interval'] += p.interval
					total_res['times'] += 1

			fail_html, flag, test_res = self.html.write_html(start_time, end_time, total_res)    # 生成测试报告
			self.test_result.update(test_res)

			logger.info('开始发送邮件')
			if self.is_send_email == '1':   # 发送邮件
				if self.plan_setting['is_email'] == 1:
					is_send = 1
				elif self.plan_setting['is_email'] == 2 and flag == 0:
					is_send = 1
				elif self.plan_setting['is_email'] == 3 and flag == 1:
					is_send = 1
				else:
					is_send = 0
					logger.info('不满足发送邮件条件，不发邮件')

				if is_send:
					email = json.loads(self.plan_setting['email'])
					# 组装邮件体
					msg = {
						'subject': email['subject'],
						'smtp_server': getConfig('SMTP'),
						'sender_name': getConfig('senderNmae'),
						'sender_email': getConfig('senderEmail'),
						'password': getConfig('senderpassword'),
						'receiver_name': email['receiver_name'],
						'receiver_email': email['receiver_email'].split(','),
						'fail_test': fail_html,
					}
					sendMsg(msg, logger)    # 发送邮件
					logger.info('邮件发送成功')

			logger.info('测试完成')

			# 将本次测试结果写到数据库
			r = Results.objects.get(id=args[0])
			r.status = 3
			r.total_num = self.test_result['all_case_num']
			r.success_num = self.test_result['success_case_num']
			r.interval = self.test_result['interval']
			r.link = self.test_result['remote_path']
			r.save()

			del self.request, self.html, self.global_variable, self.scenes, self.plan_setting, self.test_result

		except Exception as err:
			logger.error(err)
			log_str = traceback.format_exc()
			logger.error(log_str)

			r = Results.objects.get(id=args[0])
			r.status = 5
			r.error_log = log_str
			r.save()
			del self.request, self.html, self.global_variable, self.scenes, self.plan_setting, self.test_result

	def processor(self, expression, response=None):
		"""
			前置和后置处理器
		"""
		pattern = '\${(.*?)}'
		res = re.findall(pattern, expression)  # 找出所有的字段
		input_str = res[0].split(',')
		output_str = res[1].split(',')

		input_dict = {'response': response}
		output_dict = {}
		for s in input_str:
			if s:
				input_dict.update({s: self.global_variable.get[s]})

		exec(expression, input_dict, output_dict)

		for s in output_str:
			if s:
				self.global_variable.update({s: output_dict[s]})


	def compile(self, data):
		"""
		替换变量
		"""
		pattern = '\${(.*?)}'  # 如果请求参数中有变量，则需要加${}，以表明是变量
		res = re.findall(pattern, data)  # 找出所有的变量
		for r in res:
			if isinstance(self.global_variable[r], list) or isinstance(self.global_variable[r], dict):
				new_str = json.dumps(self.global_variable[r])
			else:
				new_str = str(self.global_variable[r])

			data = data.replace('${' + r + '}', new_str)  # 将变量替换成真实值

		return data

	def assert_result(self, assert_method, assert_content, response):
		flag = 0
		if assert_method == 'contain':
			if assert_content in str(response):
				flag = 1
		if assert_method == 'contained':
			if str(response) in assert_content:
				flag = 1
		if assert_method == 'equal':
			if str(assert_content) == str(response):
				flag = 1
		if assert_method == 'unequal':
			if str(assert_content) != str(response):
				flag = 1

		return flag


	def __del__(self):
		pass
