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
