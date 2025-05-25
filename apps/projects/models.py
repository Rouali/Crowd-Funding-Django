from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone 
from django.db.models import Sum
from django.utils.text import slugify

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    def __str__(self):
        return self.name

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

    def can_cancel(self):
        return self.total_donations < 0.25 * self.total_target

    def __str__(self):
        return self.title

class Donation(models.Model):
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE,
        related_name='donations' 
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE ,related_name="images")
    image = models.ImageField(upload_to='projects/images/')

    def __str__(self):
        return f"Image for {self.project.title}"