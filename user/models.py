from django.db import models

# Create your models here.


class UserModel(models.Model):
	username = models.CharField(max_length=50, unique=True)
	password = models.CharField(max_length=50, default=None)
	user_id = models.CharField(max_length=50, default=None)
	create_time = models.DateTimeField()
	last_login_time = models.DateTimeField()

	class Meta:
		db_table = 't_user'
