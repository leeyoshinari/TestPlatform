from django.db import models

# Create your models here.


class Interfaces(models.Model):
	interface_id = models.CharField(max_length=50, default=None, verbose_name='接口id')
	project_id = models.CharField(max_length=20, default=None, verbose_name='接口所属的项目id')
	name = models.CharField(max_length=50, default=None, verbose_name='接口名称')
	interface = models.CharField(max_length=200, default=None, verbose_name='接口')
	protocol = models.CharField(max_length=10, default='http', verbose_name='接口协议')
	method = models.CharField(max_length=8, default='get', verbose_name='请求方法')
	parameter = models.CharField(max_length=200, default=None, null=True, verbose_name='请求参数')
	timeout = models.IntegerField(default=500, verbose_name='接口超时时间，单位毫秒')
	header = models.CharField(max_length=200, default=None, null=True, verbose_name='请求头')
	pre_process = models.CharField(max_length=200, default=None, null=True, verbose_name='前置处理器')
	post_process = models.CharField(max_length=200, default=None, null=True, verbose_name='后置处理器')
	expect_result = models.CharField(max_length=200, default=None, null=True, verbose_name='预期结果，仅支持json')
	assert_method = models.CharField(max_length=10, default='contain', verbose_name='断言方法，包含、等于、不等于、被包含')
	true_result = models.CharField(max_length=200, default=None, null=True, verbose_name='实际结果')
	description = models.CharField(max_length=250, default=None, null=True, verbose_name='接口描述')
	created_by = models.CharField(max_length=20, default=None, null=True, verbose_name='创建人')
	updated_by = models.CharField(max_length=20, default=None, null=True, verbose_name='更新人')
	create_time = models.DateTimeField(null=True, verbose_name='创建时间')
	update_time = models.DateTimeField(null=True, verbose_name='更新时间')

	class Meta:
		db_table = 'ati_interfaces'
		indexes = [models.Index(fields=['project_id', 'update_time'])]


class Scenes(models.Model):
	id = models.CharField(max_length=20, unique=True, primary_key=True, verbose_name='测试场景id')
	project_id = models.CharField(max_length=20, default=None, verbose_name='用例所属的项目id')
	name = models.CharField(max_length=50, default=None, verbose_name='场景名称')
	description = models.CharField(max_length=250, default=None, null=True, verbose_name='场景描述')
	created_by = models.CharField(max_length=20, default=None, null=True, verbose_name='创建人')
	updated_by = models.CharField(max_length=20, default=None, null=True, verbose_name='更新人')
	create_time = models.DateTimeField(null=True, verbose_name='创建时间')
	update_time = models.DateTimeField(null=True, verbose_name='更新时间')

	class Meta:
		db_table = 'ati_scenes'
		unique_together = ('id',)
		indexes = [models.Index(fields=['project_id', 'update_time'])]


class InterfaceScene(models.Model):
	scene = models.ForeignKey(Scenes, on_delete=models.PROTECT, verbose_name='测试场景id')
	interface = models.ForeignKey(Interfaces, on_delete=models.PROTECT, verbose_name='接口id')
	is_run = models.IntegerField(default=1, verbose_name='是否执行')
	display_sort = models.IntegerField(default=0, verbose_name='接口顺序')

	class Meta:
		db_table = 'ati_interface_scene'
		indexes = [models.Index(fields=['display_sort'])]

class Plans(models.Model):
	id = models.CharField(max_length=20, unique=True, primary_key=True, verbose_name='测试计划id')
	project_id = models.CharField(max_length=20, default=None, verbose_name='测试计划所属的项目id')
	name = models.CharField(max_length=50, default=None, verbose_name='测试计划名称')
	description = models.CharField(max_length=250, default=None, null=True, verbose_name='测试计划描述')
	timing = models.IntegerField(default=0, verbose_name='定时任务，0-立即执行，1-仅执行一次，2-周期性执行，3-每天定时执行')
	time_set = models.CharField(max_length=5, default=None, null=True, verbose_name='定时任务时间设置')
	is_email = models.IntegerField(default=0, verbose_name='是否发送邮件')
	email = models.CharField(max_length=255, default=None, null=True, verbose_name='邮件信息，json格式')
	is_running = models.IntegerField(default=0, verbose_name='是否正在执行，0-未执行，1-正在执行')
	last_run_time = models.IntegerField(default=0, null=True, verbose_name='最后一次执行时间')
	created_by = models.CharField(max_length=20, default=None, null=True, verbose_name='创建人')
	updated_by = models.CharField(max_length=20, default=None, null=True, verbose_name='更新人')
	create_time = models.DateTimeField(null=True, verbose_name='创建时间')
	update_time = models.DateTimeField(null=True, verbose_name='更新时间')

	class Meta:
		db_table = 'ati_plans'
		unique_together = ('id',)
		indexes = [models.Index(fields=['project_id', 'update_time'])]


class ScenePlan(models.Model):
	plan = models.ForeignKey(Plans, on_delete=models.PROTECT, verbose_name='测试计划id')
	scene = models.ForeignKey(Scenes, on_delete=models.PROTECT, verbose_name='场景id')
	is_run = models.IntegerField(default=1, verbose_name='是否执行')
	display_sort = models.IntegerField(default=0, verbose_name='测试场景顺序')

	class Meta:
		db_table = 'ati_scene_plan'
		indexes = [models.Index(fields=['display_sort'])]


class Variables(models.Model):
	name = models.CharField(max_length=50, default=None, verbose_name='变量名')
	value = models.CharField(max_length=50, default=None, verbose_name='变量值')
	plan = models.ForeignKey(Plans, on_delete=models.PROTECT, verbose_name='变量对应的测试计划id')
	description = models.CharField(max_length=250, default=None, null=True, verbose_name='变量描述')
	created_by = models.CharField(max_length=20, default=None, null=True, verbose_name='创建人')
	updated_by = models.CharField(max_length=20, default=None, null=True, verbose_name='更新人')
	create_time = models.DateTimeField(null=True, verbose_name='创建时间')
	update_time = models.DateTimeField(null=True, verbose_name='更新时间')

	class Meta:
		db_table = 'ati_variables'
		indexes = [models.Index(fields=['update_time'])]
