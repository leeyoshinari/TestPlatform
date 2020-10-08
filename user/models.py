from django.db import models
# Create your models here.


class Projects(models.Model):
	id = models.CharField(max_length=20, unique=True, primary_key=True, verbose_name='项目id')
	name = models.CharField(max_length=150, default=None, verbose_name='项目名称')
	description = models.CharField(max_length=250, default=None, null=True, verbose_name='项目描述')
	type = models.CharField(max_length=10, default=None, verbose_name='项目对应的测试类型，ATI-接口自动化，UI-UI自动化')
	created_by = models.CharField(max_length=20, default=None, null=True, verbose_name='创建人')
	updated_by = models.CharField(max_length=20, default=None, null=True, verbose_name='更新人')
	create_time = models.DateTimeField(null=True, verbose_name='创建时间')
	update_time = models.DateTimeField(null=True, verbose_name='更新时间')

	class Meta:
		db_table = 'auth_projects'
		unique_together = ('id',)
		indexes = [models.Index(fields=['type'])]


class UserProject(models.Model):
	user_name = models.CharField(max_length=100, default=None, verbose_name='用户名')
	project = models.ForeignKey(Projects, on_delete=models.CASCADE, verbose_name='项目id')
	type = models.CharField(max_length=10, default=None, verbose_name='项目对应的测试类型，ATI-接口自动化，UI-UI自动化')
	create_time = models.DateTimeField(null=True, verbose_name='创建时间')

	class Meta:
		db_table = 'auth_user_project'
		indexes = [models.Index(fields=['type', 'create_time'])]


class Results(models.Model):
	project = models.ForeignKey(Projects, on_delete=models.CASCADE, verbose_name='项目id')
	plan_id = models.CharField(max_length=20, default=None, verbose_name='测试计划id')
	plan_name = models.CharField(max_length=50, default=None, verbose_name='测试计划名称')
	status = models.IntegerField(default=0, verbose_name='执行状态，0-未执行，1-排队中，2-执行中，3-执行完成，4-已取消，5-执行失败')
	total_num = models.IntegerField(default=0, null=True, verbose_name='测试用例总数')
	success_num = models.IntegerField(default=0, null=True, verbose_name='成功的测试用例数')
	start_time = models.DateTimeField( null=True, verbose_name='开始测试时间')
	interval = models.FloatField(default=0.0, null=True, verbose_name='测试执行时长')
	type = models.CharField(max_length=10, default=None, verbose_name='项目对应的测试类型，ATI-接口自动化，UI-UI自动化')
	link = models.CharField(max_length=150, null=True, default=None, verbose_name='测试报告地址')
	error_log = models.TextField(default=None, null=True, verbose_name='错误日志')

	class Meta:
		db_table = 'auth_results'
		indexes = [models.Index(fields=['plan_id'])]
