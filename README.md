# DjangoOven Frontend API Documentation

Документация описывает публичный контракт API для фронтенда: URL, параметры, пагинацию и структуру ответов.

## 1. Base URL и общие правила

- Base URL локально: `http://127.0.0.1:8000`
- API prefix: `/api/v1/`
- Формат: JSON
- Публичные endpoint работают без авторизации
- Медиа-файлы обычно приходят как `/media/...`; при запросе с полным host могут быть абсолютными URL

## 2. Пагинация

List endpoint используют page-number пагинацию:

- `page` — номер страницы
- `page_size` — размер страницы
- `page_size` по умолчанию: `9`
- максимальный `page_size`: `10000`

Типовой ответ:

```json
{
  "count": 37,
  "next": "http://127.0.0.1:8000/api/v1/catalog/products/?page=2",
  "previous": null,
  "results": []
}
```

Форматы данных, на которые стоит ориентироваться:

- `datetime` приходит строкой в формате `2026-03-07T12:44:10.123456+0000`;
- цены (`price`, `discount_price`, `price.min`, `price.max`) приходят числами;
- значения числовых характеристик в карточках товара приходят строками, например `"18.50"`;
- диапазоны числовых характеристик в `/catalog/filters/` приходят числами;
- boolean-значения приходят как `true` или `false`.

## 3. Быстрый список endpoint

- `GET /api/v1/health/` — healthcheck
- `POST /api/v1/send-email-request/` — заявка с телефона и ссылки
- `GET /api/v1/catalog/filters/` — дерево разделов, бренды и доступные фильтры
- `GET /api/v1/catalog/products/` — список товаров каталога
- `GET /api/v1/catalog/products/{id}/` — карточка товара
- `GET /api/v1/catalog/portfolio/` — список портфолио
- `GET /api/v1/catalog/products/{product_id}/portfolio/` — портфолио товара
- `GET /api/v1/catalog/reviews/` — все отзывы
- `GET /api/v1/catalog/products/{product_id}/reviews/` — отзывы товара
- `GET /api/v1/catalog/manufacturers/` — список производителей
- `GET /api/v1/catalog/manufacturers/{id}/` — карточка производителя
- `GET /api/v1/catalog/banners/` — список баннеров

## 4. Catalog Filters API

### `GET /api/v1/catalog/filters/`

Возвращает данные для построения каталожных фильтров. Endpoint можно вызывать без параметров или с текущими выбранными фильтрами в query-параметре `filters`.

`filters` передается как JSON-строка, закодированная для URL:

```js
const filters = encodeURIComponent(JSON.stringify([
  { type: "section", ids: [3] },
  { type: "manufacturer", ids: [7] }
]));

fetch(`/api/v1/catalog/filters/?filters=${filters}`);
```

Если `filters` невалидный JSON или не массив объектов, ответ будет `400`:

```json
{
  "detail": "Некорректный формат filters. Ожидается JSON-список объектов."
}
```

### Структура ответа

```json
{
  "sections": [
    {
      "id": 1,
      "name": "Каталог",
      "slug": "catalog-root",
      "products_count": 5,
      "children": []
    }
  ],
  "price": {
    "min": 45000,
    "max": 210000
  },
  "has_discount": true,
  "manufacturers": [
    {
      "id": 1,
      "name": "Aurora",
      "slug": "aurora",
      "logo": "manufacturers/aurora.webp",
      "products_count": 3
    }
  ],
  "attributes": []
}
```

- `sections` возвращаются всегда, только активные, с любой вложенностью.
- `products_count` у раздела учитывает товары в самом разделе и во всех дочерних разделах.
- Разделы без товаров не скрываются, у них `products_count: 0`.
- `price.min/max` считаются по итоговой цене товара: `discount_price`, если она есть, иначе `price`.
- `manufacturers` и `attributes` могут отсутствовать, если для текущей выборки нет данных.
- Все счетчики и диапазоны пересчитываются с учетом переданного `filters`.

### Форматы атрибутов

`choice`:

```json
{
  "id": 10,
  "name": "Тип топлива",
  "slug": "fuel-type",
  "type": "choice",
  "unit": "",
  "allow_multiple": false,
  "products_count": 4,
  "options": [
    {
      "id": 101,
      "value": "Дрова",
      "slug": "wood",
      "products_count": 2
    }
  ]
}
```

`number`:

```json
{
  "id": 11,
  "name": "Мощность",
  "slug": "moshchnost",
  "type": "number",
  "unit": "кВт",
  "allow_multiple": false,
  "products_count": 4,
  "min": 10.0,
  "max": 22.0
}
```

`boolean`:

```json
{
  "id": 12,
  "name": "Водяной контур",
  "slug": "water-circuit",
  "type": "boolean",
  "unit": "",
  "allow_multiple": false,
  "products_count": 4,
  "values": [
    { "value": true, "products_count": 2 },
    { "value": false, "products_count": 2 }
  ]
}
```

## 5. Products Catalog API

### `GET /api/v1/catalog/products/`

Возвращает активные товары каталога (`is_active=true`) с пагинацией.

Каталог использует тот же query-параметр `filters`, что и `/catalog/filters/`:

```bash
curl "http://127.0.0.1:8000/api/v1/catalog/products/?filters=%5B%7B%22type%22%3A%22section%22%2C%22ids%22%3A%5B3%5D%7D%5D&page=1&page_size=9"
```

### Поддерживаемые фильтры

Между объектами фильтра применяется `AND`. Внутри `ids` и `option_ids` применяется `OR`.

Раздел:

```json
{ "type": "section", "ids": [3, 4] }
```

Фильтр по разделу включает выбранные разделы и всех активных потомков.

Производитель:

```json
{ "type": "manufacturer", "ids": [7, 8] }
```

Вариант характеристики:

```json
{
  "type": "choice",
  "attribute_id": 10,
  "option_ids": [101, 102]
}
```

Числовая характеристика:

```json
{
  "type": "number",
  "attribute_id": 11,
  "gte": "10",
  "lte": "20"
}
```

Boolean-характеристика:

```json
{
  "type": "boolean",
  "attribute_id": 12,
  "value": true
}
```

Цена:

```json
{
  "type": "price",
  "gte": 50000,
  "lte": 150000
}
```

Цена фильтруется по итоговой цене товара: `discount_price`, если она есть, иначе `price`.

Скидка:

```json
{
  "type": "has_discount",
  "value": true
}
```

`has_discount=true` возвращает товары с заполненным `discount_price`. `has_discount=false` возвращает товары без скидки.

Старые query-параметры каталога вроде `section=`, `manufacturer=`, `fuel_type=`, `price_from=`, `price_to=`, `search=` и `ordering=` сейчас не являются контрактом `GET /catalog/products/`.

### Сортировка каталога

Отдельный query-параметр сортировки сейчас не используется. Текущий порядок выдачи:

1. хиты (`is_bestseller=true`) с `priority`, где `1` — самый высокий приоритет;
2. хиты без `priority`;
3. товары с `priority`, но без флага хита;
4. остальные товары, внутри группы сначала новые.

### Элемент в `results`

```json
{
  "id": 15,
  "name": "Aurora Pro 18 Duo",
  "sections": [
    [
      { "id": 1, "name": "Каталог", "slug": "catalog-root" },
      { "id": 2, "name": "Банные печи", "slug": "sauna-stoves" },
      { "id": 3, "name": "Дровяные печи", "slug": "wood-fired-stoves" }
    ]
  ],
  "manufacturer": "Aurora",
  "is_new": true,
  "is_bestseller": true,
  "priority": 1,
  "has_video": true,
  "price": 162000,
  "discount_price": 129000,
  "power": {
    "name": "Мощность",
    "slug": "moshchnost",
    "value": "18.50",
    "unit": "кВт"
  },
  "images": [
    {
      "id": 1,
      "image": "/media/products/images/aurora-pro-main.webp",
      "ordering": 20,
      "is_main": true
    }
  ]
}
```

Особенности:

- `manufacturer` — строка с названием бренда или `null`.
- `sections` — массив breadcrumb-путей. Каждый путь идет от корневого раздела к разделу товара.
- `power` берется из числовой характеристики со slug `moshchnost`; если значения нет, будет `null`.
- `images` сортируются так, чтобы главное изображение было первым, затем `ordering`, затем `id`.
- `is_main` в изображении приходит только у главного изображения; у остальных ключ может отсутствовать.

Если товар привязан к нескольким разделам, в `sections` будет несколько путей. Для хлебных крошек страницы товара можно взять нужный путь и добавить перед ним `Главная`, а после него название товара:

```text
Главная / Каталог / Банные печи / Электрокаменка Эверест Черный Кристалл (Black Crystal) с пультом - 6кВт
```

## 6. Product Detail API

### `GET /api/v1/catalog/products/{id}/`

Возвращает детальную карточку активного товара. Если товар не найден или неактивен, ответ будет `404`.

```json
{
  "id": 15,
  "name": "Harvia Legend GreenFlame 240 Duo",
  "slug": "harvia-legend-greenflame-240-duo",
  "manufacturer": "Harvia Legend",
  "price": 189900,
  "discount_price": 174500,
  "description": "Подробное описание товара",
  "is_new": true,
  "is_bestseller": true,
  "priority": 7,
  "created_at": "2026-03-07T12:44:10.123456+0000",
  "sections": [
    [
      { "id": 1, "name": "Каталог", "slug": "catalog-root" },
      { "id": 2, "name": "Банные печи", "slug": "sauna-stoves" }
    ]
  ],
  "images": [],
  "videos": [],
  "documents": [],
  "attributes": []
}
```

Текущий detail-контракт отдает только перечисленные поля. SEO-поля, `sku`, `series`, `schema`, `video_preview`, `in_stock` и `free_delivery` сейчас в ответе detail не приходят.

### Изображения, видео, документы

`images`:

```json
{
  "id": 1,
  "image": "/media/products/images/legend-main.webp",
  "ordering": 10,
  "is_main": true
}
```

`videos`:

```json
{
  "id": 1,
  "url": "https://www.youtube.com/watch?v=legend-installation",
  "preview_url": "https://img.youtube.com/vi/legend-installation/maxresdefault.jpg",
  "ordering": 10
}
```

`documents`:

```json
{
  "id": 1,
  "title": "Инструкция по монтажу",
  "file": "/media/products/documents/legend-installation.pdf",
  "ordering": 20
}
```

### Характеристики товара

Все технические характеристики товара приходят в `attributes`.

`choice` с одним значением:

```json
{
  "id": 10,
  "name": "Тип топлива",
  "slug": "fuel-type",
  "type": "choice",
  "value": {
    "id": 101,
    "name": "Дрова",
    "slug": "wood"
  }
}
```

`choice` с несколькими значениями:

```json
{
  "id": 11,
  "name": "Материалы отделки",
  "slug": "finish-materials",
  "type": "choice",
  "value": [
    { "id": 201, "name": "Талькохлорит", "slug": "soapstone" },
    { "id": 202, "name": "Нержавеющая сталь", "slug": "stainless-steel" }
  ]
}
```

`number`:

```json
{
  "id": 12,
  "name": "Мощность",
  "slug": "power-kw",
  "type": "number",
  "unit": "кВт",
  "value": "18.50"
}
```

`boolean`:

```json
{
  "id": 13,
  "name": "Водяной контур",
  "slug": "water-circuit",
  "type": "boolean",
  "value": true
}
```

`text`:

```json
{
  "id": 14,
  "name": "Комментарий к монтажу",
  "slug": "installation-note",
  "type": "text",
  "value": "Нужен негорючий экран"
}
```

## 7. Portfolio API

### `GET /api/v1/catalog/portfolio/`

Список портфолио, сортировка: новые сначала (`-created_at`).

Query-параметры:

- `product` — ID товара
- `section` — ID раздела; учитывается выбранный раздел и дочерние разделы
- `manufacturer` — ID производителя; можно передавать повтором или CSV: `manufacturer=1&manufacturer=2` или `manufacturer=1,2`
- `main=true` — только записи для главной

Если `product`, `section` или `manufacturer` переданы не числом, ответ будет `400`. Если `section` не найден, ответ будет `404`.

Пример:

```bash
curl "http://127.0.0.1:8000/api/v1/catalog/portfolio/?section=2&manufacturer=1,2&main=true&page=1&page_size=9"
```

Элемент в `results`:

```json
{
  "id": 1,
  "title": "Монтаж печи",
  "main": true,
  "duration": 7,
  "date": "2026-03-07",
  "object_type": "Баня",
  "price": 150000,
  "video_link": "https://example.com/video",
  "type_work": "Монтаж",
  "product_id": 15,
  "product_name": "Aurora Pro 18 Duo",
  "images": [
    {
      "id": 1,
      "image": "/media/portfolio_image/example.webp",
      "order": 0
    }
  ],
  "created_at": "2026-03-07T12:44:10.123456+0000"
}
```

### `GET /api/v1/catalog/products/{product_id}/portfolio/`

Возвращает портфолио конкретного товара. Остальные query-параметры работают так же, как у общего списка.

## 8. Reviews API

### `GET /api/v1/catalog/reviews/`

Список всех отзывов, сортировка по убыванию `created_at`.

### `GET /api/v1/catalog/products/{product_id}/reviews/`

Список отзывов конкретного товара.

Элемент в `results`:

```json
{
  "id": 1,
  "name": "Отзыв",
  "client_name": "Иван",
  "installation_time": "2 дня",
  "location": "Екатеринбург",
  "date": "2026-03-07",
  "work_description": "Описание работ",
  "price": 150000,
  "video_url": "https://example.com/video",
  "preview_image": "/media/reviews/example.webp",
  "product_id": 15,
  "product_name": "Aurora Pro 18 Duo",
  "created_at": "2026-03-07T12:44:10.123456+0000"
}
```

## 9. Manufacturers API

### `GET /api/v1/catalog/manufacturers/`

Возвращает активных производителей (`is_active=true`) с пагинацией.

Query-параметры:

- `ordering=priority` — сортировка по `priority` по убыванию, затем `name`
- без `ordering` — кастомная сортировка: цифры, латиница, кириллица, прочее; внутри группы по `name`

Поля элемента:

- `id`
- `name`
- `slug`
- `logo`
- `priority`

### `GET /api/v1/catalog/manufacturers/{id}/`

Карточка активного производителя. Если производитель не найден или неактивен, ответ будет `404`.

Поля:

- `id`
- `name`
- `slug`
- `is_active`
- `logo`
- `priority`
- `seo_title`
- `seo_description`
- `seo_keywords`
- `description`
- `video`
- `images` — массив `{ id, image, ordering }`

## 10. Banners API

### `GET /api/v1/catalog/banners/`

Query-параметры:

- `section` — ID раздела
- `brand` — ID производителя

Логика:

- если передан `section`, вернутся баннеры выбранного раздела и глобальные баннеры без раздела;
- если передан `brand`, вернутся баннеры выбранного производителя и глобальные баннеры без производителя;
- если переданы оба параметра, применяются оба условия.

Поля элемента:

- `id`
- `title`
- `image`
- `link`

## 11. Send Email Request API

### `POST /api/v1/send-email-request/`

Тело запроса:

```json
{
  "phone": "+7 999 000-00-00",
  "link": "https://kamini-melnika.ru/catalog/products/15"
}
```

Правила:

- `phone` — строка от 5 до 20 символов после trim;
- `link` должен вести на `kamini-melnika.ru` или `www.kamini-melnika.ru`.

Успешный ответ:

```json
{
  "status": "ok"
}
```

## 12. Healthcheck

### `GET /api/v1/health/`

- `200`: `{ "status": "ok" }`
- `503`: `{ "status": "db_error" }`
