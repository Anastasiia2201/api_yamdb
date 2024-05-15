# Проект YaMDb 
 Стек технологий: Python, Django REST Framework

### Описание. 
 Проект YaMDb собирает отзывы пользователей на произведения. Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.
 Благодарные или возмущённые пользователи оставляют к произведениям текстовые отзывы и ставят произведению оценку в диапазоне от одного до десяти (целое число); из пользовательских оценок формируется рейтинг произведения.
 Пользователи могут оставлять комментарии к отзывам.  
 
### Установка: 
 Клонировать репозиторий и перейти в него в командной строке:

 ```
 git clone https://github.com/Anastasiia2201/api_yamdb
 ```
 
 ```
 cd api_yamdb
 ```

 Cоздать и активировать виртуальное окружение:

 ```
 python3 -m venv venv 
 ```

 * Если у вас Linux/macOS 

  ```
    source venv/bin/activate 
  ```

 * Если у вас windows

  ```
    source venv/scripts/activate 
  ```

 Установить зависимости из файла requirements.txt:

 ```
 python3 -m pip install --upgrade pip
 ```

 ```
 pip install -r requirements.txt 
 ```

 Выполнить миграции:

 ```
 python3 manage.py migrate
 ```

 Запустить проект:

 ```
 python3 manage.py runserver
 ```

### Примеры. 
 
 GET http://127.0.0.1:8000/api/v1/titles/12/
 Content-Type: application/json
 {
     "id": 12,
     "name": "Матрица",
     "year": 1999,
     "rating": 8,
     "description": null,
     "genre": [
         "drama",
         "sci-fi",
         "detective",
         "tale"
     ],
     "category": "movie"
 }

### Дополнительная информация.

 Чтобы добавить данные в БД из csv файлов, выполните:

 ```
 python3 manage.py importcsv
 ```
