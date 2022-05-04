from django.shortcuts import render

import spotipy
import logging

logger = logging.getLogger('app')
not_found_logger = logging.getLogger('notfound')
spotify = spotipy.Spotify()


def oops(request):

    """
    Return oops page
    """
    template_name = 'Recommender/oops.html'
    return render(request, template_name)