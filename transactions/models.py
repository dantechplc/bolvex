import datetime

from dateutil.relativedelta import relativedelta

import djmoney
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.functional import cached_property
from djmoney.models.fields import MoneyField

from boss.models import AdminWallet
from .constants import TRANSACTION_TYPE_CHOICES
from accounts.models import *
from .utils import generate_ref_code

status = (
    ('pending', 'pending'),
    ('Awaiting Approval', 'Awaiting Approval'),
    ('Successful', 'Successful'),
    ('Received', 'Received'),
    ('failed', 'failed'),
    ('Active', 'Active'),
    ('Expired', 'Expired')
)





x = datetime.datetime.now()




class Transaction(models.Model):
    account = models.ForeignKey(
        Account,
        related_name='transactions',
        on_delete=models.CASCADE,
    )
    amount = MoneyField(max_digits=19, decimal_places=2, default_currency='USD')
    hash_id = models.CharField(null=True, blank=True, max_length=200)
    trx_id = models.CharField(max_length=100, blank=True, unique=True)
    payment_methods = models.ForeignKey(AdminWallet, blank=True, null=True, on_delete=models.CASCADE)
    wallet_id = models.CharField(null=True, blank=True, max_length=200)
    investment_name = models.ForeignKey(Investment, blank=True, null=True, on_delete=models.CASCADE)
    status = models.CharField(max_length=200, choices=status, blank=True, default='pending')
    balance_after_transaction = MoneyField(max_digits=19, decimal_places=2, default_currency='USD', blank=True,
                                           null=True)
    transaction_type = models.PositiveSmallIntegerField(
        choices=TRANSACTION_TYPE_CHOICES,
        blank=True,
        null=True

    )
    date = models.DateField(blank=True, null=True, auto_now_add=True)
    expired = models.BooleanField(default=False)
    transfer_type = models.CharField(max_length=100, blank=True, null='True')
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return str(self.account)


    def deposit_check_email(account, amount):
        mail_subject = "Deposit on Bolvex Capital"
        message = 'Deposit from ' + str(account) + '\n Amount ' + str(
            amount) + ' proceed to your admin dashboard to confirm or decline.'
        to_email = 'bolvexcapital@gmail.com'
        email = EmailMultiAlternatives(
            mail_subject, message, to=[to_email]
        )
        email.attach_alternative(message, 'text/html')
        email.content_subtype = 'html'
        email.mixed_subtype = 'related'

        email.send()

    def withdrawal_check_email(account, amount):
        mail_subject = "Withdrawal on Bolvex Capital"
        message = 'Withdrawal from ' + str(account) + '\n Amount ' + str(
            amount) + ' proceed to your admin dashboard to confirm or decline.'
        to_email = 'bolvexcapital@gmail.com'
        email = EmailMultiAlternatives(
            mail_subject, message, to=[to_email]
        )
        email.attach_alternative(message, 'text/html')
        email.content_subtype = 'html'
        email.mixed_subtype = 'related'
        email.send()

    def transfer_check_email(account, amount):
        mail_subject = 'Bolvex Capital Transfer Service'
        now = x.strftime("%c")
        to_email = account
        message1 = render_to_string('transactions/balance_email.html', {
            'username': account.username,
            'amount': amount,
            'date': now,
            'balance': account.client_account.main_balance
        })
        email = EmailMultiAlternatives(
            mail_subject, message1, to=[to_email]
        )
        email.attach_alternative(message1, 'text/html')
        email.content_subtype = 'html'
        email.mixed_subtype = 'related'
        email.send()

    def referral_commission_email(account,  amount):
        mail_subject = 'Referral Commission'
        message = render_to_string('transactions/ref_com_email.html', {
            'amount': amount,
            'date': timezone.now(),
            'balance': account.client_account.bonus,
        })
        to_email = str(account)
        email = EmailMultiAlternatives(
            mail_subject, message, to=[to_email]
        )
        email.attach_alternative(message, 'text/html')
        email.content_subtype = 'html'
        email.mixed_subtype = 'related'
        email.send()

    def referral_commission(rate, amount):
        commission = int(rate)/100 * amount
        return commission

    def ROI(amount, rate, days):
        interest = (amount * rate / 100) * days + amount
        return interest

    def expiry_date(amount, rate, days):
        expected_days = ((amount * rate / 100) * days + amount) / (amount * rate / 100)
        return round(expected_days)

    def earning(amount, rate):
        earning = amount * rate / 100
        return earning

    def save(self, *args, **kwargs):
        if self.transaction_type == 3:
            self.status = 'Active'
        if self.trx_id == "":
            code = generate_ref_code()
            self.trx_id = str('Trx') + code
        if self.transaction_type == 5:
            self.status = 'Successful'

        if self.transaction_type == 4:
            self.status = 'Successful'
        if self.transaction_type == 8:
            self.status = 'Successful'

        if self.transfer_type == "Received":
            self.status = "Received"


        super().save(*args, **kwargs)

        class Meta:
            ordering = ['timestamp']



