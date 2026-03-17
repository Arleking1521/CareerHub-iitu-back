from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    username = models.CharField(max_length=125, verbose_name='Псевдоним')
    first_name= models.CharField(max_length=125, blank=True, null=True, verbose_name='Имя')
    last_name= models.CharField(max_length=125, blank=True, null=True, verbose_name='Фамилия')
    email = models.EmailField(unique=True, verbose_name='Почта')
    password = models.CharField(max_length=125, verbose_name='Пароль')
    is_student = models.BooleanField(default=False, verbose_name='Студент?')

    USERNAME_FIELD='email'
    REQUIRED_FIELDS = ['username', 'first_name']

    def save(self, *args, **kwargs):
        email_prefix = self.email.split('@')[0]
        self.username = f"{self.first_name.lower()}_{email_prefix.lower()}" 
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.username} : {self.email}'