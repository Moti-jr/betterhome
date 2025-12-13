# admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import ProjectCategory, Project, ProjectImage, ProjectUpdate, ProjectPartner


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


from django.contrib import admin

# Register your models here.
