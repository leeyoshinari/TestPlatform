from django.db import models

# Create your models here.


class Variables(models.Model):
	name = models.CharField(max_length=50, default=None, verbose_name='变量名')
	value = models.CharField(max_length=50, default=None, verbose_name='变量值')
	project_id = models.CharField(max_length=50, default=None, verbose_name='变量对应的项目id')
	description = models.CharField(max_length=250, default=None, verbose_name='变量描述')
	created_by = models.CharField(max_length=20, default=None, verbose_name='创建人')
	updated_by = models.CharField(max_length=20, default=None, verbose_name='更新人')
	create_time = models.DateTimeField(verbose_name='创建时间')
	update_time = models.DateTimeField(verbose_name='更新时间')

	class Meta:
		db_table = 'ati_group_variable'


class Interfaces(models.Model):
	interface_id = models.CharField(max_length=50, default=None, verbose_name='接口id')
	project_id = models.CharField(max_length=20, default=None, verbose_name='接口所属的项目id')
	name = models.CharField(max_length=50, default=None, verbose_name='接口名称')
	interface = models.CharField(max_length=200, default=None, verbose_name='接口')
	protocol = models.CharField(max_length=10, default='http', verbose_name='接口协议')
	method = models.CharField(max_length=8, default='get', verbose_name='请求方法')
	parameter = models.CharField(max_length=200, default=None, verbose_name='请求参数')
	timeout = models.IntegerField(default=500, verbose_name='接口超时时间，单位毫秒')
	header = models.CharField(max_length=200, default=None, verbose_name='请求头')
	pre_process = models.CharField(max_length=200, default=None, verbose_name='前置处理器')
	post_process = models.CharField(max_length=200, default=None, verbose_name='后置处理器')
	except_result = models.CharField(max_length=200, default=None, verbose_name='预期结果，仅支持json')
	assert_method = models.CharField(max_length=10, default='contain', verbose_name='断言方法，包含、等于、不等于、被包含')
	assert_result = models.CharField(max_length=200, default=None, verbose_name='断言内容')
	description = models.CharField(max_length=250, default=None, verbose_name='接口描述')
	created_by = models.CharField(max_length=20, default=None, verbose_name='创建人')
	updated_by = models.CharField(max_length=20, default=None, verbose_name='更新人')
	create_time = models.DateTimeField(verbose_name='创建时间')
	update_time = models.DateTimeField(verbose_name='更新时间')

	class Meta:
		db_table = 'ati_interfaces'


class Cases(models.Model):
	id = models.CharField(max_length=20, unique=True, primary_key=True, verbose_name='用例id')
	project_id = models.CharField(max_length=20, default=None, verbose_name='用例所属的项目id')
	is_run = models.IntegerField(default=1, verbose_name='是否执行')
	name = models.CharField(max_length=50, default=None, verbose_name='用例名称')
	description = models.CharField(max_length=250, default=None, verbose_name='用例描述')
	created_by = models.CharField(max_length=20, default=None, verbose_name='创建人')
	updated_by = models.CharField(max_length=20, default=None, verbose_name='更新人')
	create_time = models.DateTimeField(verbose_name='创建时间')
	update_time = models.DateTimeField(verbose_name='更新时间')

	class Meta:
		db_table = 'ati_cases'


class InterfaceCase(models.Model):
	case = models.ForeignKey(Cases, on_delete=models.PROTECT, verbose_name='用例id')
	interface = models.ForeignKey(Interfaces, on_delete=models.PROTECT, verbose_name='接口id')
	is_run = models.IntegerField(default=1, verbose_name='是否执行')
	display_sort = models.IntegerField(default=0, verbose_name='接口顺序')

	class Meta:
		db_table = 'ati_interface_case'

class Plans(models.Model):
	id = models.CharField(max_length=20, unique=True, primary_key=True, verbose_name='测试计划id')
	project_id = models.CharField(max_length=20, default=None, verbose_name='测试计划所属的项目id')
	name = models.CharField(max_length=50, default=None, verbose_name='测试计划名称')
	description = models.CharField(max_length=250, default=None, verbose_name='测试计划描述')
	veriables = models.CharField(max_length=255, default=None, verbose_name='全局变量设置，json格式')
	timing = models.IntegerField(default=0, verbose_name='定时任务，0-不定时，1-周期性执行，2-每天定时执行')
	time_set = models.CharField(max_length=5, default=None, verbose_name='定时任务时间设置')
	is_email = models.IntegerField(default=0, verbose_name='是否发送邮件')
	email = models.CharField(max_length=255, default=None, verbose_name='邮件信息，json格式')
	created_by = models.CharField(max_length=20, default=None, verbose_name='创建人')
	updated_by = models.CharField(max_length=20, default=None, verbose_name='更新人')
	create_time = models.DateTimeField(verbose_name='创建时间')
	update_time = models.DateTimeField(verbose_name='更新时间')

	class Meta:
		db_table = 'ati_plans'


class CasePlan(models.Model):
	plan = models.ForeignKey(Plans, on_delete=models.PROTECT, verbose_name='测试计划id')
	case = models.ForeignKey(Cases, on_delete=models.PROTECT, verbose_name='用例id')
	is_run = models.IntegerField(default=1, verbose_name='是否执行')
	display_sort = models.IntegerField(default=0, verbose_name='用例顺序')

	class Meta:
		db_table = 'ati_case_plan'
