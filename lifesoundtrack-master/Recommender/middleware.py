from django.utils import translation


class ForceLangMiddleware:

    def process_request(self, request):
        if request.session.get(u'lang') is None:
            request.LANG = 'ca'
        else:
            request.LANG = request.session['lang']
        translation.activate(request.LANG)
        request.LANGUAGE_CODE = request.LANG