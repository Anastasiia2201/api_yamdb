from django.urls import path, include
from rest_framework import routers

from .views import (
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    UserViewSet,
    signup,
    confirm_signup
)

router = routers.DefaultRouter()
router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')
router.register('titles', TitleViewSet, basename='titles')
router.register('users', UserViewSet, basename='users')

authpatterns = [
    path('signup/', signup, name='signup'),
    path('token/', confirm_signup, name='confirm_signup'),
]

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/', include(authpatterns)),
]
