from django.contrib import admin
from .models import Project, ContactMessage, UserProfile

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'tech_stack', 'presentation_file', 'date_added')
    list_editable = ('order',)
    list_display_links = ('title',)
    search_fields = ('title', 'tech_stack', 'description')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'bio_title')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'submitted_at')
    readonly_fields = ('submitted_at',)
    search_fields = ('name', 'email', 'message')
