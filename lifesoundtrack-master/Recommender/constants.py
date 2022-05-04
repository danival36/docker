# -*- coding: UTF-8 -*-

# CONSTANTS CLASS:
#
# This class contains all the constraints of the project.
# In order to use them we must import this class as follows:
# from Recommender.constants import Constants
# And after that we use Constants.CONTANT_NAME
import os


class Constants(object):

    # USERS
    PWD_MIN_LENGTH = 8
    EMAIL_CONFIRMATION = False
    LAST_BIRTH_YEAR_FOR_HITS = 1975

    # PARAMETERS
    NUMBER_OF_FIELDS = 10
    NUMBER_OF_GENRES = 34
    WAITING_TIME = 5

    # PLAYLIST
    MAX_SONGS_PER_ARTIST = 4
    CANDIDATES_MULTIPLE = 4
    PLAYLIST_LENGTH = [10, 15, 20, 25, 30]
    DIRECT_SONGS = [4, 6, 8, 10, 10]
    PREF_ARTISTS_SONGS = [1, 2, 3, 4, 5]
    SIMILARITY_SONGS = [2, 4, 5, 6, 8]
    GENRE_SONGS = [1, 1, 1, 2, 3]
    YOUTH_HIT_SONGS = [2, 2, 3, 3, 4]

    # HITS
    USER_POPULARITY_TO_BE_HIT = 5

    # SPOTIFY
    SPOTIFY_USERNAME = 'lifesoundtrackproject'
    SPOTIPY_CLIENT_ID = ''
    SPOTIPY_CLIENT_SECRET = ''
    SPOTIPY_SCOPE = 'playlist-modify-public'
    SPOTIPY_REDIRECT_URI = 'http://localhost/spotify_redirect'
    SPOTIFY_CACHE = os.path.join(os.environ['HOME'], 'log', '.cache-')

    # YOUTUBE
    YOUTUBE_ACTIVE = True
    YOUTUBE_KEY = ''
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'
