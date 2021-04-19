# **Yatube blog**
Социальная сеть, блог. **Учебный проект**.
***

Сообщество для публикаций. Блог с возможностью публикации постов, подпиской на авторов и группы, комментированием и лайками.
***

## Запуск проекта (Локальный)
1. Создание виртуального окружения и подключение к нему.

`python3 -m venv venv`

`source venv/bin/activate`

2. Настройка перменных окружения. 
Создайте файл `.env` и добавьте в него следующие переменные:

`DB_ENGINE # база данных, например, postgresql (django.db.backends.postgresql)`

`DB_NAME # имя базы данных`

`POSTGRES_USER # логин для подключения к базе данных`

`POSTGRES_PASSWORD # пароль для подключения к БД`

`DB_HOST # название сервиса (контейнера)`

`DB_PORT # порт для подключения к БД`

3. Установка зависимостей

`pip install -r requirements.txt`

4. Развёртывание проекта

`python3 manage.py runserver`

***

## **Технологии**
- [Python](https://www.python.org/)
- [Django](https://www.djangoproject.com/)
- [Nginx](https://nginx.org/)
- [Gunicorn](https://gunicorn.org/)
- [Яндекс.Облако](https://cloud.yandex.ru/)
