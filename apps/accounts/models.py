from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

egypt_phone_regex = RegexValidator(
    regex=r'^01[0125][0-9]{8}$',
    message="Phone number must be valid Egyptian mobile number (11 digits starting with 010, 011, 012, or 015)."
)

class User(AbstractUser):
    email = models.EmailField(unique=True)
    mobile_phone = models.CharField(validators=[egypt_phone_regex], max_length=11, unique=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    # Extra optional fields
    birthdate = models.DateField(null=True, blank=True)
    facebook_profile = models.URLField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)

    REQUIRED_FIELDS = ['email', 'mobile_phone', 'first_name', 'last_name']

    def __str__(self):
        return str(self.username)
