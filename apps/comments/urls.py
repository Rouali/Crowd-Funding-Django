from django.urls import path
from . import views

app_name = "comments"

urlpatterns = [
    path('report/<int:comment_id>/', views.report_comment, name='report_comment'),
    # باقي المسارات
]
