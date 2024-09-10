# Generated by Django 5.0.7 on 2024-09-09 02:21

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0003_alter_userdeposits_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='billbook',
            options={'ordering': ['book_number']},
        ),
        migrations.CreateModel(
            name='DailyReadyItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ready_items', to='management.item')),
            ],
        ),
    ]