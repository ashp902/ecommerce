# Generated by Django 4.1.7 on 2023-03-17 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_rename_user_id_address_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='address_name',
            field=models.CharField(default='Home', max_length=255),
            preserve_default=False,
        ),
    ]
