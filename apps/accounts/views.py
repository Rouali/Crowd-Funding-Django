from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login, logout as auth_logout
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_protect
from django.conf import settings

from .forms import RegistrationForm

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # deactivate account until email confirmed
            user.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            send_activation_email(user, uid, token)

            messages.success(request, "Registration successful. Please check your email to activate your account.")
            return redirect('accounts/login.html')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, ObjectDoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated. You can now log in.')
        return redirect('login')
    else:
        return render(request, 'accounts/activation_invalid.html')


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    auth_logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')


@csrf_protect
def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            email = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(email=email)
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "accounts/password_reset_email.html"
                    context = {
                        "email": user.email,
                        "domain": get_current_site(request).domain,
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "token": default_token_generator.make_token(user),
                    }
                    email_message = render_to_string(email_template_name, context)
                    EmailMessage(subject, email_message, to=[user.email]).send()
                messages.success(request, "Check your email to reset your password.")
                return redirect('login')
    else:
        password_reset_form = PasswordResetForm()
    return render(request, "accounts/password_reset.html", {"form": password_reset_form})


@csrf_protect
def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, ObjectDoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been reset. You can now log in.")
                return redirect('login')
        else:
            form = SetPasswordForm(user)
        return render(request, 'accounts/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'Invalid reset link.')
        return redirect('password_reset')


def delete_account(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            request.user.delete()
            messages.success(request, "Your account has been deleted.")
            return redirect('register')
        return render(request, 'accounts/delete_account.html')
    else:
        messages.error(request, "You must be logged in to delete your account.")
        return redirect('login')


def send_activation_email(user, uid, token):
    subject = 'Activate Your Account'
    from_email = settings.EMAIL_HOST_USER
    to_email = user.email

    activation_url = f"http://{settings.DOMAIN}/accounts/activate/{uid}/{token}/"
    
    context = {
        'user': user,
        'activation_url': activation_url,
        'site_name': settings.SITE_NAME,
    }

    html_content = render_to_string('emails/activation_email.html', context)
    text_content = f'Hi {user.username}, activate your account using this link: {activation_url}'

    email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    email.attach_alternative(html_content, "text/html")
    email.send()
