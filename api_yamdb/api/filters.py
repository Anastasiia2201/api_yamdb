from django_filters import rest_framework

from reviews.models import Title


class TitlesFilter(rest_framework.FilterSet):
    genre = rest_framework.CharFilter(
        field_name='genre__slug',
        lookup_expr='iexact')
    category = rest_framework.CharFilter(
        field_name='category__slug',
        lookup_expr='iexact')
    name = rest_framework.CharFilter(field_name='name', lookup_expr='iexact')

    class Meta:
        fields = ('category__slug', 'genre__slug', 'name', 'year')
        model = Title
