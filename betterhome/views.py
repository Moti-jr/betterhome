from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def home(request):
    return render(request, 'index.html')


def contact(request):
    return render(request, 'contact.html')


def events(request):
    return render(request, 'events.html')


def donate(request):
    return render(request, 'donate.html')


def projects(request):
    return render(request, 'projects.html')


def project_detail(request):
    return render(request, 'project_detail.html')


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