from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login, logout as auth_logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm, PasswordResetForm
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
from django.urls import reverse

from .forms import RegistrationForm
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.forms import PasswordResetForm

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # deactivate until email confirmation
            user.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            send_activation_email(user, uid, token)

            messages.success(request, "Registration successful. Please check your email to activate your account.")
            return redirect('login')
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


def send_password_reset_email(user, domain, uid, token):
    subject = 'Reset Your Password'
    reset_url = f"http://{domain}/accounts/password-reset-confirm/{uid}/{token}/"

    context = {
        'user': user,
        'reset_url': reset_url,
        'site_name': settings.SITE_NAME,
    }

    html_content = render_to_string('emails/password_reset.html', context)
    text_content = f"Hello {user.username},\n\nPlease reset your password by clicking the link below:\n{reset_url}\n\nIf you did not request this, please ignore this email."

    email = EmailMultiAlternatives(subject, text_content, to=[user.email])
    email.attach_alternative(html_content, "text/html")
    email.send()


class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'emails/password_reset_email.txt'
    html_email_template_name = 'emails/password_reset.html'
    subject_template_name = 'emails/password_reset_subject.txt'

    def form_valid(self, form):
        email = form.cleaned_data['email']
        for user in PasswordResetForm().get_users(email):
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            current_site = get_current_site(self.request)
            protocol = 'https' if self.request.is_secure() else 'http'

            reset_url = self.request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )

            context = {
                'email': user.email,
                'domain': current_site.domain,
                'site_name': current_site.name,
                'uid': uid,
                'user': user,
                'token': token,
                'protocol': protocol,
                'reset_url': reset_url,
            }

            subject = render_to_string(self.subject_template_name, context).strip()
            text_body = render_to_string(self.email_template_name, context)
            html_body = render_to_string(self.html_email_template_name, context)

            email_message = EmailMultiAlternatives(subject, text_body, None, [user.email])
            email_message.attach_alternative(html_body, 'text/html')
            email_message.send()

        return super().form_valid(form)

    # Removed get_email_context method as PasswordResetView does not have this method.

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        context['reset_url'] = self.request.build_absolute_uri(
            context['protocol'] + "://" + context['domain'] +
            reverse('password_reset_confirm', kwargs={
                'uidb64': urlsafe_base64_encode(force_bytes(context['user'].pk)),
                'token': context['token']
            })
        )

        subject = render_to_string(subject_template_name, context).strip()
        body = render_to_string(email_template_name, context)
        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])

        if html_email_template_name:
            html_email = render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()
