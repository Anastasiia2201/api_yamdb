import datetime as dt

from rest_framework import serializers

from reviews.models import Title, Genre, Category


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
