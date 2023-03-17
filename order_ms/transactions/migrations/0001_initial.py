# Generated by Django 4.1.7 on 2023-03-10 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('transaction_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('sender', models.CharField(max_length=255)),
                ('receiver', models.CharField(max_length=255)),
                ('payment_type', models.CharField(max_length=255)),
                ('payment_status', models.CharField(max_length=255)),
                ('payment_time', models.DateTimeField()),
            ],
        ),
    ]
