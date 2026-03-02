from django.db import models
from django.utils.text import slugify


class Section(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name="Название",
    )

    slug = models.SlugField(
        max_length=255,
        verbose_name="ЧПУ(Slug)",
        help_text="Используется в URL",
    )

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
        verbose_name="Родительский раздел",
    )

    description = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Описание раздела",
    )

    image = models.ImageField(
        upload_to="sections/images/",
        null=True,
        blank=True,
        verbose_name="Изображение раздела",
    )

    menu_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Название для меню",
    )

    browser_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Заголовок вкладки браузера",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )

    meta_description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Описание страницы для поиска",
    )

    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Ключевые слова для поиска",
    )

    ordering = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок",
        help_text="Сортировка внутри одного родителя",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Раздел активен",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создан",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Обновлён",
    )

    class Meta:
        verbose_name = "Раздел"
        verbose_name_plural = "Разделы"
        ordering = ["parent__id", "ordering", "name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["parent"]),
        ]

    def __str__(self):
        return f"{self.get_indent()}{self.name}"

    def get_depth(self) -> int:
        depth = 0
        parent = self.parent
        while parent:
            depth += 1
            parent = parent.parent
        return depth

    def get_indent(self) -> str:
        return "-- " * self.get_depth()

    def get_path(self):
        path = []
        node = self

        while node:
            path.append(node)
            node = node.parent

        return list(reversed(path))

    def get_descendants(self, include_self=True):
        nodes = [self] if include_self else []

        for child in self.children.all():
            nodes.extend(child.get_descendants(include_self=True))

        return nodes

    def get_descendants_ids(self, include_self=True):
        return [s.id for s in self.get_descendants(include_self)]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
