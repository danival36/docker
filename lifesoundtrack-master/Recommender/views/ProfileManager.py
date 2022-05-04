from django.shortcuts import render, redirect, reverse
from django.utils import translation
from Recommender.models import BsvUser, UserProfile
from Recommender.utils import QuestionnaireFields
from Spotify import spotify_login, SpotifyManager


def profile_manager_menu(request):
    bsv_user = get_bsv_user(request.user, request.GET.get('user'))

    # If it's correct go to profile manager menu
    if bsv_user is not None and user_is_correct(request.user, request.GET.get('user'), bsv_user):
        profiles = []
        for profile in bsv_user.profiles.all():
            profiles.append({
                'id': profile.id,
                'name': profile.name,
                'birth_year': profile.birth_year,
                'birth_place': profile.birth_place,
                'language': profile.language,
            })
        no_profiles_yet = False
        if len(profiles) == 0:
            no_profiles_yet = True
        user_id = get_user_id(request.user, bsv_user.id)
        username, user_first_name = get_user_names(request.user, bsv_user.user.username, bsv_user.user.first_name)
        # Load Profile manager menu
        template_name = 'Recommender/profile_manager_menu.html'
        context = {
            'user_id': user_id,
            'user': username,
            'user_first_name': user_first_name,
            'profiles': profiles,
            'no_profiles_yet': no_profiles_yet
        }
        return render(request, template_name, context)
    else:
        # TODO: something went wrong page instead of oops
        return render(request, 'Recommender/oops.html')


def get_user_id(user, user_id):
    if not user.is_superuser:
        user_id = user.bsvuser.id
    return user_id


def get_user_names(user, username, user_first_name):
    if not user.is_superuser:
        username = user.username
        user_first_name = user.first_name
    return username, user_first_name


def get_bsv_user(user, user_id):
    # Check if it's a superuser or a user using the correct id in the request to assign bsv_user
    if user.is_superuser:
        bsv_user = BsvUser.objects.get(id=user_id)
    elif str(user.bsvuser.id) == user_id:
        bsv_user = user.bsvuser
    else:
        bsv_user = None
    return bsv_user


def user_manages_profile(user, profile):
    if user.is_superuser or profile in user.bsvuser.profiles.all():
        manages_profile = True
    else:
        manages_profile = False
    return manages_profile


def user_is_correct(user, user_id, bsv_user):
    if user.is_superuser or str(bsv_user.id) == user_id:
        is_correct = True
    else:
        is_correct = False
    return is_correct


def show_profile(request):
    profile = UserProfile.objects.get(id=request.GET.get('id'))

    if profile is not None and user_manages_profile(request.user, profile):
        form = None
        playlist = None

        if profile.form is not None:
            # Get all profile data
            other_data, music, memories, \
                playlist_url, playlist_fb_text, playlist, playlist_length \
                = get_profile_data(profile)

            form = {
                'other_data': other_data,
                'music': music,
                'memories': memories
            }

            if len(profile.playlist.all()) != 0:
                playlist = {
                    'tracks': playlist,
                    'length': playlist_length,
                    'url': playlist_url,
                    'feedback_text': playlist_fb_text
                }
            else:
                playlist = None

        user_id = get_user_id(request.user, request.GET.get('user'))

        profile_data = {
            'superuser': request.user.is_superuser,
            'user_id': user_id,
            'id': profile.id,
            'name': profile.name,
            'birth_year': profile.birth_year,
            'birth_place': profile.birth_place,
            'language': profile.language,
            'form': form,
            'playlist': playlist
        }

        context = {'profile': profile_data}
        template_name = 'Recommender/profile.html'
        translation.activate(profile.language)
        return render(request, template_name, context)

    else:
        # TODO: something went wrong page instead of oops
        return render(request, 'Recommender/oops.html')


def create_profile(request):
    bsv_user = get_bsv_user(request.user, request.GET.get('user'))
    if bsv_user is not None and user_is_correct(request.user, request.GET.get('user'), bsv_user):
        if request.session.get('lang') is not None:
            language = request.session['lang']
        else:
            language = bsv_user.language
        regions = QuestionnaireFields.regions
        user_id = get_user_id(request.user, request.GET.get('user'))
        context = {
            'user_id': user_id,
            'regions': regions[language],
        }
        template_name = 'Recommender/profile_create.html'
        return render(request, template_name, context)
    else:
        # TODO: something went wrong page instead of oops
        return render(request, 'Recommender/oops.html')


def save_profile(request):
    bsv_user = get_bsv_user(request.user, request.GET.get('user'))
    if bsv_user is not None and user_is_correct(request.user, request.GET.get('user'), bsv_user):
        new_profile = UserProfile()
        new_profile.name = request.POST.get(u'name')
        new_profile.birth_year = request.POST.get(u'birthyear')
        new_profile.birth_place = request.POST.get(u'birthplace')
        new_profile.language = request.POST.get(u'language')
        new_profile.save()
        bsv_user.profiles.add(new_profile)
        bsv_user.save()
        user_id = get_user_id(request.user, request.GET.get('user'))
        return redirect(reverse('Recommender:profile_manager_menu') + '?user=' + str(user_id))
    else:
        # TODO: something went wrong page instead of oops
        return render(request, 'Recommender/oops.html')


def delete_profile_data(request, profile_id):
    deleted_profile = False

    profile = UserProfile.objects.get(id=profile_id)

    if profile is not None and user_manages_profile(request.user, profile):

        # Get Playlist ID
        playlist_id = None
        if profile.playlist_url is not None and profile.playlist_url != '#':
            playlist_id = profile.playlist_url.split('/playlist/')[1]

        # Delete playlist's UserTrack(s) from DB
        all_track_ids = []
        playlist = profile.playlist.all()
        for user_track in playlist:
            all_track_ids.append(user_track.track.spotify_id)
            user_track.delete()

        # Delete user's Form from DB
        if profile.form is not None:
            profile.form.delete()

        # Delete Profile
        profile.delete()

        # Remove Spotify playlist
        if playlist_id is not None:
            spotify_login(request)
            spotify = SpotifyManager()
            spotify.remove_playlist(playlist_id, all_track_ids, request.session.get('spotify_token'))

        deleted_profile = True

    return deleted_profile


def delete_profile(request):
    if delete_profile_data(request, request.GET.get('id')):
        # Redirect to profile manager
        user_id = get_user_id(request.user, request.GET.get('user'))
        return redirect(reverse('Recommender:profile_manager_menu') + '?user=' + str(user_id))
    else:
        # TODO: something went wrong page instead of oops
        return render(request, 'Recommender/oops.html')


def get_profile_data(profile):

    # Load form
    form = profile.form

    if form is not None:
        # Get profile form (music)
        profile_music = {
            'worked_at': form.worked_at,
            'music_at_work': form.music_at_work,
            'instrument': form.instrument,
            'like_singing': form.like_singing,
            'group_singing': form.group_singing,
            'like_dancing': form.like_dancing,
            'preferred_genres': form.preferred_genres,
            'preferred_songs': form.preferred_songs,
            'preferred_artists': form.preferred_artists
        }

        # Get profile form (memories)
        profile_memories = {
            'sing_instrumental': form.sing_instrumental,
            'upbeat_calm': form.upbeat_calm,
            'cheerful_melancholic': form.cheerful_melancholic,
            'listen_instruments': form.listen_instruments,
            'listen_languages': form.listen_language,
            'childhood': form.childhood,
            'childhood_songs': form.childhood_songs,
            'youth_dance': form.youth_dance,
            'youth_dance_songs': form.youth_dance_songs,
            'radio': form.radio,
            'radio_programmes': form.radio_programmes,
            'tv': form.tv,
            'tv_programmes': form.tv_programmes,
            'wedding_songs': form.wedding_songs,
            'good_memories': form.good_memories,
            'good_memories_songs': form.good_memories_songs,
            'bad_memories': form.bad_memories,
            'bad_memories_song': form.bad_memories_song,
            'all_preferred_songs': form.all_preferred_songs
        }

        # Get other data from profile
        profile_other_data = {
            'submit_day': form.day_submitted,
            'submit_hour': form.hour_submitted,
            'places_lived': form.places_lived
        }
    else:
        profile_music = 'N/A'
        profile_memories = 'N/A'
        profile_other_data = 'N/A'

    # Get user playlist
    profile_playlist_url = profile.playlist_url
    profile_playlist_fb_text = profile.playlist_feedback_text
    profile_playlist = []

    playlist = profile.playlist.all()

    for t in playlist:
        profile_playlist.append({
            'title': t.track.title, 'artist': t.track.artist,
            'preview': t.track.preview, 'youtube': t.youtube,
            'spotify_id': t.track.spotify_id,
            'pos': t.playlist_position, 'playlist_group': t.playlist_group,
            'fb_familiar': t.feedback_familiar, 'fb_like': t.feedback_like,
            'fb_memories': t.feedback_memories, 'fb_listen_again': t.feedback_listen_again,
            'fb_text': t.feedback_text
        })

    playlist_length = profile.playlist_length

    return profile_other_data, profile_music, profile_memories, \
        profile_playlist_url, profile_playlist_fb_text, profile_playlist, playlist_length
