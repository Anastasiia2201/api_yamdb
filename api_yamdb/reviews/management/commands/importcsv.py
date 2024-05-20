import csv

from django.core import management
from django.core.management.base import BaseCommand
from django.db import models

from reviews.models import (
    Title,
    Category,
    Genre,
    GenreTitle,
    User,
    Comment,
    Review, )

CSV_DIR = 'static/data/'


def import_model(file_path: str, model: models.Model):
    """Импорт данных из cvs файла в модель."""
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row.get('category'):
                row['category'] = Category.objects.get(pk=row['category'])
            if row.get('author'):
                row['author'] = User.objects.get(pk=row['author'])
            model.objects.get_or_create(id=row['id'], defaults=row)


class Command(BaseCommand):
    help = 'import CSV Data into Django Models'

    management.call_command('migrate')

    def handle(self, *args, **options):
        files_model = {
            'category.csv': Category,
            'genre.csv': Genre,
            'titles.csv': Title,
            'category.csv': Category,
            'genre.csv': Genre,
            'genre_title.csv': GenreTitle,
            'users.csv': User,
            'review.csv': Review,
            'comments.csv': Comment,
        }
        for file_name, model in files_model.items():
            import_model(CSV_DIR + file_name, model)
        self.stdout.write(self.style.SUCCESS('Данные добавлены'))
