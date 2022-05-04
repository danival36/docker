# -*- coding: UTF-8 -*-

from django.db import models
from django.contrib.auth.models import User
from Recommender.constants import Constants


class TrackManager(models.Manager):
    def create_track(self, track_dict, is_a_hit, is_special_genre=False):
        release_year = None
        if track_dict.get('album') is not None:
            release_year = track_dict['album']['release_date'][:4]
        elif track_dict.get('year') is not None:
            release_year = track_dict['year']

        user_popularity = 0
        if is_a_hit:
            user_popularity = Constants.USER_POPULARITY_TO_BE_HIT
        else:
            if track_dict.get('direct_song') is not None:
                user_popularity = 1

        track = self.create(
            title=track_dict.get('name'),
            artist=track_dict['artists'][0]['name'],
            year=release_year,
            genre=track_dict.get('genre'),
            language=track_dict.get('language'),
            spotify_id=track_dict.get('id'),
            preview=track_dict.get('preview_url'),
            duration_ms=track_dict.get('duration_ms'),
            popularity=track_dict.get('popularity'),
            acousticness=track_dict.get('acousticness'),
            danceability=track_dict.get('danceability'),
            energy=track_dict.get('energy'),
            instrumentalness=track_dict.get('instrumentalness'),
            mode=track_dict.get('mode'),
            tempo=track_dict.get('tempo'),
            valence=track_dict.get('valence'),
            user_popularity=user_popularity,
            is_a_hit=is_a_hit,
            is_special_genre=is_special_genre
        )
        return track

    @staticmethod
    def update_track(track, track_dict, is_a_hit, is_special_genre=False):
        if track.year is None or track.year == '' or track.year == 'None':
            track.year = track_dict.get('year')
        if track.genre is None or track.genre == '' or track.genre == 'None':
            track.genre = track_dict.get('genre')
        if track.language is None or track.language == '' or track.language == 'None':
            track.language = track_dict.get('language')
        if track.spotify_id is None or track.spotify_id == '' or track.spotify_id == 'None':
            track.spotify_id = track_dict.get('spotify_id')
        if track.preview is None or track.preview == '' or track.preview == 'None':
            track.preview = track_dict.get('preview_url')
        if track.duration_ms is None or track.duration_ms == '' or track.duration_ms == 'None':
            track.duration_ms = track_dict.get('duration_ms')
        if track.popularity is None or track.popularity == '' or track.popularity == 'None':
            track.popularity = track_dict.get('popularity')
        if track.acousticness is None or track.acousticness == '' or track.acousticness == 'None':
            track.acousticness = track_dict.get('acousticness')
        if track.danceability is None or track.danceability == '' or track.danceability == 'None':
            track.danceability = track_dict.get('danceability')
        if track.energy is None or track.energy == '' or track.energy == 'None':
            track.energy = track_dict.get('energy')
        if track.instrumentalness is None or track.instrumentalness == '' or track.instrumentalness == 'None':
            track.instrumentalness = track_dict.get('instrumentalness')
        if track.mode is None or track.mode == '' or track.mode == 'None':
            track.mode = track_dict.get('mode')
        if track.tempo is None or track.tempo == '' or track.tempo == 'None':
            track.tempo = track_dict.get('tempo')
        if track.valence is None or track.valence == '' or track.valence == 'None':
            track.valence = track_dict.get('valence')
        if is_a_hit:
            track.is_a_hit = True
            track.user_popularity += Constants.USER_POPULARITY_TO_BE_HIT
        if is_special_genre:
            track.is_special_genre = True
        return track


class Track(models.Model):
    title = models.CharField(max_length=500)
    artist = models.CharField(max_length=500)
    year = models.IntegerField(null=True)
    genre = models.CharField(max_length=500, null=True)
    language = models.CharField(max_length=500, null=True)
    spotify_id = models.CharField(max_length=200, null=True)
    preview = models.CharField(max_length=200, null=True, default="#")
    duration_ms = models.IntegerField(null=True, default=0)
    popularity = models.IntegerField(default=0, null=True)
    acousticness = models.FloatField(default=0, null=True)
    danceability = models.FloatField(default=0, null=True)
    energy = models.FloatField(default=0, null=True)
    instrumentalness = models.FloatField(default=0, null=True)
    mode = models.IntegerField(default=0, null=True)
    tempo = models.IntegerField(default=0, null=True)
    valence = models.FloatField(default=0, null=True)
    user_popularity = models.IntegerField(default=0, null=True)
    is_a_hit = models.BooleanField(default=False)
    is_special_genre = models.BooleanField(default=False)

    objects = TrackManager()


class UserTrack(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    youtube = models.CharField(max_length=500, null=True)
    playlist_position = models.IntegerField(null=True)
    playlist_group = models.CharField(max_length=50, null=True)
    feedback_familiar = models.CharField(max_length=10, null=True)
    feedback_like = models.CharField(max_length=10, null=True)
    feedback_memories = models.CharField(max_length=10, null=True)
    feedback_listen_again = models.CharField(max_length=10, null=True)
    feedback_text = models.CharField(max_length=1000, null=True)
    feedback_done = models.BooleanField(default=False)

    objects = models.Manager()


class Forms(models.Model):
    day_submitted = models.CharField(max_length=10, null=True)
    hour_submitted = models.CharField(max_length=5, null=True)
    places_lived = models.CharField(max_length=500)
    worked_at = models.CharField(max_length=500)
    music_at_work = models.CharField(max_length=200)
    play_instrument = models.BooleanField(default=True)
    instrument = models.CharField(max_length=200, null=True)
    like_singing = models.CharField(max_length=200)
    group_singing = models.CharField(max_length=500)
    like_dancing = models.CharField(max_length=200)
    like_dancing_bool = models.BooleanField(default=False)
    preferred_genres = models.CharField(max_length=500)
    preferred_songs = models.CharField(max_length=1500)
    preferred_artists = models.CharField(max_length=1500)
    sing_instrumental = models.CharField(max_length=200)
    upbeat_calm = models.CharField(max_length=200)
    cheerful_melancholic = models.CharField(max_length=200)
    listen_instruments = models.CharField(max_length=500)
    listen_language = models.CharField(max_length=500)
    childhood = models.CharField(max_length=100, null=True)
    childhood_songs = models.CharField(max_length=500)
    youth_dance = models.CharField(max_length=100, null=True)
    youth_dance_songs = models.CharField(max_length=500)
    radio = models.CharField(max_length=100, null=True)
    radio_programmes = models.CharField(max_length=800)
    tv = models.CharField(max_length=100, null=True)
    tv_programmes = models.CharField(max_length=800)
    wedding_songs = models.CharField(max_length=500)
    good_memories = models.CharField(max_length=100, null=True)
    good_memories_songs = models.CharField(max_length=500)
    bad_memories = models.CharField(max_length=100, null=True)
    bad_memories_song = models.CharField(max_length=200)
    all_preferred_songs = models.CharField(max_length=3000)
    desired_playlist_length = models.IntegerField(null=True)

    objects = models.Manager()


class UserProfile (models.Model):
    name = models.CharField(max_length=200, null=True)
    birth_year = models.IntegerField(null=True)
    birth_place = models.CharField(max_length=200, null=True)
    form = models.ForeignKey(Forms, null=True)
    language = models.CharField(max_length=10, default='ca', null=True)
    # TODO: Check if this is necessary
    current_view = models.CharField(max_length=200, null=True)
    playlist = models.ManyToManyField(UserTrack)
    playlist_length = models.IntegerField(null=True)
    playlist_url = models.CharField(max_length=500, null=True)
    playlist_feedback_text = models.CharField(max_length=1000, null=True)
    negative_feedback_tracks = models.ManyToManyField(Track)

    objects = models.Manager()


class BsvUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    language = models.CharField(max_length=10, default='ca', null=True)
    profiles = models.ManyToManyField(UserProfile)
    current_profile = models.IntegerField(null=True)

    objects = models.Manager()
