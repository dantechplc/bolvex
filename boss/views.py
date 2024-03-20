from datetime import datetime
from django.contrib import messages
import os
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.files import File
from dateutil.relativedelta import relativedelta
from django.shortcuts import render, redirect
from django_countries.fields import CountryField
import djmoney
from django.core.files.storage import FileSystemStorage
from django.template.loader import render_to_string
from django.core.mail import BadHeaderError, send_mail, EmailMultiAlternatives
from accounts.models import Client, User, Account, Investment_profile
from accounts.forms import UserRegistrationForm, ClientForm, AccountForm, Investment_profile_Form, VerificationForm
from boss.decorator import allowed_users
from boss.emailsender import EmailSender
from boss.forms import ClientUpdateForm
from boss.models import AdminWallet
from pages.models import CompanyProfile
from transactions.models import Transaction
from accounts.models import *
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from accounts.forms import *


# Create your views here.


def get_all_logged_in_users():
    # Query all non-expired sessions
    # use timezone.now() instead of datetime.now() in latest versions of Django
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    uid_list = []

    # Build a list of user ids from that query
    for session in sessions:
        data = session.get_decoded()
        uid_list.append(data.get('_auth_user_id', None))

    # Query all logged in users based on id list
    return User.objects.filter(id__in=uid_list)


@login_required(login_url='admin_login')
@allowed_users(allowed_roles=['admin'])
def admin_dashboard(request):
    Clients = Client.objects.all()

    Deposits = Transaction.objects.filter(transaction_type=1)
    pending_withdrawals = Transaction.objects.filter(transaction_type=2, status='pending').count()
    pending_deposit = Transaction.objects.filter(transaction_type=1, status='pending').count()
    kyc_verified = Client.objects.filter(Verification_status='Verified').count()
    kyc_unverified = Client.objects.filter(Verification_status='Unverified').count()
    kyc_under_review = Client.objects.filter(Verification_status='Under Review').count()
    active_user_count = get_all_logged_in_users().count()
    recent_withdrawals = Transaction.objects.filter(transaction_type=2)[::-1]
    payment_histories = Transaction.objects.filter(transaction_type=1)[::-1]
    recent_withdrawals_list = []
    for x in recent_withdrawals:
        recent_withdrawals_list.append(x)
    payment_histories_list = []
    for x in payment_histories:
        payment_histories_list.append(x)

    payment_history = payment_histories_list[:5]
    recent_withdrawal = recent_withdrawals_list[:5]
    # time_now = datetime.datetime.now()
    last_2day = timezone.now() - relativedelta(days=2)

    recent_client = Client.objects.filter(date_joined__gte=last_2day)[::-1]

    context = {
        'client': Clients,
        'deposit': Deposits,
        'pending_withdrawals': pending_withdrawals,
        'pending_deposit': pending_deposit,
        'kyc_verified': kyc_verified,
        'kyc_unverified': kyc_unverified,
        'kyc_under_review': kyc_under_review,
        'active_user_count': active_user_count,
        'recent_withdrawal': recent_withdrawal,
        'payment_history': payment_history,
        'recent_client': recent_client,
    }
    return render(request, 'boss/admin_ds.html', context)


@login_required(login_url='admin_login')
def client_add(request):
    users = Client.objects.all()
    #
    # if request.method == 'GET':
    #     return render(request, 'boss/client_add.html')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # inactive_user = send_verification_email(request, form)
            # inactive_user.save()

            user = form.save(commit=False)
            user.is_active = True
            username = form.cleaned_data.get('username')
            state = request.POST.get('state')
            phone_number = form.cleaned_data.get('phone_number')
            country = request.POST.get('country')
            account_password = request.POST.get('password1')

            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            gender = request.POST.get('gender')
            address = request.POST.get('address')
            city = request.POST.get('city')
            profile_pic = request.FILES.get('profile_pic')
            dob = request.POST.get('dob')
            verification_status = request.POST.get('verification_status')
            referred_by = request.POST.get('referred_by')
            email = request.POST.get('email')
            zip_code = request.POST.get('zip')

            def reff(referred_by1):
                if referred_by1 == 'None':
                    pass
                elif referred_by1 != 'None':
                    referred_by1 = User.objects.get(email=referred_by1)
                    return referred_by1

            user.save()
            a = Client.objects.create(user=user,
                                      recommended_by=reff(referred_by),
                                      phone_number=phone_number,
                                      # profile_pic=profile_pic,
                                      date_joined=timezone.now(),
                                      first_name=first_name,
                                      last_name=last_name,
                                      gender=gender,
                                      address=address,
                                      dob=dob,
                                      city=city,
                                      zip=zip_code,
                                      Verification_status=verification_status,
                                      username=username,
                                      country=country,
                                      state=state,
                                      account_password=account_password)
            # if profile_pic == {}:
            #     a.profile_pic.save('profile_pic.png', File(open('static/images/profile1.png', 'rb')))

            c = Verification.objects.create(user=user,
                                            first_name=first_name,
                                            last_name=last_name,
                                            dob=dob,
                                            gender=gender,
                                            address=address,
                                            city=city,
                                            state=state,
                                            zip=zip_code,

                                            )
            c.save()
            client_account = Account.objects.create(user=user)
            client_account.save()
            messages.success(request,
                             'Account have been created for ' + username + ' successfully')

            return redirect('/client_add')
        else:
            form = UserRegistrationForm(request.POST)

            return render(request, 'boss/client_add.html', {'form': form, 'users': users, })
    else:
        form = UserRegistrationForm()
    return render(request, 'boss/client_add.html', {'form': form, 'users': users, })


@login_required(login_url='admin_login')
def client_delete(request, id, uid):
    item = Client.objects.get(pk=id)
    user_delete = User.objects.get(pk=uid)
    user_delete.delete()
    item.delete()
    messages.success(request, 'The Client has been deleted successfully!')
    return redirect('/boss')


@login_required(login_url='admin_login')
def client_list(request):
    Clients = Client.objects.filter(date_joined__lt=timezone.now())[::-1]

    user_list = User.objects.all()
    page = request.GET.get('page', 1)

    paginator = Paginator(Clients, 10)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    context = {
        'client': Clients,
        'users': users,

    }
    return render(request, 'boss/client_list.html', context)


@login_required(login_url='admin_login')
def client_edit(request, id):
    form = ClientUpdateForm()
    clients = Client.objects.get(pk=id)
    if request.method == 'POST':
        form = ClientUpdateForm(request.POST)
        if form.is_valid():
            if request.POST.get('Verification_status') == "Verified" and clients.Verification_status != "Verified":
                EmailSender.kyc_verified(email=clients.user, name=clients.username)
            clients.Verification_status = form.cleaned_data['Verification_status']
            clients.first_name = form.cleaned_data['first_name']
            clients.last_name = form.cleaned_data['last_name']
            clients.username = form.cleaned_data['username']
            clients.gender = form.cleaned_data['gender']
            clients.phone_number = form.cleaned_data['phone_number']
            clients.city = form.cleaned_data['city']
            clients.state = form.cleaned_data['state']
            clients.zip = form.cleaned_data['zip']
            clients.address = form.cleaned_data['address']
            clients.save(update_fields=['Verification_status', 'first_name', 'last_name', 'gender', 'phone_number',
                                        'city', 'state', 'address','zip', 'username', ])
            messages.success(request, 'Client info has been edited successfully!')
            return redirect(f'/client_edit/{id}')

    return render(request, 'boss/client_edit.html',
                  {'client': clients, 'form': form, })


@login_required(login_url='admin_login')
def kyc_unverified(request):
    verification = Client.objects.filter(Verification_status='Unverified')[::-1]
    page = request.GET.get('page', 1)
    paginator = Paginator(verification, 5)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    context = {
        # 'client': client,
        'users': users,
        'verification': verification,
    }
    return render(request, 'boss/kyc_unverified.html', context)


@login_required(login_url='admin_login')
def kyc_under_review(request):
    verification = Client.objects.filter(Verification_status='Under Review')[::-1]
    page = request.GET.get('page', 1)
    paginator = Paginator(verification, 5)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    context = {
        # 'client': client,
        'users': users,
        'verification': verification,
    }
    return render(request, 'boss/kyc_under_review.html', context)


@login_required(login_url='admin_login')
def kyc_verified(request):
    # client = Client.objects.get(pk=id)
    # user = User.objects.get(email=client.user.email)
    verification = Client.objects.filter(Verification_status='Verified')[::-1]
    page = request.GET.get('page', 1)
    paginator = Paginator(verification, 5)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    context = {
        # 'client': client,
        'users': users,
        'verification': verification,
    }
    return render(request, 'boss/kyc_verified.html', context)


@login_required(login_url='admin_login')
def kyc_profile_delete(request, id):
    profile = Verification.objects.get(pk=id)
    client_id = Client.objects.get(user=profile.user)
    profile.delete()
    messages.success(request, 'KYC profile have been deleted Successfully!')
    return redirect(f"/kyc_profile_list/{client_id.id}")


@login_required(login_url='admin_login')
def kyc_profile_list(request, id):
    client = Client.objects.get(pk=id)
    user = User.objects.get(email=client.user.email)
    verification = Verification.objects.filter(user=user)[::-1]
    page = request.GET.get('page', 1)
    paginator = Paginator(verification, 5)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    context = {
        'client': client,
        'users': users,
        'verification': verification,
    }
    return render(request, 'boss/kyc_profile_list.html', context)


@login_required(login_url='admin_login')
def kyc_profile(request, id):
    client = Verification.objects.get(pk=id)
    user = User.objects.get(email=client.user.email)
    client_profile = Client.objects.get(user=user)
    form = VerificationForm(request.POST or None, instance=user)
    context = {
        'client': client,
        'client_profile': client_profile,
        'form': form,
    }
    if request.method == "POST":
        client_profile.Verification_status = request.POST.get('Verification_status')
        client_profile.save(update_fields=['Verification_status'])
        if client_profile.Verification_status == "Verified":
            EmailSender.kyc_verified(email=client_profile.user.email, name=client_profile.username)
            messages.success(request, "Verification profile have been updated")
        return redirect(f'/kyc_profile/{id}')
    return render(request, 'boss/kyc_profile.html', context)


@login_required(login_url='admin_login')
def active_clients(request):
    active_users = get_all_logged_in_users()
    context = {
        'active_user': active_users,
    }
    return render(request, 'boss/active_users.html', context)


@login_required(login_url='admin_login')
def wallet_upload(request):
    wallet = AdminWallet.objects.all()[::-1]
    context = {
        'wallet': wallet,
    }

    return render(request, 'boss/wallet_upload.html', context)


@login_required(login_url='admin_login')
def wallet_add(request):
    if request.method == "POST":
        post_doc = AdminWallet.objects.create(
            wallet_name=request.POST.get('name'),
            wallet_address=request.POST.get('wallet_address'),

        )
        post_doc.save()
        messages.success(request, 'New Wallet have been added successfully!')
        return redirect(f'/wallet_upload')

    return render(request, 'boss/wallet_add.html', )


@login_required(login_url='admin_login')
def wallet_edit(request, id):
    name = request.POST.get('name')

    # post_file_name =  request.FILES['post'].name

    wallet_edit = AdminWallet.objects.get(pk=id)
    if request.method == "POST":

        wallet_doc = AdminWallet.objects.get(
            pk=id
        )
        wallet_doc.wallet_name = name
        wallet_doc.wallet_address = request.POST.get('wallet_address')
        wallet_doc.save(update_fields=["wallet_name", "wallet_address", "wallet_barcode"])

        messages.success(request, 'Wallet have been updated successfully!')
        return redirect(f'/wallet_upload')
    context = {
        'wallet1': wallet_edit,

    }

    return render(request, 'boss/wallet_edit.html', context)


@login_required(login_url='admin_login')
def wallet_delete(request, id):
    file = AdminWallet.objects.get(pk=id)
    file.delete()
    messages.warning(request, 'Wallet have been deleted successfully! ')

    return redirect('/wallet_upload')













@login_required(login_url='admin_login')
def change_user_password(request, id):
    client = Client.objects.get(pk=id)
    context = {
        'client': client,
    }
    if request.method == "POST":
        password = request.POST.get('password')
        client_user = Client.objects.filter(pk=id)
        client = Client.objects.get(pk=id)
        client_email = client.user.email
        user = User.objects.get(email=client_email)
        user.set_password(password)
        user.save()
        client_user.update(account_password=password)
        messages.success(request, 'Client password has been changed successfully!')
        return redirect(f'/change_user_password/{id}')

    return render(request, 'boss/change_password.html', context)


@login_required(login_url='admin_login')
def account_profile(request, id):
    client = Client.objects.get(pk=id)
    user = User.objects.get(email=client.user.email)
    form = AccountForm(request.POST, instance=user)
    account = Account.objects.get(user=user)
    no_of_inv = Investment_profile.objects.filter(user=user).count()

    if request.method == "POST":
        main_balance = request.POST.get('main_balance_0')
        bonus = request.POST.get('bonus_0')

        insurance_dept = request.POST.get('insurance_dept')
        referral_dept = request.POST.get('referral_dept')
        if form.is_valid():
            form1 = AccountForm(request.POST, instance=user)
            form1.save()
            a = Account.objects.filter(user=user)
            trx = Transaction.objects.filter(account=account, transaction_type=1, status='Successful')

            a.update(main_balance=main_balance,
                     bonus=bonus,
                     )
            messages.success(request, 'Client Account has been updated successfully!')
            return redirect(f'/account_profile/{id}')
        else:

            return render(request, 'boss/account_profile.html', {'form': form, 'account': account, 'client': client})
    context = {
        'client': client,
        'form': form,
        'account': account,
        'no_of_inv': no_of_inv,

    }

    return render(request, 'boss/account_profile.html', context)


@login_required(login_url='admin_login')
def investment_profile(request, id):
    client = Investment_profile.objects.get(pk=id)
    user = User.objects.get(email=client.user.email)
    client_profile = Client.objects.get(user=user)
    form = Investment_profile_Form(request.POST or None, instance=user)
    context = {
        'client': client,
        'client_profile': client_profile,
        'form': form,
    }
    if request.method == 'POST':
        form = Investment_profile_Form(request.POST or None, instance=user)
        if form.is_valid():
            form.save(commit=True)
            messages.success(request, 'Investment Profile have been successfully edited')
            c = Investment_profile.objects.filter(pk=id)
            c.update(amount_invested=request.POST.get('amount_invested_0'),
                     expected_roi=request.POST.get('expected_roi_0'),
                     amount_earned=request.POST.get('amount_earned_0'),
                     earning=request.POST.get('earning_0'),
                     status=request.POST.get('status'),
                     )
            if request.POST.get('status') == "Expired":

                c = Transaction.objects.filter(pk=client.trx_id)

                c.update(status=request.POST.get('status'),
                         amount=request.POST.get('amount_invested_0'),
                         expired=True,
                         )
            elif request.POST.get('status') == "On Hold":
                current_date = timezone.now()
                expiry_date = client.expiry_date
                new_date = expiry_date - current_date + relativedelta(days=2)
                new_details = Investment_profile.objects.filter(pk=id)
                new_details.update(
                    status=request.POST.get('status'),
                    day_on_hold=new_date.days,
                )
                c = Transaction.objects.filter(pk=client.trx_id)

                c.update(status=request.POST.get('status'),
                         amount=request.POST.get('amount_invested_0'),

                         )
            elif request.POST.get('status') == "Active" and client.status != "Active":
                day_on_hold = client.day_on_hold
                new_date = timezone.now() + relativedelta(days=day_on_hold)
                new_details = Investment_profile.objects.filter(pk=id)
                new_details.update(
                    status=request.POST.get('status'),
                    expiry_date=new_date,
                )
                c = Transaction.objects.filter(pk=client.trx_id)

                c.update(status=request.POST.get('status'),
                         amount=request.POST.get('amount_invested_0'),

                         )
            else:
                c = Transaction.objects.filter(pk=client.trx_id)

                c.update(status=request.POST.get('status'),
                         amount=request.POST.get('amount_invested_0'),
                         )
            return redirect(f'/investment_profile/{id}')
        else:
            return render(request, 'boss/investment_profile.html', context)

    return render(request, 'boss/investment_profile.html', context)


@login_required(login_url='admin_login')
def investment_profile_list(request, id):
    client = Client.objects.get(pk=id)
    user = User.objects.get(email=client.user.email)
    investment = Investment_profile.objects.filter(user=user)[::-1]
    page = request.GET.get('page', 1)
    paginator = Paginator(investment, 5)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    context = {
        'client': client,
        'users': users,
        'investment': investment,
    }
    return render(request, 'boss/investment_profile_list.html', context)


@login_required(login_url='admin_login')
def investment_profile_delete(request, id):
    profile = Investment_profile.objects.get(pk=id)
    client_id = Client.objects.get(user=profile.user)
    profile.delete()
    messages.success(request, 'Investment profile have been deleted Successfully!')
    return redirect(f'/investment_profile_list/{client_id.id}')




@login_required(login_url='admin_login')
@allowed_users(allowed_roles=['admin'])
def active_sub(request):
    Active = Investment_profile.objects.filter(status="Active")[::-1]

    page = request.GET.get('page', 1)
    paginator = Paginator(Active, 10)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    context = {
        # 'client': client,
        'users': users,
        'Active': Active,
    }

    return render(request, 'boss/active_sub.html', context)


@login_required(login_url='admin_login')
@allowed_users(allowed_roles=['admin'])
def dep_trx_delete(request, id):
    trx = Transaction.objects.get(pk=id)
    trx.delete()
    messages.success(request, 'Deposit Transaction have been deleted successfully! ')
    return redirect('/dep_trx')


@login_required(login_url='admin_login')
@allowed_users(allowed_roles=['admin'])
def with_trx_delete(request, id):
    trx = Transaction.objects.get(pk=id)
    trx.delete()
    messages.success(request, 'Withdrawal Transaction have been deleted successfully! ')
    return redirect('/with_trx')


@login_required(login_url='admin_login')
@allowed_users(allowed_roles=['admin'])
def inv_trx_delete(request, id):
    trx = Transaction.objects.get(pk=id)
    trx.delete()
    messages.success(request, 'Investment Transaction have been deleted successfully! ')
    return redirect('/inv_trx')


@login_required(login_url='admin_login')
@allowed_users(allowed_roles=['admin'])
def dep_trx(request):
    trx = Transaction.objects.filter(transaction_type=1)[::-1]
    # client = Client.objects.get(pk=id)
    # user = User.objects.get(email=client.user.email)

    page = request.GET.get('page', 1)
    paginator = Paginator(trx, 10)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    context = {
        # 'client': client,
        'users': users,
        'trx': trx,
    }
    return render(request, 'boss/dep_trx.html', context)


@login_required(login_url='admin_login')
@allowed_users(allowed_roles=['admin'])
def with_trx(request):
    trx = Transaction.objects.filter(transaction_type=2)[::-1]
    # client = Client.objects.get(pk=id)
    # user = User.objects.get(email=client.user.email)

    page = request.GET.get('page', 1)
    paginator = Paginator(trx, 10)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    context = {
        # 'client': client,
        'users': users,
        'trx': trx,
    }
    return render(request, 'boss/with_trx.html', context)


@login_required(login_url='admin_login')
@allowed_users(allowed_roles=['admin'])
def inv_trx(request):
    trx = Transaction.objects.filter(transaction_type=3)[::-1]
    # client = Client.objects.get(user=trx.account.user)
    # user = User.objects.get(email=client.user.email)

    page = request.GET.get('page', 1)
    paginator = Paginator(trx, 10)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    context = {
        # 'client': client,
        'users': users,
        'trx': trx,
    }

    return render(request, 'boss/inv_trx.html', context)


@login_required(login_url='admin_login')
@allowed_users(allowed_roles=['admin'])
def dep_pen_trx(request):
    trx = Transaction.objects.filter(transaction_type=1, status='pending')[::-1]
    # client = Client.objects.get(user=trx.account.user)
    # user = User.objects.get(email=client.user.email)

    page = request.GET.get('page', 1)
    paginator = Paginator(trx, 10)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    context = {
        # 'client': client,
        'users': users,
        'trx': trx,
    }
    return render(request, 'boss/dep_pen_trx.html', context)


@login_required(login_url='admin_login')
@allowed_users(allowed_roles=['admin'])
def with_pen_trx(request):
    trx = Transaction.objects.filter(transaction_type=2, status='pending')[::-1]
    # client = Client.objects.get(user=trx.account.user)
    # user = User.objects.get(email=client.user.email)

    page = request.GET.get('page', 1)
    paginator = Paginator(trx, 10)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    context = {
        # 'client': client,
        'users': users,
        'trx': trx,
    }
    return render(request, 'boss/with_pen_trx.html', context)


@login_required(login_url='admin_login')
@allowed_users(allowed_roles=['admin'])
def dep_pro(request, id):
    company = CompanyProfile.objects.get(id=settings.COMPANY_ID)
    client = Transaction.objects.get(pk=id)
    if request.method == "POST":
        trx = Transaction.objects.filter(pk=id)
        amount = request.POST.get('amount_0')
        trx_id = request.POST.get('trx_id')

        method = client.payment_methods

        trx.update(status=request.POST.get('status'),
                   amount=request.POST.get('amount_0'), )
        cli = Account.objects.get(user=client.account.user)

        if request.POST.get('status') == 'Successful' and client.status != "Successful":
            cl = Account.objects.filter(user=client.account.user)
            new_amt = djmoney.money.Money(float(amount), 'USD')
            bal = new_amt + cli.main_balance
            amt_dep = cli.total_amount_deposited + new_amt
            cl.update(main_balance=bal, total_amount_deposited=amt_dep)
            email = client.account.user

            mail_subject = "Deposit Successful"

            to_email = str(email)

            message1 = render_to_string('boss/emaildep.html', {
                'amount': client.amount,
                'dep_date': timezone.now(),
                'company_address': company.company_address,
                'company_phone': company.company_phone,
                'company_email': company.company_support_email,
                'method': method,
                'name': client.account.user.username,

            })
            # message1 = message
            email = EmailMultiAlternatives(
                mail_subject, message1, to=[to_email]
            )
            email.attach_alternative(message1, 'text/html')
            email.content_subtype = 'html'
            email.mixed_subtype = 'related'

            email.send()

        messages.success(request, 'Deposit details have been saved successfully!')
        return redirect(f'/dep_pro/{id}')
    context = {
        'client': client,
    }
    return render(request, 'boss/dep_pro.html', context)


@login_required(login_url='admin_login')
@allowed_users(allowed_roles=['admin'])
def with_pro(request, id):
    company = CompanyProfile.objects.get(id=settings.COMPANY_ID)
    client = Transaction.objects.get(pk=id)
    if request.method == "POST":
        trx = Transaction.objects.filter(pk=id)
        amount = request.POST.get('amount_0')
        trx_id = request.POST.get('trx_id')

        method = client.payment_methods
        trx.update(status=request.POST.get('status'),
                   amount=request.POST.get('amount_0'),
                   hash_id=request.POST.get('hash_id'), )
        cli = Account.objects.get(user=client.account.user)

        if request.POST.get('status') == 'Successful' and client.status != "Successful":
            cl = Account.objects.filter(user=client.account.user)
            new_amt = djmoney.money.Money(float(amount), 'USD')
            bal = cli.main_balance - new_amt
            amt_with = cli.total_amount_withdrawn + new_amt
            cl.update(main_balance=bal, total_amount_withdrawn=amt_with)
            email = client.account.user

            mail_subject = "Withdrawal Successful"

            to_email = str(email)

            message1 = render_to_string('boss/emailwith.html', {
                'amount': client.amount,
                'with_date': timezone.now(),
                'method': method,
                'name': client.account.user.username,
                'company_address': company.company_address,
                'company_phone': company.company_phone,
                'company_email': company.company_support_email,

            })
            # message1 = message
            email = EmailMultiAlternatives(
                mail_subject, message1, to=[to_email]
            )
            email.attach_alternative(message1, 'text/html')
            email.content_subtype = 'html'
            email.mixed_subtype = 'related'

            email.send()

        messages.success(request, 'Withdrawal details have been saved successfully!')
        return redirect(f'/with_pro/{id}')
    context = {
        'client': client,
    }
    return render(request, 'boss/with_pro.html', context)


@login_required(login_url='admin_login')
@allowed_users(allowed_roles=['admin'])
def trx_add(request):
    if request.method == 'POST':
        if request.POST.get('transaction_type') == 1:
            usr = User.objects.get(email=request.POST.get('account'))
            acct = Account.objects.get(user=usr)
            trx = Transaction.objects.create(
                account=acct,
                transaction_type=1,
                amount=request.POST.get('amount_0'),
                status=request.POST.get('status'),
            )
            trx.save()
        elif request.POST.get('transaction_type') == 2:
            usr = User.objects.get(email=request.POST.get('account'))
            acct = Account.objects.get(user=usr)
            trx = Transaction.objects.create(
                account=acct,
                transaction_type=1,
                amount=request.POST.get('amount_0'),
                status=request.POST.get('status'),
            )
            trx.save()
    return render(request, 'boss/trx_add.html')


def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')
        valuenext = request.GET.get('next')

        user = authenticate(request, email=username, password=password)
        if user is not None:
            if user.is_staff == True:
                login(request, user)

                return redirect('/boss')

        else:
            messages.warning(request, 'Email or Password is incorrect. Note: Email is case-sensitive')

    context = {}
    return render(request, 'boss/admin_login.html')


@login_required(login_url='admin_login')
@allowed_users(allowed_roles=['admin'])
def admin_email_group(request):
    subject = request.POST.get('subject')

    message = request.POST.get('content')

    context = {
        'user_list': Client.objects.all(),

    }
    if request.method == 'POST':

        sender = Client.objects.all()

        for i in sender:
            email_message = request.POST.get('content')
            message = email_message

            email = EmailMultiAlternatives(
                subject, message, to=[i]
            )
            email.attach_alternative(message, 'text/html')
            email.content_subtype = 'html'
            email.mixed_subtype = 'related'

            email.send()

        messages.success(request, 'your email have been sent successfully to all Clients')
        return redirect('/admin_email_group')

    return render(request, "boss/admin_email_group.html", context)


@login_required(login_url='admin_login')
@allowed_users(allowed_roles=['admin'])
def admin_email(request):
    subject = request.POST.get('subject')
    file = request.FILES.get('pdf')
    users = request.POST.get('user_list')
    all_user = request.POST.get('all_user')
    message = request.POST.get('content')

    context = {
        'user_list': Client.objects.all(),

    }
    if request.method == 'POST':

        usr = User.objects.get(email=users)
        sender = Client.objects.get(user=usr)
        email_message = request.POST.get('content')
        message = email_message

        email = EmailMultiAlternatives(
            subject, message, to=[sender]
        )
        if file == None:
            email.attach_alternative(message, 'text/html')
            email.content_subtype = 'html'
            email.mixed_subtype = 'related'

            email.send()
        else:
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            fileurl = fs.url(filename)
            email.attach_file("static" + fileurl, )
            email.attach_alternative(message, 'text/html')
            email.content_subtype = 'html'
            email.mixed_subtype = 'related'

            email.send()

        messages.success(request, 'your email have been sent successfully')
        return redirect('/admin_email')

    return render(request, "boss/admin_email.html", context)


def admin_logout(request):
    logout(request)
    return redirect('/admin_login')


@login_required(login_url='admin_login')
def create_trx(request):
    if request.method == "POST":
        trx_type = request.POST.get('transaction_type')
        user = request.POST.get('email')
        amount = request.POST.get('amount_0', 'USD')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')
        hash_id = request.POST.get('hash_id')
        user_id = User.objects.get(email=user)
        account = Account.objects.get(user=user_id)
        # Create Transaction
        trx = Transaction.objects.create(
            account=account,
            amount=amount,
            payment_methods=AdminWallet.objects.get(wallet_name=payment_method),
            status=status,
            hash_id=hash_id,
            transaction_type=trx_type,
        )
        trx.save()
        if request.POST.get('status') == 'Successful' and trx_type == "1":
            cli = Account.objects.get(user=user_id)
            cl = Account.objects.filter(user=user_id)
            new_amt = djmoney.money.Money(float(amount), 'USD')
            bal = new_amt + cli.main_balance
            cl.update(main_balance=bal)
            email = user

            mail_subject = "Deposit Successful"

            to_email = str(email)

            message1 = render_to_string('boss/emaildep.html', {
                'amount': trx.amount,
                'dep_date': timezone.now().date,
                'trx_id': trx.trx_id,
                'method': payment_method,
                'name': account.user.username,

            })
            # message1 = message
            email = EmailMultiAlternatives(
                mail_subject, message1, to=[to_email]
            )
            email.attach_alternative(message1, 'text/html')
            email.content_subtype = 'html'
            email.mixed_subtype = 'related'

            email.send()
        if request.POST.get('status') == 'Successful' and trx_type == "2":
            cli = Account.objects.get(user=user_id)
            cl = Account.objects.filter(user=user_id)
            new_amt = djmoney.money.Money(float(amount), 'USD')
            bal = cli.main_balance - new_amt
            cl.update(main_balance=bal)
            email = user

            mail_subject = "Withdrawal Successful"

            to_email = str(email)

            message1 = render_to_string('boss/emailwith.html', {
                'amount': trx.amount,
                'with_date': timezone.now().date,
                'hash_id': hash_id,
                'method': payment_method,
                'name': account.user.username,

            })
            # message1 = message
            email = EmailMultiAlternatives(
                mail_subject, message1, to=[to_email]
            )
            email.attach_alternative(message1, 'text/html')
            email.content_subtype = 'html'
            email.mixed_subtype = 'related'

            email.send()
        if trx_type == '1':
            messages.success(request, 'Deposit transaction have been created successfully')
            return redirect('/dep_trx')
        elif trx_type == '2':
            messages.success(request, 'Withdrawal transaction have been created successfully')
            return redirect('/with_trx')
    trans = Transaction.objects.all()
    users = Account.objects.all()
    wallet = AdminWallet.objects.all()
    context = {
        'trans': trans,
        'users': users,
        'wallet': wallet,
    }

    return render(request, 'boss/create_trx.html', context)