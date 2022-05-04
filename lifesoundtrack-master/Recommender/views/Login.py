from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User


def bsv_login(request):
    # Load BSV Login Page
    template_name = 'Recommender/bsv_login.html'
    return render(request, template_name)


def user_login(request):
    username = request.POST.get('inputUsername')
    password = request.POST.get('inputPassword')
    user = authenticate(request, username=username, password=password)

    if User.objects.filter(username__iexact=username).exists():
        # User exists
        if user is not None:
            # User exists and it's active
            login(request, user)
            request.session['lang'] = user.bsvuser.language
            if request.session['lang'] is None:
                request.session['lang'] = 'ca'
        return redirect(reverse('Recommender:profile_manager_menu') + '?user=' + str(user.bsvuser.id))
    else:
        # Render oops page because of access error:
        template_name = 'Recommender/bsv_login_error.html'
        return render(request, template_name)