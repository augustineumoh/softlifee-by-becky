import random
import string
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def generate_referral_codes(apps, schema_editor):
    User = apps.get_model('users', 'User')
    used = set()
    for user in User.objects.all():
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if code not in used:
                used.add(code)
                break
        user.referral_code = code
        user.save(update_fields=['referral_code'])


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        # Step 1: add nullable so existing rows get NULL, not ''
        migrations.AddField(
            model_name='user',
            name='referral_code',
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
        # Step 2: populate unique codes for every existing user
        migrations.RunPython(generate_referral_codes, migrations.RunPython.noop),
        # Step 3: now safe to enforce unique + not null
        migrations.AlterField(
            model_name='user',
            name='referral_code',
            field=models.CharField(blank=True, max_length=12, unique=True),
        ),
        migrations.CreateModel(
            name='ReferralUse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('referred', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='referral_source', to=settings.AUTH_USER_MODEL)),
                ('referrer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='referrals_given', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
