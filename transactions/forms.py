import datetime

import djmoney
from django import forms
from django.conf import settings

from accounts.models import User, Client
from boss.models import AdminWallet
from .models import *


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'amount',
            # 'transaction_type',

        ]

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)
        #
        # self.fields['transaction_type'].disabled = True
        # self.fields['transaction_type'].widget = forms.HiddenInput()

    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.main_balance
        return super().save()


class DepositForm(TransactionForm):
    def __init__(self, *args, **kwargs):
        # self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)

        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()

    class Meta:
        model = Transaction
        fields = [
            'amount',
            'hash_id',
            'transaction_type',
            'payment_methods'

        ]

    def clean_amount(self):
        min_deposit_amount = djmoney.money.Money(100, 'USD')
        amount = self.cleaned_data.get('amount')

        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f'You need to deposit at least {min_deposit_amount} '
            )

        return amount


class WithdrawForm(TransactionForm):
    admin_wallet = AdminWallet.objects.all()
    payment_methods = forms.ModelChoiceField(queryset=admin_wallet, required=True, empty_label='Select payment method')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_methods'].widget.attrs.update(
            {'class': 'col-lg-6 selectpicker form-control', })

        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()

    class Meta:
        model = Transaction
        fields = [
            'amount',
            'wallet_id',
            'transaction_type',
            'payment_methods',

        ]

    def clean_amount(self):
        account = self.account
        min_withdraw_amount = djmoney.money.Money(5, 'USD')
        charge = djmoney.money.Money(5, 'USD')
        max_withdraw_amount = (djmoney.money.Money(1000000000, 'USD')

                               )
        balance = account.main_balance

        amount = self.cleaned_data.get('amount')

        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at least {min_withdraw_amount} '
            )

        if amount > max_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at most {max_withdraw_amount} '
            )

        if amount > balance:
            raise forms.ValidationError(
                f'You have {balance}  in your account. '
                'You can not withdraw more than your account balance'
            )
        if account.user.account.Verification_status == 'Unverified':
            raise forms.ValidationError(
                f'Please Verify your Account !'
            )
        if account.user.account.Verification_status == 'Under Review':
            raise forms.ValidationError(
                f'Your Account is Under Review !')

        return amount


class Crypto_DepositForm(TransactionForm):
    def __init__(self, *args, **kwargs):
        # self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)

        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()

    # self.fields['amount_currency'].widget = forms.HiddenInput()

    class Meta:
        model = Transaction
        fields = [
            'amount',
            'hash_id',
            'payment_methods',
            'transaction_type',

        ]

    def clean_amount(self):
        min_deposit_amount = djmoney.money.Money(10, 'USD')
        amount = self.cleaned_data.get('amount')

        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f'You need to deposit at least {min_deposit_amount} '
            )

        return amount


class ConvertroiForm(TransactionForm):
    def __init__(self, *args, **kwargs):
        # self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)

        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()

    class Meta:
        model = Transaction
        fields = [
            'amount',
            'transaction_type'

        ]

    def clean_amount(self):
        account = self.account
        min_amount = djmoney.money.Money(10, 'USD')
        max_amount = (djmoney.money.Money(10000000, 'USD')

                               )
        balance = account.roi_balance

        amount = self.cleaned_data.get('amount')

        if amount < min_amount:
            raise forms.ValidationError(
                f'You can convert at least {min_amount} '
            )

        if amount > max_amount:
            raise forms.ValidationError(
                f'You can convert at most {max_amount} '
            )

        if amount > balance:
            raise forms.ValidationError(
                f'You have {balance}  in your ROI account. '
                'You can not convert more than your ROI balance'
            )
        if account.user.account.Verification_status == 'Unverified':
            raise forms.ValidationError(
                f'Please Verify your Account !'
            )
        if account.user.account.Verification_status == 'Under Review':
            raise forms.ValidationError(
                f'Your Account is Under Review !')
        return amount



class TransferForm(TransactionForm):
    client = forms.EmailField(required=True)

    # client1 = forms.ModelChoiceField(queryset=User.objects.get_or_create(email=client))

    def __init__(self, *args, **kwargs):
        # self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)

        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()
        # self.fields['transfer_fund'] = User.objects.get_or_create(email='dan@gmail.com')

    class Meta:
        model = Transaction
        fields = [
            'amount',
            'client',

            'transaction_type'

        ]

    def clean_amount(self):
        account = self.account
        min_withdraw_amount = djmoney.money.Money(100, 'USD')
        max_withdraw_amount = (djmoney.money.Money(1000000000, 'USD')

                               )
        balance = account.main_balance

        amount = self.cleaned_data.get('amount')

        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f'You can transfer at least {min_withdraw_amount} '
            )

        if amount > max_withdraw_amount:
            raise forms.ValidationError(
                f'You can transfer at most {max_withdraw_amount} '
            )

        if amount > balance:
            raise forms.ValidationError(
                f'You have {balance}  in your account. '
                'You can not transfer more than your account balance'
            )
        if account.user.account.Verification_status == 'Unverified':
            raise forms.ValidationError(
                f'Please Verify your Account !'
            )
        if account.user.account.Verification_status == 'Under Review':
            raise forms.ValidationError(
                f'Your Account is Under Review !')

        return amount

    def clean_client(self):
        account = self.account
        min_withdraw_amount = djmoney.money.Money(10, 'USD')
        max_withdraw_amount = (djmoney.money.Money(1000000000, 'USD')

                               )
        balance = account.main_balance

        amount = self.cleaned_data.get('amount')
        client = self.cleaned_data.get('client')

        if User.objects.filter(email=client).exists() == False:
            raise forms.ValidationError(
                f'This account is not yet registered with Bolvex Capital'
            )

        if account.user == User.objects.get(email=client):
            raise forms.ValidationError(
                f'Self transfer not supported'
            )
        return client


class ConvertbonusForm(TransactionForm):
    def __init__(self, *args, **kwargs):
        # self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)

        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()

    class Meta:
        model = Transaction
        fields = [
            'amount',

            'transaction_type'

        ]

    def clean_amount(self):
        account = self.account
        min_withdraw_amount = djmoney.money.Money(100, 'USD')
        max_withdraw_amount = (djmoney.money.Money(10000000, 'USD')

                               )
        balance = account.bonus

        amount = self.cleaned_data.get('amount')

        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f'You can convert at least {min_withdraw_amount} '
            )

        if amount > max_withdraw_amount:
            raise forms.ValidationError(
                f'You can convert at most {max_withdraw_amount} '
            )

        if amount > balance:
            raise forms.ValidationError(
                f'You have {balance}  in your Bonus account. '
                'You can not convert more than your bonus balance'
            )
        if account.user.account.Verification_status == 'Unverified':
            raise forms.ValidationError(
                f'Please Verify your Account !'
            )
        if account.user.account.Verification_status == 'Under Review':
            raise forms.ValidationError(
                f'Your Account is Under Review !')
        return amount


class InvestmentForm(TransactionForm):
    def __init__(self, *args, **kwargs):
        # self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)

        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()

    class Meta:
        model = Transaction
        fields = [
            'amount',
            'transaction_type',
            'investment_name',
        ]

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        investment_plan = Investment.objects.get(id=self.data['investment_name'])
        account = self.account
        min_amount = investment_plan.min_amount
        max_amount = investment_plan.max_amount
        balance = account.main_balance

        if amount < min_amount:
            raise forms.ValidationError(
                f'You can invest at least {min_amount}'
            )

        if amount > max_amount:
            raise forms.ValidationError(
                f'You can invest at most {max_amount} '
            )

        if amount > balance:
            raise forms.ValidationError(
                f'You have {balance}  in your account. '
                'You can not invest more than you have in your account balance'
            )

        return amount


class TransactionDateRangeForm(forms.Form):
    daterange = forms.CharField(required=False)

    def clean_daterange(self):
        daterange = self.cleaned_data.get("daterange")
        print(daterange)

        try:
            daterange = daterange.split(' - ')
            print(daterange)
            if len(daterange) == 2:
                for date in daterange:
                    datetime.datetime.strptime(date, '%Y-%m-%d')
                return daterange
            else:
                raise forms.ValidationError("Please select a date range.")
        except (ValueError, AttributeError):
            raise forms.ValidationError("Invalid date range")


class TransactionDateRangeForm1(forms.Form):
    daterange = forms.CharField(required=False)

    def clean_daterange(self):
        daterange = self.cleaned_data.get("daterange")
        print(daterange)

        try:
            daterange = daterange.split(' - ')
            print(daterange)
            if len(daterange) == 2:
                for date in daterange:
                    datetime.datetime.strptime(date, '%Y-%m-%d')
                return daterange
            else:
                raise forms.ValidationError("Please select a date range.")
        except (ValueError, AttributeError):
            raise forms.ValidationError("Invalid date range")


#


class Payment_MethodForm(forms.Form):
    admin_wallet = AdminWallet.objects.all()
    payment_method = forms.ModelChoiceField(queryset=admin_wallet, required=True, empty_label='Select payment method')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_method'].widget.attrs.update(
            {'class': 'col-lg-6 selectpicker form-control', })


class Investment_upgrade_Form(TransactionForm):
    def __init__(self, *args, **kwargs):
        # self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)

        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()

    class Meta:
        model = Transaction
        fields = [
            'amount',
            'transaction_type',
            'status'

        ]

    def clean_amount(self):
        account = self.account
        client_invest = Invest.objects.filter(account=account.user).last()

        # user = User.objects.get(email=client_invest)
        client_invest_acct = Invest.objects.get(pk=client_invest.id)
        inv_pro = Investment_profile.objects.get(trx_id=client_invest_acct.trx_id)
        previous_amount = inv_pro.amount_invested
        min_withdraw_amount = client_invest_acct.min_amount
        amount = self.cleaned_data.get('amount')
        max_withdraw_amount = client_invest_acct.max_amount
        upgrade_method = client_invest_acct.upgrade_method

        if upgrade_method == "Account Balance":
            amount = self.cleaned_data.get('amount')

            balance = account.main_balance
            new_amt = self.cleaned_data.get('amount') + inv_pro.amount_invested
            if amount > balance:
                raise forms.ValidationError(
                    f'You have {balance}  in your account. '
                    'You can not stake more than you have in your account balance'
                )
            if new_amt < min_withdraw_amount:
                raise forms.ValidationError(
                    f'You can stake at least {min_withdraw_amount}'
                )
            if new_amt > max_withdraw_amount:
                raise forms.ValidationError(
                    f'You can stake at most {max_withdraw_amount} '
                )



        elif upgrade_method == "ROI Only":
            balance = account.roi_balance
            amount = self.cleaned_data.get('amount')
            amount1 = self.cleaned_data.get('amount')
            if amount1 > balance:
                raise forms.ValidationError(
                    f'You have {balance}  in your ROI balance. '
                    'You can not stake more than you have in your ROI balance'
                )
            if self.cleaned_data.get('amount') + inv_pro.amount_invested < min_withdraw_amount:
                raise forms.ValidationError(
                    f'You can stake at least {min_withdraw_amount} '
                )

            if self.cleaned_data.get('amount') + inv_pro.amount_invested > max_withdraw_amount:
                raise forms.ValidationError(
                    f'You can stake at most {max_withdraw_amount} '
                )

        elif upgrade_method == "Both":
            # amount = self.cleaned_data.get('amount') + previous_amount
            amount1 = self.cleaned_data.get('amount')
            balance = account.main_balance + account.roi_balance
            if amount1 > balance:
                raise forms.ValidationError(
                    f'You have {balance}  in your ROI and Availbale balance combined. '
                    'You can not stake more than you have in your balance'
                )

            if self.cleaned_data.get('amount') + inv_pro.amount_invested < min_withdraw_amount:
                raise forms.ValidationError(
                    f'You can stake at least {min_withdraw_amount} '
                )
            if self.cleaned_data.get('amount') + inv_pro.amount_invested > max_withdraw_amount:
                raise forms.ValidationError(
                    f'You can stake at most {max_withdraw_amount} '
                )

        # roi_bal = self.account.roi_balance
        # roi = amount + roi_bal
        # if amount < min_withdraw_amount:
        #     raise forms.ValidationError(
        #         f'You can stake at least {min_withdraw_amount} '
        #     )

        # if amount > max_withdraw_amount:
        #     raise forms.ValidationError(
        #         f'You can stake at most {max_withdraw_amount} '
        #     )

        # if amount > roi:
        #     raise forms.ValidationError(
        #         f'You have a total of {roi}  in your ROI and Deposit account. '
        #         'You can not stake more than your Cummulative Capital'
        #     )
        return amount
