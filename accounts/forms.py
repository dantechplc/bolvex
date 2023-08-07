from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms import ModelForm
from django_countries.fields import CountryField
from .models import *
from .constants import GENDER_CHOICE


#
# class ClientForm(forms.ModelForm):
#     class Meta:
#         model = Client
#         fields = '__all__'
#         exclude = ['user', 'gender', 'referral_code']
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)


class Investment_profile_Form(forms.ModelForm):
    class Meta:
        model = Investment_profile
        fields = '__all__'
        exclude = ['user', 'date_started', 'expiry_date', 'next_payout', ' payout_frequency', 'investment', 'trx_id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = '__all__'
        exclude = ['user', 'book_balance', 'balance_status', 'transaction_pin', 'total_expected_roi',
                   'last_deposit_date',
                   'last_withdrawal_date', 'total_amount_deposited', 'insurance_dept', 'referral_dept', 'trx_id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UserRegistrationForm(UserCreationForm):
    phone_number = forms.CharField()

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')

        if Client.objects.filter(phone_number=phone_number).exists() == True:
            raise forms.ValidationError(
                'Phone Number already exist'
            )

        return phone_number


#
class VerificationForm(forms.ModelForm):
    class Meta:
        model = Verification
        fields = ['first_name', 'last_name', 'dob', 'gender', 'address', 'id_view', 'Document_type']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'form-control '

                )
            })


class ClientForm(ModelForm):

    class Meta:
        model = Client
        fields = ['username', 'first_name', 'last_name', 'profile_pic', ]
        exclude = ['user']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'form-control '

                )
            })