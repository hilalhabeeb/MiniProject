"""
This module demonstrates the usage of the datetime module.
It includes examples of how to work with dates and times.
"""
from datetime import datetime 
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login as auth
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import Usertable



# Create your views here.
def index(request):
    return render(request, "index.html")

def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")

def signup(request):
    if request.method == 'POST':
        role = request.POST['role']
        fname = request.POST['fname']
        lname = request.POST['lname']
        dob_str = request.POST['dob']  # Corrected variable name to dob_str
        dob = datetime.strptime(dob_str, "%Y-%m-%d")  # Corrected datetime conversion
        email = request.POST['email']
        password = request.POST['password']
        hashed_password = make_password(password)
        user = Usertable(role=role, fname=fname, lname=lname, dob=dob, email=email, password=hashed_password)
        user.save()
        return redirect('user_login')
    return render(request, "registration.html")

def user_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
    
        myuser = Usertable.objects.get(email=email)
        if myuser is not None:
            auth(request, myuser)
            messages.success(request, "Login successful")
            return redirect('index')  # Redirect to userpage.html after successful login
        else:
            messages.error(request, "Login failed. Please check your credentials.")
            return redirect('user_login')  # Redirect back to the signin page if login fails
    return render(request, 'login.html')







  
