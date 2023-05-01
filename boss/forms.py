from django.contrib.auth.forms import UserCreationForm

from accounts.models import Client, User
from django import forms


class UserRegistrationForm(UserCreationForm):
    phone_number = forms.CharField()


    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')

        if Client.objects.filter(phone_number=phone_number).exists() == True:
            raise forms.ValidationError(
                'Phone Number already exist'
            )

        return phone_number



