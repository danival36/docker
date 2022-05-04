# -*- coding: UTF-8 -*-

import logging
import re

from django.shortcuts import redirect, render, reverse
from Recommender.constants import Constants
from Recommender.models import UserTrack, Track, UserProfile
from Recommender.utils import map_value, is_track_in_list, track_to_spotify_dict, all_genres, track_genres
from Spotify import SpotifyManager, spotify_login
from Youtube import YoutubeManager
from random import shuffle
import ProfileManager

logger = logging.getLogger('app')
not_found_logger = logging.getLogger('notfound')


def create_playlist_request(request):
    profile = UserProfile.objects.get(id=request.GET.get('id'))
    profile_data = {
        'id': profile.id,
        'name': profile.name
    }
    user_id = ProfileManager.get_user_id(request.user, request.GET.get('user'))
    template_name = 'Recommender/playlist_request.html'
    wait = ((Constants.WAITING_TIME - 1) * 1000) / 100
    context = {
        'user_id': user_id,
        'profile': profile_data,
        'wait': wait
    }
    return render(request, template_name, context)


def create_playlist(request):

    user_profile = UserProfile.objects.get(id=request.GET.get('id'))

    if ProfileManager.user_manages_profile(request.user, user_profile):

        # Get profile data from form
        profile = get_profile_data(request.user.email, user_profile)

        # Search for candidates and populate playlist
        candidates = get_playlist_candidates(profile)
        playlist = populate_playlist(profile, candidates)

        # Add Youtube Links
        yt_manager = YoutubeManager()
        playlist = yt_manager.add_youtube_links_to_playlist(playlist)

        # Create Spotify Playlist
        sp_manager = SpotifyManager()
        spotify_login(request)
        playlist_url = sp_manager.create_playlist(profile, playlist, request.session.get('spotify_token'))

        # Save Playlist to DB
        save_playlist_to_db(user_profile, playlist, playlist_url)

        # Go to playlist view:
        user_id = ProfileManager.get_user_id(request.user, request.GET.get('user'))
        return redirect(reverse('Recommender:playlist') + '?user=' + str(user_id) + '&id=' + str(user_profile.id))

    else:
        # TODO: something went wrong page instead of oops
        return render(request, 'Recommender/oops.html')


# ================================================================================================ #
#                                       FUNCTIONS                                                  #
# ================================================================================================ #

# Load User Information
def get_profile_data(user_name, user_profile):
    # Create profile
    profile = dict()

    # User ID
    profile['id'] = user_profile.id

    # User Data & User Form:
    profile_form = user_profile.form

    # User Personal Data:
    profile['user_name'] = user_name
    profile['profile_name'] = user_profile.name
    profile['birth_year'] = user_profile.birth_year
    profile['birth_place'] = user_profile.birth_place
    profile['playlist_url'] = user_profile.playlist_url
    profile['places_lived'] = []
    places_lived = profile_form.places_lived.split('//')
    for place_raw in places_lived:
        if place_raw:
            place_and_years = re.search('^.*', place_raw)
            place = place_and_years.group(0)
            year = re.findall('[0-9]{4}', place_raw)
            if len(year) < 2:
                year = [None, None]  # None if we don't have a range of years
            place_lived = {"City": place, "Start": year[0], "End": year[1]}
            profile['places_lived'].append(place_lived)

    if profile_form.listen_language != '':
        profile['languages'] = profile_form.listen_language.split(',')
    else:
        profile['languages'] = []

    # User Preference for Genres, Instruments
    profile['genres'] = []
    if user_profile.language == 'es' or user_profile.language == 'ca':
        if profile_form.preferred_genres != '':
            user_genres = profile_form.preferred_genres.split('//')
            for genre in user_genres:
                for idx, bsv_genre in enumerate(all_genres[user_profile.language]):
                    if genre == bsv_genre.decode('utf-8'):
                        profile['genres'].append(track_genres[idx].decode('utf-8'))
                        break

    if profile_form.play_instrument:
        profile['instrument'] = profile_form.instrument
    else:
        profile['instrument'] = None

    # Preference filter data
    profile['valence'] = True
    if profile_form.cheerful_melancholic == 'cheerful':
        profile['valence_range'] = [0.5, 1]
    elif profile_form.cheerful_melancholic == 'melancholic':
        profile['valence_range'] = [0.5, 0]
    else:
        profile['valence'] = False
        profile['valence_range'] = [0, 1]

    profile['danceability'] = True
    if profile_form.like_dancing != '':
        if profile_form.like_dancing_bool:
            profile['danceability_range'] = [0.5, 1]
        else:
            profile['danceability_range'] = [0.5, 0]
    else:
        profile['danceability'] = False
        profile['danceability_range'] = [0, 1]

    profile['instrumentalness'] = True
    if profile_form.sing_instrumental == 'instrumental':
        profile['instrumentalness_range'] = [0.5, 1]
    elif profile_form.sing_instrumental == 'sing':
        profile['instrumentalness_range'] = [0.5, 0]
    else:
        profile['instrumentalness'] = False
        profile['instrumentalness_range'] = [0, 1]

    profile['upbeat'] = True
    if profile_form.upbeat_calm == 'upbeat':
        profile['tempo_range'] = [100, 200]
        profile['energy_range'] = [0.5, 1]
    elif profile_form.upbeat_calm == 'calm':
        profile['tempo_range'] = [100, 0]
        profile['energy_range'] = [0.5, 0]
    else:
        profile['upbeat'] = False
        profile['tempo_range'] = [0, 200]
        profile['energy_range'] = [0, 1]

    # User Preferred Songs and Preferred Songs Artists
    profile['songs'] = []
    profile['direct_song_artists'] = []
    titles_and_artists = profile_form.all_preferred_songs.split('//')
    logger.info(profile_form.all_preferred_songs.split('//'))
    for title_and_artist in titles_and_artists:
        if title_and_artist != '':
            artist = re.search('\(.*\)$', title_and_artist)
            try:
                artist = artist.group(0)[1:-1]
                if artist in profile_form.preferred_songs \
                        and artist not in profile_form.preferred_artists \
                        and artist not in profile['direct_song_artists']:
                    profile['direct_song_artists'].append(artist)
            except AttributeError:
                artist = None
            title = re.sub('\(.*\)$', '', title_and_artist)
            preferred_song = {"Title": title, "Artist": artist}
            profile['songs'].append(preferred_song)

    # Preferred/Direct Artists:
    if profile_form.preferred_artists != '':
        profile['artists'] = profile_form.preferred_artists.split('//')
    else:
        # If there are no preferred artists, add direct songs' artists
        profile['artists'] = profile['direct_song_artists']
    profile['artists_uri'] = [None] * len(profile['artists'])

    # If user already has a playlist, check for track feedback
    profile['positive_feedback_tracks'] = []
    profile['negative_feedback_tracks'] = []
    if len(user_profile.playlist.all()) > 0:
        for user_track in user_profile.playlist.all():
            if user_track.feedback_listen_again == 'Yes':
                # If listen again feedback is Yes, we include it in new playlist
                profile['positive_feedback_tracks'].append(user_track.track)
            # Remove track from DB
            user_track.delete()
        for negative_feedback_track in user_profile.negative_feedback_tracks.all():
            profile['negative_feedback_tracks'].append(negative_feedback_track)

    # Get user's desired playlist length
    profile['desired_playlist_length'] = profile_form.desired_playlist_length
    profile['length_index'] = Constants.PLAYLIST_LENGTH.index(profile['desired_playlist_length'])

    return profile


# Get candidate tracks for playlist
def get_playlist_candidates(user):
    logger.debug("PLAYLIST CANDIDATES: Getting playlist candidates...")

    candidates = dict()
    sp_manager = SpotifyManager()

    # DIRECT SONGS - Preferred, childhood, youth_dance, wedding, good_memories
    direct_songs = []
    if Constants.DIRECT_SONGS[user['length_index']] > 0:
        # Limit number of candidates to find in Spotify
        n_candidates = len(user['songs'])
        if len(user['songs']) > int(Constants.DIRECT_SONGS[user['length_index']] * 2):
            n_candidates = int(Constants.DIRECT_SONGS[user['length_index']] * 2)
        # Search direct songs in Spotify
        for user_song in user['songs']:
            logger.debug("PLAYLIST CANDIDATES: Processing track... %s", user_song['Title'])
            if user_song['Title'] != '':
                # Get track
                direct_song = sp_manager.get_track(user_song['Title'], user_song['Artist'])
                if direct_song is not None:
                    logger.debug("PLAYLIST CANDIDATES: --> track found in Spotify")
                    # Append track to direct songs list
                    if not is_track_in_list(direct_song, direct_songs) and \
                            not is_track_in_list(direct_song, user['positive_feedback_tracks']) and \
                            not is_track_in_list(direct_song, user['negative_feedback_tracks']):
                        add_track, candidates = check_max_songs_per_artist(direct_song['artists'][0]['name'],
                                                                           candidates)
                        if add_track:
                            direct_song['direct_song'] = True
                            direct_song['playlist_group'] = 'direct_songs'
                            direct_songs.append(direct_song)
            if len(direct_songs) == n_candidates:
                break
    candidates['direct_songs'] = direct_songs

    # PREF ARTISTS SONGS - Preferred artists, direct song artists
    pref_artists_songs = []
    if Constants.PREF_ARTISTS_SONGS[user['length_index']] > 0 and len(user['artists']) > 0:
        logger.debug("PLAYLIST CANDIDATES: Preferred user artists: %s", user['artists'])
        # Number of candidates to add
        n_candidates = Constants.PREF_ARTISTS_SONGS[user['length_index']] * Constants.CANDIDATES_MULTIPLE
        n_songs_per_artist = int(n_candidates / len(user['artists']))
        if n_songs_per_artist == 0:
            n_songs_per_artist = 1
        for artist_idx, user_artist in enumerate(user['artists']):
            if user_artist != '':
                top_tracks = sp_manager.get_artist_top_tracks(user_artist, n_songs_per_artist)
                if len(top_tracks) > 0:
                    user['artists_uri'][artist_idx] = top_tracks[0]['artists'][0]['uri']
                    logger.debug("PLAYLIST CANDIDATES: Adding preferred artists songs from artist:" + user_artist)
                    for top_track in top_tracks:
                        if not is_track_in_list(top_track, pref_artists_songs) and \
                                not is_track_in_list(top_track, direct_songs) and \
                                not is_track_in_list(top_track, user['positive_feedback_tracks']) and \
                                not is_track_in_list(top_track, user['negative_feedback_tracks']):
                            add_track, candidates = check_max_songs_per_artist(top_track['artists'][0]['name'],
                                                                               candidates)
                            if add_track:
                                top_track['playlist_group'] = 'pref_artists_songs'
                                pref_artists_songs.append(top_track)
                    if len(pref_artists_songs) >= n_candidates:
                        break
    candidates['pref_artists_songs'] = pref_artists_songs

    # SIMILARITY SONGS - Songs from similar artists (similar to user's preferred artists)
    similarity_songs = []
    if Constants.SIMILARITY_SONGS[user['length_index']] > 0 and len(user['artists']) > 0:
        n_candidates = Constants.SIMILARITY_SONGS[user['length_index']] * Constants.CANDIDATES_MULTIPLE
        n_songs_per_artist = 1
        n_artists_required = int(n_candidates / n_songs_per_artist)
        n_artists_per_artist = int(n_artists_required / len(user['artists']))
        if n_artists_per_artist == 0:
            n_artists_per_artist = 1
        logger.debug("PLAYLIST CANDIDATES: Adding similarity songs")
        for artist_uri in user['artists_uri']:
            if artist_uri is not None:
                similar_artists = sp_manager.get_similar_artists(artist_uri, n_artists_per_artist)
                for similar_artist in similar_artists:
                    top_tracks = sp_manager.get_artist_top_tracks(similar_artist['name'], n_songs_per_artist)
                    for top_track in top_tracks:
                        if not is_track_in_list(top_track, similarity_songs) and \
                                not is_track_in_list(top_track, pref_artists_songs) and \
                                not is_track_in_list(top_track, direct_songs) and \
                                not is_track_in_list(top_track, user['positive_feedback_tracks']) and \
                                not is_track_in_list(top_track, user['negative_feedback_tracks']):
                            add_track, candidates = check_max_songs_per_artist(top_track['artists'][0]['name'],
                                                                               candidates)
                            if add_track:
                                top_track['playlist_group'] = 'similarity_songs'
                                similarity_songs.append(top_track)
            if len(similarity_songs) >= n_candidates:
                break
    candidates['similarity_songs'] = similarity_songs

    # GENRE TRACKS - Songs of user's preferred genres
    special_genres_songs = []
    if Constants.GENRE_SONGS[user['length_index']] > 0:
        logger.debug("PLAYLIST CANDIDATES: Adding special genre songs")
        for genre in user['genres']:
            genre_tracks = []
            for result in Track.objects.filter(is_special_genre=True, genre=genre).order_by('?'):
                track = track_to_spotify_dict(result)
                if not is_track_in_list(track, special_genres_songs) and \
                        not is_track_in_list(track, similarity_songs) and \
                        not is_track_in_list(track, pref_artists_songs) and \
                        not is_track_in_list(track, direct_songs) and \
                        not is_track_in_list(track, user['positive_feedback_tracks']) and \
                        not is_track_in_list(track, user['negative_feedback_tracks']):
                    track['playlist_group'] = 'genre_tracks'
                    genre_tracks.append(track)
            shuffle(genre_tracks)
            special_genres_songs += genre_tracks[:Constants.GENRE_SONGS[user['length_index']] * 2]
    candidates['special_genres'] = special_genres_songs

    # YOUTH HITS - Hits from user's youth years
    youth_hits = []
    if Constants.YOUTH_HIT_SONGS[user['length_index']] > 0 and user['birth_year'] < Constants.LAST_BIRTH_YEAR_FOR_HITS:
        logger.debug("PLAYLIST CANDIDATES: Adding youth hit songs")
        hits = []
        # Get hit tracks within a year range
        hits_by_year = Track.objects.filter(is_a_hit=True,
                                            year__gte=user['birth_year'] + 10,
                                            year__lte=user['birth_year'] + 25)
        # Add tracks that have user's genre & language combination
        for genre in user['genres']:
            for language in user['languages']:
                hits += hits_by_year.filter(genre=genre, language=language).order_by('?')
        if len(hits) < Constants.YOUTH_HIT_SONGS[user['length_index']] * 10:
            # Add tracks from user's genres
            for genre in user['genres']:
                for hit in hits_by_year.filter(genre=genre).order_by('?'):
                    if hit not in hits:
                        hits.append(hit)
        if len(hits) < Constants.YOUTH_HIT_SONGS[user['length_index']] * 10:
            # Add tracks from year range
            for hit in hits_by_year.order_by('?'):
                if hit not in hits:
                    hits.append(hit)
                if len(hits) >= Constants.YOUTH_HIT_SONGS[user['length_index']] * 10:
                    break
        else:
            # Crop list if it's too long
            hits = hits[:Constants.YOUTH_HIT_SONGS[user['length_index']] * 10]
        # Add candidate tracks
        for hit in hits:
            track = track_to_spotify_dict(hit)
            if not is_track_in_list(track, youth_hits) and \
                    not is_track_in_list(track, special_genres_songs) and \
                    not is_track_in_list(track, similarity_songs) and \
                    not is_track_in_list(track, pref_artists_songs) and \
                    not is_track_in_list(track, direct_songs) and \
                    not is_track_in_list(track, user['positive_feedback_tracks']) and \
                    not is_track_in_list(track, user['negative_feedback_tracks']):
                track['playlist_group'] = 'youth_hits'
                youth_hits.append(track)
    candidates['youth_hits'] = youth_hits

    return candidates


# Populates Playlist
def populate_playlist(user, candidates):
    logger.debug("POPULATE PLAYLIST: Adding tracks to playlist...")
    playlist = []
    sp_manager = SpotifyManager()

    # Add the positive feedback tracks
    for idx, track in enumerate(user['positive_feedback_tracks']):
        user['positive_feedback_tracks'][idx] = track_to_spotify_dict(track)
        user['positive_feedback_tracks'][idx]['playlist_group'] = 'positive_feedback'
    playlist += user['positive_feedback_tracks']

    # DIRECT SONGS - add
    n_direct_songs = 0
    if Constants.DIRECT_SONGS[user['length_index']] > 0:
        # Get number of (desired) direct songs
        if len(candidates['direct_songs']) > Constants.DIRECT_SONGS[user['length_index']]:
            n_direct_songs = Constants.DIRECT_SONGS[user['length_index']]
        else:
            n_direct_songs = len(candidates['direct_songs'])
        if n_direct_songs > 0:
            logger.debug("POPULATE PLAYLIST: Adding Direct Songs to playlist...")
            candidates['direct_songs'] = sp_manager.get_audio_features(candidates['direct_songs'][:n_direct_songs])
            playlist += candidates['direct_songs']

    # PREF ARTISTS SONGS - add
    n_pref_artists_songs = 0
    if Constants.PREF_ARTISTS_SONGS[user['length_index']] > 0:
        # Get number of (desired) preferred artists songs
        if n_direct_songs < Constants.DIRECT_SONGS[user['length_index']]:
            total = Constants.PREF_ARTISTS_SONGS[user['length_index']] + Constants.DIRECT_SONGS[user['length_index']] \
                    - n_direct_songs - len(user['positive_feedback_tracks'])
            if len(candidates['pref_artists_songs']) > total:
                n_pref_artists_songs = total
            else:
                n_pref_artists_songs = len(candidates['pref_artists_songs'])
        else:
            n_pref_artists_songs = Constants.PREF_ARTISTS_SONGS[user['length_index']]
        if n_pref_artists_songs > 0:
            logger.debug("POPULATE PLAYLIST: Adding Preferred Artists Songs to playlist...")
            candidates['pref_artists_songs'] = sp_manager.get_audio_features(candidates['pref_artists_songs'])
            candidates['pref_artists_songs'] = apply_preference_filter(user, candidates['pref_artists_songs'])
            playlist += candidates['pref_artists_songs'][:n_pref_artists_songs]

    # SIMILARITY SONGS - add
    if Constants.SIMILARITY_SONGS[user['length_index']] > 0:
        # Get number of (desired) preferred artists songs
        if n_direct_songs + n_pref_artists_songs < \
                Constants.DIRECT_SONGS[user['length_index']] + Constants.PREF_ARTISTS_SONGS[user['length_index']]:
            total = Constants.SIMILARITY_SONGS[user['length_index']] + Constants.PREF_ARTISTS_SONGS[user['length_index']] \
                    + Constants.DIRECT_SONGS[user['length_index']] \
                    - n_pref_artists_songs - n_direct_songs - len(user['positive_feedback_tracks'])
            if len(candidates['similarity_songs']) > total:
                n_similarity_songs = total
            else:
                n_similarity_songs = len(candidates['similarity_songs'])
        else:
            n_similarity_songs = Constants.SIMILARITY_SONGS[user['length_index']]
        if n_similarity_songs > 0:
            logger.debug("POPULATE PLAYLIST: Adding Similarity Songs to playlist...")
            candidates['similarity_songs'] = sp_manager.get_audio_features(candidates['similarity_songs'])
            candidates['similarity_songs'] = apply_preference_filter(user, candidates['similarity_songs'])
            playlist += candidates['similarity_songs'][:n_similarity_songs]

    # GENRE TRACKS - add
    if Constants.GENRE_SONGS[user['length_index']] > 0:
        n_missing_songs = user['desired_playlist_length'] - len(playlist) \
            - Constants.GENRE_SONGS[user['length_index']] \
            - Constants.YOUTH_HIT_SONGS[user['length_index']]
        if user['birth_year'] < Constants.LAST_BIRTH_YEAR_FOR_HITS:
            # When birth year is within our Youth Hits database
            n_genre_songs = Constants.GENRE_SONGS[user['length_index']] + int(n_missing_songs/2)
        else:
            # When we don't have Youth Hit tracks for user's birth year
            # Complete playlist just with genre songs
            n_genre_songs = Constants.GENRE_SONGS[user['length_index']] + \
                            Constants.YOUTH_HIT_SONGS[user['length_index']] + n_missing_songs
        if n_genre_songs > 0:
            logger.debug("POPULATE PLAYLIST: Adding Special Genres Songs to playlist...")
            shuffle(candidates['special_genres'])
            playlist += candidates['special_genres'][:n_genre_songs]

    # YOUTH HITS - add
    if Constants.YOUTH_HIT_SONGS[user['length_index']] > 0 and user['birth_year'] < Constants.LAST_BIRTH_YEAR_FOR_HITS:
        n_youth_hits = user['desired_playlist_length'] - len(playlist)
        logger.debug("POPULATE PLAYLIST: Adding Youth Hit Songs to playlist...")
        candidates['youth_hits'] = apply_preference_filter(user, candidates['youth_hits'])
        playlist += candidates['youth_hits'][:n_youth_hits]

    return playlist


# Save playlist to Users DB
def save_playlist_to_db(profile, playlist, playlist_url):
    for i, track in enumerate(playlist):
        # Search for track in DB
        track_in_db = Track.objects.filter(spotify_id=track['id'])
        if len(track_in_db.all()) == 0:
            # If we don't have it in our Track database, add
            db_track = Track.objects.create_track(track, is_a_hit=False)
            db_track.save()
        else:
            # If it's already in our db
            db_track = track_in_db.all()[0]
            if track.get('direct_song') is not None:
                # If it's from direct songs, add user popularity
                db_track.user_popularity += 1
        user_track = UserTrack()
        user_track.track = db_track
        user_track.youtube = track['youtube_url']
        user_track.playlist_position = i + 1
        user_track.playlist_group = track['playlist_group']
        user_track.save()
        profile.save()
        profile.playlist.add(user_track)
        profile.save()
    profile.save()
    profile.playlist_url = playlist_url
    profile.playlist_length = len(playlist)
    profile.playlist_feedback_text = None
    profile.save()


# User Preference Filtering (Audio Features)
def apply_preference_filter(user, tracks):
    # Rate the tracks according to their audio features and user preferences
    rating_range = [0, 0.20]
    for i, track in enumerate(tracks):
        track_rating = 0
        if user['danceability']:
            user_range = user['danceability_range']
            track_rating += map_value(track['danceability'], user_range[0], user_range[1],
                                      rating_range[0], rating_range[1])
        if user['upbeat']:
            user_range = user['tempo_range']
            track_rating += map_value(track['tempo'], user_range[0], user_range[1],
                                      rating_range[0]/2, rating_range[1]/2)
            user_range = user['energy_range']
            track_rating += map_value(track['energy'], user_range[0], user_range[1],
                                      rating_range[0]/2, rating_range[1]/2)
        if user['instrumentalness']:
            user_range = user['instrumentalness_range']
            track_rating += map_value(track['instrumentalness'], user_range[0], user_range[1],
                                      rating_range[0], rating_range[1])
        if user['valence']:
            user_range = user['valence_range']
            track_rating += map_value(track['valence'], user_range[0], user_range[1],
                                      rating_range[0], rating_range[1])
        track_rating += map_value(track['popularity'], 0, 100,
                                  rating_range[0], rating_range[1])
        tracks[i]['rating'] = track_rating

    # Sort tracks in order by rating (from better to worse)
    tracks = sorted(tracks, key=lambda k: '%f' % k['rating'], reverse=True)
    return tracks


# Check maximum songs per artist
def check_max_songs_per_artist(artist, candidates):
    if 'n_tracks_per_artist' not in candidates:
        candidates['n_tracks_per_artist'] = dict()
    add_track = True
    if artist not in candidates['n_tracks_per_artist']:
        candidates['n_tracks_per_artist'][artist] = 1
    else:
        if candidates['n_tracks_per_artist'][artist] + 1 <= Constants.MAX_SONGS_PER_ARTIST:
            candidates['n_tracks_per_artist'][artist] += 1
        else:
            add_track = False
    return add_track, candidates
