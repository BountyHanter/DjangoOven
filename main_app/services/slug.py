from slugify import slugify


def build_unique_slug(instance, value, fallback):
    slug_field = instance._meta.get_field("slug")
    max_length = slug_field.max_length
    base_slug = slugify(value) or fallback
    base_slug = base_slug[:max_length]
    slug = base_slug
    counter = 1

    queryset = instance.__class__.objects.exclude(pk=instance.pk)

    while queryset.filter(slug=slug).exists():
        suffix = f"-{counter}"
        slug = f"{base_slug[: max_length - len(suffix)]}{suffix}"
        counter += 1

    return slug
