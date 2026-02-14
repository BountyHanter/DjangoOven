from django.db import models


class Portfolio(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name="Название",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Комментарий",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Портфолио для главной"
        verbose_name_plural = "Портфолио для главной"

    def __str__(self):
        return self.title


class PortfolioImage(models.Model):
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name="images",
    )

    image = models.ImageField(
        upload_to="main_portfolio_image/",
        verbose_name="Изображение",
    )

    class Meta:
        verbose_name = "Изображение портфолио (глав)"
        verbose_name_plural = "Изображения портфолио (глав)"
