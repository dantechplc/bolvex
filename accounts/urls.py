from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path
from boss.views import *
from django.contrib.auth import views as auth_views

from . import views



urlpatterns = [
    path('signup/<str:ref_code>', views.signup, name="signup"),
    path('signup/', views.signup, name="signup"),

    path('login/', views.loginPage, name='login'),
    # path('login/', views.loginPage, name="login"),
    #     path('login/', LoginView.as_view(template_name='accounts/login.html'), name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('account_settings/', views.accountSettings, name="account_settings"),
    path('verification/', views.verification, name="verification"),
    path('change_user_pswd/<id>', views.change_password, name="change_password"),
    path('activate/<uidb64>/<token>/',views.activate, name='activate'),


    path('admin_login/', admin_login, name="admin_login"),

    # path('account/', views.accountSettings, name="account"),
    #
    path('reset_password/',
         auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html"),
         name="reset_password"),
    #
    path('reset_password_sent/',
         auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_sent.html"),
         name="password_reset_done"),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_form.html"),
         name="password_reset_confirm"),

    path('reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_done.html"),
         name="password_reset_complete"),

]

'''
1 - Submit email form                         //PasswordResetView.as_view()
2 - Email sent success message                //PasswordResetDoneView.as_view()
3 - Link to password Rest form in email       //PasswordResetConfirmView.as_view()
4 - Password successfully changed message     //PasswordResetCompleteView.as_view()
'''