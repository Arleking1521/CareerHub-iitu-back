from django.contrib import admin
from .models import AssessmentQuestion, Candidate, Company, Invitation, PricingPlan, TestAttempt, User
from django.contrib.auth.admin import UserAdmin
# Register your models here.
# admin.site.register(User)
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        ('Authorization datas', {'fields': ('email', 'password', 'is_active')}),
        ('Personal Information', {'fields': ('first_name', 'last_name', 'username')}),
        ('Access datas', {'fields': ('role', 'is_superuser', 'is_staff', 'is_student', 'groups')}),
        ('Additinaly information', {'fields': ('date_joined', 'last_login')}),
        
    )
    add_fieldsets = (
        ('Authorization datas', {'fields': ('email', 'password')}),
        ('Personal Information', {'fields': ('first_name', 'last_name')}),
    )
    list_display = ('email', 'username', 'role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name')
    filter_horizontal = ('groups',)


admin.site.register(Company)
admin.site.register(Candidate)
admin.site.register(AssessmentQuestion)
admin.site.register(TestAttempt)
admin.site.register(PricingPlan)
admin.site.register(Invitation)
