from django.contrib.auth.models import AbstractUser
from django.db import models


CHOICES = (
    ('admin', 'Администратор'),
    ('user', 'Пользователь'),
    ('moderator', 'Модератор'),
)


class CustomUser(AbstractUser):
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Роль',
        max_length=10,
        choices=CHOICES,
        default='user'
    )
    email = models.EmailField('Email', max_length=254, unique=True)
    confirmation_code = models.CharField(max_length=6)
    username = models.CharField(max_length=150, unique=True, null=False)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.username
