from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from pages.models import *
from transactions.models import *


class StaticViewSitemap(Sitemap):
    def items(self):
        return ['pages:about', 'pages:services', 'pages:index', 'pages:contact', 'pages:services',
                'pages:investors_relation', 'pages:kyc', 'pages:t_c', 'pages:privacy',
                'pages:faq']

    def location(self, item):
        return reverse(item)
