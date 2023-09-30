#from django.contrib import admin
from django.urls import path
#from django.contrib.auth import views as auth_views
from .import views

urlpatterns = [
   path('',views.index,name='index'),
   path('about/', views.about, name='about'),
   path('contact/', views.contact, name='contact'),
   path('signup/', views.signup, name='signup'),
   path('login/', views.user_login, name='user_login'),
]