import datetime
from decimal import Decimal
import requests
from django_countries.fields import CountryField
import djmoney
from imagekit.models import ImageSpecField
from pilkit.processors import ResizeToFill
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
)
from django.db import models
# from djmoney.models.fields import MoneyField
from djmoney.models.fields import MoneyField

from .constants import *
from .managers import UserManager
from .utils import generate_ref_code

x = datetime.datetime.now()
status = (
    ('pending', 'pending'),
    ('successful', 'successful'),
    ('failed', 'failed')
)

verification_status = (
    ('Unverified', 'Unverified'),
    ('Under Review', 'Under Review'),
    ('Verified', 'Verified')
)

investment_status = (
    ('Active', 'Active'),
    ('Expired', 'Expired'),
    ('On Hold', 'On Hold'),
)

payout_frequency = (
    ('Weekly', 'Weekly'),
    ('Twice a month (1st and 15th)', 'Twice a month (1st and 15th)'),
    ('Monthly (1st business day)', 'Monthly(1st business day)'),
    ('At the end of investment period', 'At the end of investment period'),
)

payment_date = (
    ('Not Due for Payment', 'Not Due for Payment'),
    (' Due for Payment', ' Due for Payment'),

)

insurance = (
    ('paid', 'paid'),
    ('debt', 'debt'),

)

referral_stage = (
    ('stage1', 'stage1'),
    ('stage2', 'stage2'),
    ('stage3', 'stage3'),
    ('stage4', 'stage4'),

)


class User(AbstractUser):
    username = models.CharField(_('username'), unique=False, max_length=100)
    email = models.EmailField(unique=True, null=False, blank=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    @property
    def balance(self):
        if hasattr(self, 'client_account'):
            return self.client_account.book_balance
        return 0


class Client(models.Model):
    user = models.OneToOneField(
        User,
        related_name='account',
        on_delete=models.CASCADE,
    )

    profile_pic = models.ImageField(upload_to='client/profile_pic', default='client/profile_pic/avatar.jpg', null=True,
                                    blank=True)
    profile_pic_thumbnail = ImageSpecField(source='profile_pic',
                                           processors=[ResizeToFill(100, 100)],
                                           format="JPEG",
                                           options={'quality': 60})
    username = models.CharField(max_length=200, blank=True, null=True, )
    first_name = models.CharField(max_length=200, blank=True, null=True, )
    last_name = models.CharField(max_length=200, blank=True, null=True, )
    gender = models.CharField(max_length=200, blank=True, null=True, choices=GENDER_CHOICE)
    dob = models.DateTimeField(blank=True, null=True)
    address = models.CharField(max_length=1000, blank=True, null=True, )
    city = models.CharField(max_length=200, blank=True, null=True, )
    state = models.CharField(max_length=200, blank=True, null=True, )
    country = CountryField(blank_label='(select country)', blank=True, null=True)
    zip = models.PositiveIntegerField(blank=True, null=True)
    Verification_status = models.CharField(max_length=200, choices=verification_status, blank=True,
                                           default='Unverified')
    date_joined = models.DateTimeField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True)
    referral_code = models.CharField(blank=True, max_length=6)
    recommended_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='ref_by')
    account_password = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        if self.referral_code == "":
            code = generate_ref_code()
            self.referral_code = code

        super().save(*args, **kwargs)


class Investment(models.Model):
    name = models.CharField(max_length=200)
    min_amount = MoneyField(max_digits=19, decimal_places=2, default_currency='USD', default=0, blank=True, null=True)
    max_amount = MoneyField(max_digits=19, decimal_places=2, default_currency='USD', default=0, blank=True, null=True)
    daily_rate = models.FloatField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    period_in_days = models.IntegerField(blank=True, null=True)
    referral_commission = models.FloatField(blank=True, null=True)
    percentage = models.IntegerField(blank=True, null=True, default=100)

    def __str__(self):
        return str(self.name)


class Investment_profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inv')
    trx_id = models.CharField(max_length=300, blank=True, null=True, )
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE, null=True, blank=True)
    amount_invested = MoneyField(max_digits=19, decimal_places=2, default_currency='USD', default=0, blank=True,
                                 null=True)
    amount_earned = MoneyField(max_digits=19, decimal_places=2, default_currency='USD', default=0, blank=True,
                               null=True)
    expected_roi = MoneyField(max_digits=19, decimal_places=2, default_currency='USD', default=0, blank=True, null=True)
    earning = MoneyField(max_digits=19, decimal_places=2, default_currency='USD', default=0, blank=True, null=True)
    status = models.CharField(max_length=300, blank=True, null=True, choices=investment_status)
    payout_frequency = models.CharField(max_length=300, choices=payout_frequency, blank=True, null=True)
    date_started = models.DateTimeField(blank=True, null=True)
    expiry_date = models.DateTimeField(blank=True, null=True)
    next_payout = models.DateTimeField(blank=True, null=True)
    expired = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)

    # def upgrade_status(self, plan):
    #     active_investment = Investment_profile.objects.filter(user=self.user, status='Active')
    #     investment = Investment.object.get(name=plan)


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_account')
    trx_id = models.CharField(max_length=300, blank=True, null=True, )
    main_balance = MoneyField(max_digits=19, decimal_places=2, default_currency='USD', default=0, blank=True, null=True)
    book_balance = MoneyField(max_digits=19, decimal_places=2, default_currency='USD', default=0, blank=True, null=True)
    balance_status = models.CharField(max_length=200, choices=status, null=True, blank=True, default='pending')
    total_amount_investment = MoneyField(max_digits=19, decimal_places=2, default_currency='USD', default=0, blank=True,
                                         null=True)
    total_amount_deposited = MoneyField(max_digits=19, decimal_places=2, default_currency='USD', default=0, blank=True,
                                        null=True)
    bonus = MoneyField(max_digits=19, decimal_places=2, default_currency='USD', default=0, blank=True, null=True)
    transaction_pin = models.CharField(max_length=4, null=True, blank=True)
    total_expected_roi = MoneyField(max_digits=19, decimal_places=2, default_currency='USD', default=0, blank=True, null=True)
    total_roi_received = MoneyField(max_digits=19, decimal_places=2, default_currency='USD', default=0, blank=True,
                                    null=True)
    total_amount_withdrawn = MoneyField(max_digits=19, decimal_places=2, default_currency='USD', default=0, blank=True,
                                        null=True)
    roi_balance = MoneyField(max_digits=19, decimal_places=2, default_currency='USD', default=0, blank=True,
                                    null=True)
    last_deposit_date = models.DateTimeField(blank=True, null=True)
    last_withdrawal_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        if self.balance_status == 'successful':
            c = self.main_balance + self.book_balance
            self.main_balance = c

        super().save(*args, **kwargs)


class Verification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=200, null=True)
    last_name = models.CharField(max_length=200, null=True)
    dob = models.DateField(null=True)
    gender = models.CharField(max_length=100, choices=GENDER_CHOICE, null=True)

    address = models.CharField(max_length=500, null=True)
    Document_type = models.CharField(max_length=50, choices=ID, null=True)

    id_view = models.FileField()


    def __str__(self):
        return str(self.user)


class Investment_upgrade(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inv_upgrade')
    trx_id = models.CharField(max_length=300, blank=True, null=True, )
    previous_plan = models.ForeignKey(Investment, on_delete=models.CASCADE, null=True, blank=True,
                                      related_name='pre_plan')
    upgraded_plan = models.ForeignKey(Investment, on_delete=models.CASCADE, null=True, blank=True,
                                      related_name='up_plan')
    upgrade_method = models.CharField(max_length=200, blank=True, null=True, choices=upgrade_method)
    previous_amount = MoneyField(max_digits=19, decimal_places=2, default_currency='USD', default=0, blank=True,
                                 null=True)
    upgrade_amount = MoneyField(max_digits=19, decimal_places=2, default_currency='USD', default=0, blank=True,
                                null=True)
    date = models.DateField(blank=True, null=True)

    def __str__(self):
        return str(self.user)


class WithdrawalWallet(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "Withdrawal Wallet"
