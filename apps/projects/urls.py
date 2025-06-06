from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'projects' 

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('create/', views.project_create, name='project_create'),
    path('<int:project_id>/edit/', views.project_update, name='project_update'),
    path('<int:project_id>/delete/', views.project_delete, name='project_delete'),
    path('<int:project_id>/cancel/', views.project_cancel, name='project_cancel'),
    path('<int:project_id>/', views.project_detail, name='project_detail'),
    path('category/<int:category_id>/', views.projects_by_category, name='projects_by_category'),
    path('donate/<int:project_id>/', views.donate_to_project, name='donate_to_project'),
    path('report/<str:model_name>/<int:object_id>/', views.report_content, name='report_content'),
    path('<int:project_id>/ajax-rate/', views.ajax_rate_project, name='ajax_rate_project'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
