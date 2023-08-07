from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError, EmailMultiAlternatives
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import *

# Create your views here.
from accounts.models import Client, Investment


def index_view(request, ):
    if request.method == 'POST':
        messages.success(request, 'your message have been submitted successfully')
        return redirect('/contact')
    plan = Investment.objects.all()
    context = {'plan': plan}
    return render(request, 'pages/index.html', context)


def about_view(request):
    return render(request, 'pages/about.html')


def investment_view(request):
    return render(request, 'pages/investment.html')


def faq_view(request):
    return render(request, 'pages/faq.html')


def contact(request):
    #form = ContactForm(request.POST)
    if request.method == 'POST':
        #email_subject = request.POST.get('subject')
        # sender = request.POST.get('email')
        # email_message = request.POST.get('message')
        # message = email_message + f" sender is {sender}"
        # email = 'bolvexcapital@gmail.com'

        # email = EmailMultiAlternatives(
        #     email_subject, message, to=[email]
        # )
        # email.attach_alternative(message, 'text/html')
        # email.content_subtype = 'html'
        # email.mixed_subtype = 'related'

        # email.send()

        messages.success(request, 'your message have been submitted successfully')
        return redirect('/contact')
    form = ContactForm()
    context = {'form': form}
    return render(request, 'pages/contact.html', context)

def privacy_view(request):
    return render(request, 'pages/privacy.html')


def t_c_view(request):
    return render(request, 'pages/t_c.html')


def legal_view(request):
    return render(request, 'pages/legal.html')


def investors_relation_view(request):
    return render(request, 'pages/investors_relation.html')

def kyc_view(request):
    return render(request, 'pages/kyc.html')

def services_view(request):
    return render(request, 'pages/services.html')

def BingSiteAuth(request):
    return render(request, 'BingSiteAuth.xml')
