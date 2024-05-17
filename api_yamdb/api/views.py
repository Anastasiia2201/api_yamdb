import random

from django.db.models import Avg
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Review, Title
from users.models import CustomUser
from .filters import TitlesFilter
from .permissions import IsAdmin, IsAdminOrSafeMethod, IsAuthorOrAdmin
from .serializers import (CategorySerializer, CommentSerializer,
                          CommonUserSerializer, GenreSerializer,
                          ReviewSerializer, SignupSerializer,
                          TitleDisplaySerializer, TitleInputSerializer,
                          TokenSerializer, UserSerializer)


class CreateDestroyListViewSet(
    CreateModelMixin, DestroyModelMixin, ListModelMixin, GenericViewSet
):
    pass


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Title."""

    queryset = Title.objects.annotate(rating=Avg("reviews__score")).order_by(
        "id")
    serializer_class = TitleDisplaySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = TitlesFilter
    search_fields = ['name']
    permission_classes = (IsAdminOrSafeMethod,)
    http_method_names = ["get", "post", "patch", "delete"]

    def perform_create(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = TitleInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        instance_serializer = TitleDisplaySerializer(instance)
        return Response(
            instance_serializer.data,
            status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.queryset.get(pk=kwargs.get('pk'))
        except ValueError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = TitleInputSerializer(
            instance,
            data=request.data,
            partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        instance_serializer = TitleDisplaySerializer(instance)
        return Response(
            instance_serializer.data,
            status=status.HTTP_200_OK)


class CategoryViewSet(CreateDestroyListViewSet):
    """Вьюсет для модели Category."""

    queryset = Category.objects.all()
    lookup_field = 'slug'
    serializer_class = CategorySerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']
    permission_classes = (IsAdminOrSafeMethod,)


class GenreViewSet(CreateDestroyListViewSet):
    """Вьюсет для модели Genre."""

    queryset = Genre.objects.all()
    lookup_field = 'slug'
    serializer_class = GenreSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']
    permission_classes = (IsAdminOrSafeMethod,)


class UserViewSet(viewsets.ModelViewSet):
    """CRUD для пользователей."""

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    http_method_names = ["get", "post", "patch", "delete"]
    search_fields = ['username']
    lookup_field = 'username'

    @action(
        detail=False,
        methods=['GET', 'PUT', 'PATCH'],
        permission_classes=[IsAuthenticated],
        url_path='me',
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        serializer = CommonUserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role, partial=True)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def signup(request):
    """
    Создание пользователя и отправление код подтверждения на email.

    Если пользователь уже зарегистрирован, то отправляется только
    код подтверждения.
    """
    serializer = SignupSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    confirmation_code = random.randint(100_000, 999_999)
    send_mail(
        subject='Ваш код подтверждения',
        message=f'Ваш код подтверждения {str(confirmation_code)}',
        from_email='yamdb.ru',
        recipient_list=[request.data['email']],
        fail_silently=False,
    )
    try:
        user = CustomUser.objects.get(
            username=request.data['username'],
            email=request.data['email'])
    except CustomUser.DoesNotExist:
        user = None
    if user:
        user.confirmation_code = str(confirmation_code)
        user.save()
    else:
        CustomUser.objects.create(
            username=request.data['username'],
            email=request.data['email'],
            confirmation_code=confirmation_code)
    return Response(
        request.data,
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def confirm_signup(request):
    """Подтверждение e-mail пользователя по коду и создание токена."""
    serializer = TokenSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    refresh = RefreshToken.for_user(CustomUser.objects.get(
        username=request.data['username'],
        confirmation_code=request.data['confirmation_code']
    )
    )
    return Response({'token': f'{refresh.access_token}'})


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Review."""

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrAdmin]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs['title_id'])

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Comment."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrAdmin]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_review(self):
        return get_object_or_404(
            Review.objects.filter(title_id=self.kwargs['title_id']),
            pk=self.kwargs['review_id'])

    def get_queryset(self):
        return self.get_review().comments.all().select_related(
            'author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
