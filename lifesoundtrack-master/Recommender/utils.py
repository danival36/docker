# -*- coding: UTF-8 -*-
from difflib import SequenceMatcher
from unidecode import unidecode
from Recommender.models import Track
import re


# Map Value
def map_value(in_value, in_min, in_max, out_min, out_max, clamp=True):
    in_span = in_min - in_max
    out_span = out_min - out_max
    value_scaled = float(in_value - in_min) / float(in_span)
    out_value = out_min + (value_scaled * out_span)
    if clamp and out_value < 0.0:
        out_value = 0.0
    return out_value


# Get Similarity
def similarity(item_1, item_2, threshold):
    is_similar = False
    sim_ratio = SequenceMatcher(None, item_1.lower(), item_2.lower()).ratio()
    if sim_ratio > threshold:
        is_similar = True
    return is_similar


# Say if track is already in list (Spotify's Track Dict)
def is_track_in_list(track, track_list):
    artist = unidecode(track['artists'][0]['name'].lower())
    title = unidecode(track['name'].lower())
    track_in_list = False
    for t in track_list:
        if type(t) is Track:
            t_artist = unidecode(t.artist.lower())
            t_title = unidecode(t.title.lower())
        else:
            t_artist = unidecode(t['artists'][0]['name'].lower())
            t_title = unidecode(t['name'].lower())
        if ((artist in t_artist or t_artist in artist) and (title in t_title or t_title in title)) \
                or similarity(title, t_title, 0.95):
            track_in_list = True
            break
    return track_in_list


# Track model to Spotify Dict
def track_to_spotify_dict(track_model):
    track = dict()
    track['name'] = track_model.title
    track['artists'] = []
    track['artists'].append({'name': track_model.artist})
    track['year'] = track_model.year
    track['genre'] = track_model.genre
    track['id'] = track_model.spotify_id
    track['preview_url'] = track_model.preview
    track['duration_ms'] = track_model.duration_ms
    track['popularity'] = track_model.popularity
    track['acousticness'] = track_model.acousticness
    track['danceability'] = track_model.danceability
    track['energy'] = track_model.energy
    track['instrumentalness'] = track_model.instrumentalness
    track['mode'] = track_model.mode
    track['tempo'] = track_model.tempo
    track['valence'] = track_model.valence
    return track


# Get track list from a slashed string (like is saved in forms)
def get_track_list_from_slashed_string(slashed_string):
    output_list = []
    if slashed_string != 'N/A':
        splitted = slashed_string.split('//')
        for item in splitted:
            if item != '':
                artist_re = re.search('\(.*\)$', item)
                try:
                    artist = artist_re.group(0)[1:-1]
                except AttributeError:
                    artist = ''
                title = re.sub('\(.*\)$', '', item)
                output_list.append({
                    'title': title,
                    'artist': artist
                })
    return output_list


# Questionnaire fields utils (bsv admin)
class QuestionnaireFields(object):
    single_item_fields = [
        'birth_year', 'birth_place', 'music_at_work', 'like_singing', 'group_singing', 'like_dancing',
        'sing_instrumental', 'upbeat_calm', 'cheerful_melancholic', 'childhood', 'youth_dance',
        'radio', 'tv', 'good_memories', 'bad_memories', 'playlist_feedback'
    ]
    list_fields = [
        'worked_at', 'play_instrument', 'preferred_genres', 'preferred_artists', 'listen_instruments',
        'listen_language', 'radio_programmes', 'tv_programmes'
    ]
    track_list_fields = [
        'preferred_songs', 'childhood_songs', 'youth_dance_songs', 'wedding_songs',
        'good_memories_songs', 'bad_memories_song'
    ]
    playlist_fields = [
        'familiar', 'like', 'memories', 'listen again'
    ]
    playlist_groups = [
        'direct_songs', 'pref_artists_songs', 'similarity_songs', 'genre_tracks', 'youth_hits', 'positive_feedback'
    ]
    special_genres = [
        'Zarzuela', 'Cançó infantil', 'Tango', 'Jota', 'Flamenc', 'Ranchera',
        'Pasodoble', 'Copla', 'Bolero', 'Havanera', 'Folk', 'Sardana',
        'Vals', 'Òpera', 'Clàssica', 'Coro'
    ]
    special_genres_dec = [
        'Zarzuela', 'Canco infantil', 'Tango', 'Jota', 'Flamenc', 'Ranchera',
        'Pasodoble', 'Copla', 'Bolero', 'Havanera', 'Folk', 'Sardana',
        'Vals', 'Opera', 'Classica', 'Coro'
    ]

    slash_song_lists_fields = [
        'bad_memories_song', 'childhood_songs', 'good_memories_songs',
        'preferred_songs', 'wedding_songs', 'youth_dance_songs'
    ]
    slash_list_fields = [
        'preferred_artists', 'preferred_genres', 'places_lived'
    ]
    comma_list_fields = [
        'listen_instruments', 'listen_language', 'play_instrument', 'worked_at',
        'radio_programmes', 'tv_programmes'
    ]
    song_lists = [
        'all_preferred_songs',
        'bad_memories_song', 'childhood_songs', 'good_memories_songs',
        'preferred_songs', 'wedding_songs', 'youth_dance_songs'
    ]

    genre = dict()
    genre['modern'] = dict()
    genre['modern']['ca'] = [
        'Reggae', 'Rock', 'Country', 'Jazz', 'Soul', 'Rumba', 'Disco', 'Swing', 'Blues', 'Electrònica', 'Funk',
    ]
    genre['modern']['es'] = [
        'Reggae', 'Rock', 'Country', 'Jazz', 'Soul', 'Rumba', 'Disco', 'Swing', 'Blues', 'Electrónica', 'Funk',
    ]
    genre['modern']['en'] = [
        'Reggae', 'Rock', 'Country', 'Jazz', 'Soul', 'Rumba', 'Disco', 'Swing', 'Blues', 'Electronic', 'Funk',
    ]
    genre['popular'] = dict()
    genre['popular']['ca'] = [
        'Zarzuela', 'Cançó infantil', 'Cançó popular', 'Balada', 'Cançó lleugera', 'Pop', 'Pasodoble', 'Jota',
        'Flamenc', 'Ranchera', 'Tango', 'Cantautor', 'Havanera', 'Sardana', 'Copla', 'Folk', 'Bolero',
        'Chanson (cançó francesa)', 'Cançó italiana'
    ]
    genre['popular']['es'] = [
        'Zarzuela', 'Canción infantil', 'Canción popular', 'Balada', 'Canción ligera', 'Pop', 'Pasodoble', 'Jota',
        'Flamenco', 'Ranchera', 'Tango', 'Cantautor', 'Habanera', 'Sardana', 'Copla', 'Folk', 'Bolero',
        'Chanson (canción francesa)', 'Canción italiana'
    ]
    genre['popular']['en'] = [
        'Zarzuela', 'Children', 'Canción popular', 'Ballad', 'Canción ligera', 'Pop', 'Pasodoble', 'Jota',
        'Flamenco', 'Ranchera', 'Tango', 'Singer/Songwriter', 'Habanera', 'Sardana', 'Copla', 'Folk', 'Bolero',
        'Chanson', 'Canción italiana'
    ]
    genre['classic'] = dict()
    genre['classic']['ca'] = [
        'Vals', 'Cor', 'Clàssica', 'Òpera',
    ]
    genre['classic']['es'] = [
        'Vals', 'Cor', 'Clásica', 'Ópera',
    ]
    genre['classic']['en'] = [
        'Waltz', 'Choral', 'Classical', 'Opera',
    ]

    regions = dict()
    regions['ca'] = [
        'Andalusia', 'Aragó', 'Asturies', 'Balears', 'Canàries', 'Cantàbria', 'Castella i Lleó',
        'Castella-La Manxa', 'Catalunya', 'Ceuta', 'Comunitat Valenciana', 'Extremadura', 'Galícia',
        'La Rioja', 'Madrid', 'Melilla', 'Múrcia', 'Navarra', 'País Basc',
    ]
    regions['es'] = [
        'Andalucía', 'Aragón', 'Asturias', 'Baleares', 'Canarias', 'Cantabria', 'Castilla y León',
        'Castilla-La Mancha', 'Cataluña', 'Ceuta', 'Comunidad Valenciana', 'Extremadura', 'Galicia',
        'La Rioja', 'Madrid', 'Melilla', 'Murcia', 'Navarra', 'País Vasco',
    ]
    regions['en'] = [
        'Andalusia', 'Aragon', 'Asturias', 'Balearic Islands', 'Canary Islands', 'Cantabria', 'Castile and Leon',
        'Castilla-La Mancha', 'Catalonia', 'Ceuta', 'Valencia', 'Extremadura', 'Galicia',
        'La Rioja', 'Madrid', 'Melilla', 'Murcia', 'Navarre', 'Basque Country',
    ]

    work_places = dict()
    work_places['ca'] = [
        'Oficina', 'A la fàbrica', 'A casa', 'Al camp', 'Botiga/Treball de cara al públic',
    ]
    work_places['es'] = [
        'Oficina', 'Fábrica', 'En casa', 'En el campo', 'Tienda/Trabajo de cara al público',
    ]
    work_places['en'] = [
        'Office', 'Factory', 'Home', 'Fields/Farm', 'Shop/Customer service',
    ]

    instruments = dict()
    instruments['ca'] = [
        'Saxòfon', 'Violí', 'Cant', 'Percussió', 'Guitarra', 'Piano'
    ]
    instruments['es'] = [
        'Saxo', 'Violín', 'Canto', 'Percusión', 'Guitarra', 'Piano',
    ]
    instruments['en'] = [
        'Sax', 'Violin', 'Voice', 'Percussion', 'Guitar', 'Piano'
    ]

    languages = dict()
    languages['ca'] = [
        'Català', 'Castellà', 'Anglès', 'Francès', 'Italià',
    ]
    languages['es'] = [
        'Catalán', 'Castellano', 'Inglés', 'Francés', 'Italiano',
    ]
    languages['en'] = [
        'Catalan', 'Spanish', 'English', 'French', 'Italian',
    ]


track_languages = [
    'Arabic',
    'Aragonese',
    'Asturian',
    'Basque',
    'Catalan',
    'English',
    'French',
    'Galician',
    'German',
    'Greek',
    'Italian',
    'Instrumental',
    'Portuguese',
    'Spanish',
    'Other',
]

track_genres = [
    'Reggae', 'Rock', 'Country', 'Jazz', 'Soul', 'Rumba',
    'Disco', 'Swing', 'Blues', 'Electronic', 'Funk',
    'Zarzuela', 'Children', 'Canción popular', 'Ballad',
    'Canción ligera', 'Pop', 'Pasodoble', 'Jota', 'Flamenco',
    'Ranchera', 'Tango', 'Singer/Songwriter', 'Habanera', 'Sardana',
    'Copla', 'Folk', 'Bolero',
    'Chanson', 'Canción italiana',
    'Waltz', 'Choral', 'Classical', 'Opera',
]

all_genres = dict()
all_genres['es'] = [
    'Reggae', 'Rock', 'Country', 'Jazz', 'Soul', 'Rumba',
    'Disco', 'Swing', 'Blues', 'Electrónica', 'Funk',
    'Zarzuela', 'Canción infantil', 'Canción popular', 'Balada',
    'Canción ligera', 'Pop', 'Pasodoble', 'Jota', 'Flamenco',
    'Ranchera', 'Tango', 'Cantautor', 'Habanera', 'Sardana',
    'Copla', 'Folk', 'Bolero',
    'Chanson', 'Canción italiana',
    'Vals', 'Coro', 'Clásica', 'Ópera',
]

all_genres['ca'] = [
    'Reggae', 'Rock', 'Country', 'Jazz', 'Soul', 'Rumba',
    'Disco', 'Swing', 'Blues', 'Electrònica', 'Funk',
    'Zarzuela', 'Cançó infantil', 'Cançó popular', 'Balada',
    'Cançó lleugera', 'Pop', 'Pasodoble', 'Jota', 'Flamenc',
    'Ranchera', 'Tango', 'Cantautor', 'Havanera', 'Sardana',
    'Copla', 'Folk', 'Bolero',
    'Chanson', 'Cançó italiana',
    'Vals', 'Coro', 'Clàssica', 'Òpera',
]