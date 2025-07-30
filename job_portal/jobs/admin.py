from django.contrib import admin
from .models import Job, Application

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company_name', 'location', 'posted_by', 'created_at']
    list_filter = ['created_at', 'location']
    search_fields = ['title', 'company_name', 'location']

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['job', 'applicant', 'applied_at']
    list_filter = ['applied_at']
    search_fields = ['job_title', 'applicant_username']