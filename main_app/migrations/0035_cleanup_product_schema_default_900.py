from django.db import migrations


def set_schema_900_to_null(apps, schema_editor):
    Product = apps.get_model("main_app", "Product")
    Product.objects.filter(schema="900").update(schema=None)


def noop_reverse(apps, schema_editor):
    # Irreversible cleanup: keep NULL values on rollback.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("main_app", "0034_alter_product_schema"),
    ]

    operations = [
        migrations.RunPython(set_schema_900_to_null, noop_reverse),
    ]
