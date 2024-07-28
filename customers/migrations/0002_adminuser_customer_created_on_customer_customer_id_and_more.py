# Generated by Django 4.2.7 on 2024-07-26 14:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='customer',
            name='customer_id',
            field=models.CharField(default='DEFAULT_ID', max_length=20, unique=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='updated_on',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
