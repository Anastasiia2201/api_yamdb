from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

RATING_MIN = 1
RATING_MAX = 10


class Category(models.Model):
    """Модель Category (Категория)."""

    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        default_related_name = 'categories'


class Genre(models.Model):
    """Модель Genre (Жанр)."""

    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        default_related_name = 'genres'


class Title(models.Model):
    """Модель Title (Произведение)."""

    name = models.CharField(verbose_name='Название', max_length=256)
    year = models.IntegerField(verbose_name='Год создания',)
    description = models.TextField(verbose_name='Описание', null=True)
    rating = models.IntegerField(verbose_name='Рейтинг', default=0)
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        null=True,
        on_delete=models.SET_NULL,
        related_name='categories',)
    genre = models.ManyToManyField(Genre, verbose_name='Жанр',
                                   through='GenreTitle')

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Модель GenreTitle (Название жанра)."""

    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.genre} {self.title}'


class Review(models.Model):
    """Модель Review (Отзывы на произведения)."""

    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Рейтинг',
        validators=[
            MinValueValidator(
                RATING_MIN,
                message=f'Рейтинг не может быть ниже {RATING_MIN}.',
            ),
            MaxValueValidator(
                RATING_MAX,
                message=f'Рейтинг не может быть выше {RATING_MAX}.',
            ),
        ],
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class Comment(models.Model):
    """Модель Comment (Комментарии)."""

    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        on_delete=models.CASCADE,
        related_name='comments',
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
