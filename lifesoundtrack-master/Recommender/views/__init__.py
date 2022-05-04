# Home view
from Home import home, switch_language

# User Signup
from SignUp import signup, email_validation, password_validation, register_button_validation, \
    user_registration, user_confirmation, user_activation, \
    forgot_password, send_reset_password_email, \
    reset_password, reset_pwd_button_validation, save_new_password
# User Login
from Login import bsv_login, user_login

# User Profile Manager
from ProfileManager import profile_manager_menu, show_profile, create_profile, save_profile, delete_profile

# Data entry & Playlist generation
from DataEntry import data_entry, save_data
from CreatePlaylist import create_playlist_request, create_playlist
# Spotify
from Spotify import spotify_login, spotify_redirect
# Playlist feedback & listen
from UserPlaylist import user_playlist, save_track_feedback, save_feedback_text

# Admin BSV users
from BsvAdmin import bsv_admin_login, admin_login, admin_menu, admin_users_list, admin_user_removal, \
    admin_user_download_playlist_urls, admin_user_download_options, admin_data_download
from BsvAdminSongs import admin_hits, add_hits_to_db, download_hits_db, download_model_hits_db, remove_hits_db, \
    admin_songs_tagger, admin_songs_add_tags, track_search, track_results, add_track_to_hits, \
    admin_genre_tracks, download_genre_tracks_db, add_genre_tracks_to_db, \
    download_model_genre_tracks_db, remove_genre_tracks_db

# OTHER
from Errors import oops
