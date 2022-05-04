# -*- coding: UTF-8 -*-
from Recommender.models import Track
from Recommender.constants import Constants
from Recommender.utils import track_genres, track_languages
from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils.encoding import smart_str
from django.http import HttpResponse
from Spotify import SpotifyManager
import logging
import csv
import random


logger = logging.getLogger('app')
hits_db_fields = [
    'artist', 'title', 'year', 'id', 'popularity',
    'acousticness', 'danceability', 'energy', 'instrumentalness', 'mode', 'tempo', 'valence',
    'duration_ms', 'preview_url', 'genre', 'language'
]
genre_tracks_db_fields = [
    'artist', 'title', 'year', 'id', 'genre', 'language'
]


def admin_hits(request):
    if request.user.is_superuser:
        template_name = 'Recommender/admin_hits.html'
        return render(request, template_name)
    else:
        # TODO: something went wrong page instead of oops
        return render(request, 'Recommender/oops.html')


def track_search(request):
    if request.user.is_superuser:
        template_name = 'Recommender/track_search.html'
        page_id = request.POST.get('pageId')
        context = dict()
        if page_id == 'admin_hits':
            context = {
                'page_id': page_id,
            }
        return render(request, template_name, context)
    else:
        # TODO: something went wrong page instead of oops
        return render(request, 'Recommender/oops.html')


def track_results(request):
    page_id = request.POST.get('pageId')
    track_title = request.POST.get('trackTitle')
    track_artist = request.POST.get('trackArtist')
    if track_artist == '':
        track_artist = None

    tracks = []
    sp_results = []
    sp_manager = SpotifyManager()
    if track_title != '':
        sp_results = sp_manager.get_track(track_title, track_artist, get_all_results=True)
        sp_results = sp_results['tracks']['items']
    else:
        if track_artist is not None:
            sp_results = sp_manager.get_artist_top_tracks(track_artist, 20)
    if len(sp_results) > 0:
        for track in sp_results:
            artists = ''
            for idx, t_artist in enumerate(track['artists']):
                artists += t_artist['name']
                if idx != len(track['artists']) - 1:
                    artists += ' & '
            album = track['album']['name']
            release = track['album']['release_date']
            title = track['name']
            preview = track['preview_url']
            spotify_id = track['id']
            tracks.append({
                'artists': artists,
                'album': album,
                'release': release,
                'title': title,
                'preview': preview,
                'spotify_id': spotify_id
            })
    context = dict()
    context['tracks'] = tracks
    context['page_id'] = page_id
    template_name = 'Recommender/track_results.html'
    return render(request, template_name, context)


def add_track_to_hits(request):
    spotify_id = request.POST.get('spotifyId')
    # Search for track in DB
    track_in_db = Track.objects.filter(spotify_id=spotify_id)
    if len(track_in_db.all()) == 0:
        # If we don't have it in our Track database, complete dict and add to DB
        sp_manager = SpotifyManager()
        track = sp_manager.get_track_by_id(spotify_id)
        track['genre'] = None
        track['language'] = None
        track = sp_manager.get_audio_features([track])
        db_track = Track.objects.create_track(track[0], is_a_hit=True)
        db_track.save()
    template_name = 'Recommender/track_results.html'
    return render(request, template_name)


def download_hits_db(request):
    if request.user.is_superuser:
        content_disp = 'attachment; filename=hits_database.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = content_disp
        response.write(u'\ufeff'.encode('utf-8'))
        writer = csv.DictWriter(response, dialect=csv.excel, fieldnames=hits_db_fields)
        writer.writeheader()
        for hit in Track.objects.filter(is_a_hit=True):
            writer.writerow({
                'artist': smart_str(hit.artist),
                'title': smart_str(hit.title),
                'year': hit.year,
                'id': smart_str(hit.spotify_id),
                'popularity': hit.popularity,
                'acousticness': str(hit.acousticness).replace('.', ','),
                'danceability': str(hit.danceability).replace('.', ','),
                'energy': str(hit.energy).replace('.', ','),
                'instrumentalness': str(hit.instrumentalness).replace('.', ','),
                'mode': hit.mode,
                'tempo': hit.tempo,
                'valence': str(hit.valence).replace('.', ','),
                'duration_ms': hit.duration_ms,
                'preview_url': hit.preview,
                'genre': smart_str(hit.genre),
                'language': smart_str(hit.language),
            })
        return response
    else:
        # TODO: something went wrong page instead of oops
        return render(request, 'Recommender/oops.html')


def add_hits_to_db(request):
    is_file_correct = False
    has_all_fields = True
    if request.method == 'POST' and request.FILES['addHitsFile'] and request.FILES['addHitsFile'].name[-4:] == '.csv':
        is_file_correct = True
        tracks = csv.DictReader(request.FILES['addHitsFile'], delimiter=';')
        for track in enumerate(tracks):
            # Check if it's delimited by comma instead of semicolon
            if len(track[1]) == 1:
                # If it's comma we need to read again
                tracks = csv.DictReader(request.FILES['addHitsFile'])
            break
        for i, track in enumerate(tracks):
            if track.get('\xef\xbb\xbfartist') is not None:
                # In the case of comma-delimited we have this issue with artist field
                track['artist'] = track.get('\xef\xbb\xbfartist')
                del track['\xef\xbb\xbfartist']
            if i == 0:
                # Check that we have all fields
                for field in hits_db_fields:
                    if field not in track:
                        has_all_fields = False
                        break
                if not has_all_fields:
                    break

            # Convert to Spotify Dict structure
            track['name'] = track.get('title')
            track['artists'] = []
            track['artists'].append({'name': track.get('artist')})
            # Change empty preview url for N/A
            if track['preview_url'] == '':
                track['preview_url'] = 'N/A'
            # Change empty features for 0
            for field in hits_db_fields:
                if track.get(field) == '':
                    track[field] = '0'
            # Change variable types
            track['year'] = int(track.get('year'))
            track['popularity'] = int(track.get('popularity'))
            track['acousticness'] = float(track.get('acousticness').replace(',', '.'))
            track['danceability'] = float(track.get('danceability').replace(',', '.'))
            track['energy'] = float(track.get('energy').replace(',', '.'))
            track['instrumentalness'] = float(track.get('instrumentalness').replace(',', '.'))
            track['mode'] = int(track.get('mode'))
            track['tempo'] = int(track.get('tempo'))
            track['valence'] = float(track.get('valence').replace(',', '.'))
            track['duration_ms'] = int(track.get('duration_ms'))
            if track.get('genre') in track_genres:
                track['genre'] = track.get('genre')
            else:
                track['genre'] = None
            if track.get('language') in track_languages:
                track['language'] = track.get('language')
            else:
                track['language'] = None

            results = Track.objects.filter(spotify_id=track['id'])
            if len(results) == 0:
                # Save Hit
                hit = Track.objects.create_track(track, is_a_hit=True)
                hit.save()
            else:
                # It's already in Track DB
                track_found = results[0]
                updated_track = Track.objects.update_track(track_found, track, is_a_hit=True)
                updated_track.save()

    if is_file_correct and has_all_fields:
        template_name = 'Recommender/admin_hits.html'
        return render(request, template_name)
    else:
        template_name = 'Recommender/oops.html'
        return render(request, template_name)


def download_model_hits_db(request):
    if request.user.is_superuser:
        content_disp = 'attachment; filename=hits_db_model.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = content_disp
        response.write(u'\ufeff'.encode('utf-8'))
        writer = csv.DictWriter(response, dialect=csv.excel, fieldnames=hits_db_fields, delimiter=';')
        writer.writeheader()
        return response
    else:
        template_name = 'Recommender/oops.html'
        return render(request, template_name)


def remove_hits_db(request):
    if request.user.is_superuser:
        Track.objects.filter(is_a_hit=True, is_special_genre=False).all().delete()
        template_name = 'Recommender/admin_hits.html'
        return render(request, template_name)
    else:
        template_name = 'Recommender/oops.html'
        return render(request, template_name)


def admin_genre_tracks(request):
    if request.user.is_superuser:
        template_name = 'Recommender/admin_genre_tracks.html'
        return render(request, template_name)
    else:
        # TODO: something went wrong page instead of oops
        return render(request, 'Recommender/oops.html')


def download_genre_tracks_db(request):
    if request.user.is_superuser:
        content_disp = 'attachment; filename=genre_tracks_database.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = content_disp
        response.write(u'\ufeff'.encode('utf-8'))
        writer = csv.DictWriter(response, dialect=csv.excel, fieldnames=genre_tracks_db_fields)
        writer.writeheader()
        for genre_track in Track.objects.filter(is_special_genre=True):
            writer.writerow({
                'artist': smart_str(genre_track.artist),
                'title': smart_str(genre_track.title),
                'year': genre_track.year,
                'id': smart_str(genre_track.spotify_id),
                'genre': smart_str(genre_track.genre),
                'language': smart_str(genre_track.language)
            })
        return response
    else:
        # TODO: something went wrong page instead of oops
        return render(request, 'Recommender/oops.html')


def add_genre_tracks_to_db(request):
    is_file_correct = False
    has_all_fields = True
    if request.method == 'POST' and request.FILES['addGenreTracksFile'] \
            and request.FILES['addGenreTracksFile'].name[-4:] == '.csv':
        is_file_correct = True
        tracks = csv.DictReader(request.FILES['addGenreTracksFile'], delimiter=';')
        for track in enumerate(tracks):
            # Check if it's delimited by comma instead of semicolon
            if len(track[1]) == 1:
                # If it's comma we need to read again
                tracks = csv.DictReader(request.FILES['addGenreTracksFile'])
            break
        for i, track in enumerate(tracks):
            if track.get('\xef\xbb\xbfartist') is not None:
                # In the case of comma-delimited we have this issue with artist field
                track['artist'] = track.get('\xef\xbb\xbfartist')
                del track['\xef\xbb\xbfartist']
            if i == 0:
                # Check that we have all fields
                for field in genre_tracks_db_fields:
                    if field not in track:
                        has_all_fields = False
                        break
                if not has_all_fields:
                    break

            if track.get('genre') in track_genres:
                # Convert to Spotify Dict structure
                track['name'] = track.get('title')
                track['artists'] = []
                track['artists'].append({'name': track.get('artist')})
                if track.get('year') == '':
                    track['year'] = None
                else:
                    track['year'] = int(track['year'])
                if track.get('language') not in track_languages:
                    track['language'] = None

                results = Track.objects.filter(spotify_id=track['id'])
                if len(results) == 0:
                    # Save Hit
                    genre_track = Track.objects.create_track(track, is_a_hit=False, is_special_genre=True)
                    genre_track.save()
                else:
                    # It's already in Track DB
                    track_found = results[0]
                    updated_track = Track.objects.update_track(track_found, track,
                                                               is_a_hit=track_found.is_a_hit, is_special_genre=True)
                    updated_track.save()
            else:
                continue

    if is_file_correct and has_all_fields:
        template_name = 'Recommender/admin_genre_tracks.html'
        return render(request, template_name)
    else:
        template_name = 'Recommender/oops.html'
        return render(request, template_name)


def download_model_genre_tracks_db(request):
    if request.user.is_superuser:
        content_disp = 'attachment; filename=genre_tracks_db_model.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = content_disp
        response.write(u'\ufeff'.encode('utf-8'))
        writer = csv.DictWriter(response, dialect=csv.excel, fieldnames=genre_tracks_db_fields, delimiter=';')
        writer.writeheader()
        return response
    else:
        template_name = 'Recommender/oops.html'
        return render(request, template_name)


def remove_genre_tracks_db(request):
    if request.user.is_superuser:
        Track.objects.filter(is_special_genre=True, is_a_hit=False).all().delete()
        template_name = 'Recommender/admin_genre_tracks.html'
        return render(request, template_name)
    else:
        template_name = 'Recommender/oops.html'
        return render(request, template_name)


def admin_songs_tagger(request):
    if request.user.is_superuser and len(Track.objects.filter(Q(genre=None) | Q(language=None)).all()) > 0:
        track_to_tag = random.choice(Track.objects.filter(Q(genre=None) | Q(language=None)))
        context = {
            'track_id': track_to_tag.id,
            'title': track_to_tag.title,
            'artist': track_to_tag.artist,
            'spotify_id': track_to_tag.spotify_id,
            'genre': str(track_to_tag.genre),
            'language': str(track_to_tag.language)
        }
        if track_to_tag.genre is None:
            sp_manager = SpotifyManager()
            context['spotify_genres'] = sp_manager.get_genres(track_to_tag.spotify_id)
        context['bsv_genres'] = sorted(track_genres)
        context['bsv_languages'] = track_languages
        template_name = 'Recommender/admin_songs_tagger.html'
        return render(request, template_name, context)
    else:
        template_name = 'Recommender/oops.html'
        return render(request, template_name)


def admin_songs_add_tags(request):
    track_id = request.POST.get('trackId')
    genre_input = request.POST.get('inputGenre')
    language_input = request.POST.get('inputLanguage')
    track = Track.objects.get(id=track_id)
    if genre_input is not None:
        track.genre = genre_input
    if language_input is not None:
        track.language = language_input.title()
    track.save()
    return redirect('Recommender:admin_songs_tagger')
