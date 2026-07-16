from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main_app", "0061_productattributeoption_description_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="productattribute",
            name="is_expanded",
            field=models.BooleanField(default=False, verbose_name="Развёрнутый"),
        ),
    ]
