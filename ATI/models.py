from django.db import models

# Create your models here.


class Project(models.Model):
	name = models.CharField(max_length=50, default=None)
	code = models.CharField(max_length=50, unique=True, primary_key=True)
	description = models.CharField(max_length=250, default=None)
	pro_type = models.CharField(max_length=10, default=None)
	create_time = models.DateTimeField()
	username = models.CharField(max_length=200, default=None)

	class Meta:
		db_table = 't_projects'


class Variables(models.Model):
	name = models.CharField(max_length=50, default=None)
	value = models.CharField(max_length=50, default=None)
	project = models.CharField(max_length=50)
	description = models.CharField(max_length=250, default=None)
	create_time = models.DateTimeField()

	class Meta:
		db_table = 't_variable'
