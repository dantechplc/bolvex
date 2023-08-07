from django.urls import path
from . import views

app_name = "pages"

urlpatterns = [
    path('', views.index_view, name="index"),

    path('index/', views.index_view, name="index"),
    
    path('about/', views.about_view, name='about'),
    path('faq/', views.faq_view, name='faq'),
    path('legal/', views.legal_view, name='legal'),
    path('investors_relation/', views.investors_relation_view, name='investors_relation'),
    path('kyc/', views.kyc_view, name='kyc'),
    path('t_c/', views.t_c_view, name='t_c'),
    path('services/', views.services_view, name='services'),
    path('contact/', views.contact, name='contact'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('BingSiteAuth.xml/', views.BingSiteAuth, name='Bing'),
    # path('services/', views.services_view, name='services'),
]