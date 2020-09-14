from django.db import models

# Create your models here.


class Projects(models.Model):
	id = models.CharField(max_length=20, unique=True, primary_key=True, verbose_name='项目id')
	name = models.CharField(max_length=150, default=None, verbose_name='项目名称')
	description = models.CharField(max_length=250, default=None, verbose_name='项目描述')
	type = models.CharField(max_length=10, default=None, verbose_name='项目对应的测试类型，ATI-接口自动化，UI-UI自动化')
	create_time = models.DateTimeField(verbose_name='创建时间')
	update_time = models.DateTimeField(verbose_name='更新时间')

	class Meta:
		db_table = 'auth_projects'


class UserProject(models.Model):
	user_name = models.CharField(max_length=100, default=None, verbose_name='用户名')
	project_id = models.CharField(max_length=50, default=None, verbose_name='项目id')
	type = models.CharField(max_length=10, default=None, verbose_name='项目对应的测试类型，ATI-接口自动化，UI-UI自动化')
	create_time = models.DateTimeField(verbose_name='创建时间')

	class Meta:
		db_table = 'auth_user_project'
