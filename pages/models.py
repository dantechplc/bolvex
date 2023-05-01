from django.db import models

# Create your models here.
class Contact(models.Model):
    name = models.CharField(max_length=150, null=False, blank=False)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()

    def __str__(self):
        return self.email


class CompanyProfile(models.Model):
    company_name = models.CharField(max_length=125)
    company_logo_dark = models.ImageField(upload_to='company', blank=True)
    company_logo_light = models.ImageField(upload_to='company', blank=True)
    company_favicon = models.ImageField(upload_to='company', null=True, blank=True)
    alt_text = models.CharField(max_length=50, blank=True, null=True)
    company_address = models.CharField(max_length=250)
    company_phone = models.CharField(max_length=125)
    company_support_email = models.EmailField(blank=True, null=True)
    forwarding_email = models.EmailField(null=True, blank=True)


    def __str__(self):
        return self.company_name

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)


