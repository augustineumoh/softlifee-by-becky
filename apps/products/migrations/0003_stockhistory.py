import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_product_sale_end_product_sale_price_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StockHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(
                    choices=[
                        ('added',      'Stock Added'),
                        ('removed',    'Stock Removed'),
                        ('adjustment', 'Manual Adjustment'),
                        ('sale',       'Sale Deduction'),
                        ('return',     'Return / Refund'),
                    ],
                    max_length=20,
                )),
                ('quantity_change', models.IntegerField()),
                ('stock_before',    models.PositiveIntegerField()),
                ('stock_after',     models.PositiveIntegerField()),
                ('note',            models.TextField(blank=True)),
                ('created_at',      models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='stock_history',
                    to='products.product',
                )),
                ('created_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name':          'Stock History',
                'verbose_name_plural':   'Stock History',
                'ordering':              ['-created_at'],
            },
        ),
    ]
