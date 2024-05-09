from django.contrib.auth.models import AbstractUser
from django.db import models

CHOICES = (
    ("admin", "Администратор"),
    ("user", "Пользователь"),
    ("moderator", "Модератор"),
)


class User(AbstractUser):
    bio = models.TextField("Биография",
                           blank=True
                           )
    role = models.CharField("Роль",
                            max_length=10,
                            choices=CHOICES,
                            default="user"
                            )
    email = models.EmailField(max_length=254, unique=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.username
