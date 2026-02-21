# DjangoOven — API каталога печей

Проект на Django + DRF для каталога товаров (печи, камины и т.д.) с фильтрами и публичным API для фронтенда.

Test
## Что внутри

- Django 5.1 + DRF
- Публичные API-эндпойнты каталога
- Админка для наполнения
- Docker Compose (PostgreSQL + gunicorn)
- SQLite для локальной разработки при `DEBUG=True`

## Быстрый старт (локально, SQLite)

1) Склонируйте проект и перейдите в папку:
```bash
cd DjangoOven
```

2) Создайте `.env` из примера:
```bash
cp .env.example .env
```

3) Убедитесь, что в `.env` стоит `DEBUG=True` (по умолчанию так и есть).

4) Создайте виртуальное окружение и установите зависимости:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5) Примените миграции и запустите сервер:
```bash
python manage.py migrate
python manage.py runserver
```

Проект будет доступен по адресу: `http://127.0.0.1:8000/`

## Запуск через Docker Compose (PostgreSQL + gunicorn)

1) Скопируйте `.env` и заполните:
```bash
cp .env.example .env
```

2) В `.env` установите `DEBUG=False` и пропишите реальные `DB_*` переменные.

3) Запустите:
```bash
docker-compose up --build -d
```

4) Проверьте healthcheck:
```bash
curl http://127.0.0.1:8000/health/
```

## Полезные URL

- `http://127.0.0.1:8000/admin/` — админка
- `http://127.0.0.1:8000/health/` — healthcheck
- `http://127.0.0.1:8000/api/v1/` — API (каталог)

---

# API документация (для фронтенда)

## Общая информация

- Базовый URL: `http://127.0.0.1:8000` (локально)
- Префикс API: `/api/v1/`
- Формат: JSON
- Аутентификация: **не требуется** (эндпойнты каталога публичные)

### Пагинация

Список товаров использует стандартную пагинацию DRF (PageNumberPagination):
- Параметр страницы: `page`
- Размер страницы: `9`

Пример ответа:
```json
{
  "count": 37,
  "next": "http://127.0.0.1:8000/api/v1/catalog/products/?page=2",
  "previous": null,
  "results": [ ... ]
}
```

### Особенности типов

- Все `DecimalField` приходят строками (например, `"100000.00"`).
- Поля файлов/картинок возвращаются как URL (обычно абсолютный) или относительный путь от `MEDIA_URL` (`/media/...`).

---

## 1) Получить фильтры каталога

**GET** `/api/v1/catalog/filters/`

Возвращает дерево разделов, список производителей и список типов топлива.

### Ответ
```json
{
  "sections": [
    {
      "id": 1,
      "name": "Основные печи",
      "slug": "main_oven",
      "menu_name": "",
      "browser_title": "",
      "description": "",
      "meta_description": "",
      "meta_keywords": "",
      "ordering": 1,
      "children": [
        {
          "id": 2,
          "name": "Дочерняя печь",
          "slug": "child_oven",
          "menu_name": "",
          "browser_title": "",
          "description": "",
          "meta_description": "",
          "meta_keywords": "",
          "ordering": 1,
          "children": []
        }
      ]
    }
  ],
  "manufacturers": [
    { "id": 1, "name": "Plamen" },
    { "id": 2, "name": "EasySteam" }
  ],
  "fuel_types": [
    { "value": "gas", "label": "Газ" },
    { "value": "wood", "label": "Дровяной" }
  ]
}
```

---

## 2) Каталог товаров (список)

**GET** `/api/v1/catalog/products/`

---

### Query-параметры

* `search` — поиск по названию товара (регистронезависимый, частичное совпадение)
* `section` — фильтр по разделам (можно несколько):
  `section=1&section=2`

  > Включает выбранные разделы **и все их дочерние категории**.
* `manufacturer` — фильтр по производителям (можно несколько):
  `manufacturer=1&manufacturer=2`
* `fuel_type` — фильтр по типу топлива (можно несколько):
  `fuel_type=wood&fuel_type=gas`
* `price_from` — минимальная цена
* `price_to` — максимальная цена
* `ordering` — сортировка:

  * `popular` — сначала популярные
  * `price_asc` — цена по возрастанию
  * `price_desc` — цена по убыванию
  * если не задано — сортировка по `created_at` (сначала новые)
* `page` — номер страницы (пагинация)

> Важно: фильтрация по цене учитывает скидку.
> Если `discount_price` заполнена — используется она, иначе обычная `price`.

---

### Пример запроса

```bash
curl "http://127.0.0.1:8000/api/v1/catalog/products/?section=1&manufacturer=2&fuel_type=wood&price_from=50000&price_to=150000&ordering=price_asc"
```

---

### Что возвращается

Каждый элемент списка — краткое представление товара (preview):

* базовые поля товара
* главное изображение и галерея
* признаки (`is_new`, `is_popular`, и т.д.)
* `fuel_type_display` — человекочитаемое название топлива
* `has_video` — наличие видеообзора
* `sections` — breadcrumb-путь категории товара

---

### ⚠️ Поле `sections`

Поле `sections` содержит полный путь категории от корня до конечного раздела.

Структура:

```
sections = [
    [root_section, ..., leaf_section]
]
```

Если товар относится к нескольким категориям — возвращается несколько путей.

Это позволяет фронтенду строить breadcrumb без дополнительных запросов.

---

### Ответ (пример)

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 15,
      "name": "Тестовая печь",
      "is_new": false,
      "is_popular": true,
      "is_bestseller": false,
      "has_video": true,
      "price": "100000.00",
      "discount_price": "90000.00",
      "fuel_type": "wood",
      "fuel_type_display": "Дровяной",
      "power_kw": "12.00",

      "sections": [
        [
          {
            "id": 1,
            "name": "Основные печи",
            "slug": "main_oven"
          },
          {
            "id": 2,
            "name": "Дровяные печи",
            "slug": "wood_oven"
          }
        ]
      ],

      "images": [
        {
          "image": "http://127.0.0.1:8000/media/products/test.jpg",
          "is_main": true,
          "ordering": 0
        },
        {
          "image": "http://127.0.0.1:8000/media/products/test1.jpg",
          "is_main": false,
          "ordering": 1
        }
      ]
    }
  ]
}
```

---
## 3) Карточка товара (детально)

**GET** `/api/v1/catalog/products/{id}/`

### Что возвращается

Возвращаются все поля модели `Product` + вложенные сущности:

* `manufacturer` — объект `{id, name}`
* `sections` — массив путей категорий (breadcrumb). Каждый элемент — полный путь раздела **от корня до конечной категории**, к которой привязан товар.
* `images` — массив `{image, is_main, ordering}`
* `documents` — массив `{title, file}`
* `fuel_type_display` — человекочитаемое название топлива

### ⚠️ Поле `sections`

Поле `sections` возвращает **не отдельные категории**, а их полный путь.

Структура:

```
sections = [
    [root_section, ..., leaf_section]
]
```

Это сделано для построения breadcrumb-навигации без дополнительной логики на фронтенде.

Если товар привязан к нескольким категориям — возвращается несколько путей.

### Пример запроса
```bash
curl "http://127.0.0.1:8000/api/v1/catalog/products/15/"
```

### Ответ (пример)
```json
{
  "id": 15,
  "name": "Тестовая печь MAX PRO",
  "slug": "testovaya-pech-max-pro",
  "manufacturer": { "id": 3, "name": "Harvia" },
  "sections": [
    [
      {
        "id": 1,
        "name": "Основные печи",
        "slug": "main_oven"
      },
      {
        "id": 2,
        "name": "Дровяные печи",
        "slug": "wood_oven"
      }
    ]
  ],
  "description": "Полное описание товара",
  "video_url": "https://youtube.com/test",
  "price": "150000.00",
  "discount_price": "120000.00",
  "price_in_euro": true,
  "free_delivery": true,
  "in_stock": true,
  "is_active": true,
  "is_popular": true,
  "is_discount": true,
  "is_new": true,
  "is_bestseller": true,
  "sku": "SKU-123,SKU-456",
  "series": "Premium",
  "dimensions": "800x600x900",
  "weight": "85.50",
  "heated_volume": 120,
  "steam_volume_from": 10,
  "steam_volume_to": 20,
  "chimney_diameter": 115,
  "power_kw": "14.50",
  "stone_weight": 90,
  "material": "cast_iron",
  "firebox_material": "steel",
  "stone_material": "natural",
  "door_type": "with_glass",
  "door_mechanism": "side_opening",
  "fire_view": "panoramic_glass",
  "glass_count": "two",
  "fuel_type": "wood",
  "fuel_type_display": "Дровяной",
  "tank_type": "samovar",
  "firebox_type": "with_extension",
  "stone_type": "combined",
  "water_heating": "with_heat_exchanger",
  "placement": "corner",
  "facing_type": "fireplace_frame",
  "heat_exchanger": true,
  "long_burning": true,
  "glass_lift": true,
  "damper": true,
  "cooking_panel": true,
  "seo_title": "SEO заголовок",
  "seo_description": "SEO описание",
  "seo_keywords": "печь, баня, harvia",
  "created_at": "2026-02-14T10:15:30.123456+0000",
  "updated_at": "2026-02-14T10:15:30.123456+0000",
  "images": [
    {
      "image": "http://127.0.0.1:8000/media/products/test_main.jpg",
      "is_main": true,
      "ordering": 0
    },
    {
      "image": "http://127.0.0.1:8000/media/products/test_2.jpg",
      "is_main": false,
      "ordering": 1
    }
  ],
  "documents": [
    {
      "title": "Инструкция",
      "file": "http://127.0.0.1:8000/media/docs/manual.pdf"
    },
    {
      "title": "Сертификат",
      "file": "http://127.0.0.1:8000/media/docs/cert.pdf"
    }
  ]
}
```

---

## Возможные ошибки

- `404 Not Found` — товар не найден
- `400 Bad Request` — некорректные параметры запроса
- `500 Internal Server Error` — ошибка на сервере

Пример ошибки:
```json
{ "detail": "Not found." }
```
