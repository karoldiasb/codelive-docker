# Generated by Django 2.0.8 on 2018-10-15 01:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ambiente_codelive', '0005_auto_20181003_1122'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='desafio',
            name='autor',
        ),
    ]
