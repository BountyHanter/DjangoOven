from django.db import models


class CatalogPortfolio(models.Model):

    CATALOG_CHOICES = (
        ("bath_stoves", "Портфолио банных печей"),
        ("fireplace_stoves", "Портфолио печей-каминов"),
        ("chimneys", "Портфолио дымохода"),
        ("fireplaces", "Портфолио каминов"),
    )

    title = models.CharField(
        max_length=255,
        verbose_name="Наименование проекта",
    )

    client_problem = models.CharField(
        max_length=255,
        verbose_name="Боль клиента",
    )

    catalog_type = models.CharField(
        max_length=50,
        choices=CATALOG_CHOICES,
        verbose_name="Раздел каталога",
    )

    project_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Стоимость проекта",
    )

    production_time = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Срок производства работ",
    )

    production_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Дата производства работ",
    )

    object_type = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Тип объекта",
    )

    work_types = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Виды работ",
    )

    video_url = models.URLField(
        blank=True,
        verbose_name="Ссылка на видео",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Портфолио каталога"
        verbose_name_plural = "Портфолио каталога"

    def __str__(self):
        return self.title


class CatalogPortfolioHistory(models.Model):
    portfolio = models.ForeignKey(
        CatalogPortfolio,
        on_delete=models.CASCADE,
        related_name="history_blocks",
    )

    text = models.TextField(
        verbose_name="История проекта",
    )

    ordering = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок",
    )

    class Meta:
        ordering = ["ordering"]
        verbose_name = "История проекта"
        verbose_name_plural = "История проекта"


class CatalogPortfolioImage(models.Model):
    portfolio = models.ForeignKey(
        CatalogPortfolio,
        on_delete=models.CASCADE,
        related_name="portfolio_images",
    )

    image = models.ImageField(
        upload_to="catalog_portfolio/",
        verbose_name="Изображение",
    )

    class Meta:
        verbose_name = "Изображение проекта"
        verbose_name_plural = "Изображения проекта"


class CatalogPortfolioProductImage(models.Model):
    portfolio = models.ForeignKey(
        CatalogPortfolio,
        on_delete=models.CASCADE,
        related_name="portfolio_product_image",
        verbose_name="Проект",
    )

    image = models.ImageField(
        upload_to="catalog_portfolio_product/",
        verbose_name="Изображение",
    )


    class Meta:
        verbose_name = "Товар участвовавший в проекте"
        verbose_name_plural = "Товары участвовавшие в проекте"

    def __str__(self):
        return f"{self.portfolio}"