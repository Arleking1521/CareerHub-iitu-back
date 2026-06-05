from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_STUDENT = 'student'
    ROLE_JOBSEEKER = 'jobseeker'
    ROLE_COMPANY = 'company'
    ROLE_CHOICES = (
        (ROLE_STUDENT, 'Student'),
        (ROLE_JOBSEEKER, 'Job seeker'),
        (ROLE_COMPANY, 'Company'),
    )

    username = models.CharField(max_length=125)
    first_name = models.CharField(max_length=125, blank=True, null=True)
    last_name = models.CharField(max_length=125, blank=True, null=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=125)
    is_student = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    university = models.CharField(max_length=160, blank=True, default='')
    student_id = models.CharField(max_length=60, blank=True, default='')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name']

    def save(self, *args, **kwargs):
        email_prefix = self.email.split('@')[0] if self.email else 'user'
        first = (self.first_name or 'user').lower()
        self.username = f'{first}_{email_prefix.lower()}'
        self.is_student = self.role == self.ROLE_STUDENT
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.username} : {self.email}'


class Company(models.Model):
    name = models.CharField(max_length=160)
    industry = models.CharField(max_length=120)
    location = models.CharField(max_length=120)
    size = models.CharField(max_length=60)
    open_jobs = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    description = models.TextField(blank=True)
    skills = models.JSONField(default=list, blank=True)
    available = models.BooleanField(default=True)
    initials = models.CharField(max_length=8, blank=True)
    website = models.CharField(max_length=160, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Candidate(models.Model):
    name = models.CharField(max_length=160)
    role = models.CharField(max_length=120)
    university = models.CharField(max_length=160, blank=True)
    level = models.CharField(max_length=40)
    location = models.CharField(max_length=120)
    gpa = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    salary = models.CharField(max_length=80, blank=True)
    format = models.CharField(max_length=40)
    experience = models.PositiveIntegerField(default=0)
    skills = models.JSONField(default=list, blank=True)
    available = models.BooleanField(default=True)
    initials = models.CharField(max_length=8, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    about = models.TextField(blank=True)

    class Meta:
        ordering = ['-rating', 'name']

    def __str__(self):
        return self.name


class AssessmentQuestion(models.Model):
    slug = models.SlugField(default='python')
    external_id = models.CharField(max_length=40)
    question = models.TextField()
    options = models.JSONField(default=list)
    correct = models.CharField(max_length=8)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        unique_together = ('slug', 'external_id')

    def __str__(self):
        return f'{self.slug}: {self.external_id}'


class TestAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_attempts')
    slug = models.SlugField(default='python')
    answers = models.JSONField(default=dict)
    score = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)
    percent = models.PositiveIntegerField(default=0)
    passed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class PricingPlan(models.Model):
    AUDIENCE_STUDENT = 'student'
    AUDIENCE_COMPANY = 'company'
    AUDIENCE_CHOICES = (
        (AUDIENCE_STUDENT, 'Student'),
        (AUDIENCE_COMPANY, 'Company'),
    )

    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES)
    plan_id = models.CharField(max_length=40)
    name = models.CharField(max_length=80)
    price = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=10, blank=True)
    period = models.CharField(max_length=40, blank=True)
    tagline = models.CharField(max_length=220, blank=True)
    description = models.TextField(blank=True)
    features = models.JSONField(default=list)
    highlighted = models.BooleanField(default=False)
    badge = models.CharField(max_length=80, blank=True)
    cta = models.CharField(max_length=120, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['audience', 'order']
        unique_together = ('audience', 'plan_id')

    def __str__(self):
        return f'{self.audience}: {self.name}'


class Invitation(models.Model):
    company_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='invitations')
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('company_user', 'candidate')
