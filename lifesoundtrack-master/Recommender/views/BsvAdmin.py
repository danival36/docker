# -*- coding: UTF-8 -*-
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.http import HttpResponse

from StringIO import StringIO
from zipfile import ZipFile
import csv
from unidecode import unidecode

from Recommender.models import BsvUser
from Recommender.constants import Constants
from Recommender.utils import QuestionnaireFields
from Recommender.utils import get_track_list_from_slashed_string
import ProfileManager


# Bsv Admin Access View
def bsv_admin_login(request):
    # Load admin login page
    template_name = 'Recommender/bsv_admin_login.html'
    return render(request, template_name)


# Bsv Admin Login
def admin_login(request):
    # Login with admin data
    username = request.POST.get('inputUsername')
    password = request.POST.get('inputPassword')
    user = authenticate(request, username=username, password=password)

    if user is not None:
        # Load admin page
        login(request, user)
        return redirect('Recommender:admin_menu')
    else:
        template_name = 'Recommender/bsv_admin_login.html'
        return render(request, template_name)


# Admin menu
def admin_menu(request):
    if request.user.is_superuser:
        template_name = 'Recommender/admin_menu.html'
        return render(request, template_name)
    else:
        # TODO: something went wrong page instead of oops
        return render(request, 'Recommender/oops.html')


# Admin List of Users View
def admin_users_list(request):
    if request.user.is_superuser:
        all_users = []
        # Load users list
        for bsv_user in BsvUser.objects.all():
            # Append user data
            all_users.append({
                'user_id': bsv_user.id,
                'username': bsv_user.user.username,
                'name': bsv_user.user.first_name,
            })
        # Load page to show all users
        template_name = 'Recommender/admin_users_list.html'
        context = {'users': all_users}
        return render(request, template_name, context)
    else:
        # TODO: something went wrong page instead of oops
        return render(request, 'Recommender/oops.html')


# Remove a user in 'See this user' view
def admin_user_removal(request):
    bsv_user = BsvUser.objects.get(id=request.GET.get('user'))

    if request.user.is_superuser and bsv_user is not None:
        # Delete all profiles
        for profile in bsv_user.profiles.all():
            ProfileManager.delete_profile_data(request, profile.id)
        # Delete User model
        bsv_user.user.delete()
        # Delete BSV User model
        bsv_user.delete()
        # Go to users list
        return redirect('Recommender:admin_users_list')
    else:
        # TODO: something went wrong page instead of oops
        return render(request, 'Recommender/oops.html')


def admin_user_download_playlist_urls(request):
    bsv_user = BsvUser.objects.get(id=request.GET.get('user'))
    profile_id = request.GET.get('id')

    if request.user.is_superuser and bsv_user is not None:
        profile = bsv_user.profiles.get(id=profile_id)
        data_list_file = StringIO()
        writer = csv.DictWriter(data_list_file, fieldnames=['artist', 'title', 'yt_url'])
        writer.writeheader()
        for track in profile.playlist.all():
            track_data = {
                'artist': unidecode(track.track.artist),
                'title': unidecode(track.track.title),
                'yt_url': track.youtube
            }
            writer.writerow(track_data)
        data_list_file.seek(0)
        filename = 'playlist_urls - ' + bsv_user.user.first_name + ' (' + \
                   bsv_user.user.username + ') - ' + profile.name + '.csv'
        response = HttpResponse(data_list_file, content_type='application/csv')
        response['Content-Disposition'] = 'attachment; filename=' + filename
        return response
    else:
        # TODO: something went wrong page instead of oops
        return render(request, 'Recommender/oops.html')


# Access to User's Data Download Options View
def admin_user_download_options(request):
    if request.user.is_superuser:
        all_profiles = []
        # Load users list
        for bsv_user in BsvUser.objects.all():
            for profile in bsv_user.profiles.all():
                # Get all profiles basic data
                all_profiles.append({
                    'id': profile.id, 'name': profile.name,
                    'birth_year': profile.birth_year, 'birth_place': profile.birth_place,
                    'user_id': bsv_user.id,
                    'username': bsv_user.user.username, 'user_first_name': bsv_user.user.first_name,
                })

        # Load user data download options page
        context = {'profiles': all_profiles}
        template_name = 'Recommender/admin_user_download_options.html'
        return render(request, template_name, context)
    else:
        # TODO: something went wrong page instead of oops
        return render(request, 'Recommender/oops.html')


# Download user data selected in options view
def admin_data_download(request):
    # Options selected
    get_data_list = False
    get_data_analysis = False
    if request.POST.get('getDataList') is not None:
        get_data_list = True
    if request.POST.get('getDataAnalysis') is not None:
        get_data_analysis = True
    if not get_data_list and not get_data_analysis:
        # TODO: something went wrong page instead of oops
        return render(request, 'Recommender/oops.html')

    # Selected profiles IDs
    select_all = request.POST.get('selectAll')
    selected_ids = []
    if select_all is None:
        for field_name, field_value in request.POST.items():
            if 'getProfileID' in field_name:
                selected_ids.append(int(field_value))
    # Selected profiles data
    profiles_data = []
    for bsv_user in BsvUser.objects.all():
        for profile in bsv_user.profiles.all():
            if select_all is not None or profile.id in selected_ids:
                profiles_data.append([profile, bsv_user.user.username])

    # Generate CSV Files
    users_data_file, formatted_users_data = create_users_data_list(profiles_data)
    csv_files = []
    csv_names = []
    if get_data_list:
        csv_files.append(users_data_file)
        csv_names.append('users_data_list')
    if get_data_analysis:
        for user in formatted_users_data:
            for field in QuestionnaireFields.slash_song_lists_fields:
                user[field] = get_track_list_from_slashed_string(user[field])
            for field in QuestionnaireFields.slash_list_fields:
                user[field] = [x.lstrip() for x in user[field].split('//')]
            for field in QuestionnaireFields.comma_list_fields:
                user[field] = [x.lstrip() for x in user[field].split(',')]
        data_manager = UserDataManager()
        data_summary = data_manager.interpret_data(formatted_users_data)
        csv_files, csv_names = create_users_data_analysis(data_summary, csv_files, csv_names)

    # Zip CSV Files
    zipped_file = StringIO()
    with ZipFile(zipped_file, 'w') as zip:
        for i, csv_file in enumerate(csv_files):
            csv_file.seek(0)
            zip.writestr('{}.csv'.format(csv_names[i]), csv_file.read())
    zipped_file.seek(0)
    response = HttpResponse(zipped_file, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=bandasonoravital_data.zip'

    return response


# Returns Users Data List
def create_users_data_list(profiles_data):
    fieldnames = [
        'name', 'e-mail', 'birth_year', 'birth_place', 'places_lived', 'worked_at', 'music_at_work',
        'play_instrument', 'like_singing', 'group_singing', 'like_dancing',
        'preferred_genres', 'preferred_songs', 'preferred_artists',
        'sing_instrumental', 'upbeat_calm', 'cheerful_melancholic',
        'listen_instruments', 'listen_language', 'childhood', 'childhood_songs',
        'youth_dance', 'youth_dance_songs', 'radio', 'radio_programmes', 'tv', 'tv_programmes',
        'wedding_songs', 'good_memories', 'good_memories_songs', 'bad_memories', 'bad_memories_song',
        'playlist_feedback'
    ]
    playlist_fields = [
        '#', 'title ', 'artist ', 'year ',
        'familiar ', 'like ', 'memories ', 'listen again ', 'feedback ', 'playlist group '
    ]
    for i in range(1, Constants.PLAYLIST_LENGTH[4] + 1):
        for p_field in playlist_fields:
            fieldnames.append(p_field + str(i))
    data_list_file = StringIO()
    writer = csv.DictWriter(data_list_file, fieldnames=fieldnames)
    writer.writeheader()
    formatted_users_data = []
    for profile in profiles_data:
        username = profile[1]
        profile = profile[0]
        data = {
            'name': unidecode(profile.name),
            'e-mail': username,
            'birth_year': profile.birth_year,
            'birth_place': '' if profile.birth_place is None else unidecode(profile.birth_place),
            'places_lived': '' if profile.form is None else unidecode(profile.form.places_lived),
            'worked_at': '' if profile.form is None else unidecode(profile.form.worked_at),
            'music_at_work': '' if profile.form is None else profile.form.music_at_work,
            'play_instrument': '' if profile.form is None else unidecode(profile.form.instrument),
            'like_singing': '' if profile.form is None else profile.form.like_singing,
            'group_singing': '' if profile.form is None else unidecode(profile.form.group_singing),
            'like_dancing': '' if profile.form is None else profile.form.like_dancing,
            'preferred_genres': '' if profile.form is None else unidecode(profile.form.preferred_genres),
            'preferred_songs': '' if profile.form is None else unidecode(profile.form.preferred_songs),
            'preferred_artists': '' if profile.form is None else unidecode(profile.form.preferred_artists),
            'sing_instrumental': '' if profile.form is None else profile.form.sing_instrumental,
            'upbeat_calm': '' if profile.form is None else profile.form.upbeat_calm,
            'cheerful_melancholic': '' if profile.form is None else profile.form.cheerful_melancholic,
            'listen_instruments': '' if profile.form is None else unidecode(profile.form.listen_instruments),
            'listen_language': '' if profile.form is None else unidecode(profile.form.listen_language),
            'childhood': '' if profile.form is None else profile.form.childhood,
            'childhood_songs': '' if profile.form is None else unidecode(profile.form.childhood_songs),
            'youth_dance': '' if profile.form is None else profile.form.youth_dance,
            'youth_dance_songs': '' if profile.form is None else unidecode(profile.form.youth_dance_songs),
            'radio': '' if profile.form is None else profile.form.radio,
            'radio_programmes': '' if profile.form is None else unidecode(profile.form.radio_programmes),
            'tv': '' if profile.form is None else profile.form.tv,
            'tv_programmes': '' if profile.form is None else unidecode(profile.form.tv_programmes),
            'wedding_songs': '' if profile.form is None else unidecode(profile.form.wedding_songs),
            'good_memories': '' if profile.form is None else profile.form.good_memories,
            'good_memories_songs': '' if profile.form is None else unidecode(profile.form.good_memories_songs),
            'bad_memories': '' if profile.form is None else profile.form.bad_memories,
            'bad_memories_song': '' if profile.form is None else unidecode(profile.form.bad_memories_song),
            'playlist_feedback': unidecode(profile.playlist_feedback_text) if profile.playlist_feedback_text is not None else 'None'
        }
        for idx, track in enumerate(profile.playlist.all()):
            data['#' + str(idx + 1)] = '----'
            data['title ' + str(idx + 1)] = unidecode(track.track.title)
            data['artist ' + str(idx + 1)] = unidecode(track.track.artist)
            data['year ' + str(idx + 1)] = track.track.year
            data['familiar ' + str(idx + 1)] = track.feedback_familiar
            data['like ' + str(idx + 1)] = track.feedback_like
            data['memories ' + str(idx + 1)] = track.feedback_memories
            data['listen again ' + str(idx + 1)] = track.feedback_listen_again
            data['feedback ' + str(idx + 1)] = unidecode(track.feedback_text) \
                if track.feedback_text is not None else 'None'
            data['playlist group ' + str(idx + 1)] = track.playlist_group
        if len(profile.playlist.all()) < Constants.PLAYLIST_LENGTH[4]:
            for add_idx in range(len(profile.playlist.all()) + 1, Constants.PLAYLIST_LENGTH[4] + 1):
                data['#' + str(add_idx)] = '----'
                data['title ' + str(add_idx)] = ''
                data['artist ' + str(add_idx)] = ''
                data['year ' + str(add_idx)] = ''
                data['familiar ' + str(add_idx)] = ''
                data['like ' + str(add_idx)] = ''
                data['memories ' + str(add_idx)] = ''
                data['listen again ' + str(add_idx)] = ''
                data['feedback ' + str(add_idx)] = ''
                data['playlist group ' + str(add_idx)] = ''
        for k, v in data.items():
            if v == '' or v == 'None' or v is None:
                data[k] = 'N/A'
            if not isinstance(data[k], basestring):
                data[k] = str(data[k])
        formatted_users_data.append(data)
        writer.writerow(data)
    data_list_file.seek(0)
    return data_list_file, formatted_users_data


# Returns all excels with data structured for its analysis
def create_users_data_analysis(data_summary, csv_files, csv_names):
    # Playlist tracks and their feedback
    playlist_tracks = data_summary['all_playlist_tracks']
    data_file = StringIO()
    fieldnames = ['artist', 'title', 'count',
                  'familiar (YES)', 'familiar (NO)', 'familiar (N/A)',
                  'like (YES)', 'like (NO)', 'like (N/A)',
                  'listen again (YES)', 'listen again (NO)', 'listen again (N/A)',
                  'memories (YES)', 'memories (NO)', 'memories (N/A)',
                  'feedback text']
    writer = csv.DictWriter(data_file, fieldnames=fieldnames)
    writer.writeheader()
    for artist, artist_track in playlist_tracks.items():
        for title, feedback in artist_track.items():
            writer.writerow({
                'artist': artist,
                'title': title,
                'count': feedback.get('count'),
                'familiar (YES)': feedback['familiar'].get('Yes'),
                'familiar (NO)': feedback['familiar'].get('No'),
                'familiar (N/A)': feedback['familiar'].get('N/A'),
                'like (YES)': feedback['like'].get('Yes'),
                'like (NO)': feedback['like'].get('No'),
                'like (N/A)': feedback['like'].get('N/A'),
                'listen again (YES)': feedback['listen again'].get('Yes'),
                'listen again (NO)': feedback['listen again'].get('No'),
                'listen again (N/A)': feedback['listen again'].get('N/A'),
                'memories (YES)': feedback['memories'].get('Yes'),
                'memories (NO)': feedback['memories'].get('No'),
                'memories (N/A)': feedback['memories'].get('N/A'),
                'feedback text': feedback['texts']
            })
    data_file.seek(0)
    csv_files.append(data_file)
    csv_names.append('bsv_playlist_tracks')

    # Playlist Track Feedback
    playlists_fb = data_summary['playlists']
    data_file = StringIO()
    fieldnames = [
        'Feedback', 'Yes', 'No', 'N/A'
    ]
    writer = csv.DictWriter(data_file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({
        'Feedback': 'familiar',
        'Yes': playlists_fb['familiar'].get('Yes'),
        'No': playlists_fb['familiar'].get('No'),
        'N/A': playlists_fb['familiar'].get('N/A'),
    })
    writer.writerow({
        'Feedback': 'like',
        'Yes': playlists_fb['like'].get('Yes'),
        'No': playlists_fb['like'].get('No'),
        'N/A': playlists_fb['like'].get('N/A'),
    })
    writer.writerow({
        'Feedback': 'listen again',
        'Yes': playlists_fb['listen again'].get('Yes'),
        'No': playlists_fb['listen again'].get('No'),
        'N/A': playlists_fb['listen again'].get('N/A'),
    })
    writer.writerow({
        'Feedback': 'memories',
        'Yes': playlists_fb['memories'].get('Yes'),
        'No': playlists_fb['memories'].get('No'),
        'N/A': playlists_fb['memories'].get('N/A'),
    })
    data_file.seek(0)
    csv_files.append(data_file)
    csv_names.append('bsv_playlists_feedback')

    # Playlist Track Feedback by Playlist Group
    for group in QuestionnaireFields.playlist_groups:
        playlist_group_fb = data_summary['playlist_groups'][group]
        data_file = StringIO()
        fieldnames = [
            'Feedback', 'Yes', 'No', 'N/A'
        ]
        writer = csv.DictWriter(data_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({
            'Feedback': 'familiar',
            'Yes': playlist_group_fb['familiar'].get('Yes'),
            'No': playlist_group_fb['familiar'].get('No'),
            'N/A': playlist_group_fb['familiar'].get('N/A'),
        })
        writer.writerow({
            'Feedback': 'like',
            'Yes': playlist_group_fb['like'].get('Yes'),
            'No': playlist_group_fb['like'].get('No'),
            'N/A': playlist_group_fb['like'].get('N/A'),
        })
        writer.writerow({
            'Feedback': 'listen again',
            'Yes': playlist_group_fb['listen again'].get('Yes'),
            'No': playlist_group_fb['listen again'].get('No'),
            'N/A': playlist_group_fb['listen again'].get('N/A'),
        })
        writer.writerow({
            'Feedback': 'memories',
            'Yes': playlist_group_fb['memories'].get('Yes'),
            'No': playlist_group_fb['memories'].get('No'),
            'N/A': playlist_group_fb['memories'].get('N/A'),
        })
        data_file.seek(0)
        csv_files.append(data_file)
        csv_names.append('bsv_playlists_feedback_' + group)

    # Playlist Track Feedback by ReleaseYear-BirthYear (Reminiscence Bump)
    reminiscence_bump = data_summary['reminiscence_bump']
    data_file = StringIO()
    fieldnames = [
        'Year Difference',
        'Familiar (Yes)', 'Familiar (No)', 'Familiar (N/A)',
        'Like (Yes)', 'Like (No)', 'Like (N/A)',
        'Listen Again (Yes)', 'Listen Again (No)', 'Listen Again (N/A)',
        'Memories (Yes)', 'Memories (No)', 'Memories (N/A)',
    ]
    writer = csv.DictWriter(data_file, fieldnames=fieldnames)
    writer.writeheader()
    for year in reminiscence_bump:
        writer.writerow({
            'Year Difference': year,
            'Familiar (Yes)': reminiscence_bump[year]['familiar'].get('Yes'),
            'Familiar (No)': reminiscence_bump[year]['familiar'].get('No'),
            'Familiar (N/A)': reminiscence_bump[year]['familiar'].get('N/A'),
            'Like (Yes)': reminiscence_bump[year]['like'].get('Yes'),
            'Like (No)': reminiscence_bump[year]['like'].get('No'),
            'Like (N/A)': reminiscence_bump[year]['like'].get('N/A'),
            'Listen Again (Yes)': reminiscence_bump[year]['listen again'].get('Yes'),
            'Listen Again (No)': reminiscence_bump[year]['listen again'].get('No'),
            'Listen Again (N/A)': reminiscence_bump[year]['listen again'].get('N/A'),
            'Memories (Yes)': reminiscence_bump[year]['memories'].get('Yes'),
            'Memories (No)': reminiscence_bump[year]['memories'].get('No'),
            'Memories (N/A)': reminiscence_bump[year]['memories'].get('N/A'),
        })
    data_file.seek(0)
    csv_files.append(data_file)
    csv_names.append('bsv_reminiscence_bump')

    # Playlist feedback texts
    data_file = StringIO()
    fieldnames = ['Text']
    writer = csv.DictWriter(data_file, fieldnames=fieldnames)
    writer.writeheader()
    for text in playlists_fb['texts']:
        writer.writerow({
            'Text': text
        })
    data_file.seek(0)
    csv_files.append(data_file)
    csv_names.append('bsv_playlist_feedback_texts')

    # All preferred songs lists
    for field in QuestionnaireFields.song_lists:
        data_file = StringIO()
        file_name = 'bsv_tracks_' + field
        fieldnames = ['artist', 'title', 'count']
        writer = csv.DictWriter(data_file, fieldnames=fieldnames)
        writer.writeheader()
        track_list = data_summary[field]
        for artist, track in track_list.items():
            for title, count in track.items():
                writer.writerow({
                    'artist': artist,
                    'title': title,
                    'count': count
                })
        data_file.seek(0)
        csv_files.append(data_file)
        csv_names.append(file_name)

    # Preferred Artists
    pref_artists = data_summary['preferred_artists']
    data_file = StringIO()
    fieldnames = ['Preferred Artist', 'Count']
    writer = csv.DictWriter(data_file, fieldnames=fieldnames)
    writer.writeheader()
    for artist, count in pref_artists.items():
        writer.writerow({
            'Preferred Artist': artist,
            'Count': count
        })
    data_file.seek(0)
    csv_files.append(data_file)
    csv_names.append('bsv_preferred_artists')

    # Preferred Genres
    pref_genres = data_summary['preferred_genres']
    data_file = StringIO()
    fieldnames = ['Preferred Genre', 'Count']
    writer = csv.DictWriter(data_file, fieldnames=fieldnames)
    writer.writeheader()
    for genre, count in pref_genres.items():
        writer.writerow({
            'Preferred Genre': genre,
            'Count': count
        })
    data_file.seek(0)
    csv_files.append(data_file)
    csv_names.append('bsv_preferred_genres')

    # Special Genres and Users
    sp_genres = data_summary['special_genres']
    for genre in QuestionnaireFields.special_genres_dec:
        data_file = StringIO()
        fieldnames = ['User', 'Birth Year', 'Contact']
        writer = csv.DictWriter(data_file, fieldnames=fieldnames)
        writer.writeheader()
        for user in sp_genres[genre]:
            writer.writerow({
                'User': user['user'],
                'Birth Year': user['birth_year'],
                'Contact': user['contact']
            })
        data_file.seek(0)
        csv_files.append(data_file)
        csv_names.append('bsv_sp_gen' + genre)

    # Preferred Features
    data_file = StringIO()
    fieldnames = ['Type', 'First', 'Second', 'Both', 'N/A']
    writer = csv.DictWriter(data_file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({
        'Type': 'Cheerful or Melancholic',
        'First': data_summary['cheerful_melancholic'].get('cheerful'),
        'Second': data_summary['cheerful_melancholic'].get('melancholic'),
        'Both': data_summary['cheerful_melancholic'].get('cheerful and melancholic'),
        'N/A': data_summary['cheerful_melancholic'].get('N/A')
    })
    writer.writerow({
        'Type': 'Sing or Instrumental',
        'First': data_summary['sing_instrumental'].get('sing'),
        'Second': data_summary['sing_instrumental'].get('instrumental'),
        'Both': data_summary['sing_instrumental'].get('sing and instrumental'),
        'N/A': data_summary['sing_instrumental'].get('N/A')
    })
    writer.writerow({
        'Type': 'Upbeat or Calm',
        'First': data_summary['upbeat_calm'].get('upbeat'),
        'Second': data_summary['upbeat_calm'].get('calm'),
        'Both': data_summary['upbeat_calm'].get('upbeat and calm'),
        'N/A': data_summary['upbeat_calm'].get('N/A')
    })
    data_file.seek(0)
    csv_files.append(data_file)
    csv_names.append('bsv_preferred_features')

    # Users: Birth year
    data_file = StringIO()
    fieldnames = ['Year', 'Count']
    writer = csv.DictWriter(data_file, fieldnames=fieldnames)
    writer.writeheader()
    for year, count in data_summary['birth_year'].items():
        writer.writerow({
            'Year': year,
            'Count': count
        })
    data_file.seek(0)
    csv_files.append(data_file)
    csv_names.append('bsv_users_birth_year')

    # Users: Birth place
    data_file = StringIO()
    fieldnames = ['Place', 'Count']
    writer = csv.DictWriter(data_file, fieldnames=fieldnames)
    writer.writeheader()
    for place, count in data_summary['birth_place'].items():
        writer.writerow({
            'Place': place,
            'Count': count
        })
    data_file.seek(0)
    csv_files.append(data_file)
    csv_names.append('bsv_users_birth_place')

    # Users: Work places
    data_file = StringIO()
    fieldnames = ['Work Place', 'Count']
    writer = csv.DictWriter(data_file, fieldnames=fieldnames)
    writer.writeheader()
    for work_place, count in data_summary['worked_at'].items():
        writer.writerow({
            'Work Place': work_place,
            'Count': count
        })
    data_file.seek(0)
    csv_files.append(data_file)
    csv_names.append('bsv_users_work_place')

    # Users: Instruments
    data_file = StringIO()
    fieldnames = ['Instrument', 'Like Listen', 'Play']
    writer = csv.DictWriter(data_file, fieldnames=fieldnames)
    writer.writeheader()
    instruments = ['bajo', 'guitar', 'n/a', 'percussion', 'sax', 'violin', 'voice']
    for instrument in instruments:
        play_instrument = instrument
        if instrument == 'bajo':
            play_instrument = 'bajo electrico'
        writer.writerow({
            'Instrument': instrument,
            'Like Listen': data_summary['listen_instruments'].get(instrument),
            'Play': data_summary['play_instrument'].get(play_instrument)
        })
    data_file.seek(0)
    csv_files.append(data_file)
    csv_names.append('bsv_users_instruments')

    # Users: Languages
    data_file = StringIO()
    fieldnames = ['Language', 'Count']
    writer = csv.DictWriter(data_file, fieldnames=fieldnames)
    writer.writeheader()
    for language, count in data_summary['listen_language'].items():
        writer.writerow({
            'Language': language,
            'Count': count
        })
    data_file.seek(0)
    csv_files.append(data_file)
    csv_names.append('bsv_users_languages')

    # Users: Memories
    data_file = StringIO()
    fieldnames = ['Memories', 'Yes', 'No']
    writer = csv.DictWriter(data_file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({
        'Memories': 'Good memories',
        'Yes': data_summary['good_memories'].get('yes'),
        'No': data_summary['good_memories'].get('no')
    })
    writer.writerow({
        'Memories': 'Bad memories',
        'Yes': data_summary['bad_memories'].get('yes'),
        'No': data_summary['bad_memories'].get('no')
    })
    data_file.seek(0)
    csv_files.append(data_file)
    csv_names.append('bsv_users_memories')

    # Users: Relation with music
    data_file = StringIO()
    fieldnames = ['Type', '3', '2', '1', '0', 'N/A']
    writer = csv.DictWriter(data_file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({
        'Type': 'Childhood Memories',
        '3': data_summary['childhood'].get('lot'),
        '2': 0,
        '1': data_summary['childhood'].get('little'),
        '0': data_summary['childhood'].get('no'),
        'N/A': data_summary['childhood'].get('n/a')
    })
    writer.writerow({
        'Type': 'Radio Memories',
        '3': data_summary['radio'].get('lot'),
        '2': 0,
        '1': data_summary['radio'].get('little'),
        '0': data_summary['radio'].get('no'),
        'N/A': data_summary['radio'].get('n/a')
    })
    writer.writerow({
        'Type': 'Tv Memories',
        '3': data_summary['tv'].get('lot'),
        '2': 0,
        '1': data_summary['tv'].get('little'),
        '0': data_summary['tv'].get('no'),
        'N/A': data_summary['tv'].get('n/a')
    })
    writer.writerow({
        'Type': 'Like Dancing',
        '3': data_summary['like_dancing'].get('like a lot'),
        '2': data_summary['like_dancing'].get('like'),
        '1': data_summary['like_dancing'].get('like a little'),
        '0': data_summary['like_dancing'].get("don't like"),
        'N/A': data_summary['like_dancing'].get('n/a')
    })
    writer.writerow({
        'Type': 'Like Singing',
        '3': data_summary['like_singing'].get('like a lot'),
        '2': data_summary['like_singing'].get('like'),
        '1': data_summary['like_singing'].get('like a little'),
        '0': data_summary['like_singing'].get("don't like"),
        'N/A': data_summary['like_singing'].get('n/a')
    })
    data_file.seek(0)
    csv_files.append(data_file)
    csv_names.append('bsv_users_relation_with_music')

    # Radio Programmes
    data_file = StringIO()
    fieldnames = ['Radio Programme', 'Count']
    writer = csv.DictWriter(data_file, fieldnames=fieldnames)
    writer.writeheader()
    for programme, count in data_summary['radio_programmes'].items():
        writer.writerow({
            'Radio Programme': programme,
            'Count': count
        })
    data_file.seek(0)
    csv_files.append(data_file)
    csv_names.append('bsv_radio_programmes')

    # Tv Programmes
    data_file = StringIO()
    fieldnames = ['Tv Programme', 'Count']
    writer = csv.DictWriter(data_file, fieldnames=fieldnames)
    writer.writeheader()
    for programme, count in data_summary['tv_programmes'].items():
        writer.writerow({
            'Tv Programme': programme,
            'Count': count
        })
    data_file.seek(0)
    csv_files.append(data_file)
    csv_names.append('bsv_tv_programmes')

    # Radio memories and Birth Year
    data_file = StringIO()
    fieldnames = ['Birth Year', 'Count']
    writer = csv.DictWriter(data_file, fieldnames=fieldnames)
    writer.writeheader()
    for year, count in data_summary['radio_birth_year'].items():
        writer.writerow({
            'Birth Year': year,
            'Count': count
        })
    data_file.seek(0)
    csv_files.append(data_file)
    csv_names.append('bsv_radio_birth_year')

    # Tv memories and Birth Year
    data_file = StringIO()
    fieldnames = ['Birth Year', 'Count']
    writer = csv.DictWriter(data_file, fieldnames=fieldnames)
    writer.writeheader()
    for year, count in data_summary['tv_birth_year'].items():
        writer.writerow({
            'Birth Year': year,
            'Count': count
        })
    data_file.seek(0)
    csv_files.append(data_file)
    csv_names.append('bsv_tv_birth_year')

    return csv_files, csv_names


class UserDataManager(object):
    def __init__(self):
        self.data_summary = dict()
        for field in QuestionnaireFields.single_item_fields:
            self.data_summary[field] = dict()
        self.data_summary['radio_birth_year'] = dict()
        self.data_summary['tv_birth_year'] = dict()
        for field in QuestionnaireFields.list_fields:
            self.data_summary[field] = dict()
        for field in QuestionnaireFields.track_list_fields:
            self.data_summary[field] = dict()
        self.data_summary['all_preferred_songs'] = dict()
        self.data_summary['all_playlist_tracks'] = dict()
        self.data_summary['playlists'] = dict()
        self.data_summary['reminiscence_bump'] = dict()
        for field in QuestionnaireFields.playlist_fields:
            self.data_summary['playlists'][field] = dict()
        self.data_summary['playlists']['texts'] = []
        self.data_summary['playlist_groups'] = dict()
        for group in QuestionnaireFields.playlist_groups:
            self.data_summary['playlist_groups'][group] = dict()
            for field in QuestionnaireFields.playlist_fields:
                self.data_summary['playlist_groups'][group][field] = dict()
        self.data_summary['special_genres'] = dict()
        for genre in QuestionnaireFields.special_genres:
            genre_dec = unidecode(genre.decode('utf-8'))
            self.data_summary['special_genres'][genre_dec] = []

    def add_to_field(self, field, item):
        item = unidecode(item.lower().decode('utf-8'))
        if item not in self.data_summary[field]:
            self.data_summary[field][item] = 1
        else:
            self.data_summary[field][item] += 1

    def add_single_track(self, field, artist, title):
        artist_dec = unidecode(artist.lower().decode('utf-8'))
        title_dec = unidecode(title.lower().decode('utf-8'))

        if artist_dec not in self.data_summary[field]:
            self.data_summary[field][artist_dec] = dict()
        if title_dec not in self.data_summary[field][artist_dec]:
            self.data_summary[field][artist_dec][title_dec] = 1
        else:
            self.data_summary[field][artist_dec][title_dec] += 1

    def add_tracks(self, field, track_list):
        for item in track_list:
            self.add_single_track(field, item['artist'], item['title'])
            if field != 'bad_memories_songs':
                self.add_single_track('all_preferred_songs', item['artist'], item['title'])

    def add_playlist_fields(self, item):
        for idx in range(1, 16):
            if item['feedback ' + str(idx)] != 'N/A':
                self.data_summary['playlists']['texts'].append(item['feedback ' + str(idx)])
            artist_dec = unidecode(item['artist ' + str(idx)].lower().decode('utf-8'))
            title_dec = unidecode(item['title ' + str(idx)].lower().decode('utf-8'))
            if artist_dec not in self.data_summary['all_playlist_tracks']:
                self.data_summary['all_playlist_tracks'][artist_dec] = dict()
            if title_dec not in self.data_summary['all_playlist_tracks'][artist_dec]:
                self.data_summary['all_playlist_tracks'][artist_dec][title_dec] = dict()
                self.data_summary['all_playlist_tracks'][artist_dec][title_dec]['count'] = 0
            self.data_summary['all_playlist_tracks'][artist_dec][title_dec]['count'] += 1
            if 'texts' not in self.data_summary['all_playlist_tracks'][artist_dec][title_dec]:
                self.data_summary['all_playlist_tracks'][artist_dec][title_dec]['texts'] = ''
            else:
                if item['feedback ' + str(idx)] != 'N/A':
                    self.data_summary['all_playlist_tracks'][artist_dec][title_dec]['texts'] += ' // '
            if item['feedback ' + str(idx)] != 'N/A':
                self.data_summary['all_playlist_tracks'][artist_dec][title_dec]['texts'] += \
                    item['feedback ' + str(idx)]

            for f in QuestionnaireFields.playlist_fields:
                # Track feedback by feedback field
                field = f + ' ' + str(idx)
                if item[field] not in self.data_summary['playlists'][f]:
                    self.data_summary['playlists'][f][item[field]] = 1
                else:
                    self.data_summary['playlists'][f][item[field]] += 1
                # Track feedback by difference year, release_year - birth_year (reminiscence bump)
                if item['year ' + str(idx)] != 'N/A' and item['birth_year'] != 'N/A':
                    year_diff = int(item['year ' + str(idx)]) - int(item['birth_year'])
                    if 0 < year_diff < 30:
                        if year_diff not in self.data_summary['reminiscence_bump']:
                            self.data_summary['reminiscence_bump'][year_diff] = dict()
                            for f_ in QuestionnaireFields.playlist_fields:
                                self.data_summary['reminiscence_bump'][year_diff][f_] = dict()
                        if item[field] not in self.data_summary['reminiscence_bump'][year_diff][f]:
                            self.data_summary['reminiscence_bump'][year_diff][f][item[field]] = 1
                        else:
                            self.data_summary['reminiscence_bump'][year_diff][f][item[field]] += 1
                # Track feedback by playlist group
                playlist_group = item['playlist group ' + str(idx)]
                if playlist_group in self.data_summary['playlist_groups']:
                    if item[field] not in self.data_summary['playlist_groups'][playlist_group][f]:
                        self.data_summary['playlist_groups'][playlist_group][f][item[field]] = 1
                    else:
                        self.data_summary['playlist_groups'][playlist_group][f][item[field]] += 1
                # Track feedback (all tracks)
                self.data_summary['all_playlist_tracks'][artist_dec][title_dec][f] = dict()
                if item[field] not in self.data_summary['all_playlist_tracks'][artist_dec][title_dec][f]:
                    self.data_summary['all_playlist_tracks'][artist_dec][title_dec][f][item[field]] = 1
                else:
                    self.data_summary['all_playlist_tracks'][artist_dec][title_dec][f][item[field]] += 1

    def interpret_data(self, data):
        for item in data:
            # Single Item Fields
            for field in QuestionnaireFields.single_item_fields:
                self.add_to_field(field, item[field])
                if field == 'radio' or field == 'tv' and item[field] == 'Lot':
                    if item['birth_year'] not in self.data_summary[field + '_birth_year']:
                        self.data_summary[field + '_birth_year'][item['birth_year']] = 0
                    self.data_summary[field + '_birth_year'][item['birth_year']] += 1
            # List Item Fields
            for field in QuestionnaireFields.list_fields:
                for sub_item in item[field]:
                    self.add_to_field(field, sub_item)
                    if sub_item in QuestionnaireFields.special_genres:
                        sub_item_dec = unidecode(sub_item.decode('utf-8'))
                        self.data_summary['special_genres'][sub_item_dec].append({
                            'user': item['name'],
                            'birth_year': item['birth_year'],
                            'contact': item['e-mail']
                        })
            # Track List Fields
            for field in QuestionnaireFields.track_list_fields:
                self.add_tracks(field, item[field])
            # Playlist Fields
            self.add_playlist_fields(item)
        return self.data_summary
