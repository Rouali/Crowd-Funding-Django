from django.urls import path
from . import views
from .views import CustomPasswordResetView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('login/', views.login_view, name='login'),
    path('', views.login_view),
    path('logout/', views.logout_view, name='logout'),
    path('delete/', views.delete_account, name='delete_account'),

    # Password reset flow with your custom password reset view

    path('password-reset/', CustomPasswordResetView.as_view(
        template_name='accounts/password_reset.html'
    ), name='password_reset'),


    path('password-reset-done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),

    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
]
