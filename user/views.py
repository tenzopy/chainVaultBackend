from django.shortcuts import render,redirect
from .models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import validators
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from .token import generate_token
from django.template.loader import render_to_string
from django.core.mail import send_mail

# Create your views here.

def signup(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not name.isalnum() or name.isnumeric() or len(name) > 20:
            error_message = {
                'error' : 'Username should contain alphabets and numbers only'
            }
            return render(request,'login.html',error_message)
        elif not validators.email(email):
            error_message = {
                'error' : 'Invalid Email'
            }
            return render(request,'login.html',error_message)
        elif len(password)<8 or len(password)>15 :
            error_message = {
                'error' : 'Invalid Password'
            }
            return render(request,'login.html',error_message)
        if User.objects.filter(email=email).exists():
            error_message = {
                'error' : 'Account already exists !'
            }
            return render(request,'login.html',error_message)
        else:
            user = User.objects.create_user(first_name=name,email=email,password=password)
            user.is_active = False
            user.save()

            # Email Confirmation
            uid = urlsafe_base64_encode(force_bytes(user.email))
            token = generate_token.make_token(user)

            Subject = "Welcome to Sliceit URL Shortener, Confirm Your E-Mail."
            current_site = get_current_site(request)
            HTML_Message = render_to_string('users/email_confirmation.html', {

            'name': user.name,
            'domain': current_site.domain,
            'uid': uid,
            'token': token

            })
            Plain_Message = render_to_string('users/email_confirmation_plain.html', {

            'name': user.name,
            'domain': current_site.domain,
            'uid': uid,
            'token': token

            })

            send_mail(Subject, Plain_Message, from_email=None, recipient_list=[user.email], html_message=HTML_Message, fail_silently=True)

            return render(request,'users/confirm_email_page.html')

    return redirect(reverse('login'))

def activate(request, uidb64, token, backend='django.contrib.auth.backends.ModelBackend'):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(email=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and generate_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return render(request,'users/confirm_email_success.html')
    else:
        return render(request, 'users/confirm_email_failed.html')
    

def signin(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        remember_me = request.POST['remember_me']
        if not validators.email(email):
            error_message = {
                'error' : 'Invalid Email'
            }
            return render(request,'login.html',error_message)
        elif len(password)<8 or len(password)>15 :
            error_message = {
                'error' : 'Invalid Password'
            }
            return render(request,'login.html',error_message)
        user = authenticate(email=email,password=password,backend='django.contrib.auth.backends.ModelBackend')
        if user:
            if user.is_active:
                login(request,user,backend='django.contrib.auth.backends.ModelBackend')
                if remember_me == 'True':
                    request.session.set_expiry(604800)
                else:
                    request.session.set_expiry(0)
                return redirect(reverse('profile'))
        else:
            error_message = {
                'error' : 'Incorrect Email or Password !'
            }
            return render(request,'login.html',error_message)
    error_message = {
            'error' : ''
        }
    return render(request,'login.html',error_message)
    
def signout(request):
    logout(request)
    return redirect(reverse('home'))