import datetime as dt
import re

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.relations import SlugRelatedField

from users.models import CustomUser
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
        fields = ('username', 'email',
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
        try:
            user_with_email = CustomUser.objects.get(email=email)
            # Если пользователь с таким email существует, проверяем,
            # совпадает ли username
            if user_with_email.username != username:
                raise serializers.ValidationError(
                    f'Username {username} не соответствует указанному email')
        except CustomUser.DoesNotExist:
            pass

        try:
            user_with_username = CustomUser.objects.get(username=username)
            # Если пользователь с таким username существует, проверяем,
            # совпадает ли email
            if user_with_username.email != email:
                raise serializers.ValidationError(
                    f'Email {email} не соответствует указанному username')
        except CustomUser.DoesNotExist:
            pass
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
        read_only_fields = ('title',)
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""

    author = SlugRelatedField(slug_field='username', read_only=True,
                              default=serializers.CurrentUserDefault())

    class Meta:
        model = Comment
        read_only_fields = ('review',)
        fields = '__all__'
