# Generated by Django 4.1.4 on 2023-02-02 22:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_control', '0002_apikey_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apikey',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
