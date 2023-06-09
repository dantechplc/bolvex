# Generated by Django 3.1.8 on 2023-04-17 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=125)),
                ('company_logo_dark', models.ImageField(blank=True, upload_to='company')),
                ('company_logo_light', models.ImageField(blank=True, upload_to='company')),
                ('company_favicon', models.ImageField(blank=True, null=True, upload_to='company')),
                ('alt_text', models.CharField(blank=True, max_length=50, null=True)),
                ('company_address', models.CharField(max_length=250)),
                ('company_phone', models.CharField(max_length=125)),
                ('company_support_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('forwarding_email', models.EmailField(blank=True, max_length=254, null=True)),
            ],
        ),
    ]
