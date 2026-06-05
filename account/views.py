from axes.handlers.proxy import AxesProxyHandler
from axes.utils import reset as axes_reset
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import AssessmentQuestion, Candidate, Company, PricingPlan, TestAttempt
from .serializers import (
    AssessmentQuestionSerializer,
    CandidateSerializer,
    CompanySerializer,
    InvitationSerializer,
    LoginSerializer,
    MeSerializer,
    MeUpdateSerializer,
    PricingPlanSerializer,
    RegisterSerializer,
    TestAttemptSerializer,
)
from .token import TokenGenerator
from .utils import send_verification_email

User = get_user_model()
acc_active_token = TokenGenerator()


def serialize_user(user):
    return MeSerializer(user).data


def issue_tokens(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token), str(refresh)


@require_GET
@ensure_csrf_cookie
def csrf(request):
    return JsonResponse({'csrfToken': get_token(request)})


def _set_auth_cookies(response: Response, refresh: str):
    response.set_cookie(
        key=settings.JWT_AUTH_REFRESH_COOKIE,
        value=refresh,
        max_age=int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()),
        httponly=settings.JWT_COOKIE_HTTPONLY,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        path=settings.JWT_COOKIE_REFRESH_PATH,
    )


def _clear_auth_cookies(response: Response):
    response.delete_cookie(settings.JWT_AUTH_REFRESH_COOKIE, path=settings.JWT_COOKIE_REFRESH_PATH)


@extend_schema(request=RegisterSerializer, responses={201: OpenApiResponse(description='Registration successful')})
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        try:
            if not settings.DEBUG:
                send_verification_email(user)
        except Exception:
            pass

        access, refresh = issue_tokens(user)
        resp = JsonResponse(
            {
                'detail': 'OK',
                'access': access,
                'user': serialize_user(user),
            },
            status=status.HTTP_201_CREATED,
        )
        _set_auth_cookies(resp, refresh=refresh)
        return resp


@extend_schema(
    parameters=[OpenApiParameter('uid', str), OpenApiParameter('token', str)],
    responses={200: OpenApiResponse(description='Email verified')},
)
class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        uid = request.query_params.get('uid')
        token = request.query_params.get('token')

        if not uid or not token:
            return JsonResponse({'detail': 'uid and token are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except Exception:
            return JsonResponse({'detail': 'Invalid verification link'}, status=status.HTTP_400_BAD_REQUEST)

        if acc_active_token.check_token(user, token):
            if not user.is_active:
                user.is_active = True
                user.save(update_fields=['is_active'])
            return JsonResponse({'detail': 'Email verified'}, status=status.HTTP_200_OK)

        return JsonResponse({'detail': 'Token is invalid or expired'}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=LoginSerializer, responses={200: OpenApiResponse(description='OK')})
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if AxesProxyHandler.is_locked(request):
            return JsonResponse({'detail': 'Too many login attempts. Try later.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        serializer = LoginSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            identifier = request.data.get('email') or 'unknown'
            AxesProxyHandler.user_login_failed(
                sender=LoginView,
                credentials={'username': str(identifier)},
                request=request,
            )
            return JsonResponse({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        user = serializer.validated_data['user']
        ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
        if ip:
            ip = ip.split(',')[0].strip()
        try:
            axes_reset(ip_address=ip) if ip else axes_reset()
        except Exception:
            pass

        access, refresh = issue_tokens(user)
        resp = JsonResponse({'detail': 'OK', 'access': access, 'user': serialize_user(user)}, status=status.HTTP_200_OK)
        _set_auth_cookies(resp, refresh=refresh)
        return resp


@extend_schema(responses={200: OpenApiResponse(description='New access token')})
class RefreshCookieView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.JWT_AUTH_REFRESH_COOKIE)
        if not refresh_token:
            return JsonResponse({'detail': 'Refresh cookie not found'}, status=401)

        try:
            refresh = RefreshToken(refresh_token)
            new_access = str(refresh.access_token)
            new_refresh = str(refresh)

            if settings.SIMPLE_JWT.get('ROTATE_REFRESH_TOKENS'):
                refresh.set_jti()
                refresh.set_exp()
                new_refresh = str(refresh)

            resp = JsonResponse({'detail': 'OK', 'access': new_access}, status=200)
            _set_auth_cookies(resp, refresh=new_refresh)
            return resp
        except Exception:
            return JsonResponse({'detail': 'Invalid refresh token'}, status=401)


@extend_schema(responses={200: OpenApiResponse(description='Logged out')})
class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        resp = JsonResponse({'detail': 'Logged out'}, status=200)
        _clear_auth_cookies(resp)
        return resp


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return JsonResponse({'user': serialize_user(request.user)})

    def patch(self, request):
        serializer = MeUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_user = serializer.save()
        return JsonResponse({'detail': 'Profile updated.', 'user': serialize_user(updated_user)}, status=status.HTTP_200_OK)


class CompanyListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CompanySerializer
    queryset = Company.objects.all()


class CandidateListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CandidateSerializer
    queryset = Candidate.objects.all()


class PricingPlanListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PricingPlanSerializer

    def get_queryset(self):
        audience = self.request.query_params.get('audience', PricingPlan.AUDIENCE_STUDENT)
        if audience not in [PricingPlan.AUDIENCE_STUDENT, PricingPlan.AUDIENCE_COMPANY]:
            audience = PricingPlan.AUDIENCE_STUDENT
        return PricingPlan.objects.filter(audience=audience)


class PythonAssessmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        questions = AssessmentQuestion.objects.filter(slug='python')
        return JsonResponse({'questions': AssessmentQuestionSerializer(questions, many=True).data})


class PythonAssessmentSubmitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        answers = request.data.get('answers') or {}
        questions = AssessmentQuestion.objects.filter(slug='python')
        total = questions.count()
        score = sum(1 for question in questions if answers.get(question.external_id) == question.correct)
        percent = round((score / total) * 100) if total else 0
        attempt = TestAttempt.objects.create(
            user=request.user,
            slug='python',
            answers=answers,
            score=score,
            total=total,
            percent=percent,
            passed=percent >= 70,
        )
        return JsonResponse({'attempt': TestAttemptSerializer(attempt).data}, status=status.HTTP_201_CREATED)


class InvitationCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InvitationSerializer
