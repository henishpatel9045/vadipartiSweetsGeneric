# Generated by Django 5.0.7 on 2024-09-08 12:25

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0002_userdeposits'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdeposits',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
