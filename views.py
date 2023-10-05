import random
import string
from django.contrib.auth import login, logout, authenticate ,get_user_model

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from .models import *
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail


@never_cache
def index(request):
    return render(request, "index.html")

def signup(request):
    if request.method == 'POST':
        role = request.POST['role']
        firstname = request.POST['fname'] #
        email = request.POST['email'] #
        lastname = request.POST['lname'] 
        dob = request.POST['dob'] #
        password = request.POST['password']
        user = Usertable(first_name=firstname,last_name=lastname,role=role,dob=dob,email=email)
        user.set_password(password)
        user.save()
        return redirect('user_login')
    return render(request,"registration.html")


def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            if user.role == 'normal_user':
                login(request, user)
                return redirect('index2')
            elif user.role == 'club_user':
                login(request, user)
                return redirect('about')
        else:
            error_message = "Invalid credentials"
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, "login.html")

def userLogout(request):
    logout(request)
    return redirect('index')

@login_required
def index2(request):
    return render(request, "index2.html")

def about(request):
    return render(request, "about.html")
def contact(request):
    return render(request,"contact.html")

def check_user_exists(request):
    email = request.GET.get('email')  # You can also use 'email' if you're checking by email
    data = {
        'exists': Usertable.objects.filter(email=email).exists()
    }
    return JsonResponse(data)
    
def forgotPassword(request):
    if request.method == 'POST':
        if 'newpassword' in request.POST:
            user = Usertable.objects.get(email=request.session["email"])
            user.set_password(request.POST['newpassword'])
            user.save()
            return redirect('user_login')
        elif 'otp' in request.POST:
            if request.session["otp"] == request.POST["otp"]:
                otp = "valid"
                # user = Usertable.objects.get(email=request.session["email"])
                return render(request, "forgotPassword.html", {"otp":otp})
            else:
                return HttpResponse("Invalid OTP")
        elif 'email' in request.POST:
            userEmail = request.POST['email']
            if Usertable.objects.filter(email=userEmail).exists():
                request.session["otp"]=generate_otp()
                user = Usertable.objects.get(email=userEmail)
                request.session["email"] = user.email
                valid = "true"
                subject = 'Hello, User'
                message = 'This is a email to Reset your Password\n The OTP to Change Password is : '+request.session["otp"]
                from_email = "spotigoturfcorporation@gmail.com"
                recipient_list = [userEmail]
                send_mail(subject, message, from_email, recipient_list)
                return render(request, "forgotPassword.html", {"valid":valid})
            else:
                return HttpResponse("User Doesn't Exists")
        return True
    return render(request, "forgotPassword.html")

def generate_otp(length=6):
    characters = string.digits  # Use digits (0-9) for OTP generation
    otp = ''.join(random.choice(characters) for _ in range(length))
    return otp

def adminreg(request):
    # Query all User objects (using the custom user model) from the database
    User = get_user_model()
    user_profiles = User.objects.all()
    
    # Pass the data to the template
    context = {'user_profiles': user_profiles}
    
    # Render the HTML template
    return render(request, 'adminreg.html', context)