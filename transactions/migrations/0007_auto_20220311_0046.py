# Generated by Django 3.1.8 on 2022-03-11 00:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0006_auto_20220311_0043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='trx_id',
            field=models.CharField(blank=True, max_length=100, unique=True),
        ),
    ]
