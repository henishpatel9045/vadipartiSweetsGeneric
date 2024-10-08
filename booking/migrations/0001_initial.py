# Generated by Django 5.0.7 on 2024-09-06 11:05

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('bill_number', models.IntegerField(db_index=True, unique=True)),
                ('customer_name', models.CharField(max_length=100)),
                ('customer_phone', models.CharField(blank=True, max_length=15, null=True)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('comment', models.TextField(blank=True, null=True)),
                ('total_order_price', models.FloatField(default=0.0)),
                ('received_amount', models.FloatField(default=0.0)),
                ('is_special_price', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order_quantity', models.IntegerField(default=0)),
                ('delivered_quantity', models.IntegerField(default=0)),
                ('comment', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
