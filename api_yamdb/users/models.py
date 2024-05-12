from django.contrib.auth.models import AbstractUser
from django.db import models


CHOICES = (
    ('admin', 'Администратор'),
    ('user', 'Пользователь'),
    ('moderator', 'Модератор'),
)


class CustomUser(AbstractUser):
    MODERATOR = 'moderator'
    ADMIN = 'admin'
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
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR
