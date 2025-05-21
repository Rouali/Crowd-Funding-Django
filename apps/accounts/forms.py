from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    mobile_phone = forms.CharField(max_length=11)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'mobile_phone', 'password1', 'password2', 'profile_picture')

    def clean_mobile_phone(self):
        phone = self.cleaned_data.get('mobile_phone')
        # RegexValidator in model should handle validation but you can add extra checks here if needed
        return phone
