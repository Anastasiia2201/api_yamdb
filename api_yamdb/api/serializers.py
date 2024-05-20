import datetime as dt
import re

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.relations import SlugRelatedField
from django.contrib.auth.tokens import default_token_generator

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""

    class Meta:
        model = Genre
        fields = ("name", "slug")


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        model = Category
        fields = ("name", "slug")


class TitleInputSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Title."""

    category = serializers.SlugRelatedField(
        slug_field="slug", queryset=Category.objects.all()
    )

    genre = serializers.SlugRelatedField(
        required=True,
        allow_empty=False,
        many=True,
        slug_field="slug",
        queryset=Genre.objects.all(),
    )

    class Meta:
        model = Title
        fields = ("id", "name", "year", "description", "genre", "category")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            representation["rating"] = instance.rating
        except Exception:
            representation["rating"] = 0
        representation["genre"] = [
            {
                "name": genre.name,
                "slug": genre.slug
            }
            for genre in instance.genre.all()
        ]
        representation["category"] = {
            "name": instance.category.name,
            "slug": instance.category.slug,
        }
        return representation

    def validate_year(self, value):
        year = dt.date.today().year
        if value > year:
            raise serializers.ValidationError("Проверьте год выпуска!")
        return value


class TitleDisplaySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Title."""

    category = CategorySerializer()
    rating = serializers.IntegerField()
    genre = GenreSerializer(many=True)

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "rating",
            "description",
            "genre",
            "category")
        read_only_fields = ("rating",)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role")

    @staticmethod
    def validate_username(value):
        """Проверка имени пользователя."""
        if value == "me":
            raise serializers.ValidationError(
                f"Имя {value} не может быть использовано")
        if not re.match(r"^[\w.@+-]+\Z", value):
            raise serializers.ValidationError(
                f"Имя {value} не может содержать спецсимволы"
            )
        return value


class SignupSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователей."""

    username = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=True, max_length=254)

    class Meta:
        fields = ("username", "email")
        model = User

    @staticmethod
    def validate_username(value):
        """Проверка имени пользователя."""
        if value == "me":
            raise serializers.ValidationError(
                f"Имя {value} не может быть использовано")
        if not re.match(r"^[\w.@+-]+\Z", value):
            raise serializers.ValidationError(
                f"Имя {value} не может содержать спецсимволы"
            )
        return value

    def validate(self, attrs):
        email = attrs.get("email")
        username = attrs.get("username")
        wrong_username = False
        wrong_email = False
        try:
            user_with_email = User.objects.get(email=email)
            if user_with_email.username != username:
                wrong_username = True
        except User.DoesNotExist:
            pass

        try:
            user_with_username = User.objects.get(username=username)
            if user_with_username.email != email:
                wrong_email = True
        except User.DoesNotExist:
            pass

        if wrong_username and wrong_email:
            raise serializers.ValidationError(
                {"username": username,
                 "email": email})
        elif wrong_username:
            raise serializers.ValidationError({"email": email})
        elif wrong_email:
            raise serializers.ValidationError({"username": username})

        return attrs


class TokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        fields = ("username", "confirmation_code")
        model = User

    def validate(self, attrs):
        """Проверка username и confirmation_code."""
        user = get_object_or_404(User, username=attrs["username"])
        if not default_token_generator.check_token(
                user, attrs["confirmation_code"]):
            raise serializers.ValidationError("Неверный код подтверждения")
        return attrs


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""

    author = SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    def validate(self, data):
        request = self.context.get("request")
        if request.method != "POST":
            return data
        title = get_object_or_404(
            Title,
            pk=self.context["view"].kwargs["title_id"])
        if title.reviews.filter(author=request.user).exists():
            raise ValidationError(
                "Пользователь может оставить только один отзыв!")
        return data

    class Meta:
        model = Review
        fields = ("id", "text", "author", "score", "pub_date")


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""

    author = SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        fields = ("id", "text", "author", "pub_date")
