from django.conf.urls import url
from django.urls import path

from .views import *


app_name = 'transactions'


urlpatterns = [
    path('dashboard/', dashboard, name="dashboard"),
    path('new_investment/', investment, name="new_investment"),
    path('transfer_funds/', Transfer_funds.as_view(), name="transfer_fund"),
    path('convert_bonus/', Convert_bonusView.as_view(), name="convert_bonus"),
    path('customer_care/', customer_care, name="customer_care"),
    path('investment_preview/<str:investment_name>', investpreview.as_view(), name="investment_preview"),
    path('investment_log/', investment_log, name="investment_log"),
    path("inv_upgrade/<int:id>", Inv_upgrade.as_view(), name="inv_upgrade"),
    # path("upgrade_inv/", upgrade_inv, name="upgrade_inv"),
    path('referral_system/', rec_sys, name="referral_system"),
    path("deposit-fund/",  wallet1, name="deposit_money"),
    path("deposit/crypto/<int:id>", CryptoView.as_view(), name="crypto"),
    path("transactions/", transactions, name="transactions"),
    path("withdraw/", WithdrawMoneyView.as_view(), name="withdraw_money"),
    path("with_log/", with_log, name="with_log"),
    path('roi_withdrawal/', Convert_roiView.as_view(), name="convert_roi"),
    url(r'^api/data/$', get_data, name='api-data'),
]
