from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.utils import timezone
from accounts.models import *
from pages.models import CompanyProfile
from transactions.models import Transaction
import datetime
import djmoney
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def daily_roi():
    today = timezone.now()
    investments = Investment_profile.objects.filter(status='Active')
    if investments is not None:
        for investment in investments:
            date = investment.next_payout
            if date <= today:
                accounts = Investment_profile.objects.filter(user=investment.user, status='Active')
                for account in accounts:
                    interest = account.earning
                    client_acct = Account.objects.get(user=investment.user)
                    bal = client_acct.roi_balance
                    new_bal = bal + interest
                    total_roi_received = client_acct.total_roi_received + interest
                    cl = Account.objects.filter(user=investment.user)
                    cl.update(roi_balance=new_bal, total_roi_received=total_roi_received)

                    # Investment Profile
                    inv_pro = Investment_profile.objects.filter(status="Active", user=investment.user)
                    inv_amt = account.amount_earned + interest
                    next_payment = timezone.now() + relativedelta(days=1)
                    inv_pro.update(amount_earned=inv_amt, next_payout=next_payment)

                    # ROI email
                    mail_subject = "INVESTMENT INTEREST"
                    to_email = str(investment.user)
                    company = CompanyProfile.objects.get(id=settings.COMPANY_ID)
                    message = render_to_string('boss/emailroi.html', {

                        'amount': interest,
                        'plan': str(investment.investment),
                        'name': investment.user.username,
                        'time': timezone.now(),
                        'company_address': company.company_address,
                        'company_phone': company.company_phone,
                        'company_email': company.company_support_email,

                    })
                    # message1 = message
                    email = EmailMultiAlternatives(
                        mail_subject, message, to=[to_email]
                    )
                    email.attach_alternative(message, 'text/html')
                    email.content_subtype = 'html'
                    email.mixed_subtype = 'related'
                    print('Roi email sent successfully')
                    email.send()


def investment_expired_check():
    qs = Investment_profile.objects.filter(expired=False, status='Active')
    for doc in qs:
        expected_amount = doc.expected_roi
        amount_earned = doc.amount_earned
        if amount_earned >= expected_amount:
            doc.expired = True
            doc.status = 'Expired'
            doc.save()
            print('Expired investment found for ', doc.user)
            trx = Transaction.objects.filter(pk=doc.trx_id)
            trx.update(status='Expired')
            email = 'bolvexcapital@gmail.com'
            # message =
            mail_subject = "Expired Investment"
            to_email = str(email)
            message1 = f'Hello Admin. {doc.user} {doc.investment} Investment plan of {doc.amount_invested} expired ' \
                       f'today. '
            email = EmailMultiAlternatives(
                mail_subject, message1, to=[to_email]
            )
            email.attach_alternative(message1, 'text/html')
            email.content_subtype = 'html'
            email.mixed_subtype = 'related'
            email.send()
