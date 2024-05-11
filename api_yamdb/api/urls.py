from django.urls import path, include
from rest_framework import routers

from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
    UserViewSet,
    signup,
    confirm_signup
)

reviews_url = r'titles/(?P<title_id>\d+)/reviews'
comments_url = rf'{reviews_url}/(?P<review_id>\d+)/comments'

router = routers.DefaultRouter()
router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')
router.register('titles', TitleViewSet, basename='titles')
router.register('users', UserViewSet, basename='users')
router.register(reviews_url, ReviewViewSet, basename='reviews')
router.register(comments_url, CommentViewSet, basename='comments')

authpatterns = [
    path('signup/', signup, name='signup'),
    path('token/', confirm_signup, name='confirm_signup'),
]

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/', include(authpatterns)),
]
