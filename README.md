# 🐾 Помощь хвостикам — Animal Shelter MVP

Веб-платформа для поиска и усыновления животных из приютов. MVP информационной системы помощи приютам для животных.

---

##  О проекте

**Проблема:** Отсутствие единой платформы для взаимодействия приютов, волонтёров и людей, желающих взять животное из приюта.

**Решение:** Централизованный сервис, где можно:
- Найти животных по фильтрам (вид, возраст, размер)
- Просмотреть информацию о питомце (фото, характер, здоровье)
- Сохранить животных в избранное
- Подать заявку на усыновление

---

##  Технологии

| Компонент | Технология |
|----------|------------|
| Backend | FastAPI (Python) |
| ORM | SQLAlchemy (асинхронный) |
| База данных | Supabase (PostgreSQL) |
| Фронтенд | HTML + CSS + JavaScript |
| Деплой | Render |

---

##  Установка и запуск

### Требования
- Python 3.11+
- PostgreSQL (или Supabase)

### Установка и запуск проекта

```bash
git clone https://github.com/Vladikw/animal-shelter-mvp.git
cd animal-shelter-mvp
python -m venv .venv
```

Активация виртуального окружения:

Windows:
```
.venv\Scripts\activate
```

Linux / Mac:
```
source .venv/bin/activate
```

Установка зависимостей:
```
pip install -r requirements.txt
```

Создать файл `.env` в папке `app` и добавить:
```
APP_CONFIG__DB__URL=postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DBNAME
```

Запуск приложения:
```
python main.py
```

или

```
uvicorn main:main_app --reload
```

---

##  API документация

После запуска:

- Swagger UI: http://localhost:8000/docs  
- ReDoc: http://localhost:8000/redoc  

---

##  Структура проекта

```
app/
 ├── api/          # Роуты (animals, adoptions, photos)
 ├── models/       # Модели базы данных (SQLAlchemy)
 ├── config/       # Конфигурация
 ├── static/       # CSS, JS
 ├── templates/    # HTML страницы
 └── main.py       # Точка входа
```

---

## Основные сущности

- User (пользователь)  
- Shelter (приют)  
- Animal (животное)  
- Photo (фото)  
- Adoption (заявка)  
- Favorite (избранное)  
- Notification (уведомления)  

 