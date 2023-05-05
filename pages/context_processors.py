from django.conf import settings

from pages.models import CompanyProfile

def company(request):
    return {'company': CompanyProfile.objects.get(id=settings.COMPANY_ID)}
