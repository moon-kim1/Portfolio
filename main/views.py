from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Project, UserProfile
from .forms import ContactForm

def home(request):
    return render(request, 'main/home.html')

def about(request):
    profile = UserProfile.objects.first()
    return render(request, 'main/about.html', {'profile': profile})

def projects(request):
    projects = Project.objects.all().order_by('order', '-date_added')
    return render(request, 'main/projects.html', {'projects': projects})

def resume(request):
    profile = UserProfile.objects.first()
    return render(request, 'main/resume.html', {'profile': profile})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            message_obj = form.save()
            
            # Send Email Notification
            subject = f"New Portfolio Message from {message_obj.name}"
            body = f"Name: {message_obj.name}\nEmail: {message_obj.email}\n\nMessage:\n{message_obj.message}"
            
            try:
                send_mail(
                    subject,
                    body,
                    settings.DEFAULT_FROM_EMAIL or 'noreply@yourportfolio.com',
                    [settings.CONTACT_EMAIL],
                    fail_silently=False,
                )
            except Exception as e:
                # In development, we can log this or just continue as the message is still saved to DB
                print(f"Email error: {e}")

            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'main/contact.html', {'form': form})
