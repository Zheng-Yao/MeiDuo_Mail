from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    """用户模型类"""
    moblie = models.CharField(max_length=11, verbose_name='手机号码')

    class Meta:
        db_table = 'users'
        verbose_name = '用户列表'
        verbose_name_plural = verbose_name

