import random

from django.core.mail import send_mail
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    DestroyModelMixin)
from rest_framework import viewsets, permissions, status
from rest_framework.filters import SearchFilter
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from reviews.models import Title, Category, Genre
from users.models import CustomUser
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    UserSerializer,
    CommonUserSerializer,
    SignupSerializer,
    TokenSerializer
)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('category__slug', 'genre__slug', 'name', 'year')


class CategoryViewSet(
    ListModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)


class UserViewSet(viewsets.ModelViewSet):
    """CRUD для пользователей"""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['username']
    lookup_field = 'username'

    @action(
        detail=False,
        methods=['GET', 'PUT', 'PATCH'],
        permission_classes=[IsAuthenticated],
        url_path="me",
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
    serializer.is_valid(raise_exception=True)
    confirmation_code = random.randint(100_000, 999_999)
    send_mail(
        subject="Ваш код подтверждения",
        message=f"Ваш код подтверждения {str(confirmation_code)}",
        from_email='yamdb.ru',
        recipient_list=[request.data['email']],
        fail_silently=False,
    )
    try:
        user, created = CustomUser.objects.get_or_create(
            Q(username=request.data['username'])
            | Q(email=request.data['email']))
    except CustomUser.DoesNotExist:
        user = None
    if user:
        user.confirmation_code = str(confirmation_code)
        user.save()
    else:
        CustomUser.objects.get_or_create(
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
    """Подтверждение e-mail пользователя по коду и создание токена"""
    serializer = TokenSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    refresh = RefreshToken.for_user(CustomUser.objects.get(
        username=request.data['username'],
        confirmation_code=request.data['confirmation_code']
    )
    )
    return Response({'token': f'{refresh.access_token}'})
