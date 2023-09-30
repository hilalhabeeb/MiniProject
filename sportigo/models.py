from django.db import models

#Create your models here.
class Usertable(models.Model):

    role =  models.CharField(max_length=15)
    fname = models.CharField(max_length=15)
    lname = models.CharField(max_length=15)
    dob = models.DateField(default='2000-01-01')
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=15)
    last_login = models.DateTimeField(blank=True,null=True)