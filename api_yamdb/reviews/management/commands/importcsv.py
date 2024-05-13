import csv

from django.core.management.base import BaseCommand

from reviews.models import (
    Title,
    Category,
    Genre,
    GenreTitle,
    User,
    Comment,
    Review)


def import_titles(file_path):
    """Импорт данных из cvs файла в модель Title."""
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            Title.objects.get_or_create(id=row['id'], defaults={
                'name': row['name'],
                'year': row['year'],
                'category': Category.objects.get(pk=row['category']), })


def import_categories(file_path):
    """Импорт данных из cvs файла в модель Category."""
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            Category.objects.get_or_create(id=row['id'], defaults={
                'name': row['name'],
                'slug': row['slug'], })


def import_genres(file_path):
    """Импорт данных из cvs файла в модель Genre."""
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            Genre.objects.get_or_create(id=row['id'], defaults={
                'name': row['name'],
                'slug': row['slug'], })


def import_genre_title(file_path):
    """Импорт данных из cvs файла в модель Genre_Title."""
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            GenreTitle.objects.get_or_create(id=row['id'], defaults={
                'title_id': row['title_id'],
                'genre_id': row['genre_id'], })


def import_users(file_path):
    """Импорт данных из cvs файла в модель User."""
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            User.objects.get_or_create(id=row['id'], defaults={
                'username': row['username'],
                'email': row['email'],
                'role': row['role'],
                'bio': row['bio'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
            })


def import_reviews(file_path):
    """Импорт данных из cvs файла в модель Review."""
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            Review.objects.get_or_create(id=row['id'], defaults={
                'title_id': row['title_id'],
                'text': row['text'],
                'author': User.objects.get(pk=row['author']),
                'score': row['score'],
                'pub_date': row['pub_date']}, )


def import_comments(file_path):
    """Импорт данных из cvs файла в модель Comment."""
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            Comment.objects.get_or_create(id=row['id'], defaults={
                'review_id': row['review_id'],
                'text': row['text'],
                'author': User.objects.get(pk=row['author']),
                'pub_date': row['pub_date'], })


class Command(BaseCommand):
    help = 'import CSV Data into Django Models'

    def handle(self, *args, **options):
        import_categories('static/data/category.csv')
        import_genres('static/data/genre.csv')
        import_titles('static/data/titles.csv')
        import_genre_title('static/data/genre_title.csv')
        import_users('static/data/users.csv')
        import_reviews('static/data/review.csv')
        import_comments('static/data/comments.csv')
        self.stdout.write(self.style.SUCCESS('Данные добавлены'))
