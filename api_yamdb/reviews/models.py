from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=256)  
    slug = models.SlugField(unique=True, max_length=50)


class Genre(models.Model):
    name = models.CharField(max_length=256)  
    slug = models.SlugField(unique=True, max_length=50)


class Title(models.Model):
    name = models.CharField(max_length=256)  
    year = models.IntegerField()
    description = models.TextField(null=True)
    rating = models.IntegerField(default=0)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='categories',)
    genre = models.ManyToManyField(Genre, through='GenreTitle')


class GenreTitle(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
