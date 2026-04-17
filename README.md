# DjangoOven Frontend API Documentation

Документация ниже описывает API именно как контракт для фронтенда.
Только фактическое поведение текущего бэкенда: URL, параметры, фильтры, пагинация, сортировка и структура ответов.

## 1. Base URL и общие правила

- Base URL (локально): `http://127.0.0.1:8000`
- API prefix: `/api/v1/`
- Формат: JSON
- Аутентификация: для публичных каталоговых endpoint не требуется
- Медиа-файлы (`image`, `file`) обычно приходят как URL вида `/media/...` или абсолютный URL (зависит от контекста запроса)

## 2. Общая пагинация (для всех list endpoint)

Все endpoint на `ListAPIView` используют одну и ту же пагинацию:

- `page` — номер страницы
- `page_size` — размер страницы
- `page_size` по умолчанию: `9`
- `max page_size`: `10000`

Типовой ответ:

```json
{
  "count": 37,
  "next": "http://127.0.0.1:8000/api/v1/catalog/products/?page=2",
  "previous": null,
  "results": []
}
```

## 3. Форматы и типы

- `datetime`: формат `%Y-%m-%dT%H:%M:%S.%f%z` (например, `2026-03-07T12:44:10.123456+0000`)
- `DecimalField`: строкой (например, `"95.50"`)
- `IntegerField`: числом
- `BooleanField`: `true/false`

## 4. Быстрый список endpoint

- `GET /api/v1/health/` — healthcheck
- `GET /api/v1/catalog/filters/` — дерево разделов + бренды + метаданные фильтров + сортировки
- `GET /api/v1/catalog/products/` — список товаров (каталог)
- `GET /api/v1/catalog/products/{id}/` — карточка товара
- `GET /api/v1/catalog/portfolio/` — список портфолио
- `GET /api/v1/catalog/products/{product_id}/portfolio/` — портфолио товара
- `GET /api/v1/catalog/reviews/` — все отзывы
- `GET /api/v1/catalog/products/{product_id}/reviews/` — отзывы товара
- `GET /api/v1/catalog/manufacturers/` — список производителей
- `GET /api/v1/catalog/manufacturers/{id}/` — карточка производителя
- `GET /api/v1/catalog/banners/` — список баннеров

---

## 5. Filters API

### `GET /api/v1/catalog/filters/`

Возвращает:

- `sections` — дерево разделов
- `manufacturers` — список активных брендов + количество активных товаров в каждом (`count`)
- `filters` — конфигурация фильтров для каталога
- `sorting` — доступные варианты сортировки

### sections (дерево)

- В корне только разделы: `is_active=true` и `parent=null`
- В `children` попадают только активные дочерние разделы
- Сортировка в каждом уровне: `ordering`, затем `name`
- `count` у раздела = количество **активных** товаров в разделе + всех дочерних разделах

Пример элемента раздела:

```json
{
  "id": 1,
  "name": "Основные печи",
  "slug": "main_oven",
  "description_main": "",
  "image": "/media/sections/images/main.png",
  "browser_title": "",
  "description": "",
  "meta_description": "",
  "meta_keywords": "",
  "ordering": 1,
  "count": 12,
  "children": []
}
```

### manufacturers в этом endpoint

Поля:

- `id`
- `name`
- `slug`
- `logo`
- `priority`
- `count` — количество активных товаров бренда

### sorting в этом endpoint

Текущие варианты:

- `new` — сначала новые
- `popular` — сначала популярное (`is_bestseller=true`), внутри по новизне
- `price_asc` — по возрастанию итоговой цены
- `price_desc` — по убыванию итоговой цены

Пример:

```json
[
  { "value": "new", "label": "Сначала новые" },
  { "value": "popular", "label": "Сначала популярные" },
  { "value": "price_asc", "label": "Сначала дешёвые" },
  { "value": "price_desc", "label": "Сначала дорогие" }
]
```

### filters в этом endpoint

`filters` — массив конфигов. Основные типы:

- `range`
- `select`
- `boolean`

Примеры:

```json
{
  "field": "price",
  "label": "Цена",
  "type": "range",
  "min": 10000,
  "max": 300000,
  "params": { "min": "price_from", "max": "price_to" }
}
```

```json
{
  "field": "fuel_type",
  "label": "Тип топлива",
  "type": "select",
  "options": [
    { "value": "wood", "label": "Дровяная", "count": 10 },
    { "value": "gas", "label": "Газовая", "count": 3 }
  ]
}
```

```json
{
  "field": "heated_volume",
  "label": "Площадь/объём отопления",
  "type": "select",
  "options": [
    { "value": 100, "label": "100", "count": 7 },
    { "value": 150, "label": "150", "count": 4 }
  ]
}
```

`heated_volume` формируется из уникальных значений в БД (только `is_active=true`), не из фиксированных `choices`.

```json
{
  "field": "water_circuit",
  "label": "Водяной контур",
  "type": "boolean",
  "count": 5
}
```

```json
{
  "field": "discount",
  "label": "Со скидкой",
  "type": "boolean"
}
```

---

## 6. Products Catalog API

### `GET /api/v1/catalog/products/`

Список активных товаров (`is_active=true`).

### 6.1 Поддерживаемые query-параметры

#### Текстовый поиск

- `search` — поиск по `name` (icontains)

#### Мульти-фильтры

Передаются повторением ключа:

- `section=1&section=2`
- `manufacturer=3&manufacturer=7`
- `fuel_type=wood&fuel_type=gas`
- аналогично для остальных `select`-полей

#### Список select-полей

- `fuel_type`
- `heated_volume`
- `lining_material`
- `firebox_material`
- `firebox_type`
- `installation_type`
- `glass_count`
- `fire_view`
- `heater_type`
- `stone_material`
- `tank_type`
- `door_mechanism`
- `chimney_connection`
- `chimney_diameter`

#### Boolean-поля

- `water_circuit`
- `long_fire`
- `heat_exchanger`
- `glass_lift`
- `damper`
- `cooking_panel`
- `discount` (только товары с заполненным `discount_price`)

Поддерживаются обычные булевы значения (`true/false`, `1/0`, и т.д.).

#### Range-поля

- `price_from`, `price_to`
- `power_kw_min`, `power_kw_max`
- `steam_volume_from`, `steam_volume_to`

#### Сортировка

- `ordering=new`
- `ordering=popular`
- `ordering=price_asc`
- `ordering=price_desc`
- если передано неизвестное значение, используется `new`

### 6.2 Важная логика фильтрации

- Фильтр по `section` включает выбранный раздел + всех его активных потомков
- Фильтр по `manufacturer` возвращает товары только активных брендов
- Цена фильтруется по `final_price`:
  - если `discount_price` задана, используется она
  - иначе используется `price`
- `discount=true` возвращает только товары, где `discount_price` не `null`
- Фильтр по `steam_volume_*` работает по пересечению диапазонов:
  - `steam_volume_to >= steam_volume_from(query)`
  - `steam_volume_from <= steam_volume_to(query)`
- Неизвестные query-параметры игнорируются

### 6.3 Пример запроса

```bash
curl "http://127.0.0.1:8000/api/v1/catalog/products/?search=печь&section=1&manufacturer=2&fuel_type=wood&price_from=50000&price_to=150000&ordering=price_asc&page=1&page_size=9"
```

### 6.4 Структура элемента в `results`

Поля:

- `id`
- `name`
- `sections` — массив breadcrumb-путей
- `manufacturer` — объект `{ "name": ... }`
- `is_new`
- `is_bestseller`
- `has_video`
- `price`
- `discount_price`
- `power_kw`
- `images` — массив `{image, is_main, ordering}`

Пример ответа:

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 15,
      "name": "Тестовая печь",
      "sections": [
        [
          { "id": 1, "name": "Основные печи", "slug": "main_oven" },
          { "id": 2, "name": "Дровяные печи", "slug": "wood_oven" }
        ]
      ],
      "manufacturer": { "name": "Harvia" },
      "is_new": false,
      "is_bestseller": true,
      "has_video": true,
      "price": 100000,
      "discount_price": 90000,
      "power_kw": 12,
      "images": [
        {
          "image": "http://127.0.0.1:8000/media/products/images/test.jpg",
          "is_main": true,
          "ordering": 0
        }
      ]
    }
  ]
}
```

### 6.5 Как читать `sections` в товарах

`sections` — это не просто список категорий, а список путей (breadcrumb):

```text
sections = [
  [root, ..., leaf],
  [root2, ..., leaf2]
]
```

Если товар привязан к нескольким разделам, путей будет несколько.

---

## 7. Product Detail API

### `GET /api/v1/catalog/products/{id}/`

Возвращает детальную карточку активного товара (`is_active=true`).

Если товар не найден или неактивен: `404`.

### 7.1 Что возвращается

- Все поля модели `Product`
- `manufacturer` в формате `{ id, name }`
- `sections` в формате breadcrumb-путей
- `images` — `{ image, is_main, ordering }`
- `documents` — `{ title, file }`
- Автоматически добавляются `*_display` для полей с `choices`

### 7.2 Поля модели Product (текущий набор)

- `id`, `name`, `slug`
- `manufacturer`
- `description`, `video_url`, `video_preview`, `schema`
- `price`, `discount_price`
- `free_delivery`, `in_stock`, `is_active`, `is_new`, `is_bestseller`
- `sku`, `series`
- `heated_volume`, `power_kw`, `lining_material`, `fuel_type`, `firebox_material`, `firebox_type`, `installation_type`
- `glass_count`, `fire_view`, `heater_type`, `water_circuit`, `stone_material`, `tank_type`, `door_mechanism`
- `chimney_diameter`, `chimney_connection`
- `dimensions`, `weight`
- `steam_volume_from`, `steam_volume_to`
- `stone_weight`, `closed_heater_volume`, `warranty_years`, `efficiency`
- `long_fire`, `heat_exchanger`, `glass_lift`, `damper`, `cooking_panel`
- `package_weight`
- `seo_title`, `seo_description`, `seo_keywords`
- `created_at`, `updated_at`

### 7.3 Пример запроса

```bash
curl "http://127.0.0.1:8000/api/v1/catalog/products/15/"
```

### 7.4 Пример ответа (сокращенный)

```json
{
  "id": 15,
  "name": "Тестовая печь MAX PRO",
  "slug": "testovaya-pech-max-pro",
  "manufacturer": { "id": 3, "name": "Harvia" },
  "sections": [
    [
      { "id": 1, "name": "Основные печи", "slug": "main_oven" },
      { "id": 2, "name": "Дровяные печи", "slug": "wood_oven" }
    ]
  ],
  "price": 150000,
  "discount_price": 120000,
  "fuel_type": "wood",
  "fuel_type_display": "Дровяная",
  "power_kw": 14,
  "water_circuit": true,
  "heat_exchanger": true,
  "images": [
    {
      "image": "http://127.0.0.1:8000/media/products/images/test_main.jpg",
      "is_main": true,
      "ordering": 0
    }
  ],
  "documents": [
    {
      "title": "Инструкция",
      "file": "http://127.0.0.1:8000/media/products/documents/manual.pdf"
    }
  ],
  "created_at": "2026-03-07T12:44:10.123456+0000",
  "updated_at": "2026-03-07T12:44:10.123456+0000"
}
```

---

## 8. Portfolio API

### 8.1 `GET /api/v1/catalog/portfolio/`

Список портфолио, сортировка: новые сначала (`-created_at`).

### 8.2 `GET /api/v1/catalog/products/{product_id}/portfolio/`

Список портфолио конкретного товара.

### 8.3 Query-параметры (`/catalog/portfolio/`)

- `product` — ID товара
- `section` — ID раздела (включая дочерние)
- `manufacturer` — ID производителя
- `main=true` — только записи для главной

### 8.4 Пример

```bash
curl "http://127.0.0.1:8000/api/v1/catalog/portfolio/?section=2&main=true&page=1&page_size=9"
```

### 8.5 Элемент в `results`

- `id`
- `title`
- `main`
- `duration`
- `date`
- `object_type`
- `price`
- `video_link`
- `type_work`
- `product_id`
- `product_name`
- `images` — `{id, image, order}`
- `created_at`

---

## 9. Reviews API

### 9.1 `GET /api/v1/catalog/reviews/`

Список всех отзывов, сортировка по убыванию `created_at`.

### 9.2 `GET /api/v1/catalog/products/{product_id}/reviews/`

Список отзывов товара.

### 9.3 Пример

```bash
curl "http://127.0.0.1:8000/api/v1/catalog/products/15/reviews/?page=1&page_size=9"
```

### 9.4 Элемент в `results`

- `id`
- `name`
- `client_name`
- `installation_time`
- `location`
- `date`
- `work_description`
- `price`
- `video_url`
- `preview_image`
- `product_id`
- `product_name`
- `created_at`

---

## 10. Manufacturers API

### 10.1 `GET /api/v1/catalog/manufacturers/`

Возвращает только активных производителей (`is_active=true`).

Query-параметры:

- `ordering=priority` — сортировка по `-priority`, затем `name`
- без `ordering` — сортировка по `name`

Поля элемента:

- `id`
- `name`
- `slug`
- `logo`
- `priority`

Пример:

```bash
curl "http://127.0.0.1:8000/api/v1/catalog/manufacturers/?ordering=priority&page=1&page_size=9"
```

### 10.2 `GET /api/v1/catalog/manufacturers/{id}/`

Карточка конкретного активного производителя.

Если `is_active=false` или id не найден: `404`.

Поля:

- `id`, `name`, `slug`, `is_active`, `logo`, `priority`
- `seo_title`, `seo_description`, `seo_keywords`
- `short_description`, `description`, `video`
- `images` — `{id, image, ordering}`

Пример:

```bash
curl "http://127.0.0.1:8000/api/v1/catalog/manufacturers/3/"
```

---

## 11. Banners API

### `GET /api/v1/catalog/banners/`

Query-параметры:

- `section` — ID раздела
- `brand` — ID производителя

Логика:

- если передан `section`, вернутся баннеры раздела + глобальные (без раздела)
- если передан `brand`, вернутся баннеры бренда + глобальные (без бренда)
- если переданы оба, применяются оба условия

Поля элемента:

- `id`
- `title`
- `image`
- `link` — URL для перехода по баннеру

Пример:

```bash
curl "http://127.0.0.1:8000/api/v1/catalog/banners/?section=1&brand=2&page=1&page_size=9"
```

---

## 12. Healthcheck

### `GET /api/v1/health/`

- `200`: `{ "status": "ok" }`
- `503`: `{ "status": "db_error" }` (нет соединения с БД)

---

## 13. Ошибки и пограничные случаи

- Не найден detail-объект: `404` + стандартный DRF ответ (`{"detail":"Not found."}`)
- Невалидные значения фильтров каталога (например неизвестный choice): `400`
- Неизвестные query-параметры в каталоге товаров: игнорируются
- Для boolean-фильтров каталога ориентируйтесь на явную передачу параметров:
  не отправляйте лишние boolean-ключи в query string, если не хотите фильтрацию по ним
- Все list endpoint отдают paginated-структуру (`count/next/previous/results`)

---

## 14. Рекомендации для фронтенда

1. Храните query state как объект фильтров и сериализуйте повторяющиеся параметры через повтор ключа (`field=a&field=b`).
2. Для каталога используйте `/catalog/filters/` как единственный источник метаданных фильтрации и сортировок.
3. Для хлебных крошек всегда используйте `sections` из ответа товара (там уже готовый путь).
4. Всегда проверяйте `next` и `previous` для пагинации; не рассчитывайте количество страниц вручную.
5. Для цены в карточках/листинге учитывайте `discount_price` как приоритетную цену показа.
