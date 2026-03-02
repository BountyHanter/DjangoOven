# DjangoOven — API каталога печей

Проект на Django + DRF для каталога товаров (печи, камины и т.д.) с фильтрами и публичным API для фронтенда.

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

- Большинство числовых полей (цены, вес, объёмы) приходят числами.
- `DecimalField` приходят строками (например, `"95.50"` для `package_weight`).
- Поля файлов/картинок возвращаются как URL (обычно абсолютный) или относительный путь от `MEDIA_URL` (`/media/...`).

---

## 1) Получить фильтры каталога

**GET** `/api/v1/catalog/filters/`

Возвращает дерево разделов, список производителей и набор фильтров по характеристикам товаров.

### Разделы (sections)

- Возвращается дерево категорий с вложенными `children`.
- В `children` попадают только активные разделы (`is_active=True`).
- Сортировка внутри одного родителя: сначала по `ordering`, затем по `name`.

### Ответ
```json
{
  "sections": [
    {
      "id": 1,
      "name": "Основные печи",
      "slug": "main_oven",
      "image": "/media/sections/images/main.png",
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
          "image": null,
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
    { "id": 1, "name": "Plamen", "slug": "plamen", "logo": "/media/manufacturers/plamen.png", "priority": 10 },
    { "id": 2, "name": "EasySteam", "slug": "easysteam", "logo": "/media/manufacturers/easysteam.png", "priority": 5 }
  ],
  "filters": {
    "fuel_type": [
      { "value": "gas", "label": "Газовая" },
      { "value": "wood", "label": "Дровяная" }
    ],
    "purpose": [
      { "value": "home", "label": "Для дома" },
      { "value": "sauna_bath", "label": "Для сауны / бани" }
    ]
  }
}
```

Ключи в `filters`:
`purpose`, `fuel_type`, `heated_volume`, `steam_room_volume`, `power_kw`,
`firebox_material`, `firebox_type`, `installation_type`, `firebox_orientation`,
`combustion_type`, `glass_count`, `fire_view`, `cladding_material`,
`heater_type`, `stone_material`, `tank_type`, `door_mechanism`, `chimney_diameter`.

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
* `price_from` — минимальная цена
* `price_to` — максимальная цена
* `discount` — только товары со скидкой (любое truthy-значение, например `1`)
* `ordering` — сортировка:

  * `popular` — сначала популярные
  * `price_asc` — цена по возрастанию
  * `price_desc` — цена по убыванию
  * иначе можно сортировать по любому полю модели `Product`:
    `ordering=price`, `ordering=-price`, `ordering=created_at` и т.д.
  * дополнительно разрешены поля `final_price` и `has_video`
  * если не задано — сортировка по `created_at` (сначала новые)
* `page` — номер страницы (пагинация)

> Важно: фильтрация по цене учитывает скидку.
> Если `discount_price` заполнена — используется она, иначе обычная `price`.

### Авто-фильтры по полям Product

Можно фильтровать по **любому** полю модели `Product` (включая `fuel_type`,
`purpose`, `installation_type`, `power_kw`, `chimney_diameter`, булевые поля и т.д.).

Примеры:

```bash
curl "http://127.0.0.1:8000/api/v1/catalog/products/?purpose=home&installation_type=wall&power_kw=kw_12"
```

Булевые параметры принимают значения `1/0`, `true/false`, `yes/no`, `on/off`.
Неизвестные параметры запроса игнорируются.

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
      "price": 100000,
      "discount_price": 90000,
      "fuel_type": "wood",
      "fuel_type_display": "Дровяная",
      "power_kw": "kw_12",

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
* `video_preview` — превью видео (URL) или `null`
* Для всех полей с choices автоматически добавляется `<field>_display`
  (например `fuel_type_display`, `combustion_type_display`, `power_kw_display`)

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
  "video_preview": "http://127.0.0.1:8000/media/products/video_previews/test.jpg",
  "price": 150000,
  "discount_price": 120000,
  "price_in_euro": true,
  "free_delivery": true,
  "in_stock": true,
  "is_active": true,
  "is_popular": true,
  "is_new": true,
  "is_bestseller": true,
  "sku": "SKU-123,SKU-456",
  "series": "Premium",
  "dimensions": "800x600x900",
  "weight": 85,
  "purpose": "home",
  "fuel_type": "wood",
  "heated_volume": "100_150",
  "steam_room_volume": "20_30",
  "power_kw": "kw_14",
  "firebox_material": "steel",
  "firebox_type": "with_extension",
  "installation_type": "corner",
  "firebox_orientation": "horizontal",
  "combustion_type": "long_burning",
  "glass_count": "two",
  "fire_view": "panoramic_glass",
  "cladding_material": "stone",
  "heater_type": "combined",
  "water_circuit": true,
  "stone_material": "natural",
  "tank_type": "samovar",
  "door_mechanism": "side_opening",
  "chimney_diameter": "115",
  "chimney_connection": "top",
  "steam_volume_from": 10,
  "steam_volume_to": 20,
  "stone_weight": 90,
  "heat_exchanger": true,
  "glass_lift": true,
  "damper": true,
  "cooking_panel": true,
  "efficiency": 82,
  "warranty_years": 5,
  "closed_heater_volume": 30,
  "package_weight": "95.50",
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

## 4) Портфолио

### 4.1) Список портфолио

**GET** `/api/v1/catalog/portfolio/`

Возвращает портфолио с возможностью фильтрации по товару, разделу, производителю и признаку `main`.

### 4.2) Портфолио по товару

**GET** `/api/v1/catalog/products/{product_id}/portfolio/`

Возвращает портфолио конкретного товара.

### Query-параметры

* `product` — фильтр по товару (ID)
* `section` — фильтр по разделу (ID)
* `manufacturer` — фильтр по производителю (ID, можно несколько)
* `main` — только для главной (`main=true`)

### Что возвращается

Каждое портфолио содержит:

* `id`
* `title` — название
* `main` — выводить на главной
* `duration` — срок работ (в днях)
* `date` — дата работ
* `object_type` — тип объекта
* `price` — стоимость
* `video_link` — ссылка на видео
* `images` — список фото
* `type_work` — тип работ
* `product_id` — ID товара
* `product_name` — название товара
* `created_at` — дата создания

Каждое изображение в `images` содержит:

* `id`
* `image` — ссылка на изображение
* `order` — порядок отображения

### Пример запроса
```bash
curl "http://127.0.0.1:8000/api/v1/catalog/portfolio/?section=2&main=true"
```

### Ответ (пример)
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 10,
      "title": "Монтаж печи",
      "main": true,
      "duration": 2,
      "date": "2026-02-10",
      "object_type": "Баня",
      "price": 120000,
      "video_link": "https://youtube.com/test",
      "images": [
        {
          "id": 101,
          "image": "http://127.0.0.1:8000/media/portfolio_image/p1.jpg",
          "order": 0
        },
        {
          "id": 102,
          "image": "http://127.0.0.1:8000/media/portfolio_image/p1-2.jpg",
          "order": 1
        }
      ],
      "type_work": "Монтаж и подключение",
      "product_id": 15,
      "product_name": "Тестовая печь MAX PRO",
      "created_at": "2026-02-20T12:10:30.123456+0000"
    },
    {
      "id": 9,
      "title": "Установка дымохода",
      "main": true,
      "duration": 1,
      "date": "2026-02-08",
      "object_type": "Дом",
      "price": 80000,
      "video_link": "",
      "images": [
        {
          "id": 103,
          "image": "http://127.0.0.1:8000/media/portfolio_image/p2.jpg",
          "order": 0
        }
      ],
      "type_work": "Монтаж",
      "product_id": 15,
      "product_name": "Тестовая печь MAX PRO",
      "created_at": "2026-02-18T09:05:10.123456+0000"
    }
  ]
}
```

---

## 5) Отзывы

### 5.1) Список всех отзывов

**GET** `/api/v1/catalog/reviews/`

Возвращает все отзывы, отсортированные от новых к старым.

### 5.2) Отзывы по товару

**GET** `/api/v1/catalog/products/{product_id}/reviews/`

Возвращает отзывы конкретного товара, отсортированные от новых к старым.

### Что возвращается

Каждый отзыв содержит:

* `id`
* `name` — название отзыва
* `client_name` — имя клиента
* `installation_time` — время, затраченное на монтаж
* `location` — локация
* `work_description` — что сделано
* `price` — стоимость
* `video_url` — ссылка на видео
* `preview_image` — превью для видео (может быть `null`)
* `product_id` — ID товара
* `product_name` — название товара
* `created_at` — дата создания

### Пример запроса
```bash
curl "http://127.0.0.1:8000/api/v1/catalog/products/15/reviews/"
```

### Ответ (пример)
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 5,
      "name": "Отзыв о монтаже",
      "client_name": "Иван Петров",
      "installation_time": "1 день",
      "location": "Москва",
      "work_description": "Установка печи и дымохода",
      "price": 120000,
      "video_url": "https://youtube.com/test",
      "preview_image": "http://127.0.0.1:8000/media/reviews/video_preview/review-5.jpg",
      "product_id": 15,
      "product_name": "Тестовая печь MAX PRO",
      "created_at": "2026-02-20T12:10:30.123456+0000"
    },
    {
      "id": 4,
      "name": "Отзыв о доставке",
      "client_name": "Мария Иванова",
      "installation_time": "2 дня",
      "location": "Тверь",
      "work_description": "Доставка и подключение",
      "price": 90000,
      "video_url": "https://youtube.com/test2",
      "preview_image": null,
      "product_id": 15,
      "product_name": "Тестовая печь MAX PRO",
      "created_at": "2026-02-18T09:05:10.123456+0000"
    }
  ]
}
```

---

## 6) Производители

### 6.1) Список производителей

**GET** `/api/v1/catalog/manufacturers/`

Возвращает активные бренды, отсортированные по алфавиту.

### Query-параметры

* `ordering` — сортировка:
  * `priority` — по приоритету (больше → выше) и затем по названию
  * если не задано — по алфавиту

### Что возвращается

Каждый производитель содержит:

* `id`
* `name`
* `slug`
* `logo` — ссылка на логотип
* `priority` — приоритет отображения

### Пример запроса
```bash
curl "http://127.0.0.1:8000/api/v1/catalog/manufacturers/?ordering=priority"
```

### Ответ (пример)
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Plamen",
      "slug": "plamen",
      "logo": "http://127.0.0.1:8000/media/manufacturers/plamen.png",
      "priority": 10
    },
    {
      "id": 2,
      "name": "EasySteam",
      "slug": "easysteam",
      "logo": "http://127.0.0.1:8000/media/manufacturers/easysteam.png",
      "priority": 5
    }
  ]
}
```

---

### 6.2) Детальная карточка производителя

**GET** `/api/v1/catalog/manufacturers/{id}/`

Возвращает данные производителя и галерею изображений.

### Что возвращается

* `id`
* `name`
* `slug`
* `logo`
* `priority`
* `is_active` — активен/неактивен
* `seo_title` — название страницы
* `seo_description` — описание страницы
* `seo_keywords` — SEO ключевые слова
* `short_description` — краткое описание
* `description` — полное описание
* `video` — видео (строка/URL)
* `images` — массив изображений производителя `{id, image, ordering}`

### Пример запроса
```bash
curl "http://127.0.0.1:8000/api/v1/catalog/manufacturers/3/"
```

### Ответ (пример)
```json
{
  "id": 3,
  "name": "Harvia",
  "slug": "harvia",
  "is_active": true,
  "logo": "http://127.0.0.1:8000/media/manufacturers/harvia.png",
  "priority": 100,
  "seo_title": "Harvia — печи для бани",
  "seo_description": "Описание страницы бренда",
  "seo_keywords": "печи, баня, harvia",
  "short_description": "Финские печи для бани",
  "description": "Полное описание бренда",
  "video": "https://youtube.com/test",
  "images": [
    {
      "id": 10,
      "image": "http://127.0.0.1:8000/media/manufacturer_images/harvia_1.jpg",
      "ordering": 0
    },
    {
      "id": 11,
      "image": "http://127.0.0.1:8000/media/manufacturer_images/harvia_2.jpg",
      "ordering": 1
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
