from email import message
from lib2to3.pgen2.tokenize import generate_tokens
import math
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from gfg import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from . token import generate_token
from django.core.mail import EmailMessage, send_mail
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

# Create your views here.
def home(request):
    return render(request, "authentication/index.html")

def signup(request):

    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]

        if User.objects.filter(username = username):
            messages.error(request, "Username already exist! Please try some other username")
            return redirect('home')
        if User.objects.filter(email = email):
            messages.error(request, "Email already registered!")
            return redirect('home')
        if len(username)>10:
            messages.error(request, "Username must be under 10 characteres")
        if pass1 != pass2:
            messages.error(request, "Passwords didn't match")
        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric")
            return redirect('home')

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False

        myuser.save()

        messages.success(request, "Your Account has been Succesfully Created. We sent you a confirmation email, please confirm your email in order to activate your account")


        #Welcome Email

        subject = "Welcome to World of Electric Vehicle Login!"
        message = "Hello "+ myuser.first_name + "!! \n" + "Welcome to World of Electric Vehicle!! \n Thank you for visiting our website \n we have also send you a confirmation email, please confirm your email address in order to activate your account,  \n\n Thanking You\n  Kajal"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently = True)


        #Email Address Confirmation Email:
        current_site = get_current_site(request)
        email_subject = "Confirm your email @ Worls of Electric Vehicle Login !!"
        message2 = render_to_string('email_confirmation.html',{
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token' : generate_token.make_token(myuser),
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()
        return redirect('signin')

    return render(request, "authentication/signup.html")


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            fname = user.first_name

            return render(request, "authentication/calculations.html",{'fname':fname,})
        else:
            messages.error(request, "Bad Credintials")
            return redirect('home')
    return render(request, "authentication/signin.html")


def add(request):
    val1 = int(request.POST['a'])
    val2 = int(request.POST['b'])
    val3 = int(request.POST['c'])
    val4 = int(request.POST['d'])
    val5 = float(request.POST['e'])
    val6 = float(request.POST['f'])
    bv = val1 * val3
    bc = val2 * val4
    bw = bv * bc
    ew = (bw/100) * val5
    lh= int(ew/val6)
    lm= ((ew % val6)/val6)*60

    #Program For Rolling Resistance:
    urr = float(request.POST['g'])
    m = float(request.POST['h'])
    x = int(request.POST['i'])
    g = 9.8

    x1 = math.radians(x)
    x2 = math.cos(x1)

    Frr= urr * m * g * x2


    #Program for Calculating Aerodynamic Drag:

    p=1.204
    Cd = float(request.POST['j'])
    Vx = float(request.POST['k'])
    V= (Vx *1000)/3600
    Vxair= float(request.POST['l'])
    Vair = (Vxair * 1000) / 3600
    A= float(request.POST['m'])
    Fad= (1/2) * p * Cd *A * (V + Vair)  * (V + Vair)

    # Program for Calculating Gradient Force:
    x2 = math.sin(x1)
    Fg = m * g * x2

    #Program for Calculating Tractive Efforts:
    Fte= Frr + Fad + Fg

    #Program for Calculating Vehicle Range on Plane Road:
    Ex=float(request.POST['n'])
    E= Ex * 3600
    power= Fte * V
    dist= (E/power) * V
    dk = dist/1000


    #Program for Calculating Vehicle Motor Specifications:
    r = float(request.POST['o'])
    G= float(request.POST['p'])
    Ng=float(request.POST['q'])
    Tw = Fte * r

    Ww = V/r
    Tm = Tw/( G * Ng)
    Wm = Ww * G




    return render(request,'authentication/result.html',{'one':bv,'two':bc,'three':bw,'four':ew,'five':lh,'six':lm,'seven':Frr,'eight':Fad,'nine':Fg,'ten':Fte,'eleven':x,'twelve':E,'thirteen':dist,'fourteen':dk,'fifteen':Tm,'sixteen':Wm,'seventeen':power})

def calculations(request):
    return render(request, 'authentication/calculations.html')

def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!")
    return redirect('home')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None
    
    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')

