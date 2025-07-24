# Django Referral System

Лёгкий REST API-сервис, демонстрирующий **аутентификацию по номеру
телефона** и **реферальную (инвайт) систему**.  
Пользователь авторизуется по 4-значному коду, получает уникальный
6-символьный инвайт-код и может один раз активировать чужой код, став
рефералом.

---

## Функционал
- Авторизация по номеру телефона (без пароля)
- 4-значный верификационный код (хранится в Redis 5 минут)
- Автосоздание пользователя при первом входе
- Уникальный 6-символьный инвайт-код для каждого нового пользователя
- Возможность активировать **только один** чужой код (само-реферал запрещён)
- В профиле отображается список приглашённых пользователей
- Токенная авторизация (DRF Token)
- Чистый код с поддержкой type hints (Pylance friendly)
- Docker-окружение (PostgreSQL + Redis)
- Postman-коллекция в репозитории

---

## Стек технологий
| Слой             | Используется |
|------------------|--------------|
| Backend          | Python 3.10, Django 5, Django REST Framework |
| Токены           | `rest_framework.authtoken` |
| БД               | PostgreSQL |
| Кэш              | Redis (`django-redis`) |

---

## Установка

### 0. Предварительно
Python 3.10+, PostgreSQL 12+, Redis, Git

### 1. Клонируем
```bash
git clone https://github.com/Udilainer/referral_project.git
cd referral-system
```

### 2. Виртуальное окружение
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Зависимости
```bash
pip install -r requirements.txt
```

### 4. База данных
```sql
CREATE DATABASE referral_db;
CREATE USER referral_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE referral_db TO referral_user;
```

### 5. Redis
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

### 6. Переменные окружения
```bash
cp .env.example .env
# отредактируйте значения
```

### 7. Миграции и суперпользователь
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 8. Запуск
```bash
python manage.py runserver
```
API: `http://localhost:8000/api/`

---

## Документация API

| Действие                  | HTTP-метод / путь               | Авторизация |
|---------------------------|---------------------------------|-------------|
| Запрос кода               | `POST /api/auth/request-code/`  | Нет |
| Проверка кода / вход      | `POST /api/auth/verify-code/`   | Нет |
| Получить профиль          | `GET  /api/profile/`            | **Token** |
| Активировать инвайт-код   | `POST /api/profile/`            | **Token** |

> Для защищённых запросов добавьте заголовок  
> `Authorization: Token <ваш-токен>`.

### Примеры запросов / ответов

#### 1. Запрос кода

`POST /api/auth/request-code/`
```json
{ "phone_number": "+79991234567" }
```
```json
{
  "success": true,
  "message": "Verification code sent to your phone number.",
  "dev_code": "1234"      // DEBUG режим
}
```

#### 2. Проверка кода

`POST /api/auth/verify-code/`
```json
{ "phone_number": "+79991234567", "code": "1234" }
```
```json
{
  "token": "7c1e2f…",
  "is_new_user": true,
  "user": {
    "id": 1,
    "phone_number": "+79991234567",
    "invite_code": "A1B2C3",
    "activated_invite_code": null
  }
}
```

#### 3. Профиль

`GET /api/profile/`
```json
{
  "id": 1,
  "phone_number": "+79991234567",
  "invite_code": "A1B2C3",
  "activated_invite_code": null,
  "referrals": [
    { "phone_number": "+79997654321" }
  ]
}
```

#### 4. Активация кода

`POST /api/profile/`
```json
{ "invite_code": "X9Y8Z7" }
```
```json
{
  "message": "Invite code activated successfully.",
  "profile": { ... }
}
```

---

## Пример `.env`

```dotenv
SECRET_KEY=your-secret-key
DEBUG=True

# Django читает:
DATABASE_NAME=referral_db
DATABASE_USER=referral_user
DATABASE_PASSWORD=postgres
DATABASE_HOST=db
DATABASE_PORT=5432

# Postgres-контейнер читает:
POSTGRES_DB=${DATABASE_NAME}
POSTGRES_USER=${DATABASE_USER}
POSTGRES_PASSWORD=${DATABASE_PASSWORD}
```

---

## Тестирование

### Postman
1. Импортируйте `postman_collection.json`.  
2. «Request Code» → копируйте `dev_code`.  
3. «Verify Code» сохраняет `auth_token` в переменную коллекции.  
4. «Get Profile» / «Activate Invite Code» работают автоматически.

### curl
```bash
TOKEN=… # ваш токен

curl -H "Authorization: Token $TOKEN" http://localhost:8000/api/profile/
```

---
## Развертывание

**Docker Compose (рекомендуется)**
```txt
docker-compose up --build -d
```
Запустите миграции внутри веб-контейнера:
```Bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

---

## Продакшн

- `DEBUG=False`, домены в `ALLOWED_HOSTS`
- `collectstatic`, WhiteNoise/NGINX/CDN
- TLS через прокси (NGINX, Traefik, Caddy)
- Резервное копирование БД
- Секреты — через vault / Docker Secrets