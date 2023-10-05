from django.db import models
from django.contrib.auth.models import AbstractUser



class Usertable(AbstractUser):
    username=models.CharField(max_length=20, blank=True, null=True, unique=False)
    role = models.CharField(max_length=25, default="normal_user")
    email = models.EmailField(primary_key=True, unique=True)
    dob = models.DateField(default='2000-01-01')

    USERNAME_FIELD= 'email'
    REQUIRED_FIELDS=[]
    def __str__(self):
        return self.email