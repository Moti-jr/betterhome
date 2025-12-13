# models.py
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from PIL import Image

from testbh import settings


class ProjectCategory(models.Model):
    """Categories for projects like Education, Healthcare, Environment, etc."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Bootstrap icon class (e.g., 'bi-book')")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Project Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Project(models.Model):
    """Main project model for BHI initiatives"""

    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
    ]

    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    category = models.ForeignKey(
        'ProjectCategory',
        on_delete=models.SET_NULL,
        null=True,
        related_name='projects'
    )

    # Descriptions
    short_description = models.TextField(
        max_length=250,
        help_text="Brief description shown in project cards (max 250 characters)"
    )
    full_description = models.TextField(
        help_text="Detailed description of the project"
    )

    # Images
    image = models.ImageField(
        upload_to='projects/%Y/%m/',
        help_text="Main project image (recommended: 800x600px)"
    )

    # Project Details
    location = models.CharField(max_length=200, help_text="Project location/region")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    # Impact Metrics
    beneficiaries = models.PositiveIntegerField(
        default=0,
        help_text="Number of people impacted"
    )
    budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Project budget in USD"
    )
    funds_raised = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Amount raised so far"
    )

    # Display Options
    is_featured = models.BooleanField(
        default=False,
        help_text="Display on homepage"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Show on website"
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        ordering = ['-is_featured', 'display_order', '-created_at']
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Auto-generate slug from title
        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'slug': self.slug})

    @property
    def funding_percentage(self):
        """Calculate percentage of funding goal reached"""
        if self.budget and self.budget > 0:
            return min(int((self.funds_raised / self.budget) * 100), 100)
        return 0

    @property
    def is_completed(self):
        return self.status == 'completed'

    @property
    def is_ongoing(self):
        return self.status == 'ongoing'

    def increment_views(self):
        """Increment view count"""
        self.views += 1
        self.save(update_fields=['views'])


class ProjectImage(models.Model):
    """Additional images for project gallery"""
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='gallery_images'
    )
    image = models.ImageField(upload_to='projects/gallery/%Y/%m/')
    caption = models.CharField(max_length=200, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', '-uploaded_at']

    def __str__(self):
        return f"{self.project.title} - Image {self.id}"


class ProjectUpdate(models.Model):
    """Progress updates for projects"""
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='updates'
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(
        upload_to='projects/updates/%Y/%m/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_milestone = models.BooleanField(
        default=False,
        help_text="Mark as major milestone"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Project Update"
        verbose_name_plural = "Project Updates"

    def __str__(self):
        return f"{self.project.title} - {self.title}"


class ProjectPartner(models.Model):
    """Partners/sponsors for projects"""
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='partners/')
    website = models.URLField(blank=True)
    projects = models.ManyToManyField(Project, related_name='partners', blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


from django.db import models

# Create your models here.
