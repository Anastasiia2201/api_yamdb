import datetime as dt

from django.contrib.auth import get_user_model
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    ValidationError,
)
from django.db import models

from reviews.constants import RATING_MAX, RATING_MIN, CATEGORY_GENRE_MAX

User = get_user_model()


class BaseCategoryGenre(models.Model):
    """Абстрактная модель для моделей Category, Genre."""

    name = models.CharField(max_length=CATEGORY_GENRE_MAX)
    slug = models.SlugField(unique=True)

    class Meta:
        abstract = True
        ordering = ('slug',)

    def __str__(self):
        return self.name


class Category(BaseCategoryGenre):
    """Модель Category (Категория)."""

    class Meta(BaseCategoryGenre.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(BaseCategoryGenre):
    """Модель Genre (Жанр)."""

    class Meta(BaseCategoryGenre.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Модель Title (Произведение)."""

    name = models.CharField(verbose_name='Название', max_length=256)
    year = models.SmallIntegerField(verbose_name='Год создания')
    description = models.TextField(
        verbose_name='Описание', null=True, default='Описание'
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles',
    )
    genre = models.ManyToManyField(
        Genre, verbose_name='Жанр', through='GenreTitle'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('-year',)

    def __str__(self):
        return self.name
    
    def clean(self):
        year = dt.date.today().year
        if self.year > year:
            raise ValidationError({'year': 'Проверьте год выпуска!'})


class GenreTitle(models.Model):
    """Модель GenreTitle (Название жанра)."""

    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='Жанр')

    class Meta:
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return f'{self.genre} {self.title}'


class BaseReviewComment(models.Model):
    """Абстрактная модель для моделей Review, Comment."""

    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True)
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE)

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text


class Review(BaseReviewComment):
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

    class Meta(BaseReviewComment.Meta):
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = (
            models.UniqueConstraint(
                fields=['author', 'title_id'],
                name='unique_author_title_id',
            ),
        )


class Comment(BaseReviewComment):
    """Модель Comment (Комментарии)."""

    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        on_delete=models.CASCADE,
        related_name='comments',
    )

    class Meta(BaseReviewComment.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
