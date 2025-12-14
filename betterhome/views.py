from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.shortcuts import render

from betterhome.models import Project, ProjectCategory, Blog, Event, TeamMember, TeamDepartment


def home(request):
    """Home page view"""
    featured_projects = Project.objects.filter(
        is_featured=True,
        is_active=True
    )[:3]  # Get top 3 featured projects

    context = {
        'featured_projects': featured_projects,
    }
    return render(request, 'index.html', context)


def contact(request):
    return render(request, 'contact.html')


def events(request):
    now = timezone.now()

    featured_event = Event.objects.filter(
        status='published',
        is_featured=True,
        start_date__gte=now
    ).order_by('start_date').first()

    events = Event.objects.filter(
        status='published',
        start_date__gte=now
    ).exclude(id=featured_event.id if featured_event else None).order_by('start_date')

    context = {
        'featured_event': featured_event,
        'events': events,
    }
    return render(request, 'events.html', context)


def donate(request):
    return render(request, 'donate.html')


def projects(request):
    """All projects listing page"""
    category_slug = request.GET.get('category')
    status = request.GET.get('status')

    projects_list = Project.objects.filter(is_active=True)

    # Filter by category
    if category_slug:
        projects_list = projects_list.filter(category__slug=category_slug)

    # Filter by status
    if status:
        projects_list = projects_list.filter(status=status)

    # Pagination
    paginator = Paginator(projects_list, 9)  # 9 projects per page
    page_number = request.GET.get('page')
    projects_page = paginator.get_page(page_number)

    categories = ProjectCategory.objects.all()

    context = {
        'projects': projects_page,
        'categories': categories,
        'selected_category': category_slug,
        'selected_status': status,
    }
    return render(request, 'projects.html', context)


def project_detail(request, slug):
    """Single project detail page"""
    project = get_object_or_404(Project, slug=slug, is_active=True)

    # Increment view count
    project.increment_views()

    # Get related projects
    related_projects = Project.objects.filter(
        category=project.category,
        is_active=True
    ).exclude(id=project.id)[:3]

    context = {
        'project': project,
        'related_projects': related_projects,
    }
    return render(request, 'project_detail.html', context)


def gallery(request):
    return render(request, 'gallery.html')


def blog_detail(request, slug):
    """Single blog detail page"""

    blog = get_object_or_404(
        Blog,
        slug=slug,
        status='published'
    )

    # Increment view count (only if field exists)
    if hasattr(blog, 'views'):
        blog.views += 1
        blog.save(update_fields=['views'])

    # Related blogs (same category, published, excluding current)
    related_blogs = Blog.objects.filter(
        category=blog.category,
        status='published'
    ).exclude(id=blog.id).order_by('-published_at')[:3]

    context = {
        'post': blog,
        'related_blogs': related_blogs,
    }

    return render(request, 'blog_detail.html', context)




def volunteer(request):
    return render(request, 'volunteer.html')


def about(request):
    """About page with team members"""
    team_members = TeamMember.objects.filter(
        is_active=True,
        show_on_homepage=True
    )

    departments = TeamDepartment.objects.filter(
        is_active=True
    ).prefetch_related('members')

    context = {
        'team_members': team_members,
        'departments': departments,
    }
    return render(request, 'about.html', context)


def team(request):
    """Full team page"""
    department_slug = request.GET.get('department')

    if department_slug:
        department = get_object_or_404(TeamDepartment, slug=department_slug, is_active=True)
        team_members = department.members.filter(is_active=True)
        current_department = department
    else:
        team_members = TeamMember.objects.filter(is_active=True)
        current_department = None

    departments = TeamDepartment.objects.filter(is_active=True)

    context = {
        'team_members': team_members,
        'departments': departments,
        'current_department': current_department,
    }
    return render(request, 'team.html', context)


def team_member_detail(request, slug):
    """Single team member detail page"""
    member = get_object_or_404(TeamMember, slug=slug, is_active=True)

    context = {
        'member': member,
    }
    return render(request, 'team_member_detail.html', context)
def newsletter_signup(request):
    return render(request, 'index.html')


def blog_list(request):
    selected_category = request.GET.get('category')

    # Only categories that have published blogs
    categories = ProjectCategory.objects.filter(
        blogs__status='published'
    ).distinct()

    blogs = Blog.objects.filter(status='published')

    if selected_category and selected_category != 'all':
        blogs = blogs.filter(category__slug=selected_category)

    context = {
        'blogs': blogs,
        'categories': categories,
        'selected_category': selected_category,
    }

    return render(request, 'blog_list.html', context)