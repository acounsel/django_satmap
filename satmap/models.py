from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField

class Layer(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    band = models.CharField(max_length=255)
    min = models.DecimalField(max_digits=10,
        decimal_places=3, blank=True, null=True)
    max = models.DecimalField(max_digits=10,
        decimal_places=3, blank=True, null=True)
    opacity = models.DecimalField(max_digits=3, decimal_places=2, default=0.5, validators=[
            MinValueValidator(0),
            MaxValueValidator(1)])
    #palette = ArrayField(models.CharField(max_length=255), default=['blue', 'purple', 'cyan', 'green', 'yellow', 'red'])
    palette = models.TextField(default = "'blue', 'purple', 'cyan', 'green', 'yellow', 'red'")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def get_palette_list(self):
        palette = self.palette.split(', ')
        palettelist = []
        for color in palette:
            palettelist.append(color[1:-1])
        return palettelist

class Project(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    datasets = models.ManyToManyField(Layer, blank=True)

    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'pk':self.id})

class Map(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, 
        blank=True, null=True)
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    zoom = models.IntegerField(default=8)
    layer = models.ManyToManyField(Layer, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['title']
    
    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        if self.project:
            return self.title + ' (' + self.project.name + ')'
        else:
            return self.title
    
    def duplicate(self, project):
        map = Map.objects.create(
            project = project,
            title = self.title,
            description = self.description,
            latitude = self.latitude,
            longitude = self.longitude,
            zoom = self.zoom,
            start_date = self.start_date,
            end_date = self.end_date,
            published_date = self.published_date
        )
        map.layer.set(self.layer.all())
