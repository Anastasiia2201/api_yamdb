import datetime as dt

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from reviews.models import Category, Comment, Genre, Review, Title


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""

    class Meta:
        model = Genre
        lookup_field = 'slug'
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        model = Category
        lookup_field = 'slug'
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Title."""

    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all())

    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        required=False,
        queryset=Genre.objects.all())

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')
        read_only_fields = ('rating',)

    def validate_year(self, value):
        year = dt.date.today().year
        if value > year:
            raise serializers.ValidationError('Проверьте год выпуска!')
        return value


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""

    def validate(self, data):
        request = self.context.get('request')
        if request.method != 'POST':
            return data
        title = get_object_or_404(
            Title, pk=self.context['view'].kwargs['title_id']
        )
        if title.reviews.filter(author=request.user).exists():
            raise ValidationError(
                "Автор может оставить только один отзыв на произведение!"
            )
        return data

    class Meta:
        model = Review
        read_only_fields = ('title',)


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""

    class Meta:
        model = Comment
        read_only_fields = ('review',)
