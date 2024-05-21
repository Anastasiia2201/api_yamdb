from django.contrib.auth.models import AbstractUser
from django.db import models

from reviews.constants import MAX_LENGTH_USERNAME, MAX_LENGTH_EMAIL


class Roles:
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    CHOICES = (
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    )

    @classmethod
    def max_length_number_role(cls):
        return max(len(role) for role, _ in cls.CHOICES)


class User(AbstractUser):
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Роль',
        max_length=Roles.max_length_number_role(),
        choices=Roles.CHOICES,
        default=Roles.USER
    )
    email = models.EmailField('Email', max_length=MAX_LENGTH_EMAIL, unique=True)
    username = models.CharField(
        'Имя пользователя',
        max_length=MAX_LENGTH_USERNAME,
        unique=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == Roles.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == Roles.MODERATOR
