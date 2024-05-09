import csv

from django.core.management.base import BaseCommand

from reviews.models import Title, Category, Genre, GenreTitle


def import_titles(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            Title.objects.get_or_create(
                id=row['id'],
                name=row['name'],
                year=row['year'],
                category=Category.objects.get(pk=row['category'])
            )


def import_categories(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            Category.objects.get_or_create(
                id=row['id'],
                name=row['name'],
                slug=row['slug'],
            )


def import_genres(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            Genre.objects.get_or_create(
                id=row['id'],
                name=row['name'],
                slug=row['slug'],
            )


def import_genre_title(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            GenreTitle.objects.get_or_create(
                id=row['id'],
                title_id=row['title_id'],
                genre_id=row['genre_id'],
            )


class Command(BaseCommand):
    help = 'import CSV Data into Django Models'

    def handle(self, *args, **options):
        import_categories('static/data/category.csv')
        import_genres('static/data/genre.csv')
        import_titles('static/data/titles.csv')
        import_genre_title('static/data/genre_title.csv')
