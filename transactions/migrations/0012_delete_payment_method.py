# Generated by Django 3.1.8 on 2022-12-13 19:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0011_payment_method'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Payment_Method',
        ),
    ]
