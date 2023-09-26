from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from pages.models import CompanyProfile


class EmailSender:
    """"This class is used to send emails"""

    def kyc_verified(*agrs, **kwargs):
        company = CompanyProfile.objects.get(id=settings.COMPANY_ID)
        email = kwargs.get('email')
        name = kwargs.get('name')
        mail_subject = "VERIFICATION SUCCESSFUL"
        to_email = str(email)
        message1 = render_to_string('boss/verifyemail.html', {
            'name': name,
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