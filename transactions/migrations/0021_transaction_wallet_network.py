# Generated by Django 3.1.8 on 2023-09-16 04:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0020_auto_20230107_1530'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='wallet_network',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]