from .models import ProjectCategory, Project, ProjectImage, ProjectUpdate, ProjectPartner, Event, Blog
from django.contrib import admin
from django.utils.html import format_html
from .models import TeamMember, TeamDepartment
from .models import GalleryCategory, GalleryImage

@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'image_count', 'display_order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

    def image_count(self, obj):
        return obj.image_count

    image_count.short_description = 'Images'


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = [
        'image_preview',
        'title',
        'category',
        'project',
        'is_featured',
        'is_active',
        'views',
        'uploaded_at'
    ]
    list_filter = ['is_featured', 'is_active', 'category', 'uploaded_at']
    search_fields = ['title', 'caption', 'location', 'photographer']
    readonly_fields = ['image_preview', 'views', 'uploaded_at', 'updated_at']

    fieldsets = (
        ('Image', {
            'fields': ('image', 'image_preview')
        }),
        ('Information', {
            'fields': ('title', 'caption', 'category', 'project')
        }),
        ('Metadata', {
            'fields': ('photographer', 'location', 'date_taken'),
            'classes': ('collapse',)
        }),
        ('Display Options', {
            'fields': ('is_featured', 'is_active', 'display_order')
        }),
        ('Statistics', {
            'fields': ('views', 'uploaded_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 150px; max-width: 200px; border-radius: 8px; object-fit: cover;"/>',
                obj.image.url
            )
        return "-"

    image_preview.short_description = 'Preview'

    actions = ['make_featured', 'remove_featured', 'activate', 'deactivate']

    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)

    make_featured.short_description = "Mark as featured"

    def remove_featured(self, request, queryset):
        queryset.update(is_featured=False)

    remove_featured.short_description = "Remove from featured"

    def activate(self, request, queryset):
        queryset.update(is_active=True)

    activate.short_description = "Activate"

    def deactivate(self, request, queryset):
        queryset.update(is_active=False)

    deactivate.short_description = "Deactivate"
@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = [
        'photo_preview',
        'name',
        'role',
        'age_display',
        'national_id_status_display',
        'is_active',
        'show_on_homepage',
        'display_order',
    ]
    list_filter = [
        'is_active',
        'show_on_homepage',
        'role_category',
        'gender',
        'national_id_verified',
        'joined_date'
    ]
    search_fields = ['name', 'role', 'bio', 'email', 'national_id']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['photo_preview', 'age_display', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'role', 'role_category')
        }),
        ('Personal Information', {
            'fields': ('date_of_birth', 'age_display', 'gender'),
            'description': 'Date of birth is used to calculate age and determine if National ID is required.'
        }),
        ('National ID (Required for 18+ years)', {
            'fields': ('national_id', 'national_id_verified'),
            'description': 'National ID is mandatory for members 18 years and above.',
            'classes': ('collapse',)
        }),
        ('Photo', {
            'fields': ('photo', 'photo_preview')
        }),
        ('Biography', {
            'fields': ('bio',)
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address'),
            'classes': ('collapse',)
        }),
        ('Social Media', {
            'fields': ('linkedin', 'twitter', 'facebook', 'instagram'),
            'classes': ('collapse',)
        }),
        ('Display Options', {
            'fields': ('is_active', 'show_on_homepage', 'display_order', 'joined_date')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover;"/>',
                obj.photo.url
            )
        return "-"

    photo_preview.short_description = 'Photo Preview'

    def age_display(self, obj):
        age = obj.age
        if age is not None:
            color = "green" if age >= 18 else "orange"
            return format_html(
                '<span style="color: {}; font-weight: bold;">{} years</span>',
                color, age
            )
        return "-"

    age_display.short_description = 'Age'

    def national_id_status_display(self, obj):
        status = obj.national_id_status
        colors = {
            'Verified': 'green',
            'Unverified': 'orange',
            'Missing': 'red',
            'Not Required': 'gray'
        }
        icons = {
            'Verified': '✓',
            'Unverified': '⚠',
            'Missing': '✗',
            'Not Required': '-'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            colors.get(status, 'black'),
            icons.get(status, ''),
            status
        )

    national_id_status_display.short_description = 'ID Status'

    actions = [
        'make_active',
        'make_inactive',
        'show_on_homepage',
        'hide_from_homepage',
        'verify_national_id',
        'unverify_national_id'
    ]

    def make_active(self, request, queryset):
        queryset.update(is_active=True)

    make_active.short_description = "Mark as active"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)

    make_inactive.short_description = "Mark as inactive"

    def show_on_homepage(self, request, queryset):
        queryset.update(show_on_homepage=True)

    show_on_homepage.short_description = "Show on homepage"

    def hide_from_homepage(self, request, queryset):
        queryset.update(show_on_homepage=False)

    hide_from_homepage.short_description = "Hide from homepage"

    def verify_national_id(self, request, queryset):
        queryset.update(national_id_verified=True)

    verify_national_id.short_description = "Mark National ID as verified"

    def unverify_national_id(self, request, queryset):
        queryset.update(national_id_verified=False)

    unverify_national_id.short_description = "Mark National ID as unverified"


@admin.register(TeamDepartment)
class TeamDepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'member_count', 'display_order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['members']

    def member_count(self, obj):
        return obj.member_count

    member_count.short_description = 'Members'
@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'project_count', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']

    def project_count(self, obj):
        return obj.projects.count()

    project_count.short_description = 'Projects'


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ['image', 'caption', 'display_order']


class ProjectUpdateInline(admin.StackedInline):
    model = ProjectUpdate
    extra = 0
    fields = ['title', 'content', 'image', 'is_milestone']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'category',
        'status',
        'location',
        'is_featured',
        'is_active',
        'image_preview',
        'views',
        'created_at'
    ]
    list_filter = ['is_featured', 'is_active', 'status', 'category', 'created_at']
    search_fields = ['title', 'short_description', 'location']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views', 'created_at', 'updated_at', 'image_preview']
    inlines = [ProjectImageInline, ProjectUpdateInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'short_description', 'full_description')
        }),
        ('Images', {
            'fields': ('image', 'image_preview')
        }),
        ('Project Details', {
            'fields': ('location', 'status', 'start_date', 'end_date')
        }),
        ('Impact & Funding', {
            'fields': ('beneficiaries', 'budget', 'funds_raised')
        }),
        ('Display Options', {
            'fields': ('is_featured', 'is_active', 'display_order')
        }),
        ('Metadata', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; border-radius: 8px;"/>',
                obj.image.url
            )
        return "-"

    image_preview.short_description = 'Preview'

    actions = ['make_featured', 'remove_featured', 'mark_completed']

    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)

    make_featured.short_description = "Mark as featured"

    def remove_featured(self, request, queryset):
        queryset.update(is_featured=False)

    remove_featured.short_description = "Remove from featured"

    def mark_completed(self, request, queryset):
        queryset.update(status='completed')

    mark_completed.short_description = "Mark as completed"


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ['project', 'caption', 'display_order', 'uploaded_at']
    list_filter = ['project', 'uploaded_at']
    search_fields = ['project__title', 'caption']


@admin.register(ProjectUpdate)
class ProjectUpdateAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'is_milestone', 'created_at']
    list_filter = ['is_milestone', 'created_at', 'project']
    search_fields = ['title', 'content', 'project__title']
    readonly_fields = ['created_at']


@admin.register(ProjectPartner)
class ProjectPartnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'website', 'is_active', 'project_count']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    filter_horizontal = ['projects']

    def project_count(self, obj):
        return obj.projects.count()

    project_count.short_description = 'Projects'


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title','category','author','status','is_featured','published_at','created_at',)
    list_filter = ('status','category','is_featured','created_at',)
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    ordering = ('-published_at',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'category', 'status')
        }),
        ('Content', {
            'fields': ('excerpt', 'content', 'featured_image')
        }),
        ('Publishing Options', {
            'fields': ('is_featured', 'published_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title','category','start_date','end_date','location','status','is_featured',)
    list_filter = ('status','category','is_featured','start_date',)
    search_fields = ('title', 'description', 'location')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-start_date',)
    date_hierarchy = 'start_date'
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'status', 'is_featured')
        }),
        ('Event Details', {
            'fields': ('description', 'location', 'featured_image')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date')
        }),
        ('Publishing', {
            'fields': ('published_at',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    readonly_fields = ('created_at', 'updated_at', 'published_at')