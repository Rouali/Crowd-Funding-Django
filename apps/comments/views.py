# apps/comments/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Comment, CommentReport
from django.contrib import messages

@login_required
def report_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.method == 'POST':
        reason = request.POST.get('reason')
        if reason:
            CommentReport.objects.create(
                reporter=request.user,
                comment=comment,
                reason=reason
            )
            messages.success(request, "Your report has been submitted.")
            return redirect('projects:project_detail', project_id=comment.project.id)
        else:
            messages.error(request, "Please provide a reason for reporting.")

    return render(request, 'comments/report_comment.html', {'comment': comment})
