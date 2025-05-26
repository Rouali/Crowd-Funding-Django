from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone 
from django.db.models import Sum
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    def __str__(self):
        return str(self.name)

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name

class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    details = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    total_target = models.DecimalField(max_digits=15, decimal_places=2)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    tags = models.ManyToManyField(Tag)
    is_cancelled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def status(self):
        now = timezone.now()
        if now < self.start_time:
            return "upcoming"
        elif now <= self.end_time:
            return "active"
        else:
            return "expired"

    @property
    def funding_percentage(self):
        if self.total_target == 0:
            return 0
        return (self.total_donations / self.total_target) * 100

    @property
    def total_donations(self):
        return self.donations.aggregate(total=models.Sum('amount'))['total'] or 0
    
    @property
    def average_rating(self):
        avg = self.ratings.aggregate(models.Avg('value'))['value__avg']
        return round(avg, 1) if avg else 0

    def can_cancel(self):
        return self.total_donations < 0.25 * self.total_target

    def __str__(self):
        return str(self.title)

class Donation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    project = models.ForeignKey(Project, related_name='donations', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    donated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} donated {self.amount} to {self.project.title}"


class Report(models.Model):
    REPORT_CHOICES = [
        ('spam', 'Spam or Scam'),
        ('offensive', 'Offensive Content'),
        ('other', 'Other'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    reason = models.CharField(max_length=50, choices=REPORT_CHOICES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Report by {self.user} on {self.content_object} ({self.reason})"        
    
class Rating(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'user')
    
class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE ,related_name="images")
    image = models.ImageField(upload_to='projects/images/')

    def __str__(self):
        return f"Image for {self.project.title}"