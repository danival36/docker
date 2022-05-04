# -*- coding: UTF-8 -*-

from django.shortcuts import redirect
from Recommender.constants import Constants
from Recommender.utils import similarity

import spotipy
from spotipy import oauth2
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials


def spotify_login(request):
    sp_oauth = oauth2.SpotifyOAuth(Constants.SPOTIPY_CLIENT_ID, Constants.SPOTIPY_CLIENT_SECRET,
                                   Constants.SPOTIPY_REDIRECT_URI, scope=Constants.SPOTIPY_SCOPE,
                                   cache_path=Constants.SPOTIFY_CACHE + Constants.SPOTIFY_USERNAME)

    token_info = sp_oauth.get_cached_token()

    if not token_info:
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    request.session['spotify_token'] = token_info
    # return redirect('Recommender:home')


def spotify_redirect(request):
    sp_oauth = oauth2.SpotifyOAuth(Constants.SPOTIPY_CLIENT_ID, Constants.SPOTIPY_CLIENT_SECRET,
                                   Constants.SPOTIPY_REDIRECT_URI, scope=Constants.SPOTIPY_SCOPE,
                                   cache_path=Constants.SPOTIFY_CACHE + Constants.SPOTIFY_USERNAME)

    code = request.GET.get('code')
    token_info = sp_oauth.get_access_token(code)

    if token_info:
        request.session['spotify_token'] = token_info
    return redirect('Recommender:home')


class SpotifyManager(object):
    def __init__(self):
        self.sp_oauth = None
        self.access_token = None
        self.spotify = None
        self.use_track_filter = True

    def get_token(self):
        self.sp_oauth = SpotifyClientCredentials(Constants.SPOTIPY_CLIENT_ID, Constants.SPOTIPY_CLIENT_SECRET)
        self.access_token = self.sp_oauth.get_access_token()
        self.spotify = spotipy.Spotify(auth=self.access_token)

    def get_cached_token(self, token):
        self.sp_oauth = SpotifyOAuth(Constants.SPOTIPY_CLIENT_ID, Constants.SPOTIPY_CLIENT_SECRET,
                                     Constants.SPOTIPY_REDIRECT_URI, scope=Constants.SPOTIPY_SCOPE,
                                     cache_path=Constants.SPOTIFY_CACHE + Constants.SPOTIFY_USERNAME)
        token_info = self.sp_oauth.get_cached_token()
        self.access_token = token_info['access_token'] if token_info else token['access_token']
        self.spotify = spotipy.Spotify(auth=self.access_token)
        self.spotify.trace = False

    def get_track(self, title, artist, get_all_results=False):
        self.get_token()

        # Build query
        if artist is not None:
            query = title + ' AND ' + artist
        else:
            query = title

        # Get results
        results = self.spotify.search(q=query, limit=20, type='track', market='ES')
        if get_all_results:
            return results
        else:
            if len(results['tracks']['items']) > 0:
                if self.use_track_filter:
                    track = self.filter_track(title, artist, results)
                else:
                    track = results['tracks']['items'][0]
            else:
                track = None
            return track

    def get_track_by_id(self, track_id):
        self.get_token()

        track = self.spotify.track(track_id)
        return track

    def get_genres(self, track_id):
        self.get_token()

        genres = []
        track = self.get_track_by_id(track_id)
        album_id = track.get('album').get('id')
        if album_id is not None:
            album = self.spotify.album(album_id)
            genres += album['genres']
        artist_id = track.get('artists')[0].get('id')
        artist = self.spotify.artist(artist_id)
        genres += artist['genres']
        return genres

    def filter_track(self, title, artist, results):
        track = None
        # Filter results
        for result in results['tracks']['items']:
            result_title = result['name']
            for item in SpotifyTitleIgnore.ignore:
                if item in result_title:
                    result_title = result_title.replace(item, '')
            if similarity(result_title, title, 0.75):
                if artist is not None:
                    result_artist = result['artists'][0]['name']
                    if similarity(result_artist, artist, 0.75):
                        track = result
                        break
                else:
                    track = result
                    break
        return track

    def get_artist_top_tracks(self, artist, max_tracks):
        self.get_token()

        # Get artist
        results = self.spotify.search(q=artist, type='artist')
        sp_artist = None
        top_tracks = []
        for result in results['artists']['items']:
            if similarity(result['name'], artist, 0.4):
                sp_artist = result
                break

        # Get top tracks with a maximum number of tracks
        artist_top_tracks = []
        if sp_artist is not None:
            top_tracks = self.spotify.artist_top_tracks(sp_artist['uri'], country='ES')['tracks']
        for top_track in top_tracks:
            if similarity(top_track['artists'][0]['name'], sp_artist['name'], 0.85):
                artist_top_tracks.append(top_track)
            if len(artist_top_tracks) == max_tracks:
                break

        return artist_top_tracks

    def get_similar_artists(self, artist, max_similar_artists):
        self.get_token()

        results = self.spotify.artist_related_artists(artist)
        similar_artists = []
        for result in results['artists']:
            similar_artists.append(result)
            if len(similar_artists) == max_similar_artists:
                break

        return similar_artists

    def get_audio_features(self, tracks):
        self.get_token()

        tracks_id = [track['id'] for track in tracks]
        results = self.spotify.audio_features(tracks_id)
        for i, result in enumerate(results):
            tracks[i]['acousticness'] = result.get(u'acousticness')
            tracks[i]['danceability'] = result.get(u'danceability')
            tracks[i]['energy'] = result.get(u'energy')
            tracks[i]['instrumentalness'] = result.get(u'instrumentalness')
            tracks[i]['mode'] = result.get(u'mode')
            tracks[i]['tempo'] = result.get(u'tempo')
            tracks[i]['valence'] = result.get(u'valence')

        return tracks

    def create_playlist(self, profile, playlist, token):
        if not token:
            return "#"

        self.get_cached_token(token)

        track_ids = [track['id'] for track in playlist if track['id']]

        # Check if this user has created a playlist before
        playlist_url = profile['playlist_url']
        if playlist_url is not None and playlist_url != '#':
            playlist_id = playlist_url.split('/playlist/')[1]
            old_playlist = self.spotify.user_playlist(Constants.SPOTIFY_USERNAME, playlist_id)
            old_track_ids = []
            for item in old_playlist['tracks']['items']:
                old_track_ids.append(item['track']['id'])
            self.spotify.user_playlist_remove_all_occurrences_of_tracks(Constants.SPOTIFY_USERNAME,
                                                                        playlist_id, old_track_ids)
            self.spotify.user_playlist_add_tracks(Constants.SPOTIFY_USERNAME, playlist_id, track_ids)
            spotify_playlist = self.spotify.user_playlist(Constants.SPOTIFY_USERNAME, playlist_id)
        else:
            playlist_name = "Banda Sonora Vital de " + profile['profile_name']
            spotify_playlist = self.spotify.user_playlist_create(Constants.SPOTIFY_USERNAME, playlist_name)
            self.spotify.user_playlist_add_tracks(Constants.SPOTIFY_USERNAME, spotify_playlist["id"], track_ids)

        playlist_url = spotify_playlist["external_urls"]["spotify"]

        return playlist_url

    def remove_playlist(self, playlist_id, track_ids, token):
        self.get_cached_token(token)

        # Empty existing user's playlist and delete (unfollow)
        self.spotify.user_playlist_remove_all_occurrences_of_tracks(
            Constants.SPOTIFY_USERNAME, playlist_id, track_ids
        )
        self.spotify.user_playlist_unfollow(Constants.SPOTIFY_USERNAME, playlist_id)

    def remove_track_from_playlist(self, playlist_id, track_id, playlist_pos, token):
        self.get_cached_token(token)

        try:
            track = [{"uri": track_id, "positions": [playlist_pos - 1]}]
            try:
                self.spotify.user_playlist_remove_specific_occurrences_of_tracks(
                    Constants.SPOTIFY_USERNAME, playlist_id, track
                )
            except spotipy.client.SpotifyException:
                pass
        except IndexError:
            pass


# Spotify items to ignore in track title
class SpotifyTitleIgnore(object):
    ignore = [
        'Mono Mix',
        'En Vivo',
        'Remix',
        'Remastered Version',
        'Remastered',
        'Remasterizada',
        'Remaster',
        'Instrumental',
        'Live',
        'Version',
        'Edit',
        ' - ',
        '-',
        '(',
        ')',
        u'¿',
        '?',
        u'¡',
        '!',
        '"',
        '...',
    ]


