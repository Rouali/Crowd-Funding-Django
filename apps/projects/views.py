from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Project, Tag, ProjectImage ,Category
from .forms import ProjectForm, ProjectImageFormSet
from django.utils.text import slugify
from django.contrib import messages
from apps.comments.models import Comment

from django.shortcuts import render, get_object_or_404


from .models import ProjectReport
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
    
    # ✅ حذف تعليق (GET)
    if 'delete_id' in request.GET:
        comment = get_object_or_404(Comment, id=request.GET.get('delete_id'))
        if comment.user == request.user:
            comment.delete()
        return redirect('projects:project_detail', project.id)

    # ✅ تبليغ عن تعليق (GET)
    # if 'report_id' in request.GET:
    #     comment = get_object_or_404(Comment, id=request.GET.get('report_id'))
    #     comment.is_reported = True
    #     comment.save()
    # ✅ إضافة تعليق أو رد (POST)
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

    # ✅ تحميل التعليقات الأساسية (parent=None)
    comments = Comment.objects.filter(project=project, parent=None).order_by('-created_at')

    return render(request, 'projects/project_detail.html', {
        'project': project,
        'comments': comments  # 👈 تم تمرير التعليقات للـ template
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
def report_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        reason = request.POST.get('reason')
        if reason:
            ProjectReport.objects.create(
                reporter=request.user,
                project=project,
                reason=reason
            )
            messages.success(request, "Your report has been submitted.")
        else:
            messages.error(request, "Please provide a reason for reporting.")
        return redirect('projects:project_detail', project.id)

    return render(request, 'projects/report_project.html', {'project': project})