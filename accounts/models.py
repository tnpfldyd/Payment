from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import UserManager
# Create your models here.

class User(AbstractUser): # email과, 패스워드만 사용하도록 했습니다.
    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
    
class Balance(models.Model): # 유저 모델 생성시 Balance 모델도 생기도록 signals.py에 작성했습니다.
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0, blank=True)