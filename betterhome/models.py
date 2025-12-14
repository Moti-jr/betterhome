# models.py
import os
from datetime import datetime

from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from PIL import Image
from django.contrib.auth import get_user_model
User = get_user_model()

from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from PIL import Image
import os
import uuid
from datetime import date, datetime


# def team_photo_path(instance, filename):
#     """Generate readable unique filename"""
#     # Get file extension
#     ext = filename.split('.')[-1].lower()
#
#     # Sanitize member name
#     name_slug = slugify(instance.name) if instance.name else 'member'
#
#     # Add short UUID for uniqueness
#     unique_id = uuid.uuid4().hex[:8]
#
#     # Result: team/2024/john-doe-a1b2c3d4.jpg
#     unique_filename = f"{name_slug}-{unique_id}.{ext}"
#
#     year = datetime.now().year
#     return os.path.join('team', str(year), unique_filename)



def team_photo_path(instance, filename):
    """Generate unique filename for team member photos"""
    ext = filename.split('.')[-1]
    name_slug = slugify(instance.name) if instance.name else 'member'
    unique_id = uuid.uuid4().hex[:8]
    unique_filename = f"{name_slug}-{unique_id}.{ext}"
    return os.path.join('team', str(instance.created_at.year if instance.pk else 2024), unique_filename)


class TeamMember(models.Model):
    """Team members and staff"""

    ROLE_CHOICES = [
        ('founder', 'Founder'),
        ('director', 'Director'),
        ('manager', 'Manager'),
        ('coordinator', 'Coordinator'),
        ('volunteer', 'Volunteer Coordinator'),
        ('officer', 'Program Officer'),
        ('admin', 'Administrator'),
        ('advisor', 'Advisor'),
        ('board', 'Board Member'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]

    # Basic Information
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    role = models.CharField(max_length=100)
    role_category = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='volunteer',
        help_text="Select role category"
    )

    # Personal Information
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text="Required for age verification"
    )
    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        blank=True
    )

    # National ID (for 18+ years only)
    national_id = models.CharField(
        max_length=20,
        blank=True,
        unique=True,
        null=True,
        validators=[MinLengthValidator(5)],
        help_text="Required for members 18 years and above. Must be unique."
    )
    national_id_verified = models.BooleanField(
        default=False,
        help_text="Check if national ID has been verified"
    )

    # Photo with unique naming
    photo = models.ImageField(
        upload_to=team_photo_path,
        help_text="Recommended: Square image (500x500px)"
    )

    # Bio and Contact
    bio = models.TextField(
        blank=True,
        help_text="Brief biography or description"
    )
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True, help_text="Physical address")

    # Social Media Links
    linkedin = models.URLField(blank=True, verbose_name="LinkedIn URL")
    twitter = models.URLField(blank=True, verbose_name="Twitter URL")
    facebook = models.URLField(blank=True, verbose_name="Facebook URL")
    instagram = models.URLField(blank=True, verbose_name="Instagram URL")

    # Display Options
    is_active = models.BooleanField(
        default=True,
        help_text="Show on website"
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first"
    )
    show_on_homepage = models.BooleanField(
        default=False,
        help_text="Display on homepage team section"
    )

    # Metadata
    joined_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"

    def __str__(self):
        return f"{self.name} - {self.role}"

    def clean(self):
        """Validate that members 18+ have national ID"""
        super().clean()

        # Check if member is 18 or above
        if self.date_of_birth:
            age = self.calculate_age()

            if age >= 18:
                if not self.national_id:
                    raise ValidationError({
                        'national_id': 'National ID is required for members 18 years and above.'
                    })

                # Validate national ID format (customize based on your country)
                if len(self.national_id) < 5:
                    raise ValidationError({
                        'national_id': 'National ID must be at least 5 characters long.'
                    })

            if age < 18 and self.national_id:
                raise ValidationError({
                    'national_id': 'National ID should not be provided for members under 18 years.'
                })

    def save(self, *args, **kwargs):
        # Auto-generate slug
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while TeamMember.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # Normalize national_id to None if empty
        if self.national_id == '':
            self.national_id = None

        # Delete old photo if updating with new photo
        if self.pk:
            try:
                old_instance = TeamMember.objects.get(pk=self.pk)
                if old_instance.photo and old_instance.photo != self.photo:
                    if os.path.isfile(old_instance.photo.path):
                        os.remove(old_instance.photo.path)
            except TeamMember.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # Optimize photo after saving
        if self.photo:
            self.optimize_photo()

    def delete(self, *args, **kwargs):
        """Delete photo file when deleting team member"""
        if self.photo:
            if os.path.isfile(self.photo.path):
                os.remove(self.photo.path)
        super().delete(*args, **kwargs)

    def calculate_age(self):
        """Calculate age from date of birth"""
        if not self.date_of_birth:
            return None

        today = date.today()
        age = today.year - self.date_of_birth.year

        # Adjust if birthday hasn't occurred this year
        if today.month < self.date_of_birth.month or \
                (today.month == self.date_of_birth.month and today.day < self.date_of_birth.day):
            age -= 1

        return age

    @property
    def age(self):
        """Property to get age"""
        return self.calculate_age()

    @property
    def is_adult(self):
        """Check if member is 18 or above"""
        age = self.calculate_age()
        return age >= 18 if age is not None else None

    @property
    def requires_national_id(self):
        """Check if member requires national ID"""
        return self.is_adult

    @property
    def national_id_status(self):
        """Get national ID status"""
        if not self.requires_national_id:
            return "Not Required"
        if not self.national_id:
            return "Missing"
        if self.national_id_verified:
            return "Verified"
        return "Unverified"

    def optimize_photo(self):
        """Optimize and resize photo to square format"""
        try:
            img = Image.open(self.photo.path)

            if img.mode != 'RGB':
                img = img.convert('RGB')

            output_size = (500, 500)
            width, height = img.size
            min_dimension = min(width, height)

            left = (width - min_dimension) / 2
            top = (height - min_dimension) / 2
            right = (width + min_dimension) / 2
            bottom = (height + min_dimension) / 2

            img = img.crop((left, top, right, bottom))
            img.thumbnail(output_size, Image.Resampling.LANCZOS)
            img.save(self.photo.path, quality=85, optimize=True)

        except Exception as e:
            print(f"Error optimizing photo: {e}")

    @property
    def has_social_links(self):
        """Check if member has any social media links"""
        return any([self.linkedin, self.twitter, self.facebook, self.instagram])

    @property
    def social_links(self):
        """Return dictionary of available social links"""
        links = {}
        if self.linkedin:
            links['linkedin'] = self.linkedin
        if self.twitter:
            links['twitter'] = self.twitter
        if self.facebook:
            links['facebook'] = self.facebook
        if self.instagram:
            links['instagram'] = self.instagram
        return links


class TeamDepartment(models.Model):
    """Departments or teams within the organization"""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Bootstrap icon class (e.g., 'bi-people')"
    )
    members = models.ManyToManyField(
        TeamMember,
        related_name='departments',
        blank=True
    )
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = "Team Department"
        verbose_name_plural = "Team Departments"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def member_count(self):
        return self.members.filter(is_active=True).count()


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


class Blog(models.Model):
    """Blog posts linked to ProjectCategory"""

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    category = models.ForeignKey(
        ProjectCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blogs'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blogs'
    )

    excerpt = models.TextField(blank=True)
    content = models.TextField()

    featured_image = models.ImageField(
        upload_to='blogs/',
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft'
    )

    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = "Blog"
        verbose_name_plural = "Blogs"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})

class Event(models.Model):
    """Events such as fundraisers, community outreach, trainings, etc."""

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    category = models.ForeignKey(
        ProjectCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events'
    )

    description = models.TextField()

    featured_image = models.ImageField(
        upload_to='events/',
        blank=True,
        null=True
    )

    location = models.CharField(max_length=255, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)

    is_featured = models.BooleanField(default=False)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['start_date']
        verbose_name = "Event"
        verbose_name_plural = "Events"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        if self.status == 'published' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'slug': self.slug})