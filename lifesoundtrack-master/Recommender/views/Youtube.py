# -*- coding: UTF-8 -*-
import requests
from Recommender.constants import Constants
from Spotify import SpotifyTitleIgnore
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from unidecode import unidecode
import re


class YoutubeManager(object):
    def __init__(self):
        self.DEVELOPER_KEY = Constants.YOUTUBE_KEY
        self.YOUTUBE_API_SERVICE_NAME = Constants.YOUTUBE_API_SERVICE_NAME
        self.YOUTUBE_API_VERSION = Constants.YOUTUBE_API_VERSION
        self.youtube = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION, developerKey=self.DEVELOPER_KEY,
                             cache_discovery=False)

        self.max_results = 20

        self.mins_range = 4

    @staticmethod
    def get_duration_in_secs(d_raw):
        hours = 0
        mins = 0
        secs = 0
        d_raw = d_raw[d_raw.find('PT') + 2:]
        if 'H' in d_raw:
            hours = int(d_raw[:d_raw.find('H')])
            d_raw = d_raw[d_raw.find('H') + 1:]
        if 'M' in d_raw:
            mins = int(d_raw[:d_raw.find('M')])
            d_raw = d_raw[d_raw.find('M') + 1:]
        if 'S' in d_raw:
            secs = int(d_raw[:d_raw.find('S')])
        duration_secs = hours * 3600 + mins * 60 + secs
        return duration_secs

    def is_duration_correct(self, youtube_duration, spotify_duration):
        spotify_duration = spotify_duration/1000
        secs_range = self.mins_range * 60
        max_duration = spotify_duration + secs_range
        min_duration = spotify_duration - secs_range
        is_duration_correct = False
        if min_duration <= youtube_duration <= max_duration:
            is_duration_correct = True
        return is_duration_correct

    @staticmethod
    def filter_title(title):
        if '"' in title:
            title = title.split('"')[0]
        if ':' in title:
            title = title.split(':')[0]
        title = re.sub("[\(\[].*?[\)\]]", "", title)
        word_limit = 4
        if len(title.split(' ')) > word_limit:
            title = ' '.join(title.split(' ')[:word_limit])
        for item in SpotifyTitleIgnore.ignore:
            if item in title:
                title = title.replace(item, '')
        match = re.match(r'.*([1-3][0-9]{3})', title)
        if match is not None:
            title = title.replace(match.group(1), '')
        title = title.lstrip()
        title = title.rstrip()
        return title

    @staticmethod
    def is_video_correct(video_title):
        is_video_correct = True
        if 'tribute' in video_title.lower() or \
            'cover' in video_title.lower() or \
                'remix' in video_title.lower() or \
                'karaoke' in video_title.lower():
            is_video_correct = False
        return is_video_correct

    def get_youtube_video(self, title, artist, spotify_duration):
        yt_result = None

        artist = unidecode(artist.lower())
        title = unidecode(self.filter_title(title).lower())
        query = artist + ' - ' + title
        search_response = self.youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=self.max_results
        ).execute()

        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#video':
                if artist in unidecode(search_result['snippet']['title'].lower()) and \
                        title in unidecode(search_result['snippet']['title'].lower()):
                    yt_id = search_result['id']['videoId']
                    url = 'https://www.googleapis.com/youtube/v3/videos?id=' + yt_id + \
                          '&part=contentDetails&key=' + self.DEVELOPER_KEY
                    r = requests.get(url)
                    yt_duration = self.get_duration_in_secs(r.json()['items'][0]['contentDetails']['duration'])
                    if spotify_duration is not None:
                        if not self.is_duration_correct(yt_duration, spotify_duration):
                            continue
                    if not self.is_video_correct(search_result['snippet']['title']):
                        continue
                    yt_link = 'https://www.youtube.com/watch?v=' + yt_id
                    yt_embed = 'https://www.youtube.com/embed/' + yt_id
                    yt_result = {
                        'id': yt_id,
                        'link': yt_link,
                        'embed': yt_embed,
                    }
                    break

        return yt_result

    def add_youtube_links_to_playlist(self, playlist):
        for i, track in enumerate(playlist):
            artist = track['artists'][0]['name']
            title = track['name']
            duration_ms = track['duration_ms']
            yt_result = self.get_youtube_video(title, artist, duration_ms)
            if yt_result is not None:
                playlist[i]['youtube_url'] = yt_result['embed']
            else:
                playlist[i]['youtube_url'] = ''
        return playlist
