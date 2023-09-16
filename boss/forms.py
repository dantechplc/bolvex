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


class ClientUpdateForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ('first_name', 'last_name', 'username',  'gender', 'city', 'address', 'country', 'state', 'zip',
                  'Verification_status', 'phone_number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'form-control '

                )
            })

