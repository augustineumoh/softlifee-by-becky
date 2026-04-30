from django.db import migrations


def sync_in_stock(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    Product.objects.filter(stock_count=0, in_stock=True).update(in_stock=False)
    Product.objects.filter(stock_count__gt=0, in_stock=False).update(in_stock=True)


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_fix_null_stock_count'),
    ]

    operations = [
        migrations.RunPython(sync_in_stock, migrations.RunPython.noop),
    ]
