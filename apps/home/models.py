from django.db import models

# class Category(models.Model):
#     name = models.CharField(max_length=100)

# class Project(models.Model):
#     title = models.CharField(max_length=200)
#     description = models.TextField()
#     image = models.ImageField(upload_to='projects/')
#     rating = models.FloatField(default=0)
#     is_featured = models.BooleanField(default=False)
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#     deadline = models.DateField()
#     is_running = models.BooleanField(default=True)  

#     def __str__(self):
#         return self.title

# class Tag(models.Model):
#     name = models.CharField(max_length=100)
#     project = models.ForeignKey(Project, related_name='tags', on_delete=models.CASCADE)
