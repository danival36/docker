# -*- coding: UTF-8 -*-

from django.conf.urls import url
from Recommender import views

urlpatterns = [url(r'^$', views.home, name='home'),
               url(r'^switch_language', views.switch_language, name='switch_language'),

               # User signup
               url(r'^signup', views.signup, name='signup'),
               url(r'^email_validation', views.email_validation, name='email_validation'),
               url(r'^password_validation', views.password_validation, name='password_validation'),
               url(r'^register_button_validation', views.register_button_validation, name='register_button_validation'),
               url(r'^user_registration', views.user_registration, name='user_registration'),
               url(r'^user_confirmation', views.user_confirmation, name='user_confirmation'),
               url(r'^user_activation/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                   views.user_activation, name='user_activation'),
               url(r'^forgot_password', views.forgot_password, name='forgot_password'),
               url(r'^send_reset_password_email', views.send_reset_password_email, name='send_reset_password_email'),
               url(r'^reset_password/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                   views.reset_password, name='reset_password'),
               url(r'^reset_pwd_button_validation',
                   views.reset_pwd_button_validation, name='reset_pwd_button_validation'),
               url(r'^save_new_password', views.save_new_password, name='save_new_password'),

               # User login
               url(r'^login', views.bsv_login, name='login'),
               url(r'^user_login', views.user_login, name='user_login'),

               # User profile manager
               url(r'^profile_manager_menu/$', views.profile_manager_menu, name='profile_manager_menu'),
               url(r'^profile/$', views.show_profile, name='profile'),
               url(r'^profile_create', views.create_profile, name='profile_create'),
               url(r'^profile_save', views.save_profile, name='profile_save'),
               url(r'^profile_delete/$', views.delete_profile, name='profile_delete'),

               # Data entry & playlist generation
               url(r'^data_entry/$', views.data_entry, name='data_entry'),
               url(r'^save_data/$', views.save_data, name='save_data'),
               url(r'^create_playlist_request/$', views.create_playlist_request, name='create_playlist_request'),
               url(r'^create_playlist', views.create_playlist, name='create_playlist'),

               # Spotify login
               url(r'^spotify_login', views.spotify_login, name='spotify_login'),
               url(r'^spotify_redirect', views.spotify_redirect, name='spotify_redirect'),

               # Playlist feedback & listen
               url(r'^playlist/$', views.user_playlist, name='playlist'),
               url(r'^save_track_feedback/$', views.save_track_feedback, name='save_track_feedback'),
               url(r'^save_feedback_text/$', views.save_feedback_text, name='save_feedback_text'),

               # Admin login
               url(r'^bsv_admin_login', views.bsv_admin_login, name='bsv_admin_login'),
               url(r'^admin_login', views.admin_login, name='admin_login'),
               url(r'^admin_menu', views.admin_menu, name='admin_menu'),

               # Admin BSV users
               url(r'^admin_users_list', views.admin_users_list, name='admin_users_list'),
               url(r'^admin_user_removal/$', views.admin_user_removal, name='admin_user_removal'),
               url(r'^admin_user_download_playlist_urls/$', views.admin_user_download_playlist_urls,
                   name='admin_user_download_playlist_urls'),
               url(r'^admin_user_download_options',
                   views.admin_user_download_options, name='admin_user_download_options'),
               url(r'^admin_data_download',
                   views.admin_data_download, name='admin_data_download'),

               # Admin songs (hits)
               url(r'^admin_hits', views.admin_hits, name='admin_hits'),
               url(r'^track_search', views.track_search, name='track_search'),
               url(r'^track_results', views.track_results, name='track_results'),
               url(r'^add_track_to_hits', views.add_track_to_hits, name='add_track_to_hits'),
               url(r'^download_hits_db', views.download_hits_db, name='download_hits_db'),
               url(r'^add_hits_to_db', views.add_hits_to_db, name='add_hits_to_db'),
               url(r'^download_model_hits_db', views.download_model_hits_db, name='download_model_hits_db'),
               url(r'^remove_hits_db', views.remove_hits_db, name='remove_hits_db'),
               url(r'^admin_genre_tracks', views.admin_genre_tracks, name='admin_genre_tracks'),
               url(r'^download_genre_tracks_db', views.download_genre_tracks_db, name='download_genre_tracks_db'),
               url(r'^add_genre_tracks_to_db', views.add_genre_tracks_to_db, name='add_genre_tracks_to_db'),
               url(r'^download_model_genre_tracks_db', views.download_model_genre_tracks_db,
                   name='download_model_genre_tracks_db'),
               url(r'^remove_genre_tracks_db', views.remove_genre_tracks_db, name='remove_genre_tracks_db'),
               url(r'^admin_songs_tagger', views.admin_songs_tagger, name='admin_songs_tagger'),
               url(r'^admin_songs_add_tags', views.admin_songs_add_tags, name='admin_songs_add_tags'),

               # OTHER
               url(r'^oops', views.oops, name='oops'), ]
