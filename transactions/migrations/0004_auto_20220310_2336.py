# Generated by Django 3.1.8 on 2022-03-10 23:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0003_transaction_trx_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
