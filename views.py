from decimal import Decimal
import random
import string
from django.contrib.auth import login, logout, authenticate ,get_user_model

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from .models import *
from django.contrib import messages 
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.utils.dateparse import parse_date
from .models import TurfProvider
from django.contrib.auth import login
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from .forms import TurfImageForm, TurfListingForm
from django.views.decorators.csrf import csrf_exempt




from io import BytesIO
import base64
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

def generate_pie_chart(normal_users_count, club_users_count, turf_providers_count):
    # Data
    labels = ['Normal Users', 'Club Users', 'Turf Providers']
    sizes = [normal_users_count, club_users_count, turf_providers_count]
    colors = ['#66b3ff', '#99ff99', '#c2c2f0']
    explode = (0.1, 0, 0)  # explode 1st slice (Admin)


    plt.figure(figsize=(6, 4))
    patches, texts, autotexts = plt.pie(
        sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', startangle=90,
        textprops={'color': 'white'}  # Set label text color to black
    )
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    for text in texts:
        text.set_fontsize(15)
    for autotext in autotexts:
        autotext.set_fontsize(12)


    chart_image = BytesIO()
    plt.savefig(chart_image, format='png', transparent=True)
    plt.close()  # Close the Matplotlib figure after saving it
    chart_image.seek(0)

    # Convert the BytesIO object to a base64-encoded string
    chart_image_base64 = base64.b64encode(chart_image.getvalue()).decode('utf-8')

    return chart_image_base64


  

# @never_cache
def index(request):
    return render(request, "index.html")


def signup(request):
    if request.method == 'POST':
        role = request.POST['role']
        firstname = request.POST['fname']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        lastname = request.POST['lname']
        dob = request.POST['dob']
        password = request.POST['password']
        user = Usertable(first_name=firstname, last_name=lastname, role=role, dob=dob, email=email, phone_number=phone_number)
        user.set_password(password)
        user.save()

        
        messages.success(request, 'Registration successful. You can now log in.')

        return redirect('user_login')
    return render(request, "registration.html")




def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Try to retrieve the user by email from TurfProvider
            provider = TurfProvider.objects.get(email=email)

            if provider.is_active:
                if provider.password_updated:

                    if password == provider.random_password:
                        request.session['email'] = email
                        return redirect('providerhome')  # Redirect to providerhome.html
                    else:
                        error_message = "Invalid credentials."
                        messages.error(request, error_message)
                else:
                    # Redirect to the password update page
                    request.session['email'] = email
                    return redirect('provider_update')
            else:
                error_message = "Inactive user."
                messages.error(request, error_message)
        except TurfProvider.DoesNotExist:
            
            try:
                user = Usertable.objects.get(email=email)
                
                if user.is_active and check_password(password, user.password):
                    request.session['email'] = email
                    login(request, user)

                    if user.role == 'admin':
                        return redirect('adminreg')
                    elif user.role == 'normal_user' or user.role == 'club_user':  
                        return redirect('index2')

                else:
                    error_message = "Invalid credentials or inactive user."
                    messages.error(request, error_message)
            except Usertable.DoesNotExist:
                error_message = "User does not exist."
                messages.error(request, error_message)

    response = render(request, 'login.html')
    response['Cache-Control'] = 'no-store, must-revalidate'
    return response



def provider_update(request):
    user_email = request.session.get('email')
    provider = TurfProvider.objects.get(email=user_email)

    if request.method == 'POST':
        
        new_password = request.POST.get('new_password')

        # Update the random_password field in the TurfProvider model
        provider.random_password = new_password
        provider.password_updated = True  # Set the flag to True
        provider.save()

        # Optionally, you can add a success message
        messages.success(request, 'Password updated successfully.')

        # Redirect the user to the providerhome page
        return redirect('providerhome')

    context = {
        'provider': provider,
    }

    return render(request, 'providerupdate.html', context)




def providerhome(request):
    if 'email' in request.session:
        # Retrieve the TurfProvider object for the authenticated provider
        provider  = TurfProvider.objects.get(email=request.session['email'])
        
        # Retrieve the list of turfs associated with the provider
        your_turfs = TurfListing.objects.filter(turf_provider=provider)

        # Get the count of the provider's turfs
        turf_count = your_turfs.count()

        # Retrieve booking details for the provider's turfs
        bookings = Booking.objects.filter(turf_listing__in=your_turfs)
        
        context = {
            'provider_name': provider.venue_name,
            'your_turfs': your_turfs,  # Pass the list of turfs to the template
            'turf_count': turf_count,  # Pass the count of turfs to the template
            'bookings': bookings  # Pass the list of booking details to the template
        }

        response = render(request, 'providerhome.html', context)
        response['Cache-Control'] = 'no-store, must-revalidate'
        return response
        
    else:
        return redirect('index')

def userLogout(request):
    logout(request) 
    return redirect('index')

def index2(request):
    if 'email' in request.session:
        # Fetch available turfs from the database
        available_turfs = TurfListing.objects.filter(is_available=True)

        response = render(request, 'index2.html', {'available_turfs': available_turfs})
        response['Cache-Control'] = 'no-store, must-revalidate'
        return response
    else:
        return redirect('index')

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
    if not request.session.get('email'):
        return redirect('index')  # Redirect to the index page if the user is not logged in

    if request.method == 'POST':
        
        for user in Usertable.objects.all():
            if user.email in request.POST:
                new_status = request.POST.get(user.email) == 'on'
                if user.is_active != new_status:
                    user.is_active = new_status
                    user.save()

                    # Send email notification for both active and inactive status changes
                    send_status_change_notification(user, new_status)

        for provider in TurfProvider.objects.all():
            if provider.email in request.POST:
                new_status = request.POST.get(provider.email) == 'on'
                if provider.is_active != new_status:
                    provider.is_active = new_status
                    provider.save()

                   
                    random_password = generate_random_password()
                    provider.random_password = random_password
                    provider.save()

                    
                    send_turf_provider_activation_notification(provider, random_password, new_status)

  
    total_users = Usertable.objects.count() + TurfProvider.objects.count()
   
    pending_providers = TurfProvider.objects.filter(is_active=False)
    
   
    admin_count = Usertable.objects.filter(role='admin').count()
    normal_users_count = Usertable.objects.filter(role='normal_user').count()
    club_users_count = Usertable.objects.filter(role='club_user').count()
    turf_providers_count = TurfProvider.objects.count()

   
    pie_chart_image = generate_pie_chart(normal_users_count, club_users_count, turf_providers_count)





    admin_users = Usertable.objects.filter(role='admin')
    normal_users = Usertable.objects.filter(role='normal_user')
    club_users = Usertable.objects.filter(role='club_user')
    turf_providers = TurfProvider.objects.all()
    

    context = {
        'admin_users': admin_users,
        'normal_users': normal_users,
        'club_users': club_users,
        'turf_providers': turf_providers,
        'total_users': total_users,
        'pending_providers': pending_providers,
        'pie_chart_image': pie_chart_image,
        
    }

    return render(request, 'adminreg.html', context)

def send_status_change_notification(user, new_status):
    subject = "Your Status Change Notification"
    if new_status:
        message = "Your status on Sportigo has been updated. Your new status is: Active"
    else:
        message = "Your status on Sportigo has been updated. Your new status is: Inactive"
    from_email = "sportigoplayspot@gmail.com"  # Your email address
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)

def generate_random_password():
    password_length = 10
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(password_length))

def send_turf_provider_activation_notification(provider, random_password,new_status):

    subject = 'Turf Provider Account Activation'
    if new_status:
        message = f'Congratulations! Your Turf Provider account is now verified by the admin. Your initial password is: {random_password}'
    else:
        message = "Sorry,your request for joining sportigo is rejected"

    from_email = 'sportigoplayspot@gmail.com'
    recipient_list = [provider.email]
    send_mail(subject, message, from_email, recipient_list)

def turfproviderreg(request):
    if request.method == 'POST':
        venue_name = request.POST.get('venue_name')
        email = request.POST.get('email')
        contact_number = request.POST.get('contact_number')
        document = request.FILES['document']
        sports_type = request.POST.get('sports_type')
        address = request.POST.get('address')
        location = request.POST.get('location') 

        
        turf_provider = TurfProvider(
            venue_name=venue_name,
            email=email,
            contact_number=contact_number,
            document=document,
            sports_type=sports_type,
            address=address,
            location=location
        )
        turf_provider.save()

        # Redirect to a success page or do something else
        return redirect('index')  # Change 'registration_success' to the appropriate URL
    return render(request, 'turfproviderreg.html')


from django.contrib import messages as django_messages
@login_required
def user_profile(request):
    user = request.user
    formatted_dob = user.dob.strftime('%Y-%m-d') if user.dob else ''

  
    messages = django_messages.get_messages(request)

    context = {'user': user, 'formatted_dob': formatted_dob, 'messages': messages}
    return render(request, 'userprofile.html', context)


@login_required
def update_user_details(request):

    if request.method == 'POST':

        new_first_name = request.POST.get('new_first_name')
        new_last_name = request.POST.get('new_last_name')
        new_phone_number = request.POST.get('new_phone_number')  # Add this line

        # Update the user's details in the database
        user = request.user

        user.first_name = new_first_name
        user.last_name = new_last_name
        user.phone_number = new_phone_number  # Add this line
        user.save()

        messages.success(request, 'User details updated successfully.')
        return redirect('user_profile')  # Redirect to the user profile page

    return render(request, 'userprofile.html')

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully changed.')
            return redirect('user_profile')  # Redirect to the user profile page
        else:
            if 'password_incorrect' in form.errors:
                messages.error(request, 'The old password you entered is incorrect.')
            elif 'password_mismatch' in form.errors:
                messages.error(request, 'The new passwords do not match.')
            else:
                messages.error(request, 'There was an error with your password change.')

            # Print form errors for debugging
            print(form.errors)

    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'userprofile.html', {'form': form})




def add_turf(request):
    if request.method == 'POST':
        turf_form = TurfListingForm(request.POST)
        image_form = TurfImageForm(request.POST, request.FILES)

        if turf_form.is_valid() and image_form.is_valid():
            turf_listing = turf_form.save(commit=False)
            turf_listing.turf_provider = TurfProvider.objects.get(email=request.session['email'])
            turf_listing.save()

            for f in request.FILES.getlist('images'):
                TurfImage.objects.create(turf_listing=turf_listing, image=f)

            return redirect('providerhome')

    else:
        turf_form = TurfListingForm()
        image_form = TurfImageForm()

    return render(request, 'addturf.html', {'turf_form': turf_form, 'image_form': image_form})






from datetime import datetime, timedelta
from django.shortcuts import render, HttpResponseRedirect
from .models import TurfListing
from django.db.models import Q

import razorpay

from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from .models import TurfListing, Booking
from datetime import datetime, timedelta
from django.db.models import Q

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from datetime import datetime, timedelta
from .models import TurfListing, Booking
from django.db.models import Q

@login_required
def turf_detail(request, turf_id):
    if request.method == 'POST':
        selected_time_slot = request.POST.get('selected_time_slot')
        selected_date = request.POST.get('booking_date')

        if not selected_time_slot or not selected_date:
            return HttpResponse("Please select a date and time slot")

        start_time_str, end_time_str = selected_time_slot.split(' - ')
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()
        turf = get_object_or_404(TurfListing, id=turf_id)
        total_cost = ((end_time.hour - start_time.hour) + 1) * turf.price_per_hour
        amount = total_cost
        amount *= Decimal('100')
        user = request.user

        existing_bookings = Booking.objects.filter(
            Q(booking_date=selected_date),
            Q(start_time__lte=start_time, end_time__gte=start_time) |
            Q(start_time__lte=end_time, end_time__gte=end_time),
            turf_listing=turf
        )

        if existing_bookings.exists():
            messages.error(request, 'This time slot is already booked. Please choose another time.')
            return redirect('turf_detail', turf_id=turf_id)

        # Storing booking information in session
        request.session['selected_date'] = selected_date
        request.session['start_time'] = start_time.strftime('%H:%M')
        request.session['end_time'] = end_time.strftime('%H:%M')
        request.session['turf_id'] = turf_id
        request.session['total_cost'] = float(total_cost)
        
        

        # Redirect to the confirmation page if the time slot is available
        context = {
            'turf': turf,
            'selected_date': selected_date,
            'start_time': start_time,
            'end_time': end_time,
            'total_cost': total_cost,
            'amount': amount
        }

        return render(request, 'confirmation.html', context)

    turf = get_object_or_404(TurfListing, id=turf_id)
    available_from = turf.available_from
    available_to = turf.available_to
    time_slots = []

    while available_from < available_to:
        time_slots.append(
            available_from.strftime('%H:%M') + ' - ' + (datetime.combine(datetime.today(), available_from) + timedelta(minutes=59)).strftime('%H:%M')
        )
        available_from = (datetime.combine(datetime.today(), available_from) + timedelta(hours=1)).time()

    context = {
        'turf': turf,
        'time_slots': time_slots
    }

    return render(request, 'turf_detail.html', context)


from django.shortcuts import get_object_or_404



from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Booking, TurfListing
from decimal import Decimal
import razorpay

from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Booking, TurfListing
from decimal import Decimal
import razorpay

@csrf_exempt
def confirmation(request):
    if request.method == 'POST':
        amount = 50000 
        
        client = razorpay.Client(auth=("rzp_test_gfHLcbNXLAqvpT", "2RsNQRDiZYjnJuYIuMVA4cDr"))
        payment = client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture': '1'})
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        
        if razorpay_payment_id:
            # Retrieve booking details from session or request.POST
            selected_date = request.session.get('selected_date')
            start_time = request.session.get('start_time')
            end_time = request.session.get('end_time')
            turf_id = request.session.get('turf_id')
            total_cost = Decimal(request.session.get('total_cost'))
            user = request.user
            
            # Get TurfListing instance
            turf = get_object_or_404(TurfListing, id=turf_id)
            
            # Create and save Booking instance
            booking = Booking.objects.create(
                user=user,
                turf_listing=turf,
                turf_provider=turf.turf_provider,  # Replace 'turf.provider' with appropriate attribute or remove if not needed
                booking_date=selected_date,
                start_time=start_time,
                end_time=end_time,
                total_cost=total_cost
            )
            
            # Construct email content without using a template
            subject = 'Booking Confirmation'
            from_email = 'sportigoplayspot@gmail.com'  # Replace with your email
            to_email = user.email
            
            email_content = (
                f"Dear {user.email},\n\n"
                f"Your booking with ID: {booking.id} has been confirmed.\n"
                f"Booking Date: {selected_date}\n"
                f"Start Time: {start_time}\n"
                f"End Time: {end_time}\n"
                f"Total Cost: {total_cost}\n\n"
                "Thank you for booking with us!\n\n"
                "Regards,\nThe Sportigo Team"
            )
            
            # Send the email
            email = EmailMultiAlternatives(subject, email_content, from_email, [to_email])
            email.send()
            
            messages.success(request, 'Payment successful! Booking confirmed. Email sent.')
            return redirect('booking_history')
        else:
            messages.error(request, 'Payment unsuccessful. Please try again.')
            return redirect('turf_detail', turf_id=turf_id)
        
    return render(request, 'confirmation.html', {'payment': payment})


from django.contrib import messages

@login_required
def booking_history(request):
    # Retrieve the user's booking history
    user_bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    messages_list = messages.get_messages(request)
    context = {
        'user_bookings': user_bookings,
        'messages': messages_list
    }

    return render(request, 'booking_history.html', context)


from django.shortcuts import get_object_or_404

from django.shortcuts import get_object_or_404

from django.shortcuts import get_object_or_404

def manage_turf(request, turf_id):
    # Get the existing turf instance
    turf = get_object_or_404(TurfListing, id=turf_id)

    if request.method == 'POST':
        # Create the form with the submitted data and instance
        form = TurfListingForm(request.POST, instance=turf)
        if form.is_valid():
            updated_turf = form.save(commit=False)

            # Check if new images are uploaded
            new_images = request.FILES.getlist('images')
            if new_images:
                # Delete existing images not included in the updated list
                existing_images = turf.images.all()
                for existing_image in existing_images:
                    if existing_image.image not in new_images:
                        existing_image.delete()

                # Add or update new images
                for f in new_images:
                    TurfImage.objects.create(turf_listing=updated_turf, image=f)

            updated_turf.save()  # Save the updated turf details
            return redirect('providerhome')

    else:
        # Create the form with the existing turf data
        form = TurfListingForm(instance=turf)

    return render(request, 'manage_turf.html', {'form': form, 'turf': turf})






from django.http import JsonResponse
from django.db.models import Q

from django.shortcuts import render
from django.http import JsonResponse
from .models import TurfListing, TurfImage
from django.db.models import Q

def search(request):
    query = request.GET.get('query')
    search_results = []

    if query:
        # Query the database for matching TurfListings by turf name or location
        turfs = TurfListing.objects.filter(
            Q(turf_name__icontains=query) | Q(location__icontains=query)
        )

        # Create a list of results with the required attributes and single image for each turf
        for turf in turfs:
            # Retrieve the first image for the turf, if available
            image = TurfImage.objects.filter(turf_listing=turf).first()
            image_url = image.image.url if image else None

            search_results.append({
                'turf_name': turf.turf_name,
                'location': turf.location,
                'image_url': image_url,
                'id': turf.id,
                'price_per_hour': turf.price_per_hour,
            })

    return JsonResponse(search_results, safe=False)




# @csrf_exempt
# def confirmation(request):
#     if request.method == 'POST':
#         amount = 50000 
        
#         client = razorpay.Client(auth=("rzp_test_gfHLcbNXLAqvpT", "2RsNQRDiZYjnJuYIuMVA4cDr"))
#         payment = client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture': '1'})
#         razorpay_payment_id = request.POST.get('razorpay_payment_id')
#         if razorpay_payment_id:
#             messages.success(request, 'Payment successful!')
#             #save the booking instance here if the payment success
#             return redirect('booking_history')
#         else:
#             return HttpResponse("Invalid request method")
        
        
#     return render(request, 'confirmation.html', {'payment': payment})
    
# from .models import Booking
# from datetime import datetime

# @csrf_exempt
# def confirmation(request):
#     if request.method == 'POST':
#         amount = 50000 
        
#         # Assuming the payment is successful and razorpay_payment_id is received
#         razorpay_payment_id = request.POST.get('razorpay_payment_id')
        
#         if razorpay_payment_id:
#             # Assuming all necessary data like turf_id, selected_date, start_time, end_time, total_cost are available in session or POST data
#             turf_id = request.session.get('turf_id')
#             selected_date = request.session.get('selected_date')
#             start_time = datetime.strptime(request.session['start_time'], '%H:%M:%S').time()
#             end_time = datetime.strptime(request.session['end_time'], '%H:%M:%S').time()
#             total_cost = Decimal(request.session['total_cost'])
            
#             # Fetching turf instance
#             turf = TurfListing.objects.get(id=turf_id)
            
#             # Creating a Booking instance after successful payment
#             booking = Booking.objects.create(
#                 user=request.user,
#                 turf_listing=turf,
#                 turf_provider=turf.provider,  # Assuming there's a reference to the turf provider in TurfListing model
#                 booking_date=selected_date,
#                 start_time=start_time,
#                 end_time=end_time,
#                 total_cost=total_cost
#             )
            
#             # Clear session data after booking creation
#             request.session.pop('turf_id', None)
#             request.session.pop('selected_date', None)
#             request.session.pop('start_time', None)
#             request.session.pop('end_time', None)
#             request.session.pop('total_cost', None)
            
#             messages.success(request, 'Payment successful! Your booking has been confirmed.')
#             return redirect('booking_history')  # Redirect to booking history or another page
            
#         else:
#             return HttpResponse("Invalid request method")
        
#     return render(request, 'confirmation.html', {'payment': razorpay.Payment})

        




# def add_turf(request):
#     if request.method == 'POST':
#         # Create the form with the submitted data
#         form = TurfListingForm(request.POST, request.FILES)
#         if form.is_valid():
#             # Associate the TurfProvider with the TurfListing
#             turf_listing = form.save(commit=False)
#             turf_listing.turf_provider = TurfProvider.objects.get(email=request.session['email'])
#             turf_listing.save()
#             return redirect('providerhome')

#     else:
#         form = TurfListingForm()

#     return render(request, 'addturf.html', {'form': form})



#before counting values to adminreg quickstat
# def adminreg(request):
#     if not request.session.get('email'):
#         return redirect('index')  # Redirect to the index page if the user is not logged in

#     if request.method == 'POST':
#         # Handle status change for users
#         for user in Usertable.objects.all():
#             if user.email in request.POST:
#                 new_status = request.POST.get(user.email) == 'on'
#                 if user.is_active != new_status:
#                     user.is_active = new_status
#                     user.save()

#                     # Send email notification for both active and inactive status changes
#                     send_status_change_notification(user, new_status)

#         # Handle status change for TurfProvider users
#         for provider in TurfProvider.objects.all():
#             if provider.email in request.POST:
#                 new_status = request.POST.get(provider.email) == 'on'
#                 if provider.is_active != new_status:
#                     provider.is_active = new_status
#                     provider.save()

#                     # Generate a random password
#                     random_password = generate_random_password()
#                     provider.random_password = random_password
#                     provider.save()

#                     # Send email notification for activation with a random password
#                     send_turf_provider_activation_notification(provider, random_password, new_status)

#     # Retrieve users based on their roles
#     admin_users = Usertable.objects.filter(role='admin')
#     normal_users = Usertable.objects.filter(role='normal_user') 
#     club_users = Usertable.objects.filter(role='club_user')
#     turf_providers = TurfProvider.objects.all()

#     context = {
#         'admin_users': admin_users,
#         'normal_users': normal_users,
#         'club_users': club_users,
#         'turf_providers': turf_providers,
#         # Add more role-specific user lists to the context
#     }

#     return render(request, 'adminreg.html', context)





#first userlogin before turf_provider
# def user_login(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')

#         try:
#             # Try to retrieve the user by email
#             user = Usertable.objects.get(email=email)

#             # Check if the user is active
#             if user.is_active and check_password(password, user.password):
#                 request.session['email'] = email
#                 login(request, user)
                
#                 # Check the role and redirect accordingly
#                 if user.role == 'admin':
#                     return redirect('adminreg')
#                 elif user.role == 'normal_user':
#                     return redirect('index2')
#                 elif user.role == 'club_user':
#                     return redirect('index2')
                
#                 # Add more role-based redirects if needed
                
#             else:
#                 error_message = "Invalid credentials or inactive user."
#                 messages.error(request, error_message)
#         except Usertable.DoesNotExist:
#             error_message = "User does not exist."
#             messages.error(request, error_message)

#     response = render(request, 'login.html')
#     response['Cache-Control'] = 'no-store, must-revalidate'
#     return response






#last adminreg before session
# def adminreg(request):
#     if request.method == 'POST':
#         for user in Usertable.objects.all():
#             if user.email in request.POST:
#                 new_status = request.POST.get(user.email) == 'on'
#                 if user.is_active != new_status:
#                     user.is_active = new_status
#                     user.save()

#                     # Send email notification for both active and inactive status changes
#                     send_status_change_notification(user, new_status)

#         # Handle status change for TurfProvider users
#         for provider in TurfProvider.objects.all():
#             if provider.email in request.POST:
#                 new_status = request.POST.get(provider.email) == 'on'
#                 if provider.is_active != new_status:
#                     provider.is_active = new_status

