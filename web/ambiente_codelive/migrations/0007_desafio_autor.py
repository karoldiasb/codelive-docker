# Generated by Django 2.0.8 on 2018-10-15 02:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ambiente_codelive', '0006_remove_desafio_autor'),
    ]

    operations = [
        migrations.AddField(
            model_name='desafio',
            name='autor',
            field=models.ForeignKey(default='0', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
