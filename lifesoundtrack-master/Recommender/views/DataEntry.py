# -*- coding: UTF-8 -*-

from django.shortcuts import render, redirect, reverse
from django.utils import translation
from Recommender.models import Forms, UserProfile
from Recommender.constants import Constants
from Recommender.utils import QuestionnaireFields
from datetime import datetime
import re
from Spotify import spotify_login
import ProfileManager


class ProfileForm(object):
    def __init__(self):
        # Personal data
        self.places_lived = ''
        self.day_submitted = ''
        self.hour_submitted = ''
        # Relationship with music
        self.worked_at = ''
        self.music_at_work = ''
        self.played_instruments = ''
        self.plays_instrument = False
        self.like_singing = ''
        self.group_singing = ''
        self.like_dancing = ''
        self.like_dancing_bool = False
        self.preferred_genres = ''
        self.preferred_songs = ''
        self.preferred_artists = ''
        self.all_preferred_songs = ''
        # Memories and music
        self.sing_instrumental = ''
        self.upbeat_calm = ''
        self.cheerful_melancholic = ''
        self.listen_instruments = ''
        self.listen_language = ''
        self.childhood = ''
        self.childhood_songs = ''
        self.youth_dance = ''
        self.youth_dance_songs = ''
        self.radio = ''
        self.radio_programmes = ''
        self.tv = ''
        self.tv_programmes = ''
        self.wedding_songs = ''
        self.good_memories = ''
        self.good_memories_songs = ''
        self.bad_memories = ''
        self.bad_memories_song = ''
        self.preferred_songs_2 = ''
        self.desired_playlist_length = Constants.PLAYLIST_LENGTH[1]

    def get_personal_data(self, request):
        # Save day and hour when the form was submitted
        date_time = datetime.now()
        self.day_submitted = str(date_time.day).zfill(2) + '-' + str(date_time.month).zfill(2) + '-' + str(date_time.year)
        self.hour_submitted = str(int(date_time.hour)+1).zfill(2) + ':' + str(date_time.minute).zfill(2)

        # Get places where the person has lived
        for index in range(1, Constants.NUMBER_OF_FIELDS):
            place = 'inputLivedPlace' + str(index)
            start = 'inputStartYear' + str(index)
            end = 'inputEndYear' + str(index)
            if request.POST.get(place) != '':
                self.places_lived = self.places_lived + request.POST.get(place) + '(' +\
                                    request.POST.get(start)[0:4] + '-' + request.POST.get(end)[0:4] + ')' + '//'
            else:
                self.places_lived = self.places_lived[:-2]
                break

    def get_relationship_with_music(self, request):
        # Work places
        work_places = QuestionnaireFields.work_places['en']
        for idx, work_place in enumerate(work_places):
            work_input = 'inputWorkPlace' + str(idx + 1)
            if request.POST.get(work_input):
                self.worked_at += work_place + ','
        if request.POST.get('inputAltreWorkPlace') != '':
            self.worked_at += request.POST.get('inputAltreWorkPlace') + ','
        self.worked_at = self.worked_at[:-1]

        # Music at work
        if request.POST.get('inputMusicAtWork'):
            self.music_at_work = request.POST.get('inputMusicAtWork')

        # Played instruments
        instruments = QuestionnaireFields.instruments['en']
        for idx, instrument in enumerate(instruments):
            inst_input = 'inputPlayInstrument' + str(idx + 1)
            if request.POST.get(inst_input):
                self.played_instruments += instrument + ','
        if request.POST.get('inputAltrePlayInst') != '':
            self.played_instruments += request.POST.get('inputAltrePlayInst') + ','
        if request.POST.get('inputPlayInstrumentNone'):
            self.played_instruments += request.POST.get('inputPlayInstrumentNone') + ','
        self.played_instruments = self.played_instruments[:-1]
        if self.played_instruments != '' and self.played_instruments != 'Cap':
            self.plays_instrument = True

        # Like Singing
        if request.POST.get('inputLikeSinging'):
            self.like_singing = request.POST.get('inputLikeSinging')
            if request.POST.get('inputGroupSinging'):
                self.group_singing = request.POST.get('inputGroupSinging')

        # Like Dancing
        if request.POST.get('inputLikeDancing'):
            self.like_dancing = request.POST.get('inputLikeDancing')
            if self.like_dancing == 'Like A Lot' or self.like_dancing == 'Like' or self.like_dancing == 'Like A Little':
                self.like_dancing_bool = True

        # Get preferred genres for this profile
        for index in range(1, Constants.NUMBER_OF_GENRES + 1):
            if index <= 11:
                genre = 'inputFavouriteGenreModern' + str(index)
            else:
                if 11 < index <= 30:
                    genre = 'inputFavouriteGenrePopular' + str(index-11)
                else:
                    genre = 'inputFavouriteGenreClassic' + str(index-30)

            if request.POST.get(genre) is not None:
                # Get genre from questionnaire
                self.preferred_genres += request.POST.get(genre)
                if index != Constants.NUMBER_OF_GENRES + 1:
                    self.preferred_genres += '//'
        self.preferred_genres = self.preferred_genres[:-2]

        # Get preferred songs for this profile
        for index in range(1, Constants.NUMBER_OF_FIELDS):
            title = 'inputFavouriteSong' + str(index)
            artist = 'inputArtistSong' + str(index)
            if request.POST.get(title) != '':
                # Add title
                self.preferred_songs += request.POST.get(title)
                if request.POST.get(artist) != '':
                    # Add artist if specified
                    self.preferred_songs += '(' + request.POST.get(artist) + ')'
                self.preferred_songs += '//'

        # Get preferred artists for this profile
        for index in range(1, Constants.NUMBER_OF_FIELDS):
            artist = 'inputFavouriteArtist' + str(index)
            if request.POST.get(artist) != '':
                self.preferred_artists += request.POST.get(artist) + '//'
        self.preferred_artists = self.preferred_artists[:-2]

    def get_memories_and_music(self, request):
        # Melody and rhythm
        if request.POST.get('inputSingInstrumental'):
            self.sing_instrumental = request.POST.get('inputSingInstrumental')

        # Upbeat and calm
        if request.POST.get('inputUpbeatCalm'):
            self.upbeat_calm = request.POST.get('inputUpbeatCalm')

        # Cheerful and melancholic
        if request.POST.get('inputCheerMelan'):
            self.cheerful_melancholic = request.POST.get('inputCheerMelan')

        # Instruments preferred to listen
        instruments = QuestionnaireFields.instruments['en']
        for idx, instrument in enumerate(instruments):
            inst_input = 'inputListenInstrument' + str(idx + 1)
            if request.POST.get(inst_input):
                self.listen_instruments += instrument + ','
        if request.POST.get('inputAltreListenInst') != '':
            self.listen_instruments += request.POST.get('inputAltreListenInst') + ','
        self.listen_instruments = self.listen_instruments[:-1]

        # Languages preferred to listen
        languages = QuestionnaireFields.languages['en']
        for idx, language in enumerate(languages):
            lan_input = 'inputLang' + str(idx + 1)
            if request.POST.get(lan_input):
                self.listen_language += language + ','
        if request.POST.get('inputAltreListenLang') != '':
            self.listen_language += request.POST.get('inputAltreListenLang') + ','
        self.listen_language = self.listen_language[:-1]

        # Childhood memories related with music
        if request.POST.get('inputChildhood'):
            self.childhood = request.POST.get('inputChildhood')
            if self.childhood == 'Lot' or self.childhood == 'Little':
                # Get childhood songs
                for index in range(1, Constants.NUMBER_OF_FIELDS):
                    title = 'inputChildhoodSong' + str(index)
                    artist = 'inputChildhoodArtist' + str(index)
                    if request.POST.get(title) != '':
                        # Add title
                        self.childhood_songs += request.POST.get(title)
                        if request.POST.get(artist) != '':
                            # Add artist if specified
                            self.childhood_songs += '(' + request.POST.get(artist) + ')'
                        self.childhood_songs += '//'

        # Music danced when the person was young
        if request.POST.get('inputYouthDance'):
            self.youth_dance = request.POST.get('inputYouthDance')
            if self.youth_dance == 'Often' or self.youth_dance == 'Sometimes':
                # Get youth dance songs
                for index in range(1, Constants.NUMBER_OF_FIELDS):
                    title = 'inputYouthDanceSong' + str(index)
                    artist = 'inputYouthDanceArtist' + str(index)
                    if request.POST.get(title) != '':
                        # Add title
                        self.youth_dance_songs += request.POST.get(title)
                        if request.POST.get(artist) != '':
                            # Add artist if specified
                            self.youth_dance_songs += '(' + request.POST.get(artist) + ')'
                        self.youth_dance_songs += '//'

        # Memories related with radio listening
        if request.POST.get('inputRadioMusic'):
            self.radio = request.POST.get('inputRadioMusic')
            if self.radio == 'Lot' or self.radio == 'Little':
                if request.POST.get('inputRadioProgrammes'):
                    self.radio_programmes = request.POST.get('inputRadioProgrammes')

        # Music memories related with tv watching
        if request.POST.get('inputTvMusic'):
            self.tv = request.POST.get('inputTvMusic')
            if self.tv == 'Lot' or self.radio == 'Little':
                if request.POST.get('inputTvProgrammes'):
                    self.tv_programmes = request.POST.get('inputTvProgrammes')

        # Get wedding songs
        for index in range(1, Constants.NUMBER_OF_FIELDS):
            title = 'inputWeddingSong' + str(index)
            artist = 'inputWeddingArtist' + str(index)
            if request.POST.get(title) != '':
                # Add title
                self.wedding_songs += request.POST.get(title)
                if request.POST.get(artist) != '':
                    # Add artist if specified
                    self.wedding_songs += '(' + request.POST.get(artist) + ')'
                self.wedding_songs += '//'

        # Good memories songs
        if request.POST.get('inputGoodMemories'):
            self.good_memories = request.POST.get('inputGoodMemories')
            if self.good_memories == 'Yes':
                # Get good memories songs
                for index in range(1, Constants.NUMBER_OF_FIELDS):
                    title = 'inputGoodMemoriesSong' + str(index)
                    artist = 'inputGoodMemoriesArtist' + str(index)
                    if request.POST.get(title) != '':
                        # Add title
                        self.good_memories_songs += request.POST.get(title)
                        if request.POST.get(artist) != '':
                            # Add artist if specified
                            self.good_memories_songs += '(' + request.POST.get(artist) + ')'
                        self.good_memories_songs += '//'

        # Join second list of preferred songs
        self.preferred_songs_2 = self.childhood_songs + self.youth_dance_songs + \
            self.wedding_songs + self.good_memories_songs

        # Join both preferred songs lists
        self.all_preferred_songs = self.preferred_songs + self.preferred_songs_2
        self.all_preferred_songs = self.all_preferred_songs[:-2]

        # Bad memories song
        if request.POST.get('inputBadMemories'):
            self.bad_memories = request.POST.get('inputBadMemories')
            if self.bad_memories == 'Yes':
                # Get bad memories song
                title = 'inputBadMemoriesSong1'
                artist = 'inputBadMemoriesArtist1'
                if request.POST.get(title) != '':
                    # Add title
                    self.bad_memories_song = request.POST.get(title)
                    if request.POST.get(artist) != '':
                        # Add artist if specified
                        self.bad_memories_song += '(' + request.POST.get(artist) + ')'

        # Desired playlist length
        if request.POST.get('inputPlaylistLength'):
            self.desired_playlist_length = int(request.POST.get('inputPlaylistLength'))


def data_entry(request):
    profile = UserProfile.objects.get(id=request.GET.get('id'))

    if profile is not None and ProfileManager.user_manages_profile(request.user, profile):
        profile_data = {
            'id': profile.id,
            'name': profile.name,
            'birth_year': profile.birth_year,
            'birth_place': profile.birth_place,
        }
        language = profile.language

        genre = QuestionnaireFields.genre
        regions = QuestionnaireFields.regions
        work_places = QuestionnaireFields.work_places
        instruments = QuestionnaireFields.instruments
        languages = QuestionnaireFields.languages
        lengths = Constants.PLAYLIST_LENGTH
        array = range(2, Constants.NUMBER_OF_FIELDS + 1)

        user_id = ProfileManager.get_user_id(request.user, request.GET.get('user'))

        context = {
            'user_id': user_id,
            'profile': profile_data,
            'genre_list_moderna': genre['modern'][language],
            'genre_list_popular': genre['popular'][language],
            'genre_list_classica': genre['classic'][language],
            'regions': regions[language],
            'array': array,
            'work_places': work_places[language],
            'play_instrument': instruments[language],
            'listen_language': languages[language],
            'lengths': lengths
        }

        if profile.form is not None:
            profile_form = get_profile_form(profile, language)
            context['user_data'] = profile_form

        spotify_login(request)
        translation.activate(profile.language)
        template_name = 'Recommender/data_entry.html'
        return render(request, template_name, context)

    else:
        # TODO: something went wrong page instead of oops
        return render(request, 'Recommender/oops.html')


def save_data(request):
    profile = UserProfile.objects.get(id=request.GET.get('id'))

    if profile is not None and ProfileManager.user_manages_profile(request.user, profile):
        # Init profile
        profile_form = ProfileForm()

        # Get personal data questions
        profile_form.get_personal_data(request)

        # Get relationship with music questions
        profile_form.get_relationship_with_music(request)

        # Get memories and music questions
        profile_form.get_memories_and_music(request)

        # Fill Database
        fill_db(profile_form, profile.id)

        user_id = ProfileManager.get_user_id(request.user, request.GET.get('user'))
        return redirect(reverse('Recommender:profile') + '?user=' + str(user_id) + '&id=' + str(profile.id))

    else:
        # TODO: something went wrong page instead of oops
        return render(request, 'Recommender/oops.html')


def fill_db(profile_form, profile_id):
    f = Forms(day_submitted=profile_form.day_submitted,
              hour_submitted=profile_form.hour_submitted,
              places_lived=profile_form.places_lived[:500],
              worked_at=profile_form.worked_at,
              music_at_work=profile_form.music_at_work,
              play_instrument=profile_form.plays_instrument,
              instrument=profile_form.played_instruments,
              like_singing=profile_form.like_singing,
              group_singing=profile_form.group_singing,
              like_dancing=profile_form.like_dancing,
              like_dancing_bool=profile_form.like_dancing_bool,
              preferred_genres=profile_form.preferred_genres[:500],
              preferred_songs=profile_form.preferred_songs[:1500],
              preferred_artists=profile_form.preferred_artists[:1500],
              sing_instrumental=profile_form.sing_instrumental,
              upbeat_calm=profile_form.upbeat_calm,
              cheerful_melancholic=profile_form.cheerful_melancholic,
              listen_instruments=profile_form.listen_instruments,
              listen_language=profile_form.listen_language,
              childhood=profile_form.childhood,
              childhood_songs=profile_form.childhood_songs[:500],
              youth_dance=profile_form.youth_dance,
              youth_dance_songs=profile_form.youth_dance_songs[:500],
              radio=profile_form.radio,
              radio_programmes=profile_form.radio_programmes[:800],
              tv=profile_form.tv,
              tv_programmes=profile_form.tv_programmes[:800],
              wedding_songs=profile_form.wedding_songs[:500],
              good_memories=profile_form.good_memories,
              good_memories_songs=profile_form.good_memories_songs[:500],
              bad_memories=profile_form.bad_memories,
              bad_memories_song=profile_form.bad_memories_song[:200],
              all_preferred_songs=profile_form.all_preferred_songs[:3000],
              desired_playlist_length=profile_form.desired_playlist_length)
    f.save()

    profile = UserProfile.objects.get(id=profile_id)
    profile.form = f
    profile.save()


def get_profile_form(profile, profile_language):
    # Places lived
    places_lived_raw = profile.form.places_lived.split('//')
    places_lived = []
    for place_raw in places_lived_raw:
        if place_raw:
            place_and_years = re.search('^.*', place_raw)
            place = place_and_years.group(0).split('(')[0]
            year = re.findall('[0-9]{4}', place_raw)
            if len(year) < 2:
                year = [None, None]  # None if we don't have a range of years
            places_lived.append({
                'place': place,
                'start': year[0],
                'end': year[1]
            })
    places_lived.append({
        'place': '',
        'start': '',
        'end': ''
    })
    array_places_lived = range(len(places_lived) + 1, Constants.NUMBER_OF_FIELDS + 1)

    # Worked At
    work_places = QuestionnaireFields.work_places
    worked_at_raw = profile.form.worked_at.split(',')
    worked_at = []
    another_work = False
    another_work_name = ''
    for idx, work_place in enumerate(work_places['en']):
        worked_at.append({
            'name': work_places[profile_language][idx],
            'id': idx + 1,
            'checked': work_place in worked_at_raw
        })
    for work_raw in worked_at_raw:
        if work_raw not in work_places['en'] and work_raw != '':
            another_work = True
            another_work_name = work_raw

    # Play Instruments
    instruments = QuestionnaireFields.instruments
    p_instr_raw = profile.form.instrument.replace(' ', '').split(',')
    play_instruments = []
    another_instrument = False
    another_instrument_name = ''
    for idx, instrument in enumerate(instruments['en']):
        play_instruments.append({
            'name': instruments[profile_language][idx],
            'id': idx + 1,
            'checked': instrument in p_instr_raw
        })
    for instr_raw in p_instr_raw:
        if instr_raw not in instruments and instr_raw != 'Cap' and instr_raw != '':
            another_instrument = True
            another_instrument_name = instr_raw
    no_instrument = not profile.form.play_instrument

    # Like Singing
    group_singing = None
    if profile.form.group_singing != '':
        group_singing = profile.form.group_singing

    # Preferred Genres
    genre_modern = QuestionnaireFields.genre['modern'][profile_language]
    genre_popular = QuestionnaireFields.genre['popular'][profile_language]
    genre_classic = QuestionnaireFields.genre['classic'][profile_language]
    genres_raw = profile.form.preferred_genres.split('//')
    g_modern = []
    g_popular = []
    g_classic = []
    for idx, genre in enumerate(genre_modern):
        g_modern.append({
            'name': genre,
            'id': idx + 1,
            'checked': genre.decode('utf-8') in genres_raw
        })
    for idx, genre in enumerate(genre_popular):
        g_popular.append({
            'name': genre,
            'id': idx + 1,
            'checked': genre.decode('utf-8') in genres_raw
        })
    for idx, genre in enumerate(genre_classic):
        g_classic.append({
            'name': genre,
            'id': idx,
            'checked': genre.decode('utf-8') in genres_raw
        })

    # Preferred Songs
    preferred_songs_raw = profile.form.preferred_songs.split('//')
    preferred_songs = []
    id = 1
    for song_raw in preferred_songs_raw:
        if song_raw != '':
            artist = re.search('\(.*\)$', song_raw)
            try:
                artist = artist.group(0)[1:-1]
            except AttributeError:
                artist = None
            title = re.sub('\(.*\)$', '', song_raw)
            preferred_songs.append({
                'title': title,
                'artist': artist,
                'id': id
            })
        id += 1
    preferred_songs.append({
        'title': '',
        'artist': '',
        'id': len(preferred_songs) + 1
    })
    array_pref_songs = range(len(preferred_songs) + 1, Constants.NUMBER_OF_FIELDS + 1)

    # Preferred Artists
    preferred_artists_raw = profile.form.preferred_artists.split('//')
    preferred_artists = []
    id = 1
    for artist_raw in preferred_artists_raw:
        preferred_artists.append({
            'name': artist_raw,
            'id': id
        })
        id += 1
    preferred_artists.append({
        'name': '',
        'id': len(preferred_artists) + 1
    })
    array_pref_artists = range(len(preferred_artists) + 1, Constants.NUMBER_OF_FIELDS + 1)

    # Listen Instruments
    l_instr_raw = profile.form.listen_instruments.replace(' ', '').split(',')
    listen_instruments = []
    another_listen_instr = False
    another_listen_instr_name = ''
    for idx, instrument in enumerate(instruments['en']):
        listen_instruments.append({
            'name': instruments[profile_language][idx],
            'id': idx + 1,
            'checked': instrument in l_instr_raw
        })
    for instr_raw in l_instr_raw:
        if instr_raw not in instruments and instr_raw != 'Cap' and instr_raw != '':
            another_listen_instr = True
            another_listen_instr_name = instr_raw

    # Listen Languages
    languages = QuestionnaireFields.languages
    listen_lang_raw = profile.form.listen_language.replace(' ', '').split(',')
    listen_languages = []
    another_listen_lang = False
    another_listen_lang_name = ''
    for idx, language in enumerate(languages['en']):
        listen_languages.append({
            'name': languages['ca'][idx],
            'id': idx + 1,
            'checked': language in listen_lang_raw
        })
    for lang_raw in listen_lang_raw:
        if lang_raw not in languages['en'] and lang_raw != '':
            another_listen_lang = True
            another_listen_lang_name = lang_raw

    # Childhood songs
    childhood_songs_raw = profile.form.childhood_songs.split('//')
    childhood_songs = []
    id = 1
    for song_raw in childhood_songs_raw:
        if song_raw != '':
            artist = re.search('\(.*\)$', song_raw)
            try:
                artist = artist.group(0)[1:-1]
            except AttributeError:
                artist = None
            title = re.sub('\(.*\)$', '', song_raw)
            childhood_songs.append({
                'title': title,
                'artist': artist,
                'id': id
            })
        id += 1
    childhood_songs.append({
        'title': '',
        'artist': '',
        'id': len(childhood_songs) + 1
    })
    array_child_songs = range(len(childhood_songs) + 1, Constants.NUMBER_OF_FIELDS + 1)

    # Youth Dance Songs
    youth_dance_songs_raw = profile.form.youth_dance_songs.split('//')
    youth_dance_songs = []
    id = 1
    for song_raw in youth_dance_songs_raw:
        if song_raw != '':
            artist = re.search('\(.*\)$', song_raw)
            try:
                artist = artist.group(0)[1:-1]
            except AttributeError:
                artist = None
            title = re.sub('\(.*\)$', '', song_raw)
            youth_dance_songs.append({
                'title': title,
                'artist': artist,
                'id': id
            })
        id += 1
    youth_dance_songs.append({
        'title': '',
        'artist': '',
        'id': len(youth_dance_songs) + 1
    })
    array_youth_songs = range(len(youth_dance_songs) + 1, Constants.NUMBER_OF_FIELDS + 1)

    # Wedding Songs
    wedding_songs_raw = profile.form.wedding_songs.split('//')
    wedding_songs = []
    id = 1
    for song_raw in wedding_songs_raw:
        if song_raw != '':
            artist = re.search('\(.*\)$', song_raw)
            try:
                artist = artist.group(0)[1:-1]
            except AttributeError:
                artist = None
            title = re.sub('\(.*\)$', '', song_raw)
            wedding_songs.append({
                'title': title,
                'artist': artist,
                'id': id
            })
        id += 1
    wedding_songs.append({
        'title': '',
        'artist': '',
        'id': len(wedding_songs) + 1
    })
    array_wedding_songs = range(len(wedding_songs) + 1, Constants.NUMBER_OF_FIELDS + 1)

    # Good Memories Songs
    good_mem_songs_raw = profile.form.good_memories_songs.split('//')
    good_memories_songs = []
    id = 1
    for song_raw in good_mem_songs_raw:
        if song_raw != '':
            artist = re.search('\(.*\)$', song_raw)
            try:
                artist = artist.group(0)[1:-1]
            except AttributeError:
                artist = None
            title = re.sub('\(.*\)$', '', song_raw)
            good_memories_songs.append({
                'title': title,
                'artist': artist,
                'id': id
            })
        id += 1
    good_memories_songs.append({
        'title': '',
        'artist': '',
        'id': len(good_memories_songs) + 1
    })
    array_good_mem_songs = range(len(good_memories_songs) + 1, Constants.NUMBER_OF_FIELDS + 1)

    # Bad Memories Song
    bad_mem_song_raw = profile.form.bad_memories_song
    if bad_mem_song_raw != '':
        artist = re.search('\(.*\)$', bad_mem_song_raw)
        try:
            artist = artist.group(0)[1:-1]
        except AttributeError:
            artist = None
        title = re.sub('\(.*\)$', '', bad_mem_song_raw)
        bad_memories_song = {
            'title': title,
            'artist': artist
        }
    else:
        bad_memories_song = {
            'title': '',
            'artist': ''
        }

    profile_data = {
        'places_lived': places_lived,
        'array_places_lived': array_places_lived,

        'worked_at': worked_at,
        'another_work': another_work,
        'another_work_name': another_work_name,

        'music_at_work': profile.form.music_at_work,

        'play_instruments': play_instruments,
        'no_instrument': no_instrument,
        'another_instrument': another_instrument,
        'another_instrument_name': another_instrument_name,

        'like_singing': profile.form.like_singing,
        'group_singing': group_singing,

        'like_dancing': profile.form.like_dancing,

        'g_mod_check': g_modern,
        'g_pop_check': g_popular,
        'g_cla_check': g_classic,

        'preferred_songs': preferred_songs,
        'array_pref_songs': array_pref_songs,

        'preferred_artists': preferred_artists,
        'array_pref_artists': array_pref_artists,

        'sing_instrumental': profile.form.sing_instrumental,
        'upbeat_calm': profile.form.upbeat_calm,
        'cheerful_melancholic': profile.form.cheerful_melancholic,

        'listen_instruments': listen_instruments,
        'another_listen_instr': another_listen_instr,
        'another_listen_instr_name': another_listen_instr_name,

        'listen_languages': listen_languages,
        'another_listen_lang': another_listen_lang,
        'another_listen_lang_name': another_listen_lang_name,

        'childhood': profile.form.childhood,
        'childhood_songs': childhood_songs,
        'array_child_songs': array_child_songs,

        'youth_dance': profile.form.youth_dance,
        'youth_dance_songs': youth_dance_songs,
        'array_youth_songs': array_youth_songs,

        'radio': profile.form.radio,
        'radio_programmes': profile.form.radio_programmes,

        'tv': profile.form.tv,
        'tv_programmes': profile.form.tv_programmes,

        'wedding_songs': wedding_songs,
        'array_wedding_songs': array_wedding_songs,

        'good_memories': profile.form.good_memories,
        'good_memories_songs': good_memories_songs,
        'array_good_mem_songs': array_good_mem_songs,

        'bad_memories': profile.form.bad_memories,
        'bad_memories_song': bad_memories_song
    }
    return profile_data
