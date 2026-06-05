from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from .models import AssessmentQuestion, Candidate, Company, Invitation, PricingPlan, TestAttempt

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, default=User.ROLE_STUDENT)
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'name',
            'password',
            'role',
            'university',
            'student_id',
        )
        extra_kwargs = {
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
            'university': {'required': False, 'allow_blank': True},
            'student_id': {'required': False, 'allow_blank': True},
        }

    def validate(self, attrs):
        name = attrs.pop('name', '').strip()
        if name and not attrs.get('first_name'):
            parts = name.split()
            attrs['first_name'] = parts[0]
            attrs['last_name'] = ' '.join(parts[1:])
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=False)

    def validate(self, attrs):
        request = self.context.get('request')

        user = authenticate(
            request=request,
            email=attrs.get('email'),
            password=attrs.get('password')
        )

        if not user:
            raise serializers.ValidationError('Invalid email or password.')

        if not user.is_active:
            raise serializers.ValidationError('Account is inactive.')

        requested_role = attrs.get('role')

        if requested_role and user.role != requested_role:
            raise serializers.ValidationError('This account has another role.')

        attrs['user'] = user
        return attrs


class MeSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'name',
            'email',
            'role',
            'is_student',
            'university',
            'student_id',
        )

    def get_name(self, obj):
        full_name = f'{obj.first_name or ""} {obj.last_name or ""}'.strip()
        return full_name or obj.email


class MeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'university', 'student_id')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'email': {'required': False},
            'university': {'required': False},
            'student_id': {'required': False},
        }


class CompanySerializer(serializers.ModelSerializer):
    openJobs = serializers.IntegerField(source='open_jobs')

    class Meta:
        model = Company
        fields = (
            'id',
            'name',
            'industry',
            'location',
            'size',
            'openJobs',
            'rating',
            'description',
            'skills',
            'available',
            'initials',
            'website',
        )


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = (
            'id',
            'name',
            'role',
            'university',
            'level',
            'location',
            'gpa',
            'salary',
            'format',
            'experience',
            'skills',
            'available',
            'initials',
            'rating',
            'about',
        )


class AssessmentQuestionSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='external_id')

    class Meta:
        model = AssessmentQuestion
        fields = ('id', 'question', 'options', 'correct')


class TestAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestAttempt
        fields = ('id', 'slug', 'answers', 'score', 'total', 'percent', 'passed', 'created_at')


class PricingPlanSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='plan_id')

    class Meta:
        model = PricingPlan
        fields = (
            'id',
            'name',
            'price',
            'currency',
            'period',
            'tagline',
            'description',
            'features',
            'highlighted',
            'badge',
            'cta',
        )


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ('id', 'candidate', 'message', 'created_at')
        read_only_fields = ('id', 'created_at')

    def create(self, validated_data):
        return Invitation.objects.create(
            company_user=self.context['request'].user,
            **validated_data,
        )
