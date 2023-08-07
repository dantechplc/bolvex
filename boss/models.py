from django.db import models


# Create your models here.


class AdminWallet(models.Model):
    wallet_name = models.CharField(max_length=255)
    wallet_address = models.CharField(max_length=255)
    wallet_barcode = models.ImageField(upload_to="admin_wallet/")

    def __str__(self):
        return self.wallet_name



