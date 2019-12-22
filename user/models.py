from django.db import models

# Create your models here.


class UserModel(models.Model):
	username = models.CharField(max_length=50, default='')
	password = models.CharField(max_length=50, default='')

	class Meta:
		db_table = 't_user'
