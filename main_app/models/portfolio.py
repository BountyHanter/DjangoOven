from django.db import models

class Portfolio(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name="Название",
    )

    main = models.BooleanField(
        default=False,
        verbose_name="На главную",
        help_text="Отметьте, если это портфолио должно быть на главной странице",
    )

    duration = models.PositiveIntegerField(
        default=0,
        verbose_name="Срок работ",
        help_text="Указывайте количество в днях"
    )

    date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Дата работ"
    )

    object_type = models.CharField(
        max_length=255,
        verbose_name="Тип объекта",
        null=True,
        blank=True,
    )

    price = models.PositiveIntegerField(
        default=0,
        verbose_name="Стоимость"
    )

    video_link = models.TextField(
        null=True,
        blank=True,
        verbose_name="Ссылка на видео"
    )

    picture = models.ImageField(
        upload_to="portfolio_image/",
        verbose_name="Фото"
    )

    type_work = models.TextField(
        blank=True,
        null=True,
        verbose_name="Тип работ",
    )

    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="portfolio",
        verbose_name="Товар",
        help_text="Выберите товар к которому относится данное портфолио",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Портфолио"
        verbose_name_plural = "Портфолио"

    def __str__(self):
        return self.title
