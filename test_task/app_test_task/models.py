"""
Модели табличек БД Пользователь и Сообщение связанных ForeignKey
"""
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # name уникальный
    name = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    username = None
    # Меняем отображение username на name
    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = []


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message_text = models.CharField(max_length=255)

    class Meta:
        # В обратном порядке для возвращения последних сообщений
        ordering = ['-id']
