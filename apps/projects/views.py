from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Project, Tag, ProjectImage
from .forms import ProjectForm, ProjectImageFormSet
from django.utils.text import slugify
from django.contrib import messages

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
    return render(request, 'projects/project_detail.html', {'project': project})  

@login_required
def project_list(request):
    projects = Project.objects.all()
    return render(request, 'projects/project_list.html', {'projects': projects})