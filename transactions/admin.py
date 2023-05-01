from django.contrib import admin

from transactions.models import *


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("account",'transaction_type', 'status', 'amount', 'timestamp')