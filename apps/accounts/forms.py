from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.contrib.auth import get_user_model

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
    

User = get_user_model()

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'mobile_phone',
                  'profile_picture', 'birthdate',
                  'facebook_profile', 'country']
        widgets = {
            'birthdate': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control form-control-lg'
            }),
            'facebook_profile': forms.URLInput(attrs={
                'class': 'form-control form-control-lg'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control form-control-lg'
            }),
        }