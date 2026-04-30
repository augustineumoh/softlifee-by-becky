from django.db import migrations


def fix_null_stock(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    Product.objects.filter(stock_count__isnull=True).update(stock_count=0)


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_stockhistory'),
    ]

    operations = [
        migrations.RunPython(fix_null_stock, migrations.RunPython.noop),
    ]
