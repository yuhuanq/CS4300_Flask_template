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
ARTIST_NAMES = ["Kendrick Lamar"]

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
    song_dict = {}
    for i, song_id in enumerate(song_ids):
        print('id:' + str(song_id) + ' start. ->')

        path = 'songs/{}?text_format=plain'.format(song_id)
        data = _get(path=path)['response']['song']

        song_id = data["id"]
        referents = get_referents(song_id)
        print(song_id)

        pageviews = 0
        if "pageviews" in data["stats"]:
            pageviews =  data["stats"]["pageviews"]
        else:
            pageviews = -1
        song = {
                 "accepted_annotations" : data["stats"]["accepted_annotations"],
                 "full_title" : data["full_title"],
                 "title" : data["title"],
                 "description" : data["description"]["plain"],
                 "header_image_url" : data["header_image_url"],
                 "song_art_image_url" : data["song_art_image_url"],
                 "pyongs_count" : data["pyongs_count"],
                 "release_date" : data["release_date"],
                 "hot" : data["stats"]["hot"],
                 "page_views" : pageviews,
                 "artists_names" : data["primary_artist"]["name"],
                 "album" : data["album"],
                 "producer_artists" : data["producer_artists"],
                 "writer_artists" : data["writer_artists"],
                 "referents" : referents
                 }


        song_dict[song_id] = song
        print("-> id:" + str(song_id) + " is finished. \n")
    return song_dict

def get_referents(song_id):
    print('id:' + str(song_id) + ' start referents. ->')

    path = 'referents?song_id={}&text_format=plain&per_page=50'.format(song_id)
    data = _get(path=path)['response']['referents']

    referent_list = []

    for i, referent in enumerate(data):
        referent_list.append(
        {
            "lyric": referent["fragment"],
            "url": referent["url"],
            "id": referent["id"],
            "annotations": [
                {
                    "verified": annotation['verified'],
                    "votes_total": annotation['votes_total'],
                    "annotation": annotation['body']['plain'],
                    "id": annotation['id']
                } for annotation in referent['annotations']
            ]
        }

        )

    print("-> id:" + str(song_id) + " referents is finished. \n")

    return referent_list

def get_referents_list(song_ids):
    referents_list = []
    for song_id in song_ids:
        referents_list.append(
            {
            "song_id": song_id,
            "referents": get_referents(song_id)
            }
        )

    return referents_list


def get_song_list(artist_list):
    artist_id = None
    song_ids = []

    for artist_name in ARTIST_NAMES:
        print("getting song ids for artist {}".format(artist_name))
        search_resp = _get('search', {'q': artist_name})
        for hit in search_resp['response']['hits']:
           if hit["result"]["primary_artist"]["name"] == artist_name:
               artist_id = hit["result"]["primary_artist"]["id"]
               break

        if not artist_id:
            print("failed to search for artist id")
            continue

        song_ids_artist = get_artist_songs(artist_id)

        song_ids.extend(song_ids_artist)

    return song_ids

song_ids = get_song_list(ARTIST_NAMES)

print(song_ids)
print('got song ids')
print('getting meta data of each song')

songs_lst = get_song_information(song_ids)
#referents_list = get_referents_list(song_ids)

print("finished; dumping to json")

with open('./songs.json', 'w') as fo:
    fo.write(json.dumps(songs_lst))

# with open('./referents.json', 'w') as fo:
#     fo.write(json.dumps(referents_list))
# print('done')

