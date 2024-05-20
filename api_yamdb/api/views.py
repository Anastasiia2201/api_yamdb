from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin, )
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly, )
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Review, Title
from .filters import TitlesFilter
from .permissions import IsAdmin, IsAdminOrSafeMethod, IsAuthorOrAdmin
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    SignupSerializer,
    TitleDisplaySerializer,
    TitleInputSerializer,
    TokenSerializer,
    UserSerializer,
)

User = get_user_model()


class CreateDestroyListViewSet(
    CreateModelMixin, DestroyModelMixin, ListModelMixin, GenericViewSet
):
    lookup_field = "slug"
    filter_backends = [SearchFilter]
    search_fields = ("name",)
    permission_classes = (IsAdminOrSafeMethod,)


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Title."""

    queryset = Title.objects.annotate(
        rating=Avg("reviews__score")).order_by("id")
    serializer_class = TitleDisplaySerializer
    filter_backends = (
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter)
    filterset_class = TitlesFilter
    search_fields = ("name",)
    ordering_fields = ("name", "year")
    permission_classes = (IsAdminOrSafeMethod,)
    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_class(self):
        if (
            self.action == "create"
            or self.action == "partial_update"
            or self.action == "update"
        ):
            print(7)
            return TitleInputSerializer
        return TitleDisplaySerializer


class CategoryViewSet(CreateDestroyListViewSet):
    """Вьюсет для модели Category."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CreateDestroyListViewSet):
    """Вьюсет для модели Genre."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class UserViewSet(viewsets.ModelViewSet):
    """CRUD для пользователей."""

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    http_method_names = ["get", "post", "patch", "delete"]
    search_fields = ["username"]
    lookup_field = "username"

    @action(
        detail=False,
        methods=["GET", "PUT", "PATCH"],
        permission_classes=[IsAuthenticated],
        url_path="me",
    )
    def me(self, request):
        if request.method == "GET":
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role, partial=True)
        return Response(serializer.data)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def signup(request):
    """
    Создание пользователя и отправление код подтверждения на email.

    Если пользователь уже зарегистрирован, то отправляется только
    код подтверждения.
    """
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user, created = User.objects.get_or_create(
        username=request.data["username"], email=request.data["email"])
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject="Ваш код подтверждения",
        message=f"Ваш код подтверждения {str(confirmation_code)}",
        recipient_list=[request.data["email"]],
        from_email=settings.DEFAULT_FROM_EMAIL,
        fail_silently=False,
    )
    return Response(request.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def confirm_signup(request):
    """Подтверждение e-mail пользователя по коду и создание токена."""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    refresh = RefreshToken.for_user(
        User.objects.get(
            username=request.data["username"],
        )
    )
    return Response({"token": f"{refresh.access_token}"})


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Review."""

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrAdmin, IsAuthenticatedOrReadOnly]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs["title_id"])

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Comment."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrAdmin, IsAuthenticatedOrReadOnly]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_review(self):
        return get_object_or_404(
            Review.objects.filter(title_id=self.kwargs["title_id"]),
            pk=self.kwargs["review_id"],
        )

    def get_queryset(self):

        return self.get_review().comments.all().select_related("author")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
