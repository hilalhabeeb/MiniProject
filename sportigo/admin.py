# Register your models here.
from django.contrib import admin
from .models import Usertable

class UsertableAdmin(admin.ModelAdmin):
    list_display=('role','fname','lname','dob','email','password')
admin.site.register(Usertable,UsertableAdmin)