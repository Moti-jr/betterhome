from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.shortcuts import render

from betterhome.models import Project, ProjectCategory


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
    return render(request, 'events.html')


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


def blog_detail(request):
    return render(request, 'blog_detail.html')


def volunteer(request):
    return render(request, 'volunteer.html')


def about(request):
    return render(request, 'about.html')


def newsletter_signup(request):
    return render(request, 'index.html')


def blog_list(request):
    return render(request, 'blog_list.html')