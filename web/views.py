from django.core.paginator import Paginator
from django.shortcuts import render
from django.contrib import messages
from core.models import Project
from support.helpers import send_text_mail

# Create your views here.


def home(request):
    projects_list = Project.objects.filter(is_published=True).order_by("-created_at")
    paginator = Paginator(projects_list, 10)  # Show 6 projects per page
    page_number = request.GET.get("page")
    projects = paginator.get_page(page_number)

    context = {
        "projects": projects,
    }
    return render(request, "index.html", context)


def about(request):
    return render(request, "about.html")


def contact(request):
    if request.method == "POST":
        # Handle form submission here
        email = request.POST.get("email")
        message = request.POST.get("message")
        name = request.POST.get("name")
        message = request.POST.get("message")
        # send the email
        subject = f"New message from {name}"
        plain_message = f"Name: {name}\nEmail: {email}\nMessage: {message}"
        # recipient_list = ["izuchukwukorie@gmail.com", "nwaforglory6@gmail.com"]
        recipient_list = ["nwaforglory6@gmail.com"]
        send_text_mail(subject, plain_message, recipient_list)
        # user sjango messages to send the user a success message
        messages.success(request, "Your message has been sent successfully.")

    return render(request, "contact.html")


def post(request, pk):
    project = Project.objects.get(pk=pk)
    if not project.is_published:
        return render(request, "404.html")
    context = {
        "project": project,
    }
    # Add any other context variables you need for the post page
    return render(request, "post.html", context)
