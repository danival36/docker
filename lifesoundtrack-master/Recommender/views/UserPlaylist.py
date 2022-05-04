from django.shortcuts import render
from django.http import HttpResponse
from Recommender.models import UserProfile
from Spotify import SpotifyManager, spotify_login
import ProfileManager


def user_playlist(request):
    profile = UserProfile.objects.get(id=request.GET.get('id'))

    if ProfileManager.user_manages_profile(request.user, profile):
        profile_data = {
            'id': profile.id,
            'name': profile.name,
        }

        playlist_url = profile.playlist_url
        playlist_obj = profile.playlist.all()
        playlist = []

        for track in playlist_obj:
            if track.feedback_listen_again != 'No':
                playlist.append({'Title': track.track.title,
                                 'Artist': track.track.artist,
                                 'Preview': track.track.preview,
                                 'Youtube': track.youtube,
                                 'FeedbackDone': track.feedback_done,
                                 'ID': track.track.spotify_id})

        user_id = ProfileManager.get_user_id(request.user, request.GET.get('user'))
        username, user_first_name = \
            ProfileManager.get_user_names(request.user, request.user.username, request.user.first_name)

        # Render playlist and feedback for this user:
        template_name = 'Recommender/playlist.html'
        context = {'user_id': user_id,
                   'user_email': username,
                   'playlist': playlist,
                   'playlist_url': playlist_url,
                   'profile': profile_data,
                   'playlist_feedback_text': profile.playlist_feedback_text}
        return render(request, template_name, context)

    else:
        # TODO: something went wrong page instead of oops
        return render(request, 'Recommender/oops.html')


def save_feedback_text(request):
    profile = UserProfile.objects.get(id=request.GET.get('id'))
    is_text_saved = False

    if request.method == 'GET' and ProfileManager.user_manages_profile(request.user, profile):
        p = request.GET.copy()
        if 'playlist_feedback_text' in p:
            profile.playlist_feedback_text = p['playlist_feedback_text'][:1000]
            profile.save()
            is_text_saved = True
        return HttpResponse(is_text_saved)

    else:
        # TODO: something went wrong page instead of oops
        return render(request, 'Recommender/oops.html')


def save_track_feedback(request):
    profile = UserProfile.objects.get(id=request.GET.get('id'))
    is_fb_saved = False
    familiarity = ''
    like = ''
    memories = ''
    listen = ''
    text = ''

    if request.method == "GET" and ProfileManager.user_manages_profile(request.user, profile):
        p = request.GET.copy()
        if 'track_name' in p:
            track_name = p['track_name']
            if 'n_track' in p:
                n_track = int(p['n_track'])
            if 'familiarity' in p:
                familiarity = p['familiarity']
            if 'like' in p:
                like = p['like']
            if 'memories' in p:
                memories = p['memories']
            if 'listen' in p:
                listen = p['listen']
            if 'text' in p:
                text = p['text']

            playlist_obj = profile.playlist.all()

            for item in playlist_obj:
                if item.track.title in track_name and item.track.artist in track_name:
                    profile.playlist.remove(item)
                    item.feedback_done = True
                    item.feedback_familiar = familiarity
                    item.feedback_like = like
                    item.feedback_memories = memories
                    item.feedback_listen_again = listen
                    item.feedback_text = text
                    if listen == 'No':
                        spotify_login(request)
                        spotify = SpotifyManager()
                        playlist_id = profile.playlist_url.split('/playlist/')[1]
                        spotify.remove_track_from_playlist(
                            playlist_id, item.track.spotify_id, item.playlist_position,
                            request.session.get('spotify_token')
                        )
                        item.playlist_position = 0
                        new_pos = 1
                        for track in profile.playlist.all():
                            if track.playlist_position != 0:
                                track.playlist_position = new_pos
                                track.save()
                                new_pos += 1
                        profile.playlist_length -= 1
                        profile.negative_feedback_tracks.add(item.track)
                    elif listen == 'Yes':
                        item.track.user_popularity += 1
                    item.save()
                    profile.save()
                    profile.playlist.add(item)
                    profile.save()
                    is_fb_saved = True
        return HttpResponse(is_fb_saved)

    else:
        # TODO: something went wrong page instead of oops
        return render(request, 'Recommender/oops.html')

