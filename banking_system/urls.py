from django.contrib import admin
from django.urls import include, path
from pages.sitemaps import *
from django.contrib.sitemaps.views import sitemap

from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

# from .views import UserRegistrationView, LogoutView, UserLoginView
from django.contrib import admin
from pages.urls import *

sitemaps = {

    'static': StaticViewSitemap
}

urlpatterns = [
    path('secure/', admin.site.urls),
    path('', include('accounts.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),
    path('BingSiteAuth.xml', views.BingSiteAuth, name='Bing'),
    path('', include('pages.urls', namespace='pages')),
    path('', include('boss.urls', namespace='boss')),
    path('account/', include('transactions.urls', namespace='transaction')),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_URL)

handler404 = 'transactions.views.error_404_view'
handler500 = 'transactions.views.error_500_view'
admin.site.index_title = "Bolvex Capital Admin"
admin.site.site_header = "BOLVEX CAPITAL"
