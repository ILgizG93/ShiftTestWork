# Тестовое задание для [ШИФТ](https://vk.com/project_shift)

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)

Приложение, написанное на fastAPI, для регистрации пользователя, аутентификации по JWT-токену и промотра ЗП (Пользователь видит только свои данные).

## 📌 Особенности

- Регистрация/аутентификация JWT
- Документация Swagger/ReDoc
- Миграции при помощи alembic
- Асинхронные запросы к БД
- Валидация данных через Pydantic
- Установка зависимостей через poetry
- Проект и БД запускаются в Docker

## 🚀 Установка

- Копируем из github
```sh
git clone https://github.com/ILgizG93/ShiftTestWork.git
```

- Переходим в директорию fastapi-app
```sh
cd ShiftTestWork/fastapi-app/
```

- Настраиваем .env
```sh
cp .env.template .env
nano .env
```

- Генерируем приватный и публичный ключи для формирования токена
> (если меняли значения в .env, то укажите валидные для себя данные)
```sh
mkdir certs
openssl genrsa -out certs/private_key.pem 2048
openssl rsa -in certs/private_key.pem -outform PEM -pubout -out certs/public_key.pem
```

- Переходим в корневую директорию приложения (ShiftTestWork)
```sh
cd ..
```

- Собираем и запускаем образы Docker
```sh
docker compose build
docker compose up -d
```
> или одной командой
```sh
docker compose build && docker compose up -d
```




## 📚 Документация

| Метод | Эндпоинт              | Входящие данные                  | Пример ответа |
|-------|-----------------------|----------------------------------|---------------|
| POST   | `/user/create`       | `{ "login": "string", "password": "string", "full_name": "string", "salary": 0, "next_raise_date": "2025-08-03 14:53:16" }` | `{ "user_id": "string", "employee_id": "string", "salary": 0, "next_raise_date": "2025-08-03 14:53:18", "login": "string", "full_name": "string" }` |
| POST   | `/user/login`        | `{ "login": "string", "password": "string" }` | `{ "token_type": "Bearer", "access_token": "string", "refresh_token": "string" }`<br><br>`{ "detail": "Incorrect username or password" }` |
| GET    | `/user/salary/get`   | Требуется аутентификация Bearer по access токену | `{ "user_id": "string", "employee_id": "string", "salary": 0, "next_raise_date": "2025-08-03 15:13:53" }`<br><br>`{ "detail": "Invalid token error" }` <br><br>`{ "detail": "Not authenticated" }` |
| POST   | `/token/refresh/`    | Требуется аутентификация Bearer по refresh токену | `{ "token_type": "Bearer", "access_token": "string" }`<br><br>`{ "detail": "Invalid token type 'access' expected 'refresh'" }` |

Больше подробностей доступно по ссылкам:<br>
Swagger UI: YOUR_URL/docs<br>
ReDoc: YOUR_URL/redoc


