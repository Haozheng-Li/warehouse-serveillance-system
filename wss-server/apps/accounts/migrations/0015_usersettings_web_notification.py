# Generated by Django 4.1.7 on 2023-04-04 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_loginhistory_is_tablet'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersettings',
            name='web_notification',
            field=models.BooleanField(default=True),
        ),
    ]
