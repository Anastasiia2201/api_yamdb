from django.urls import path, include
from rest_framework import routers

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet)

reviews_url = r'titles/(?P<title_id>\d+)/reviews'
comments_url = rf'{reviews_url}/(?P<review_id>\d+)/comments'

router = routers.DefaultRouter()
router.register('categories', CategoryViewSet, basename='categories')
router.register('comments', CommentViewSet, basename='comments')
router.register('genres', GenreViewSet, basename='genres')
router.register(reviews_url, ReviewViewSet, basename='reviews')
router.register(comments_url, TitleViewSet, basename='titles')


urlpatterns = [
    path('v1/', include(router.urls)),
]
