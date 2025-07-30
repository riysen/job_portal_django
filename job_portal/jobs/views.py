from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Job, Application
from .forms import JobForm, ApplicationForm
from accounts.models import UserProfile

def job_list(request):
    jobs = Job.objects.all()
    query = request.GET.get('q')
    
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(company_name__icontains=query) |
            Q(location__icontains=query)
        )
    
    return render(request, 'jobs/job_list.html', {
        'jobs': jobs,
        'query': query
    })

def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    user_applied = False
    is_job_owner = False
    can_apply = False
    
    if request.user.is_authenticated:
        # Check if user is the job owner
        is_job_owner = (job.posted_by == request.user)
        
        # Check if user has already applied
        user_applied = Application.objects.filter(
            job=job, applicant=request.user
        ).exists()
        
        # Check if user can apply (must be applicant and not job owner)
        try:
            profile = UserProfile.objects.get(user=request.user)
            can_apply = (profile.user_type == 'applicant' and not is_job_owner and not user_applied)
        except UserProfile.DoesNotExist:
            can_apply = False
    
    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'user_applied': user_applied,
        'is_job_owner': is_job_owner,
        'can_apply': can_apply
    })
@login_required
def post_job(request):
    # Check if user is employer
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.user_type != 'employer':
            messages.error(request, 'Only employers can post jobs.')
            return redirect('job_list')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('my_jobs')
    else:
        form = JobForm()
    
    return render(request, 'jobs/job_form.html', {'form': form})

@login_required
def my_jobs(request):
    jobs = Job.objects.filter(posted_by=request.user)
    return render(request, 'jobs/my_jobs.html', {'jobs': jobs})

@login_required
def job_applications(request, pk):
    job = get_object_or_404(Job, pk=pk, posted_by=request.user)
    applications = Application.objects.filter(job=job)
    return render(request, 'jobs/applications.html', {
        'job': job,
        'applications': applications
    })

@login_required
def apply_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    
    # Check if user is the job owner
    if job.posted_by == request.user:
        messages.error(request, 'You cannot apply to your own job posting.')
        return redirect('job_detail', pk=pk)
    
    # Check if user is applicant
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.user_type != 'applicant':
            messages.error(request, 'Only applicants can apply for jobs.')
            return redirect('job_detail', pk=pk)
    except UserProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile.')
        return redirect('dashboard')
    
    # Check if already applied
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('job_detail', pk=pk)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, 'Application submitted successfully!')
            return redirect('job_detail', pk=pk)
    else:
        form = ApplicationForm()
    
    return render(request, 'jobs/apply_job.html', {
        'form': form,
        'job': job
    })
@login_required
def my_applications(request):
    applications = Application.objects.filter(applicant=request.user)
    return render(request, 'jobs/my_applications.html', {
        'applications': applications
    })