from dateutil.relativedelta import relativedelta
from django.utils import timezone
from accounts.models import *
from transactions.models import Transaction
import datetime
import djmoney
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def calculate_interest():
    transactions = Transaction.objects.filter(
        transaction_type=3,
        status='Active',
        expired=False,

    )
    this_month = timezone.now().month
    date = datetime.datetime.now()
    today_date = date.strftime("%x")

    created_transactions = []
    updated_accounts = []
    for transaction in transactions:
        active = transaction.status
        if active == "Active":
            if transaction.amount >= djmoney.money.Money(300, 'USD') and transaction.amount <= djmoney.money.Money(9999,
                                                                                                                   'USD'):
                interest = (transaction.amount * 2 / 100)
                transaction_obj = Transaction.objects.create(
                    account=transaction.account,
                    transaction_type=6,
                    amount=interest,
                    status='Successful'
                )
                client_acct = Account.objects.get(user=transaction.account.user)
                bal = client_acct.roi_balance
                new_bal = bal + interest
                total_roi_received = client_acct.total_roi_received + interest
                cl = Account.objects.filter(user=transaction.account.user)
                cl.update(roi_balance=new_bal, total_roi_received=total_roi_received)
                inv_pro = Investment_profile.objects.filter(user=transaction.account.user, trx_id=transaction.id)
                inv = Investment_profile.objects.get(trx_id=transaction.id)
                inv_amt = inv.amount_earned + interest
                inv_pro.update(amount_earned=inv_amt)

                email = transaction.account
                # message =
                mail_subject = "INVESTMENT INTEREST"

                to_email = str(email)

                message1 = render_to_string('boss/emailroi.html', {

                    'amount': interest,
                    'plan': 'STARTER',
                    'name': transaction.account.user.username,
                    'time': timezone.now()

                })
                # message1 = message
                email = EmailMultiAlternatives(
                    mail_subject, message1, to=[to_email]
                )
                email.attach_alternative(message1, 'text/html')
                email.content_subtype = 'html'
                email.mixed_subtype = 'related'
                print('Roi email sent successfully')
                email.send()
                # created_transactions.append(transaction_obj)
            if transaction.amount >= djmoney.money.Money(10000, 'USD') and transaction.amount <= djmoney.money.Money(
                    24999, 'USD'):
                interest = (transaction.amount * 3 / 100)
                transaction_obj = Transaction.objects.create(
                    account=transaction.account,
                    amount=interest,
                    status='Successful',
                    transaction_type=6
                )
                client_acct = Account.objects.get(user=transaction.account.user)
                bal = client_acct.roi_balance
                total_roi_received = client_acct.total_roi_received + interest
                new_bal = bal + interest
                cl = Account.objects.filter(user=transaction.account.user)
                cl.update(roi_balance=new_bal, total_roi_received=total_roi_received)
                inv_pro = Investment_profile.objects.filter(user=transaction.account.user, trx_id=transaction.id)
                inv = Investment_profile.objects.get(trx_id=transaction.id)
                inv_amt = inv.amount_earned + interest
                inv_pro.update(amount_earned=inv_amt)
                email = transaction.account
                # message =
                mail_subject = "INVESTMENT INTEREST"

                to_email = str(email)

                message1 = render_to_string('boss/emailroi.html', {

                    'amount': interest,
                    'plan': 'AMATEUR',
                    'name': transaction.account.user.username,
                    'time': timezone.now()

                })
                # message1 = message
                email = EmailMultiAlternatives(
                    mail_subject, message1, to=[to_email]
                )
                email.attach_alternative(message1, 'text/html')
                email.content_subtype = 'html'
                email.mixed_subtype = 'related'
                print('Roi email sent successfully')
                email.send()
                # created_transactions.append(transaction_obj)

        if transaction.amount >= djmoney.money.Money(25000, 'USD') and transaction.amount <= djmoney.money.Money(
                49999, 'USD'):
            interest = (transaction.amount * 4 / 100)
            transaction_obj = Transaction.objects.create(
                account=transaction.account,
                transaction_type=6,
                amount=interest,
                status='Successful'
            )
            client_acct = Account.objects.get(user=transaction.account.user)
            bal = client_acct.roi_balance
            new_bal = bal + interest
            total_roi_received = client_acct.total_roi_received + interest
            cl = Account.objects.filter(user=transaction.account.user)
            cl.update(roi_balance=new_bal, total_roi_received=total_roi_received)
            inv_pro = Investment_profile.objects.filter(user=transaction.account.user, trx_id=transaction.id)
            inv = Investment_profile.objects.get(trx_id=transaction.id)
            inv_amt = inv.amount_earned + interest
            inv_pro.update(amount_earned=inv_amt)
            email = transaction.account
            # message =
            mail_subject = "INVESTMENT INTEREST"

            to_email = str(email)

            message1 = render_to_string('boss/emailroi.html', {

                'amount': interest,
                'plan': 'PROFESSIONAL',
                'name': transaction.account.user.username,
                'time': timezone.now()

            })
            # message1 = message
            email = EmailMultiAlternatives(
                mail_subject, message1, to=[to_email]
            )
            email.attach_alternative(message1, 'text/html')
            email.content_subtype = 'html'
            email.mixed_subtype = 'related'
            print('Roi email sent successfully')
            email.send()
            # created_transactions.append(transaction_obj)
        if transaction.amount >= djmoney.money.Money(50000, 'USD') and transaction.amount <= djmoney.money.Money(
                99999, 'USD'):
            interest = (transaction.amount * 5 / 100)
            transaction_obj = Transaction.objects.create(
                account=transaction.account,
                transaction_type=6,
                amount=interest,
                status='Successful'
            )
            client_acct = Account.objects.get(user=transaction.account.user)
            bal = client_acct.roi_balance
            new_bal = bal + interest
            total_roi_received = client_acct.total_roi_received + interest
            cl = Account.objects.filter(user=transaction.account.user)
            cl.update(roi_balance=new_bal, total_roi_received=total_roi_received)
            inv_pro = Investment_profile.objects.filter(user=transaction.account.user, trx_id=transaction.id)
            inv = Investment_profile.objects.get(trx_id=transaction.id)
            inv_amt = inv.amount_earned + interest
            inv_pro.update(amount_earned=inv_amt)
            email = transaction.account
            # message =
            mail_subject = "INVESTMENT INTEREST"

            to_email = str(email)

            message1 = render_to_string('boss/emailroi.html', {

                'amount': interest,
                'plan': 'MASTER',
                'name': transaction.account.user.username,
                'time': timezone.now()

            })
            # message1 = message
            email = EmailMultiAlternatives(
                mail_subject, message1, to=[to_email]
            )
            email.attach_alternative(message1, 'text/html')
            email.content_subtype = 'html'
            email.mixed_subtype = 'related'
            print('Roi email sent successfully')
            email.send()
            # created_transactions.append(transaction_obj)
        if transaction.amount >= djmoney.money.Money(100000, 'USD') and transaction.amount <= djmoney.money.Money(
                500000, 'USD'):
            interest = (transaction.amount * 6 / 100)
            transaction_obj = Transaction.objects.create(
                account=transaction.account,
                transaction_type=6,
                amount=interest,
                status='Successful'
            )
            client_acct = Account.objects.get(user=transaction.account.user)
            bal = client_acct.roi_balance
            new_bal = bal + interest
            total_roi_received = client_acct.total_roi_received + interest
            cl = Account.objects.filter(user=transaction.account.user)
            cl.update(roi_balance=new_bal, total_roi_received=total_roi_received)
            inv_pro = Investment_profile.objects.filter(user=transaction.account.user, trx_id=transaction.id)
            inv = Investment_profile.objects.get(trx_id=transaction.id)
            inv_amt = inv.amount_earned + interest
            inv_pro.update(amount_earned=inv_amt)
            email = transaction.account
            # message =
            mail_subject = "INVESTMENT INTEREST"

            to_email = str(email)

            message1 = render_to_string('boss/emailroi.html', {

                'amount': interest,
                'plan': 'DIAMOND',
                'name': transaction.account.user.username,
                'time': timezone.now()

            })
            # message1 = message
            email = EmailMultiAlternatives(
                mail_subject, message1, to=[to_email]
            )
            email.attach_alternative(message1, 'text/html')
            email.content_subtype = 'html'
            email.mixed_subtype = 'related'
            print('Roi email sent successfully')
            email.send()
            # created_transactions.append(transaction_obj)

    # if created_transactions:
    # Transaction.objects.bulk_create(created_transactions)


def daily_roi():
    today = timezone.now()
    qs = Investment_profile.objects.filter(expired=False)
    investments = Investment_profile.objects.filter(status='Active')
    if investments is not None:
        for investment in investments:
            date = investment.next_payment
            if today == date:
                accounts = Investment_profile.objects.get(user=investment.user)
                interest = accounts.earning
                client_acct = Account.objects.get(user=investment.user)
                bal = client_acct.roi_balance
                new_bal = bal + interest
                total_roi_received = client_acct.total_roi_received + interest
                cl = Account.objects.filter(user=investment.user)
                cl.update(roi_balance=new_bal, total_roi_received=total_roi_received)

                # Investment Profile
                inv_pro = Investment_profile.objects.filter(status="Active", user=investment.user)
                inv_amt = accounts.amount_earned + interest
                next_payment = timezone.now() + relativedelta(days=1)
                inv_pro.update(amount_earned=inv_amt, next_payment=next_payment)

                # ROI email
                mail_subject = "INVESTMENT INTEREST"
                to_email = str(email)
                message1 = render_to_string('boss/emailroi.html', {

                    'amount': interest,
                    'plan': str(investment.investment),
                    'name': investment.user.username,
                    'time': timezone.now()

                })
                # message1 = message
                email = EmailMultiAlternatives(
                    mail_subject, message1, to=[to_email]
                )
                email.attach_alternative(message1, 'text/html')
                email.content_subtype = 'html'
                email.mixed_subtype = 'related'
                print('Roi email sent successfully')
                email.send()


def investment_expired_check():
    qs = Investment_profile.objects.filter(expired=False, status='Active')
    for doc in qs:
        expected_amount = doc.expected_roi
        amount_earned = doc.amount_earned
        if amount_earned > expected_amount:
            doc.expired = True
            doc.status = 'Expired'
            doc.save()
            # profile = Investment_profile.objects.filter(trx_id=doc.trx_id)
            # profile.update(status='Expired')
            print('Expired')
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
