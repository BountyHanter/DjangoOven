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
      "description_main": "Главный раздел каталога",
      "image": "/media/sections/catalog-root.webp",
      "browser_title": "Каталог печей",
      "description": "Полное описание каталога",
      "meta_description": "SEO описание каталога",
      "meta_keywords": "каталог, печи",
      "ordering": 1,
      "count": 5,
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
- `sections` содержит SEO/content-поля раздела, нужные для каталожных страниц.
- `count` и `products_count` сейчас дублируют одно значение: количество товаров в разделе с учетом дочерних разделов.
- `products_count` у раздела учитывает товары в самом разделе и во всех дочерних разделах.
- Разделы без товаров не скрываются, у них `products_count: 0`.
- `price.min/max` считаются по итоговой цене товара: `discount_price`, если она есть, иначе `price`.
- `manufacturers` и `attributes` могут отсутствовать, если для текущей выборки нет данных.
- Все счетчики и диапазоны пересчитываются с учетом переданного `filters`.
- Характеристики с галочкой "Не выводить в фильтр" не попадают в `attributes`, но остаются в карточке товара.
- Порядок `attributes` и `options` задается приоритетом в админке: положительные приоритеты идут первыми по возрастанию, `0` означает "без ручного приоритета" и идет после них. Сам `priority` в API не возвращается.

### Поля ответа фильтров

Раздел (`sections`):

| Поле | Название |
|---|---|
| `id` | ID раздела |
| `name` | Название |
| `slug` | ЧПУ / slug |
| `description_main` | Описание для главной |
| `image` | Изображение раздела |
| `browser_title` | Заголовок вкладки браузера |
| `description` | Описание |
| `meta_description` | Описание страницы для поиска |
| `meta_keywords` | Ключевые слова для поиска |
| `ordering` | Порядок |
| `count` | Количество товаров |
| `products_count` | Количество товаров |
| `children` | Дочерние разделы |

Производитель (`manufacturers`):

| Поле | Название |
|---|---|
| `id` | ID производителя |
| `name` | Производитель |
| `slug` | ЧПУ / slug |
| `logo` | Логотип |
| `products_count` | Количество товаров |

Характеристика фильтра (`attributes`):

| Поле | Название |
|---|---|
| `id` | ID характеристики |
| `name` | Название характеристики |
| `slug` | Slug |
| `type` | Тип характеристики |
| `unit` | Единица измерения |
| `allow_multiple` | Можно несколько значений |
| `products_count` | Количество товаров |
| `options` | Варианты значения для `choice` |
| `min` | Минимальное значение для `number` |
| `max` | Максимальное значение для `number` |
| `values` | Значения для `boolean` |

Вариант характеристики (`options`):

| Поле | Название |
|---|---|
| `id` | ID варианта |
| `value` | Значение |
| `slug` | Slug |
| `products_count` | Количество товаров |

Значение boolean-фильтра (`values`):

| Поле | Название |
|---|---|
| `value` | Значение |
| `products_count` | Количество товаров |

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
    { "value": true, "products_count": 2 }
  ]
}
```

Для boolean-фильтров в `/catalog/filters/` выводится только `true` ("Да"). `false` ("Нет") в фильтрах не показывается, чтобы не смешивать явное "Нет" с незаполненными характеристиками.

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

Поля элемента товара:

| Поле | Название |
|---|---|
| `id` | ID товара |
| `name` | Наименование |
| `sections` | Разделы |
| `manufacturer` | Производитель |
| `is_new` | Новинка |
| `is_bestseller` | Хит продаж |
| `priority` | Приоритет |
| `has_video` | Есть видео |
| `price` | Обычная цена |
| `discount_price` | Цена со скидкой |
| `power` | Мощность |
| `images` | Изображения товара |

Поля изображения:

| Поле | Название |
|---|---|
| `id` | ID изображения |
| `image` | Изображение |
| `ordering` | Порядок |
| `is_main` | Главное изображение |

Поля раздела в `sections`:

| Поле | Название |
|---|---|
| `id` | ID раздела |
| `name` | Название |
| `slug` | ЧПУ / slug |

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
  "manufacturer": {
    "id": 1,
    "name": "Harvia Legend"
  },
  "price": 189900,
  "discount_price": 174500,
  "description": "Подробное описание товара",
  "schema": "/media/products/schema/legend-240-schema.pdf",
  "free_delivery": true,
  "in_stock": true,
  "is_active": true,
  "is_new": true,
  "is_bestseller": true,
  "priority": 7,
  "sku": "HL-240-DUO, HL-240-DUO-GF",
  "series": "Legend GreenFlame",
  "seo_title": "Harvia Legend GreenFlame 240 Duo купить",
  "seo_description": "Карточка товара Harvia Legend GreenFlame 240 Duo",
  "seo_keywords": "harvia legend, greenflame, банная печь",
  "created_at": "2026-03-07T12:44:10.123456+0000",
  "updated_at": "2026-03-08T12:44:10.123456+0000",
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

Поля карточки товара:

| Поле | Название |
|---|---|
| `id` | ID товара |
| `name` | Наименование |
| `slug` | Slug |
| `manufacturer` | Производитель |
| `price` | Обычная цена |
| `discount_price` | Цена со скидкой |
| `description` | Описание |
| `schema` | Схема (формат pdf) |
| `free_delivery` | Бесплатная доставка |
| `in_stock` | В наличии на складе |
| `is_active` | Активен в каталоге |
| `is_new` | Новинка |
| `is_bestseller` | Хит продаж |
| `priority` | Приоритет |
| `sku` | Артикул(ы) |
| `series` | Серия товара |
| `seo_title` | Название страницы товара |
| `seo_description` | Описание страницы товара |
| `seo_keywords` | Ключевые слова товара |
| `created_at` | Создан |
| `updated_at` | Обновлён |
| `sections` | Разделы |
| `images` | Изображения товара |
| `videos` | Видео товара |
| `documents` | Документы товара |
| `attributes` | Характеристики |

`manufacturer` — объект `{ id, name }` или `null`.

Поля производителя в карточке товара:

| Поле | Название |
|---|---|
| `id` | ID производителя |
| `name` | Производитель |

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
  "preview": "/media/products/video_previews/legend-installation.webp",
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

Поля изображения товара:

| Поле | Название |
|---|---|
| `id` | ID изображения |
| `image` | Изображение |
| `ordering` | Порядок |
| `is_main` | Главное изображение |

Поля видео товара:

| Поле | Название |
|---|---|
| `id` | ID видео |
| `url` | Ссылка на видео |
| `preview` | Превью видео |
| `ordering` | Порядок |

`preview` — URL загруженного файла превью из media. В админке превью загружается файлом, а не вводится внешней ссылкой.

Поля документа товара:

| Поле | Название |
|---|---|
| `id` | ID документа |
| `title` | Название документа |
| `file` | Файл |
| `ordering` | Порядок |

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

Поля характеристики товара:

| Поле | Название |
|---|---|
| `id` | ID характеристики |
| `name` | Название характеристики |
| `slug` | Slug |
| `type` | Тип характеристики |
| `unit` | Единица измерения |
| `value` | Значение характеристики |

Для `choice` значение — объект `{ id, name, slug }` или массив таких объектов, если у характеристики включено несколько значений.

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

Поля элемента портфолио:

| Поле | Название |
|---|---|
| `id` | ID портфолио |
| `title` | Название |
| `main` | На главную |
| `duration` | Срок работ |
| `date` | Дата работ |
| `object_type` | Тип объекта |
| `price` | Стоимость |
| `video_link` | Ссылка на видео |
| `type_work` | Тип работ |
| `product_id` | ID товара |
| `product_name` | Наименование товара |
| `images` | Фото портфолио |
| `created_at` | Создан |

Поля изображения портфолио:

| Поле | Название |
|---|---|
| `id` | ID фото |
| `image` | Фото |
| `order` | Порядок |

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

Поля отзыва:

| Поле | Название |
|---|---|
| `id` | ID отзыва |
| `name` | Название |
| `client_name` | Клиент |
| `installation_time` | Время затраченное на монтаж |
| `location` | Локация |
| `date` | Дата монтажа |
| `work_description` | Что сделано |
| `price` | Стоимость |
| `video_url` | Ссылка на видео |
| `preview_image` | Превью видео |
| `product_id` | ID товара |
| `product_name` | Наименование товара |
| `created_at` | Создан |

## 9. Manufacturers API

### `GET /api/v1/catalog/manufacturers/`

Возвращает активных производителей (`is_active=true`) с пагинацией.

Query-параметры:

- `ordering=priority` — сортировка по `priority` по убыванию, затем `name`
- без `ordering` — кастомная сортировка: цифры, латиница, кириллица, прочее; внутри группы по `name`

Поля элемента:

| Поле | Название |
|---|---|
| `id` | ID производителя |
| `name` | Производитель |
| `slug` | ЧПУ / slug |
| `logo` | Логотип |
| `priority` | Приоритет |
| `count` | Количество товаров |

### `GET /api/v1/catalog/manufacturers/{id}/`

Карточка активного производителя. Если производитель не найден или неактивен, ответ будет `404`.

Поля:

| Поле | Название |
|---|---|
| `id` | ID производителя |
| `name` | Производитель |
| `slug` | ЧПУ / slug |
| `is_active` | Активен |
| `logo` | Логотип |
| `priority` | Приоритет |
| `seo_title` | Название страницы |
| `seo_description` | Описание страницы |
| `seo_keywords` | Ключевые слова |
| `description` | Полное описание |
| `video` | Видео |
| `images` | Фото производителя |

`images` — массив объектов `{ id, image, ordering }`.

Поля фото производителя:

| Поле | Название |
|---|---|
| `id` | ID фото |
| `image` | Фото |
| `ordering` | Порядок |

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

| Поле | Название |
|---|---|
| `id` | ID баннера |
| `title` | Название |
| `image` | Картинка |
| `link` | Ссылка |

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

Поля запроса:

| Поле | Название |
|---|---|
| `phone` | Телефон |
| `link` | Ссылка |

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
