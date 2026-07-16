from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main_app", "0062_productattribute_is_expanded"),
    ]

    operations = [
        migrations.AddField(
            model_name="productattribute",
            name="do_not_use_for_direct_url",
            field=models.BooleanField(
                default=False,
                verbose_name="Не использовать для прямой ссылки",
            ),
        ),
    ]
