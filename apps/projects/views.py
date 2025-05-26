from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Project, Tag, ProjectImage ,Category, Report, Donation, Rating
from .forms import ProjectForm, ProjectImageFormSet, DonationForm, ReportForm
from django.utils.text import slugify
from django.contrib import messages
from apps.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.http import Http404, JsonResponse


@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        formset = ProjectImageFormSet(
            request.POST,
            request.FILES,
            queryset=ProjectImage.objects.none()
        )
        
        if form.is_valid() and formset.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            form.save_m2m()

            tags = [tag.strip() for tag in form.cleaned_data['tags'].split(',') if tag.strip()]
            for tag_name in tags:
                slug = slugify(tag_name)
                tag, created = Tag.objects.get_or_create(
                    slug=slug,
                    defaults={'name': tag_name}
                )
                project.tags.add(tag)

            images = formset.save(commit=False)
            for image in images:
                image.project = project
                image.save()

            return redirect('projects:project_detail', project.id)
        else:
            print("Form errors:", form.errors)
            print("Formset errors:", formset.errors)
    else:
        form = ProjectForm()
        formset = ProjectImageFormSet(queryset=ProjectImage.objects.none())

    return render(request, 'projects/project_form.html', {
        'form': form,
        'formset': formset
    })

@login_required
def project_update(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        formset = ProjectImageFormSet(
            request.POST,
            request.FILES,
            instance=project
        )
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('projects:project_detail', project_id=project.id)
        else:
            print("Form errors:", form.errors)
            print("Formset errors:", formset.errors)
    else:
        form = ProjectForm(instance=project, initial={
            'tags': ', '.join(t.name for t in project.tags.all())
        })
        formset = ProjectImageFormSet(instance=project)

    return render(request, 'projects/project_form.html', {
        'project': project,
        'form': form,
        'formset': formset
    })

@login_required
def project_delete(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    if request.method == 'POST':
        project.delete()
        return redirect('projects:project_list')
    return render(request, 'projects/project_confirm_delete.html', {'project': project})

@login_required
def project_cancel(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    
    if request.method == 'POST':
        if project.funding_percentage >= 25:
            messages.error(request, 
                "Cannot cancel project with 25% or more funding")
            return redirect('projects:project_detail', project.id)
            
        project.is_cancelled = True
        project.save()
        messages.success(request, "Project cancelled successfully")
        return redirect('projects:project_detail', project.id)
        
    return redirect('projects:project_list')

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if 'delete_id' in request.GET:
        comment = get_object_or_404(Comment, id=request.GET.get('delete_id'))
        if comment.user == request.user:
            comment.delete()
        return redirect('projects:project_detail', project.id)

    if 'report_id' in request.GET:
        comment = get_object_or_404(Comment, id=request.GET.get('report_id'))
        comment.is_reported = True
        comment.save()
        return redirect('projects:project_detail', project.id)

    if request.method == 'POST' and 'content' in request.POST:
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        parent = Comment.objects.filter(id=parent_id).first() if parent_id else None
        Comment.objects.create(
            user=request.user,
            project=project,
            parent=parent,
            content=content
        )
        return redirect('projects:project_detail', project.id)

    comments = Comment.objects.filter(project=project, parent=None).order_by('-created_at')

    has_reported_project = False
    if request.user.is_authenticated:
        content_type = ContentType.objects.get(app_label='projects', model='project')
        has_reported_project = Report.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=project.id
        ).exists()

    user_rating = 0
    if request.user.is_authenticated:
        user_rating_obj = Rating.objects.filter(project=project, user=request.user).first()
        user_rating = user_rating_obj.value if user_rating_obj else 0

    return render(request, 'projects/project_detail.html', {
        'project': project,
        'comments': comments,
        'has_reported_project': has_reported_project,
        'user_rating': user_rating,
    })

@login_required
def project_list(request):
    projects = Project.objects.all()
    return render(request, 'projects/project_list.html', {'projects': projects})



def projects_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    projects = Project.objects.filter(category=category)
    return render(request, 'projects/projects_by_category.html', {
        'category': category,
        'projects': projects
    })

@login_required
def donate_to_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.project = project
            if request.user.is_authenticated:
                donation.user = request.user
            donation.save()
            messages.success(request, "Thank you for your donation!")
            return redirect('projects:project_detail', project_id=project.id)
            # return redirect('project_detail', project_id=project.id)
    else:
        form = DonationForm()
    return render(request, 'projects/donate_form.html', {'form': form, 'project': project})


@login_required
def report_content(request, model_name, object_id):
    # Get app_label from the URL or as a parameter, or set it based on model_name
    # Example: /api/report/projects/project/10/ or /api/report/comments/comment/5/
    # If you want to keep your current URL, you can map model_name to app_label here:
    model_app_map = {
        'project': 'projects',
        'comment': 'comments',
        # add more if needed
    }
    app_label = model_app_map.get(model_name.lower())
    if not app_label:
        raise Http404("Unknown model for reporting.")

    try:
        content_type = ContentType.objects.get(app_label=app_label, model=model_name.lower())
    except ContentType.DoesNotExist:
        raise Http404("Content type not found.")
    model = content_type.model_class()
    content_object = get_object_or_404(model, pk=object_id)
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.content_object = content_object
            if request.user.is_authenticated:
                report.user = request.user
            report.save()
            messages.success(request, "Thank you for your report. Our team will review it soon.")
            # Redirect to the related project detail page
            if model_name == 'comment':
                return redirect('projects:project_detail', project_id=content_object.project.id)
            elif model_name == 'project':
                return redirect('projects:project_detail', project_id=content_object.id)
            else:
                return redirect('projects:project_list')
    else:
        form = ReportForm()
    return render(request, 'projects/report_form.html', {'form': form, 'content_object': content_object})

@login_required
def ajax_rate_project(request, project_id):
    if request.method == 'POST':
        value = int(request.POST.get('value'))
        project = get_object_or_404(Project, id=project_id)
        rating, created = Rating.objects.update_or_create(
            project=project, user=request.user,
            defaults={'value': value}
        )
        avg = project.average_rating
        review_count = project.ratings.count()  
        return JsonResponse({
            'success': True, 
            'average': avg, 
            'your_rating': value,
            'review_count': review_count  
        })
    return JsonResponse({'success': False}, status=400)