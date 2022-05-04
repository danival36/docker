from django.shortcuts import render, redirect


def home(request):
    """
    Return home page
    """
    template_name = 'Recommender/home.html'
    if request.session.get(u'lang') is None:
        request.session['lang'] = 'ca'
    return render(request, template_name)


def switch_language(request):
    if request.session['lang'] == 'ca':
        request.session['lang'] = 'es'
    elif request.session['lang'] == 'es':
        request.session['lang'] = 'ca'
    home_page = 'Recommender:home'
    return redirect(home_page)
