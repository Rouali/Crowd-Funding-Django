from django.contrib import admin
from django.urls import path, include
from django.conf import settings              
from django.conf.urls.static import static   
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to the crowdfunding home page!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('api/', include('apps.projects.urls')),
    path('projects/', include('apps.projects.urls', namespace='projects')),
    path('home/', include('apps.home.urls')),
    path('', include('apps.accounts.urls')),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)


