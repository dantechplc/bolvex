# Generated by Django 3.1.8 on 2022-12-12 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdminWallet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wallet_name', models.CharField(max_length=255)),
                ('wallet_address', models.CharField(max_length=255)),
                ('wallet_barcode', models.ImageField(upload_to='admin_wallet/')),
            ],
        ),
    ]
