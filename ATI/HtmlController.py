#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: leeyoshinari

import os
import time
from common.config import getConfig
from common.UploadFDFS import upload_file, upload_by_buffer


class HtmlController(object):
	def __init__(self):
		self.index = 0
		self.name = getConfig('htmlTitle')
		self.title = '<h2 align="center">{}</h2>'.format(self.name)
		self.path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static/result')
		self.html = '<html><head><meta http-equiv="Content-Type";content="text/html";charset="utf-8">{}</head><body>{}</body></html>'
		self.overview = '<h3>本次执行情况</h3><table width="100%" cellspacing="0" cellpadding="6" border="1" ' \
						'align="center"><tbody><tr><th>用例总数</th><th>用例执行成功数</th><th>用例执行失败数</th>' \
						'<th>执行总耗时</th><th>执行成功率</th></tr><tr><td align="center">{}</td><td align="center">' \
						'{}</td><td align="center">{}</td><td align="center">{:.2f} s</td><td align="center">{:.2f}%</td>' \
						'</tr></tbody></table>'
		self.overview1 = '<h3 style="margin-top: 50px;">历史执行情况</h3><table width="100%" cellspacing="0" ' \
						 'cellpadding="6" border="1" align="center"><tbody><tr><th>累计执行次数</th>' \
						 '<th>累计执行用例数</th><th>累计失败用例数</th><th>累计执行用时</th><th>执行成功率</th>' \
						 '</tr><tr><td align="center">{}</td><td align="center">{}</td><td align="center">{}</td>' \
						 '<td align="center">{}</td><td align="center">{:.2f}%</td></tr></tbody></table>'
		self.fail1 = '<h3 style="margin-top: 50px;">本次执行失败用例详情</h3><p>如需查看所有用例测试结果，<a href="{}" target="_blank">请点我</a></p>'     # 如果有失败的用例
		self.fail2 = '<p style="margin-top: 50px;">如需查看本次所有用例测试结果，<a href="{}" target="_blank">请点我</a></p>'        # 如果所有用例都成功
		self.success = '<h3 style="margin-top: 50px;">本次测试结果详情</h3>'      # 测试结果详情
		self.table = '<table width="100%" border="1" cellspacing="0" cellpadding="6" align="center" ' \
					 'style="table-layout:fixed; word-wrap:break-word;>{}</table>'      # 表格
		self.table_head = '<tr bgcolor="#99CCFF" align="center">' \
						  '<th width="10%">用例ID</th>' \
						  '<th width="30%">请求接口</th>' \
						  '<th width="20%">请求参数</th>' \
						  '<th width="15%">响应值</th>' \
						  '<th width="5%">响应时间</th>' \
						  '<th width="5%">测试结果</th>' \
						  '<th width="15%">失败原因</th></tr>'    # 表头，如需定制化测试报告，请修改表头
		self.tr = '<tr>{}</tr>'    # 表格中的每一行
		self.td = '<td>{}</td>'    # 每一个单元格
		self.td_reason = '<td><div class="tooltiper">{}<span class="tooltiptext">{}</span></div></td>'
		self.td_fail = '<td><font color="red">Failure</font></td>'      # 失败用例测试结果红色展示
		self.td_success = '<td><font color="blue">Success</font></td>'    # 成功用例测试结果蓝色展示
		self.last = '<p style="color:blue">此邮件自动发出，请勿回复。</p>'        # 最后一句话
		self.css = '<style>.tooltiper {display: inline-block;color: red;}.tooltiper .tooltiptext {display: none;' \
				   'visibility: hidden;right: 12%;max-width: 60%;background-color: #ff0000;color: #ffffff;' \
				   'text-align: left;padding: 5px 5px;border-radius: 6px;position: absolute;z-index: 1;}' \
				   '.tooltiper:hover .tooltiptext {visibility: visible;display: block;}</style>'

		self._fail_case = []
		self._all_case = []

		if not os.path.exists(self.path):
			os.mkdir(self.path)

	@property
	def all_case(self):
		return self._all_case

	@all_case.setter
	def all_case(self, value):
		case_id = self.td.format(value['case_id'])
		case_name = self.td.format(value['case_name'])
		url = self.td.format(value['url'])
		method = self.td.format(value['method'])
		param = self.td.format(value['param'])
		response = self.td.format(value['response'])
		response_time = self.td.format(str(value['response_time']) + ' ms')
		if value['result'] == 'Failure':
			result = self.td_fail.format(value['result'])
		else:
			result = self.td_success.format(value['result'])

		if value['reason']:
			reason = self.td_reason.format(value['reason'], value['logger'])
		else:
			reason = self.td.format(value['reason'])

		# 把所有结果写到一行里
		# 如需定制化测试报告，可在此修改
		res = self.tr.format('{}{}{}{}{}{}{}'.format(case_id, url, param, response, response_time, result, reason))

		if value['result'] == 'Failure':    # 失败用例单独存储，用于发送邮件
			self._fail_case.append(res)

		self._all_case.append(res)

	def write_html(self, start_time, end_time, total_res):
		"""
			生成html测试报告
		"""
		test_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))
		test_time = f'<p align="right">测试时间：{test_time}</p>'
		fail_case_num = len(self._fail_case)    # 失败用例数
		all_case_num = len(self._all_case)      # 所有用例数
		success_rate = (1 - fail_case_num / all_case_num) * 100     # 计算成功率
		spend_time = end_time - start_time      # 测试花费总时间

		# 历史数据，加上本次数据
		total_res['times'] += 1
		total_res['case_num'] += all_case_num
		total_res['success_num'] += all_case_num - fail_case_num
		total_res['interval'] += spend_time

		total_time = total_res['interval'] if total_res['interval'] < 1800 else total_res['interval']/3600
		total_time = f'{total_time:.2f} s' if total_res['interval'] < 1800 else f'{total_time:.2f} h'

		# 把所有用例连接起来，拼成完整的表格
		fail_rows = ''.join(self._fail_case)
		all_rows = ''.join(self._all_case)

		# 失败用例表格和所有用例表格分开保存
		fail_table = self.table.format('{}{}'.format(self.table_head, fail_rows))
		all_table = self.table.format('{}{}'.format(self.table_head, all_rows))

		# 测试结果概览详情
		detail = self.overview.format(all_case_num, all_case_num-fail_case_num, fail_case_num, spend_time, success_rate)
		detail1 = self.overview1.format(total_res['times'], total_res['case_num'], total_res['case_num']-total_res['success_num'], total_time, total_res['success_num']/total_res['case_num']*100)
		# 测试报告标题
		header = '{}{}{}{}'.format(self.title, test_time, detail, detail1)

		# 生成所有用例测试报告
		all_html = self.html.format(self.css, '{}{}{}'.format(header, self.success, all_table))

		# 将所有用例测试报告保存到本地
		html_path = os.path.join(self.path, self.name + str(int(start_time)) + '.html')
		with open(html_path, 'w') as f:
			f.writelines(all_html)

		# 获取访问地址
		if getConfig('isFDFS') == '1':
			remote_path = f"{getConfig('FDFSURL')}{upload_file(html_path)}"
		else:
			_, name = os.path.split(html_path)
			remote_path = f"http://{getConfig('host')}:{getConfig('port')}/static/result/{name}"

		# 根据成功率决定邮件正文内容，生成失败用例测试报告
		if success_rate == 100:
			flag = 1
			fail_html = self.html.format('', '{}{}{}'.format(header, self.fail2.format(remote_path), self.last))
		else:
			flag = 0
			fail_html = self.html.format(self.css, '{}{}{}{}'.format(header, self.fail1.format(remote_path), fail_table, self.last))

		result = {
			'start_time': time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime(start_time)),
			'success_case_num': all_case_num - fail_case_num,
			'all_case_num': all_case_num,
			'interval': spend_time,
			'remote_path': remote_path,
		}

		return fail_html, flag, result

	def __del__(self):
		pass
