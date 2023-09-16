from decimal import Decimal
from os.path import sep

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from unicodedata import decimal
from django.contrib.sites.shortcuts import get_current_site
# import djmoney
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.http import HttpResponseRedirect, request, HttpResponse, JsonResponse

from boss.models import AdminWallet
from .forms import *
from .models import *

from django.shortcuts import render, redirect, get_object_or_404

from django.contrib import messages

from django.utils import timezone
import time
from django.core.mail import BadHeaderError, send_mail, EmailMultiAlternatives
from django.shortcuts import render, redirect
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView
import datetime
import accounts
import urllib.request
import urllib.parse
from pages.forms import ContactForm
from transactions.constants import DEPOSIT, WITHDRAWAL, INVESTMENT, CONVERT_BONUS, TRANSFER, Investment_Upgrade, \
    CONVERT_ROI
from transactions.forms import *
from transactions.models import Transaction

x = datetime.datetime.now()


class TransactionRepostView(LoginRequiredMixin, ListView):
    template_name = 'transactions/transactions.html'
    model = Transaction
    form_data = {}

    def get(self, request, *args, **kwargs):
        form = TransactionDateRangeForm(request.GET or None)
        if form.is_valid():
            self.form_data = form.cleaned_data

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            account=self.request.user.client_account
        )

        daterange = self.form_data.get("daterange")

        if daterange:
            queryset = queryset.filter(timestamp__date__range=daterange)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account,
            'form': TransactionDateRangeForm(self.request.GET or None),

        })

        return context


class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transactions/deposit_preview.html'
    model = Transaction
    title = ''
    success_url = reverse_lazy('transactions:transactions')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.client_account
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title
        })

        return context


@login_required(login_url='login')
def wallet1(request):
    form = Payment_MethodForm(request.POST)
    transaction = Transaction.objects.filter(account=request.user.client_account, transaction_type=1)[::-1][:5]
    context = {
        'form': form,
        'transaction': transaction,
    }
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        return redirect('transaction:crypto', payment_method)

    return render(request, 'transactions/deposit_fund.html', context)


class CryptoView(TransactionCreateMixin):
    success_url = reverse_lazy('transactions:transactions')
    form_class = Crypto_DepositForm
    title = 'Deposit Money to Your Account'
    template_name = 'transactions/crpto.html'

    def get_initial(self):
        initial = {'transaction_type': DEPOSIT
                   }
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.client_account

        Transaction.deposit_check_email(account, amount)
        return super(CryptoView, self).form_valid(form)

    def setup(self, request, *args, **kwargs):
        self.payment_method = kwargs['id']
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        payment_method = self.payment_method
        currency = get_object_or_404(AdminWallet, id=payment_method)
        context = super().get_context_data(**kwargs)
        context.update({
            'crypto': currency,
        })
        return context


class WithdrawMoneyView(TransactionCreateMixin):
    success_url = reverse_lazy('transactions:dashboard')
    form_class = WithdrawForm
    title = 'Withdrawal'
    template_name = 'transactions/withdraw.html'

    def get_initial(self):
        initial = {'transaction_type': WITHDRAWAL}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount', 'USD')
        account = self.request.user.client_account
        Transaction.withdrawal_check_email(account, amount)

        messages.success(
            self.request,
            f' Your withdrawal is been processed!'
        )
        form.save(commit=True)

        return super(WithdrawMoneyView, self).form_valid(form)


class Convert_roiView(TransactionCreateMixin):
    success_url = reverse_lazy('transactions:transactions')
    form_class = ConvertroiForm
    title = ''
    template_name = 'transactions/roi_withdrawal.html'

    def get_initial(self):
        initial = {'transaction_type': CONVERT_ROI}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount', 'USD')

        self.request.user.client_account.roi_balance -= form.cleaned_data.get('amount')
        self.request.user.client_account.main_balance += form.cleaned_data.get('amount')
        self.request.user.client_account.save(update_fields=['roi_balance', 'main_balance'])

        return super().form_valid(form)


class Convert_bonusView(TransactionCreateMixin):
    success_url = reverse_lazy('transactions:transactions')
    form_class = ConvertbonusForm
    title = ''
    template_name = 'transactions/convert_bonus.html'

    def get_initial(self):
        initial = {'transaction_type': CONVERT_BONUS}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount', 'USD')

        self.request.user.client_account.bonus -= form.cleaned_data.get('amount')
        self.request.user.client_account.main_balance += form.cleaned_data.get('amount')
        self.request.user.client_account.save(update_fields=['bonus', 'main_balance'])

        return super().form_valid(form)


class Transfer_funds(TransactionCreateMixin):
    success_url = reverse_lazy('transactions:transactions')
    form_class = TransferForm
    title = ''
    template_name = 'transactions/transfer_funds.html'

    def get_initial(self):
        initial = {'transaction_type': TRANSFER}
        return initial

    def form_valid(self, form):
        account = self.request.user
        amount = form.cleaned_data.get('amount', 'USD')
        address = form.cleaned_data['client']
        user = User.objects.get(email=address)
        trans_to = Account.objects.filter(user=user)
        receiver = Account.objects.get(user=user)
        add_up = receiver.main_balance + amount
        trans_to.update(main_balance=add_up)
        Transaction.transfer_check_email(account, amount)

        self.request.user.client_account.main_balance -= form.cleaned_data.get('amount')
        self.request.user.client_account.save(update_fields=['main_balance'])
        transaction = Transaction.objects.create(account=receiver,
                                                 amount=amount,
                                                 transaction_type=TRANSFER,
                                                 balance_after_transaction=receiver.main_balance,
                                                 date=timezone.now(),
                                                 status='Received',
                                                 transfer_type="Received"
                                                 )
        transaction.save()
        return super().form_valid(form)


class investpreview(TransactionCreateMixin):
    success_url = reverse_lazy('transactions:transactions')
    form_class = InvestmentForm
    title = 'Investment'
    template_name = 'transactions/investment_preview.html'

    def get_initial(self):
        initial = {'transaction_type': INVESTMENT}
        return initial

    def form_valid(self, form):
        account = self.request.user
        investment_id = form.cleaned_data.get('investment_name')
        investment_name = Investment.objects.get(name=investment_id)
        amount = form.cleaned_data.get('amount', 'USD')
        investment_acct_name = Investment.objects.get(name=investment_name)
        min_amount = investment_acct_name.min_amount
        max_amount = investment_acct_name.max_amount
        client = Client.objects.get(user=self.request.user)
        client_recommended_by = client.recommended_by

        if client_recommended_by is not None:
            bonus_goes_to = Account.objects.filter(user=client_recommended_by)  # the recommender Client
            bonus_acct = Account.objects.get(user=client_recommended_by)
            current_bonus = bonus_acct.bonus  # current bonus balance
            commission = Transaction.referral_commission(rate=investment_acct_name.referral_commission,
                                                         amount=amount)  # Referral commission function
            bonus = current_bonus + commission
            bonus_goes_to.update(bonus=bonus)
            Transaction.referral_commission_email(account=client_recommended_by, amount=commission)

        roi = Transaction.ROI(amount=amount, rate=investment_acct_name.daily_rate,
                              days=investment_acct_name.period_in_days)
        self.request.user.client_account.main_balance -= form.cleaned_data.get('amount')
        self.request.user.client_account.total_amount_investment += form.cleaned_data.get('amount')
        self.request.user.client_account.total_expected_roi += roi
        self.request.user.client_account.save(
            update_fields=['main_balance', 'total_amount_investment', 'total_expected_roi'])

        earning = Transaction.earning(amount=amount, rate=investment_acct_name.daily_rate)
        expiry_date = Transaction.expiry_date(amount=amount, rate=investment_acct_name.daily_rate,
                                              days=investment_acct_name.period_in_days)
        sa = form.save(commit=True)

        # investment_profile_creation
        client_investment = Investment_profile.objects.create(
            user=self.request.user,
            investment=Investment.objects.get(name=investment_acct_name),
            amount_invested=amount,
            expected_roi=roi,
            earning=earning,
            status='Active',
            trx_id=sa.pk,
            date_started=timezone.now(),
            expiry_date=timezone.now() + relativedelta(days=expiry_date),
            next_payout=timezone.now() + relativedelta(days=1),
        )
        client_investment.save()

        return super(investpreview, self).form_valid(form)

    def setup(self, request, *args, **kwargs):
        self.investment_name = kwargs['investment_name']
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        investment = Investment.objects.get(name=str(self.investment_name))
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user,
            'trans': TransactionDateRangeForm(self.request.GET or None),
            'time': datetime.datetime.now(),
            'investment': investment,
        })

        return context


class Inv_upgrade(TransactionCreateMixin):
    success_url = reverse_lazy('transactions:transactions')
    form_class = Investment_upgrade_Form
    title = ''
    template_name = 'transactions/inv_upgrade.html'

    def get_initial(self):
        initial = {'transaction_type': Investment_Upgrade,

                   }
        return initial

    def form_valid(self, form):
        account = self.request.user.client_account
        q = idi[-1]
        client1 = Invest.objects.filter(account=self.request.user)
        a = client1.get(id=q)
        invest_name = a.invest_type
        investment_name = invest_name
        upgrade_method = a.upgrade_method
        amount = form.cleaned_data.get('amount', 'USD')

        investment_acct_name = Investment.objects.get(name=invest_name)
        min_amount = investment_acct_name.min_amount
        max_amount = investment_acct_name.max_amount

        new_plan = investment_name
        trx_no = a.trx_id
        trx = Transaction.objects.get(id=trx_no)
        inv_pro = Investment_profile.objects.get(trx_id=trx_no)
        trx_update = Transaction.objects.filter(id=trx_no)

        pre_exp = inv_pro.expiry_date - timezone.now()

        exp = relativedelta(days=investment_acct_name.period_in_days) - relativedelta(days=pre_exp.days)
        print(inv_pro.expiry_date, type(inv_pro.expiry_date))

        new_exp = inv_pro.expiry_date + exp
        investment_acct_name = Investment.objects.get(name=new_plan)
        min_amount = investment_acct_name.min_amount
        max_amount = investment_acct_name.max_amount
        # earning = (inv_pro.amount_invested + amount) * investment_acct_name.daily_rate / 100
        # amount_earned = inv_pro.amount_earned - inv_pro.amount_earned
        invest_pro = Investment_profile.objects.filter(trx_id=trx_no)

        if upgrade_method == "Account Balance":
            balance = account.main_balance
            self.request.user.client_account.main_balance -= form.cleaned_data.get('amount')
            self.request.user.client_account.total_amount_investment += form.cleaned_data.get('amount')
            self.request.user.client_account.save(update_fields=['main_balance', 'total_amount_investment', ])
            amount_invested = amount + inv_pro.amount_invested
            earning = (inv_pro.amount_invested + amount) * investment_acct_name.daily_rate / 100

            def ROI(amount=amount_invested):
                if amount >= min_amount and amount <= max_amount:
                    interest = (
                                       amount * investment_acct_name.daily_rate / 100) * investment_acct_name.period_in_days
                    return interest

                return ROI()

            trx_update.update(amount=amount_invested, investment_name=new_plan, status="Active")
            Investment_upgrade.objects.create(
                user=self.request.user,
                previous_plan=inv_pro.investment,
                upgraded_plan=Investment.objects.get(name=investment_name),
                trx_id=trx_no,
                upgrade_method=upgrade_method,
                previous_amount=inv_pro.amount_invested,
                upgrade_amount=amount,
                date=timezone.now()
            )
            invest_pro.update(expiry_date=new_exp, investment=Investment.objects.get(name=investment_name),
                              amount_invested=amount_invested, expected_roi=ROI(), earning=earning, upgraded="True")

        elif upgrade_method == "ROI Only":
            balance = account.roi_balance
            amount = form.cleaned_data.get('amount')
            self.request.user.client_account.roi_balance -= form.cleaned_data.get('amount')
            self.request.user.client_account.total_amount_investment += form.cleaned_data.get('amount')
            self.request.user.client_account.save(update_fields=['total_amount_investment', 'roi_balance'])
            amount_invested = amount + inv_pro.amount_invested
            trx_update.update(amount=amount_invested, investment_name=new_plan, status="Upgraded")
            earning = (inv_pro.amount_invested + amount) * investment_acct_name.daily_rate / 100

            def ROI(amount=c):
                if amount >= min_amount and amount <= max_amount:
                    interest = (
                                       amount * investment_acct_name.daily_rate / 100) * investment_acct_name.period_in_days
                    return interest

                return ROI()

            Investment_upgrade.objects.create(
                user=self.request.user,
                previous_plan=inv_pro.investment,
                upgraded_plan=Investment.objects.get(name=investment_name),
                trx_id=trx_no,
                upgrade_method=upgrade_method,
                previous_amount=inv_pro.amount_invested,
                upgrade_amount=amount,
                date=timezone.now()
            )

            invest_pro.update(expiry_date=new_exp, investment=Investment.objects.get(name=investment_name),
                              amount_invested=amount_invested, expected_roi=ROI(), earning=earning, upgraded="True")
        elif upgrade_method == "Both":
            balance = account.main_balance + account.roi_balance
            self.request.user.client_account.total_amount_investment += form.cleaned_data.get('amount')
            new_bal = balance - form.cleaned_data.get('amount')
            self.request.user.client_account.roi_balance -= self.request.user.client_account.roi_balance
            self.request.user.client_account.main_balance = new_bal
            amount_earned = inv_pro.amount_earned - inv_pro.amount_earned
            amount_invested = amount + inv_pro.amount_invested
            trx_update.update(amount=amount_invested, investment_name=new_plan, status="Upgraded")

            earning = (inv_pro.amount_invested + amount) * investment_acct_name.daily_rate / 100

            def ROI(amount=amount_invested):
                if amount >= min_amount and amount <= max_amount:
                    interest = (
                                       amount * investment_acct_name.daily_rate / 100) * investment_acct_name.period_in_days
                    return interest

                return ROI()

            Investment_upgrade.objects.create(
                user=self.request.user,
                previous_plan=inv_pro.investment,
                upgraded_plan=Investment.objects.get(name=investment_name),
                trx_id=trx_no,
                upgrade_method=upgrade_method,
                previous_amount=inv_pro.amount_invested,
                upgrade_amount=amount,
                date=timezone.now()
            )
            invest_pro.update(expiry_date=new_exp, investment=Investment.objects.get(name=investment_name),
                              amount_earned=amount_earned, amount_invested=amount_invested, expected_roi=ROI(),
                              earning=earning, upgraded="True")
            self.request.user.client_account.save(
                update_fields=['main_balance', 'total_amount_investment', 'roi_balance'])

        return super().form_valid(form)

    def setup(self, request, *args, **kwargs):
        self.investment_id = kwargs['id']
        return super().setup(request, *args, **kwargs)



@login_required(login_url='login')
def dashboard(request):
    client = Account.objects.get(user=request.user)
    account = request.user.client_account
    a = Transaction.objects.filter(account=account)
    b = a.filter(transaction_type=3).count()
    c_e = a.filter(expired=True).count()
    roi = client.total_expected_roi

    # account = request.user.account
    c = Transaction.objects.filter(account=account, )[::-1]

    e = []

    for x in c:
        e.append(x)

    transaction = e[:3]

    balance = client.main_balance
    date = client.last_deposit_date
    code = Client.objects.get(user=request.user).referral_code
    total_invest = Account.objects.get(user=request.user)

    total_amount_mined = djmoney.money.Money(0, 'USD')
    mined = Investment_profile.objects.filter(user=request.user)
    amount_mined = []

    for x in mined:
        amount_mined.append(x.amount_earned.amount)
    for x in range(0, len(amount_mined)):
        total_amount_mined = 0 + amount_mined[x]

    bonus = client.bonus
    month = datetime.datetime.now()

    date = client.last_deposit_date
    code = Client.objects.get(user=request.user).referral_code
    total_invest = Account.objects.get(user=request.user).total_amount_investment
    bonus = client.bonus
    current_site = get_current_site(request)
    context = {
        'balance': balance,
        'expired': c_e,
        "domain": current_site.domain,
        'date': date,
        'bonus': bonus,
        'code': code,
        'roi': roi,
        'total_invest': total_invest,
        'transaction': transaction,
    }
    return render(request, "transactions/dashboard.html", context)


def get_data(request):
    date = datetime.datetime.now()
    month = timezone.now().month
    account = Account.objects.get(user=request.user)

    payload = Investment_profile.objects.filter(user=request.user, status='Active')
    dep_data = []
    labels = []

    for payload in payload:
        dep_data.append(str(payload.amount_earned.amount))
        labels.append(str(payload.date_started.strftime('%x')))

    data = {
        "Deposit": dep_data,
        'labels': labels,
    }
    return JsonResponse(data)


@login_required(login_url='login')
def customer_care(request):
    client = Client.objects.get(user=request.user)
    if request.method == 'POST':
        email_subject = request.POST.get('subject')
        sender = request.POST.get('email')
        email_message = request.POST.get('message')
        message = email_message + f" \n sender is {sender}"
        email = 'bolvexcapital@gmail.com'

        email = EmailMultiAlternatives(
            email_subject, message, to=[email]
        )
        email.attach_alternative(message, 'text/html')
        email.content_subtype = 'html'
        email.mixed_subtype = 'related'

        email.send()

        messages.success(request, 'your message have been submitted successfully')
        return redirect('transaction:customer_care')

    return render(request, "transactions/customer_services.html")


@login_required(login_url='login')
def rec_sys(request):
    client = Client.objects.get(user=request.user)
    my_recs = Client.objects.filter(recommended_by=request.user)
    code = client.referral_code
    current_site = get_current_site(request)
    context = {
        'domain': current_site.domain,
        'c': my_recs,
        'code': code
    }
    return render(request, 'transactions/referral_system.html', context)


@login_required(login_url='login')
def investment(request):
    investment = Investment.objects.all()
    context = {
        'investment': investment,
    }
    if request.method == 'POST':
        investment_name = request.POST.get('investment_name')
        return redirect('transaction:investment_preview', investment_name)

    return render(request, "transactions/new_investment.html", context)


@login_required(login_url='login')
def investment_log(request):
    account = request.user.client_account
    transactions = Transaction.objects.filter(account=account, transaction_type=3, )[::-1]
    transaction = []
    page = request.GET.get('page', 1)
    paginator = Paginator(transactions, 10)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    for x in transactions:
        transaction.append(x)

    context = {'transaction': transaction,
               'users': users,
               }
    return render(request, 'transactions/investment_log.html', context)


def error_404_view(request, exception):
    return render(request, '404.html')


def error_500_view(request):
    return render(request, '500.html')


@login_required(login_url='login')
def transactions(request):
    account = request.user.client_account
    c = Transaction.objects.filter(account=account)[::-1]
    e = []
    page = request.GET.get('page', 1)
    paginator = Paginator(c, 10)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    for x in c:
        e.append(x)

    transaction = e
    context = {'transaction': transaction,
               'users': users,
               }
    return render(request, 'transactions/transactions.html', context)


# @login_required(login_url='login')
# def upgrade_inv(request):
#     active_investment = Investment_profile.objects.filter(user=request.user, status='Active')
#
#     context = {
#                 'investment': active_investment,
#                 }
#     return render(request, 'transactions/upgrade_inv.html', context)


@login_required(login_url='login')
def with_log(request):
    account = request.user.client_account
    c = Transaction.objects.filter(account=account, transaction_type=2)[::-1]
    e = []
    page = request.GET.get('page', 1)
    paginator = Paginator(c, 5)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    for x in c:
        e.append(x)

    transaction = e
    context = {'transaction': transaction,
               'users': users,
               }
    return render(request, 'transactions/with_log.html', context)
