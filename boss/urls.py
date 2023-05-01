from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = "boss"

urlpatterns = [
    path('boss/', views.admin_dashboard, name='boss'),
    path('client_add/', views.client_add, name="client_add"),
    path('client_delete/<id>/<uid>', views.client_delete, name="client_delete"),
    path('client_edit/<id>', views.client_edit, name="client_edit"),
    path('account_profile/<id>', views.account_profile, name="account_profile"),
    path('client_list/', views.client_list, name="client_list"),
    path('kyc_verified/', views.kyc_verified, name="kyc_verified"),
    path('kyc_profile_list/<id>', views.kyc_profile_list, name="kyc_profile_list"),
    path('kyc_profile/<id>', views.kyc_profile, name="kyc_profile"),
    path('kyc_profile_delete/<id>', views.kyc_profile_delete, name="kyc_profile_delete"),
    path('kyc_unverified/', views.kyc_unverified, name="kyc_unverified"),
    path('kyc_under_review/', views.kyc_under_review, name="kyc_under_review"),
    path('active_users/', views.active_clients, name="active_clients"),

    path('wallet_upload/', views.wallet_upload, name="wallet_upload"),
    path('wallet_add/', views.wallet_add, name="wallet_add"),
    path('wallet_edit/<id>', views.wallet_edit, name="wallet_edit"),
    path('wallet_delete/<id>', views.wallet_delete, name="wallet_delete"),
    path('change_user_password/<id>', views.change_user_password, name="change_user_password"),
    path('investment_profile_list/<id>', views.investment_profile_list, name="investment_profile_list"),
    path('investment_profile/<id>', views.investment_profile, name="investment_profile"),
    path('investment_profile_delete/<id>', views.investment_profile_delete, name="investment_profile_delete"),

    path('active_sub/', views.active_sub, name="active_sub"),
    path('dep_pen_trx/', views.dep_pen_trx, name="dep_pen_trx"),
    path('with_pen_trx/', views.with_pen_trx, name="with_pen_trx"),
    path('dep_trx/', views.dep_trx, name="dep_trx"),
    path('create_trx/', views.create_trx, name="create_trx"),
    path('dep_pro/<id>', views.dep_pro, name="dep_pro"),
    path('dep_trx_delete/<id>', views.dep_trx_delete, name="dep_trx_delete"),
    path('with_trx_delete/<id>', views.with_trx_delete, name="with_trx_delete"),
    path('inv_trx_delete/<id>', views.inv_trx_delete, name="inv_trx_delete"),
    path('with_pro/<id>', views.with_pro, name="with_pro"),
    path('inv_trx/', views.inv_trx, name="inv_trx"),
    path('trx_add/', views.trx_add, name="trx_add"),
    path('with_trx/', views.with_trx, name="with_trx"),
    path('admin_email/', views.admin_email, name="admin_email"),
    path('admin_email_group/', views.admin_email_group, name="admin_email_group"),

    path('admin_logout/', views.admin_logout, name="admin_logout"),


]

