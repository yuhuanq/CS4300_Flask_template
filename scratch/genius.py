#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 yqiu <yqiu@f24-suntzu>
#
# Distributed under terms of the MIT license.

"""
fetch song metadata by artist i.e. 21 savage
"""

import requests
import json


BASE_URL = "https://api.genius.com"
CLIENT_ACCESS_TOKEN = "bnT0xmyBXNVQSplx3fAwLtKiCPLQFmyctUIiL1BxKEWIkDvI0583WkiBxQbwRtpI"
ARTIST_NAME = "21 Savage"

# send request and get response in json format.
def _get(path, params=None, headers=None):
    requrl = '/'.join([BASE_URL, path])
    token = "Bearer {}".format(CLIENT_ACCESS_TOKEN)
    if headers:
        headers['Authorization'] = token
    else:
        headers = {"Authorization":token}
    response = requests.get(url=requrl, params=params, headers=headers)
    response.raise_for_status()
    return response.json()

def get_artist_songs(artist_id):
    # paging; default 20 items returned per page
    current_page = 1
    next_page = True
    songs = []
    while next_page:
        path = "artists/{}/songs/".format(artist_id)
        params = {'page': current_page}
        data = _get(path=path, params=params)

        page_songs = data['response']['songs']

        if page_songs:
            songs += page_songs
            current_page += 1
        else:
            next_page = False
    # song ids, excluding songs where [artist_id] is not primary
    songs = [song['id'] for song in songs if song['primary_artist']['id'] ==
             artist_id]
    return songs


def get_song_information(song_ids):
    song_list = {}
    for i, song_id in enumerate(song_ids):
        print('id:' + str(song_id) + ' start. ->')

        path = 'songs/{}'.format(song_id)
        data = _get(path=path)['response']['song']
        song_list.update({
        i: {
            "title": data["title"],
            "album": data["album"]["name"] if data["album"] else "<single>",
            "release_date": data["release_date"] if data["release_date"] else "unidentified",
            "featured_artists":
                [feat["name"] if data["featured_artists"] else "" for feat in data["featured_artists"]],
            "producer_artists":
                [feat["name"] if data["producer_artists"] else "" for feat in data["producer_artists"]],
            "writer_artists":
                [feat["name"] if data["writer_artists"] else "" for feat in data["writer_artists"]],
            "genius_track_id": song_id,
            "genius_album_id": data["album"]["id"] if data["album"] else "none"}
        })
        print("-> id:" + str(song_id) + " is finished. \n")
    return song_list

print("searching " + ARTIST_NAME + "'s artist id.")



artist_id = None
search_resp = _get('search', {'q': ARTIST_NAME})
for hit in search_resp['response']['hits']:
   if hit["result"]["primary_artist"]["name"] == ARTIST_NAME:
       artist_id = hit["result"]["primary_artist"]["id"]
       break

if not artist_id:
    print("failed to search for artist id. terminating...")
    exit(1)

print("getting song ids.")
song_ids = get_artist_songs(artist_id)

print(song_ids)
print('got song ids')
print('getting meta data of each song')

songs_lst = get_song_information(song_ids)

print("finished; dumping to json")

with open('./' + ARTIST_NAME + '_songs.json', 'w') as fo:
    fo.write(json.dumps(songs_lst))

print('done')

