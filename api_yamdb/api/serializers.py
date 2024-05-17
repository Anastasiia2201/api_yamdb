import datetime as dt
import re

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.relations import SlugRelatedField

from reviews.constants import RATING_MAX, RATING_MIN
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import CustomUser


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class TitleInputSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Title."""

    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all())

    genre = serializers.SlugRelatedField(
        required=True,
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all())

    class Meta:
        model = Title
        fields = ('id', 'name', 'year',
                  'description', 'genre', 'category')
        read_only_fields = ('rating',)

    def validate_year(self, value):
        year = dt.date.today().year
        if value > year:
            raise serializers.ValidationError('Проверьте год выпуска!')
        return value

    def validate_genre(self, value):
        if len(value) == 0:
            raise serializers.ValidationError()
        return value


class TitleDisplaySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Title."""

    category = CategorySerializer()
    rating = serializers.IntegerField(required=False)
    genre = GenreSerializer(many=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')
        read_only_fields = ('rating',)


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
        if not re.match(r"^[\w.@+-]+\Z", value):
            raise serializers.ValidationError(
                f'Имя {value} не может содержать спецсимволы')
        return value


class CommonUserSerializer(UserSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role',
                  'first_name', 'last_name', 'bio')
        read_only_fields = ('role',)

    @staticmethod
    def validate_username(value):
        """Проверка имени пользователя."""
        if value.lower() == 'me':
            raise serializers.ValidationError(
                f'Имя {value} не может быть использовано')
        if not re.match(r"^[\w.@+-]+\Z", value):
            raise serializers.ValidationError(
                f'Имя {value} не может содержать спецсимволы')
        return value


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
        if not re.match(r"^[\w.@+-]+\Z", value):
            raise serializers.ValidationError(
                f'Имя {value} не может содержать спецсимволы')
        return value

    def validate(self, attrs):
        email = attrs.get('email')
        username = attrs.get('username')
        wrong_username = False
        wrong_email = False
        try:
            user_with_email = CustomUser.objects.get(email=email)
            if user_with_email.username != username:
                wrong_username = True
        except CustomUser.DoesNotExist:
            pass

        try:
            user_with_username = CustomUser.objects.get(username=username)
            if user_with_username.email != email:
                wrong_email = True
        except CustomUser.DoesNotExist:
            pass

        if wrong_username and wrong_email:
            raise serializers.ValidationError(
                {'username': username,
                 'email': email})
        elif wrong_username:
            raise serializers.ValidationError({'email': email})
        elif wrong_email:
            raise serializers.ValidationError({'username': username})

        return attrs


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


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""

    author = SlugRelatedField(slug_field='username', read_only=True,
                              default=serializers.CurrentUserDefault())

    def validate(self, data):
        request = self.context.get("request")
        if request.method != "POST":
            return data
        title = get_object_or_404(
            Title, pk=self.context['view'].kwargs['title_id']
        )
        if title.reviews.filter(author=request.user).exists():
            raise ValidationError(
                "Пользователь может оставить только один отзыв!"
            )
        return data

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""

    author = SlugRelatedField(slug_field='username', read_only=True,
                              default=serializers.CurrentUserDefault())

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
