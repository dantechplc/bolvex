from django.core.mail import EmailMultiAlternatives


class EmailSender:

    def __init__(self):
        pass
    def kyc_email_sender(*args, **kwargs):
        email_subject = 'KYC Verification'
        email_message = 'Verification process just got started by ' + str(kwargs.get('user')) + \
                        ' proceed to the admin dashboard to confirm details'
        to_email = 'bolvexcapital@gmail.com'
        email = EmailMultiAlternatives(
            email_subject, email_message, to=[to_email]
        )
        email.attach_alternative(email_message, 'text/html')
        email.content_subtype = 'html'
        email.mixed_subtype = 'related'

        email.send()
