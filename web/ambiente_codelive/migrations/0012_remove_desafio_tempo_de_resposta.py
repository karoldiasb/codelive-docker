# Generated by Django 2.1.2 on 2018-11-05 00:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ambiente_codelive', '0011_auto_20181104_2215'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='desafio',
            name='tempo_de_resposta',
        ),
    ]
