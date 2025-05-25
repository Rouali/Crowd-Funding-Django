from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('', views.home_view, name='home'),
    path('search/', views.search_projects, name='search_projects'),
    path('projects/', views.all_projects, name='all_projects'),
    # path('', views.index, name='index'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


