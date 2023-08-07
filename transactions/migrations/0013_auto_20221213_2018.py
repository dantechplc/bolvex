# Generated by Django 3.1.8 on 2022-12-13 19:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('boss', '0001_initial'),
        ('transactions', '0012_delete_payment_method'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='payment_method',
        ),
        migrations.AddField(
            model_name='transaction',
            name='payment_methods',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='boss.adminwallet'),
        ),
    ]
