# Generated manually for the CareerAI frontend integration.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(
                choices=[('student', 'Student'), ('jobseeker', 'Job seeker'), ('company', 'Company')],
                default='student',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='student_id',
            field=models.CharField(blank=True, default='', max_length=60),
        ),
        migrations.AddField(
            model_name='user',
            name='university',
            field=models.CharField(blank=True, default='', max_length=160),
        ),
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=160)),
                ('role', models.CharField(max_length=120)),
                ('university', models.CharField(blank=True, max_length=160)),
                ('level', models.CharField(max_length=40)),
                ('location', models.CharField(max_length=120)),
                ('gpa', models.DecimalField(blank=True, decimal_places=1, max_digits=3, null=True)),
                ('salary', models.CharField(blank=True, max_length=80)),
                ('format', models.CharField(max_length=40)),
                ('experience', models.PositiveIntegerField(default=0)),
                ('skills', models.JSONField(blank=True, default=list)),
                ('available', models.BooleanField(default=True)),
                ('initials', models.CharField(blank=True, max_length=8)),
                ('rating', models.DecimalField(decimal_places=1, default=0, max_digits=3)),
                ('about', models.TextField(blank=True)),
            ],
            options={'ordering': ['-rating', 'name']},
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=160)),
                ('industry', models.CharField(max_length=120)),
                ('location', models.CharField(max_length=120)),
                ('size', models.CharField(max_length=60)),
                ('open_jobs', models.PositiveIntegerField(default=0)),
                ('rating', models.DecimalField(decimal_places=1, default=0, max_digits=3)),
                ('description', models.TextField(blank=True)),
                ('skills', models.JSONField(blank=True, default=list)),
                ('available', models.BooleanField(default=True)),
                ('initials', models.CharField(blank=True, max_length=8)),
                ('website', models.CharField(blank=True, max_length=160)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='AssessmentQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(default='python')),
                ('external_id', models.CharField(max_length=40)),
                ('question', models.TextField()),
                ('options', models.JSONField(default=list)),
                ('correct', models.CharField(max_length=8)),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={'ordering': ['order', 'id'], 'unique_together': {('slug', 'external_id')}},
        ),
        migrations.CreateModel(
            name='PricingPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('audience', models.CharField(choices=[('student', 'Student'), ('company', 'Company')], max_length=20)),
                ('plan_id', models.CharField(max_length=40)),
                ('name', models.CharField(max_length=80)),
                ('price', models.PositiveIntegerField(default=0)),
                ('currency', models.CharField(blank=True, max_length=10)),
                ('period', models.CharField(blank=True, max_length=40)),
                ('tagline', models.CharField(blank=True, max_length=220)),
                ('description', models.TextField(blank=True)),
                ('features', models.JSONField(default=list)),
                ('highlighted', models.BooleanField(default=False)),
                ('badge', models.CharField(blank=True, max_length=80)),
                ('cta', models.CharField(blank=True, max_length=120)),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={'ordering': ['audience', 'order'], 'unique_together': {('audience', 'plan_id')}},
        ),
        migrations.CreateModel(
            name='TestAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(default='python')),
                ('answers', models.JSONField(default=dict)),
                ('score', models.PositiveIntegerField(default=0)),
                ('total', models.PositiveIntegerField(default=0)),
                ('percent', models.PositiveIntegerField(default=0)),
                ('passed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='test_attempts', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitations', to='account.candidate')),
                ('company_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_invitations', to=settings.AUTH_USER_MODEL)),
            ],
            options={'unique_together': {('company_user', 'candidate')}},
        ),
    ]
