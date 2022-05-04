from django.shortcuts import render, redirect, reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.http import HttpResponse
from Recommender.constants import Constants
from Recommender.models import BsvUser
from Recommender.tokens import account_activation_token
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
import re
from django.contrib.auth import authenticate, login
from django.core import mail


def signup(request):
    return render(request, 'Recommender/bsv_signup.html')


def is_valid_email(email):
    is_valid = False
    match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)
    if match is not None:
        is_valid = True
    return is_valid


def email_validation(request):
    if request.method == "GET":
        p = request.GET.copy()
        response = 0
        if 'email' in p:
            email = p['email']
            if email != '':
                if is_valid_email(email):
                    if not User.objects.filter(username__iexact=email):
                        # E-mail as username available
                        response = 3
                    else:
                        # E-mail as username already in db
                        response = 2
                else:
                    # Incorrect e-mail format
                    response = 1
            else:
                # E-mail field is empty
                response = 0
        if request.session['lang'] == 'es' and (response == 3 or response == 2 or response == 1):
            response += 3
        return HttpResponse(response)


def is_password_strong(password):
    is_strong = False
    # At least MIN_LENGTH long
    if len(password) >= Constants.PWD_MIN_LENGTH:
        # At least one letter and at least one digit/punctuation
        if any(c.isalpha() for c in password) and not password.isalpha():
            is_strong = True
    return is_strong


def password_validation(request):
    # There is no password1 input - response 0
    response = 0
    if request.method == "GET":
        p = request.GET.copy()
        if 'password1' in p:
            pwd1 = p['password1']
            if pwd1 != '':
                # There is password1 input, incorrect format - response 1
                response += 1
                if is_password_strong(pwd1):
                    # There is password1 input, correct format - response 2
                    response += 1
                    if 'password2' in p:
                        pwd2 = p['password2']
                        if pwd2 != '':
                            # There is also password2 input, not same as password1 - response 3
                            response += 1
                            if pwd2 == pwd1:
                                # There is also password2 input, same as password1 - response 4
                                response += 1
    if request.session['lang'] == 'es' and (response == 3 or response == 1):
        response += 4
    return HttpResponse(response)


def register_button_validation(request):
    is_usr_pwd_valid = False
    if request.session['lang'] == 'ca':
        if email_validation(request).content == str(3) and password_validation(request).content == str(4):
            is_usr_pwd_valid = True
    elif request.session['lang'] == 'es':
        if email_validation(request).content == str(6) and password_validation(request).content == str(4):
            is_usr_pwd_valid = True
    return HttpResponse(is_usr_pwd_valid)


def user_registration(request):
    form = UserCreationForm(request.POST)
    password = form.is_valid()
    if password:
        # Get user from form
        user = form.save()
        user.first_name = form.data.get('first_name')
        user.email = user.username
        user.save()
        # Save new Bsv user
        new_user = BsvUser(user=user,
                           language=request.session['lang'])
        new_user.save()
        # Depending on email confirmation
        if Constants.EMAIL_CONFIRMATION:
            # new_user.user_view = 'Recommender:user_confirmation'
            # User not active until activation
            new_user.user.is_active = False
            new_user.user.save()
            new_user.save()
            send_confirmation_email(request, new_user)
            template_name = 'Recommender/user_confirmation.html'
            context = {
                'user_email': user.email,
            }
            return render(request, template_name, context)
        else:
            # Login new user
            login_user = request.POST['username']
            login_pwd = request.POST['password1']
            user_auth = authenticate(request, username=login_user, password=login_pwd)
            login(request, user_auth)
            request.session['lang'] = new_user.language
            # Go to Data Entry (User form)
            return redirect(reverse('Recommender:profile_manager_menu') + '?user=' + str(new_user.id))
    else:
        # TODO: something went wrong page instead of oops
        return render(request, 'Recommender/oops.html')


def user_confirmation(request):
    return render(request, 'Recommender/user_confirmation.html')


def send_confirmation_email(request, new_user):
    username = new_user.user.username
    user = new_user.user
    user_email = username
    subject = 'Banda Sonora Vital: Confirmar usuari'
    message = render_to_string('Recommender/user_confirmation_msg.html', {
        'user': user,
        'domain': get_current_site(request),
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    email_from = 'bandasonoravital@upf.edu'
    email_to = [user_email]
    with mail.get_connection() as connection:
        mail.EmailMessage(
            subject, message,
            email_from, email_to,
            connection=connection,
        ).send()


def user_activation(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        # Activate User
        user.bsvuser.user_view = 'Recommender:profile_manager_menu'
        user.is_active = True
        user.save()
        user.bsvuser.save()
        # Redirect to BSV Login Page
        return redirect('Recommender:login')
    else:
        # TODO: something went wrong page instead of oops
        return render(request, 'Recommender/oops.html')


def forgot_password(request):
    return render(request, 'Recommender/forgot_password.html')


def send_reset_password_email(request):
    username = request.POST['username']
    user = User.objects.get(username=username)
    user_email = username
    subject = 'Banda Sonora Vital: Canviar contrasenya'
    message = render_to_string('Recommender/forgot_password_msg.html', {
        'user': user,
        'domain': get_current_site(request),
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    email_from = 'bandasonoravital@upf.edu'
    email_to = [user_email]
    with mail.get_connection() as connection:
        mail.EmailMessage(
            subject, message,
            email_from, email_to,
            connection=connection,
        ).send()
    template_name = 'Recommender/forgot_password_sent.html'
    context = {
        'user_email': user_email,
    }
    return render(request, template_name, context)


def reset_password(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        request.session['reset_pwd_username'] = user.username
        request.session['reset_pwd_id'] = user.id
        return render(request, 'Recommender/reset_password.html')
    else:
        # TODO: something went wrong page instead of oops
        return render(request, 'Recommender/oops.html')


def reset_pwd_button_validation(request):
    is_usr_pwd_valid = False
    if request.session['lang'] == 'ca':
        if email_validation(request).content == str(2) and password_validation(request).content == str(4):
            is_usr_pwd_valid = True
    elif request.session['lang'] == 'es':
        if email_validation(request).content == str(5) and password_validation(request).content == str(4):
            is_usr_pwd_valid = True
    return HttpResponse(is_usr_pwd_valid)


def save_new_password(request):
    username = request.POST.get('username')
    password = make_password(request.POST.get('password1'))
    user = User.objects.get(username=username)
    if username == request.session['reset_pwd_username'] and user.id == request.session['reset_pwd_id']:
        user.password = password
        user.save()
        return render(request, 'Recommender/reset_password_done.html')
    else:
        # TODO: something went wrong page instead of oops
        return render(request, 'Recommender/oops.html')
