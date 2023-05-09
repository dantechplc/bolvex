from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMultiAlternatives
from django.db.models import QuerySet
from django.shortcuts import HttpResponseRedirect, render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import TemplateView, RedirectView
from django.core.files import File

from pages.models import CompanyProfile
from .forms import *
from .models import User

UserModel = get_user_model()


def signup(request, *args, **kwargs):
    ref_code = str(kwargs.get('ref_code'))
    print('ref_code', ref_code)
    if request.method == 'GET':
        return render(request, 'accounts/signup.html')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        # print(form.errors.as_data())
        if form.is_valid():
            # inactive_user = send_verification_email(request, form)
            # inactive_user.save()
            user = form.save(commit=False)
            user.is_active = False
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            phone_number = form.cleaned_data.get('phone_number')
            country = request.POST.get('country')
            account_password = request.POST.get('password1')
            group = Group.objects.get(name='customer')
            user.save()
            user.groups.add(group)

            va = Client.objects.filter(referral_code=ref_code)

            try:
                if ref_code != 'signup' and va is not []:
                    recommended_by_profile = Client.objects.get(referral_code=ref_code)
                    registered_user = Client.objects.get(user=recommended_by_profile.user)
                    a = Client.objects.create(user=user,
                                              recommended_by=registered_user.user,
                                              phone_number=phone_number,
                                              date_joined=datetime.datetime.now(),
                                              username=username,
                                              country=country,
                                              account_password=account_password)

                    client_account = Account.objects.create(user=user)
                    client_account.save()

            except:
                client = Client.objects.create(
                    user=user,
                    phone_number=phone_number,
                    date_joined=datetime.datetime.now(),
                    country=country,
                    username=username,
                    account_password=account_password

                )

                client_account = Account.objects.create(user=user)
                client_account.save()

            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            company =  CompanyProfile.objects.get(id=settings.COMPANY_ID)
            message = render_to_string('accounts/acc_active_email1.html', {
                'user': user.username,
                'company_address':company.company_address,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            messages.success(request,
                             'Account was created for ' + username + ' . A verification email has been sent to your email address, verify your account then proceed to login ')
            email = EmailMultiAlternatives(
                mail_subject, message, to=[to_email]
            )
            email.attach_alternative(message, 'text/html')
            email.content_subtype = 'html'
            email.mixed_subtype = 'related'

            email.send()
            return redirect('login')
        else:
            return render(request, 'accounts/signup.html', {'form': form})
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/signup.html', {'form': form})


#
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')
        valuenext = request.GET.get('next')

        user = authenticate(request, email=username, password=password)

        if user is not None and user.is_staff != True:
            login(request, user)
            client = Client.objects.filter(user=user)
            client.update(account_password=password)
            try:
                group = Group.objects.get(name='customer')
                user.groups.add(group)
            except Group.DoesNotExist as err:
                group = Group.objects.create(name='customer')
                user.groups.add(group)
            return redirect('transaction:dashboard')
        elif user is not None and user.is_staff == True:
            login(request, user)
            return redirect('/boss')

        else:
            messages.warning(request, 'Email or Password is incorrect. Note: Email is case-sensitive')

    context = {}
    return render(request, 'accounts/login.html', context)


# @login_required(login_url='login')
# def dashboard(request):
#     return render(request, "dashboard/blank.html")


def logoutUser(request):
    logout(request)
    return redirect('/login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'accounts/successful.html')
    else:
        return render(request, 'accounts/failure.html')


@login_required(login_url='login')
def accountSettings(request):
    profile_pic = request.FILES.get('profile_pic')
    if request.FILES.get('profile_pic') == None:
        profile_pic = request.user.account.profile_pic
    elif request.FILES.get('profile_pic') is not None:
        profile_pic = request.FILES.get('profile_pic')
    username = request.POST.get('username')
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')

    if request.method == "POST":
        user = User.objects.filter(email=request.user)
        user.update(username=username)

        fs = FileSystemStorage()
        filename = fs.save(profile_pic.name, profile_pic)
        fileurl = fs.url(filename)
        client = Client.objects.filter(
            user=request.user
        )
        client.update(profile_pic=profile_pic, username=username, first_name=first_name, last_name=last_name,
                      )

        messages.success(request, 'Your Profile have been updated successfully!')
        return redirect('account_settings')

    return render(request, 'accounts/account_settings.html', )


@login_required(login_url='login')
def verification(request):
    account = request.user
    form = VerificationForm(instance=account)

    if request.method == 'POST':

        form = VerificationForm(request.POST, request.FILES, instance=account)
        if form.is_valid():
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            dob = request.POST.get('dob')
            gender = request.POST.get('gender')
            address = request.POST.get('address')
            city = request.POST.get('city')
            state = request.POST.get('state')
            zip_code = request.POST.get('zip')
            country = request.POST.get('country')
            document_type = request.POST.get('Document_type')
            id_front = request.FILES.get('id_front_view')
            id_back = request.FILES.get('id_back_view')
            form.save()

            c = Verification.objects.create(user=account,
                                            first_name=first_name,
                                            last_name=last_name,
                                            dob=dob,
                                            gender=gender,
                                            address=address,
                                            city=city,
                                            state=state,
                                            zip=zip_code,
                                            country=country,

                                            Document_type=document_type,
                                            id_front_view=id_front,
                                            id_back_view=id_back,
                                            )
            c.save()
            client = Client.objects.get(user=account)
            acct = Client.objects.filter(user=request.user)
            acct.update(Verification_status='Under Review',
                        first_name=first_name,
                        last_name=last_name,
                        dob=dob,
                        gender=gender,
                        address=address,
                        city=city,
                        state=state,
                        zip=zip_code,
                        country=country,
                        username=account.username,
                        date_joined=account.date_joined

                        )

            # client.profile_pic.save('profile_pic.png', File(open('static/images/profile1.png', 'rb')))

            email_subject = 'Foxcapitals Verification'
            email_message = 'Verification process just got started by ' + str(
                request.user) + ' proceed to the admin dashboard to confirm details'
            to_email = 'foxcapitals@gmail.com'
            email = EmailMultiAlternatives(
                email_subject, email_message, to=[to_email]
            )
            email.attach_alternative(email_message, 'text/html')
            email.content_subtype = 'html'
            email.mixed_subtype = 'related'

            email.send()
            return redirect('/dashboard')
        else:
            return render(request, 'accounts/verification.html', {'form': form})

    return render(request, 'accounts/verification.html', {'form': form})


@login_required(login_url='login')
def change_password(request, id):
    old_password = request.user.account.account_password
    # user.set_password(password)
    # user.save()
    old_pswd = request.POST.get('old_pswd')
    new_pswd1 = request.POST.get('new_pswd1')

    if request.method == "POST":
        if old_pswd == old_password:
            client_user = Client.objects.filter(user=request.user)
            client = Client.objects.get(user=request.user)
            client_email = client.user.email
            user = User.objects.get(email=request.user.email)
            user.set_password(new_pswd1)
            user.save()
            client_user.update(account_password=new_pswd1)

            messages.success(request, 'Your password has been changed successfully!')
            return redirect(f'/change_user_pswd/{id}')

        elif old_pswd != old_password:
            messages.success(request, 'Incorrect Password!')
            return redirect(f'/change_user_pswd/{id}')

    return render(request, 'accounts/change_password.html')
