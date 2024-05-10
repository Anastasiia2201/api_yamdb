import datetime as dt

from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from reviews.models import Title, Genre, Category
from users.models import CustomUser


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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'email',
                  'first_name', 'last_name', 'bio', 'role')

    @staticmethod
    def validate_username(value):
        """Проверка имени пользователя."""
        if value.lower() == 'me':
            raise serializers.ValidationError(
                f'Имя {value} не может быть использовано')
        return value


class CommonUserSerializer(UserSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'email',
                  'first_name', 'last_name', 'bio')
        read_only_fields = ('role',)


class SignupSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователей."""
    username = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=True, max_length=254)

    class Meta:
        fields = ("username", "email")
        model = CustomUser
        read_only_fields = ('role',)

    @staticmethod
    def validate_username(value):
        """Проверка имени пользователя."""
        if value.lower() == 'me':
            raise serializers.ValidationError(
                f'Имя {value} не может быть использовано')
        return value


class TokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        fields = ("username", "confirmation_code")
        model = CustomUser

    def validate(self, attrs):
        """Проверка username и confirmation_code."""
        user = get_object_or_404(CustomUser, username=attrs['username'])
        if attrs.get('confirmation_code') != user.confirmation_code:
            raise serializers.ValidationError(
                'Неверный код подтверждения')
        return attrs
