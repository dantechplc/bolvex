import qrcode
from django.core.files.base import ContentFile
from django.db import models
from io import BytesIO

# Create your models here.


class AdminWallet(models.Model):
    wallet_name = models.CharField(max_length=255)
    wallet_address = models.CharField(max_length=255)
    wallet_barcode = models.ImageField(upload_to="admin_wallet/")

    def generate_qr_code(self):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(self.wallet_address)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        image_binary = buffer.getvalue()
        buffer.close()

        file_name = f"{self.wallet_name}.png"
        self.wallet_barcode.save(file_name, ContentFile(image_binary), save=False)
    def __str__(self):
        return self.wallet_name

    def save(self, *args, **kwargs):
        self.generate_qr_code()
        super().save(*args, **kwargs)



