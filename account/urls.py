from django.urls import path
from .views import (
    CandidateListView,
    CompanyListView,
    InvitationCreateView,
    LoginView,
    LogoutView,
    MeView,
    PricingPlanListView,
    PythonAssessmentSubmitView,
    PythonAssessmentView,
    RefreshCookieView,
    RegisterView,
    VerifyEmailView,
    csrf,
)

urlpatterns = [
    path("csrf/", csrf, name="csrf"),
    path('register/', RegisterView.as_view(), name='api_register'),
    path("verify-email/", VerifyEmailView.as_view(), name="verify_email"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshCookieView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path("companies/", CompanyListView.as_view(), name="companies"),
    path("candidates/", CandidateListView.as_view(), name="candidates"),
    path("pricing/", PricingPlanListView.as_view(), name="pricing"),
    path("tests/python/", PythonAssessmentView.as_view(), name="python_test"),
    path("tests/python/submit/", PythonAssessmentSubmitView.as_view(), name="python_test_submit"),
    path("invitations/", InvitationCreateView.as_view(), name="invitations"),
]
