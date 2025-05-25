# from django.shortcuts import render
# from .models import Project, Category
# from django.http import HttpResponse

# def home_view(request):
#     top_rated = Project.objects.filter(is_running=True).order_by('-rating')[:5]
#     latest = Project.objects.order_by('-created_at')[:5]
#     featured = Project.objects.filter(is_featured=True).order_by('-created_at')[:5]
#     categories = Category.objects.all()

#     return render(request, 'home/index.html', {
#         'top_rated': top_rated,
#         'latest': latest,
#         'featured': featured,
#         'categories': categories
#     })



from django.shortcuts import render
# from .models import Project, Category
from django.http import HttpResponse
from django.db.models import Q
from django.utils import timezone
from apps.projects.models import Tag, Project , Category
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404

def index(request):
    return HttpResponse("Hello, this is the homepage.")


def home_view(request):
    now = timezone.now()
    top_rated = Project.objects.filter(is_cancelled=False, start_time__lte=now, end_time__gte=now)\
                               .annotate(total_rating=Sum('donations__amount'))\
                               .order_by('-total_rating')[:5]

    latest = Project.objects.order_by('-created_at')[:5]

    featured = Project.objects.filter(is_cancelled=False).order_by('?')[:5]

    categories = Category.objects.all()

    return render(request, 'home/index.html', {
        'top_rated': top_rated,
        'latest': latest,
        'featured': featured,
        'categories': categories
    })


def search_projects(request):
    query = request.GET.get('query', '')
    now = timezone.now()

    results = Project.objects.filter(
        Q(title__icontains=query) |
        Q(details__icontains=query) |
        Q(tags__name__icontains=query),
        is_cancelled=False
    ).distinct()

    return render(request, 'home/search_results.html', {
        'projects': results,
        'query': query
    })


def all_projects(request):
    projects = Project.objects.filter(is_cancelled=False)
    return render(request, 'home/all_projects.html', {
        'projects': projects
    })



