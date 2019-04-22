from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel #same as cosine similarity
from collections import Counter
from functools import reduce

project_name = "Song Finder"
net_id = "James Zhou: jlz44, Tristan Stone: tjs264, Dylan Hecht: dkh55, Yiwen Huang: yw385, Yuhuan Qiu: yq56"

#Global variables
annotation_to_song = {} # annotation_id as key and song_id as value
song_to_name = {} #song_id to name of song
annotation_to_text = {} #annotation_id to annotation text
annotation_to_fragment = {} #annotation_id to lyric fragment

with open('songs.json') as json_file:
    all_songs = json.load(json_file)

def create_dictionarys(json_file="songs.json", annotation_to_song={}, song_to_name={},
                       annotation_to_text={}, annotation_to_fragment={},
                      ):
    """
    Using songs.json as json_data
    Creates annotation dictionary: {annotation_id:[song_id,fragment/text,annotation_text]}
    """

    #load song json file
    with open(json_file) as song_json:
        songs = json.load(song_json)

        #iterate through all songs and input data accordingly
        for song_id in songs:
            song_data = songs[song_id]

            #process annotations
            for referent in song_data["referents"]:
                lyric_fragment = referent["lyric"]
                for annotation in referent["annotations"]:
                    annotation_id = annotation["id"]
                    annotation_text = annotation["annotation"]

                    annotation_votes = annotation["votes_total"] # here is where we would record vote numbers

                    if annotation_votes >= 1:
                        if annotation_id not in annotation_to_song:
                            annotation_to_song[annotation_id] = song_id

                        if annotation_id not in annotation_to_text:
                            annotation_to_text[annotation_id] = annotation_text

                        if annotation_id not in annotation_to_fragment:
                            annotation_to_fragment[annotation_id] = lyric_fragment

    return (annotation_to_song,song_to_name,annotation_to_text,annotation_to_fragment)

annotation_to_song,song_to_name,annotation_to_text,annotation_to_fragment = create_dictionarys()
vectorizer = TfidfVectorizer(stop_words = "english",
                           max_df = 0.8,
                          norm = 'l2')
tf_idf = vectorizer.fit_transform(list(annotation_to_text.values()))
index_to_annotation = {i:v for i, v in enumerate(vectorizer.get_feature_names())}
index_to_id = {i:v for i, v in enumerate(list(annotation_to_text.keys()))}


def find_most_similar(query,n_results):
    """
    finds n most similar annotations to query
    """
    #Define used global variables
    global vectorizer, tf_idf, annotation_to_text, annotation_to_song, annotation_to_fragment,song_to_name

    #vectorize query
    query_vector = vectorizer.transform([query])

    #find cosine similarities and the indices of related docs
    cosine_similarities = linear_kernel(query_vector, tf_idf).flatten()
    related_docs_indices = cosine_similarities.argsort()[-n_results:]


    #find highest similarity scores
    sim_scores = cosine_similarities[related_docs_indices]

    #find ids of most similar annotations
    annotation_ids = [index_to_id[index] for index in related_docs_indices] #can later be used to find lyric fragment maybe

    # group them by songs
    song_id_to_annotations = {}
    max_sim_sum = 0
    max_song_page_views = 0
    for annotation_id, sim_score in zip(annotation_ids, sim_scores):
        if sim_score == 0:
            continue
        song_id = annotation_to_song[annotation_id]
        if song_id not in song_id_to_annotations:
            song_id_to_annotations[song_id] = []
        song_id_to_annotations[song_id].append((annotation_id, sim_score))
        song_id_to_annotations[song_id].sort(key=lambda x: x[1], reverse=True)
        max_sim_sum = max(
            max_sim_sum,
            reduce(
                lambda acc, x: acc + x[1],
                song_id_to_annotations[song_id],
                0,
            )
        )
        max_song_page_views = max(max_song_page_views,
                                  all_songs[song_id]['page_views'])

    print("max_song_page_views", max_song_page_views)
    print("max_sim_sum", max_sim_sum)

    result = []
    for song_id in song_id_to_annotations:
        song = {}
        song['id'] = song_id
        song["song"] = all_songs[song_id]["title"]
        song["artist"] = all_songs[song_id]["artists_names"]
        song["image"] = all_songs[song_id]["header_image_url"]
        if not all_songs[song_id]["album"] == None:
            song["album"] = all_songs[song_id]["album"]["full_title"]
        else:
            song["album"] = "No album found"
        song['release_date'] = all_songs[song_id]['release_date']


        song["annotations"] = [
            {'text':annotation_to_text[aid],
             'similarity': score,
             'lyric': annotation_to_fragment[aid]
            }
            for aid, score in song_id_to_annotations[song_id]
        ]

        # TODO take into page_views (need to normalize though before weighting)
        song['page_views'] = max(all_songs[song_id]['page_views'], 0)

        # score calculation
        similarity_sum_normalized = reduce(
            lambda acc, x: acc + x[1],
            song_id_to_annotations[song_id],
            0,
        )/max_sim_sum
        page_views_normalized = song['page_views'] / max_song_page_views

        song['score'] = .8 * similarity_sum_normalized + .2 * page_views_normalized

        result.append(song)

    result.sort(key = lambda x : x['score'], reverse = True)
    return result

@irsystem.route('/', methods=['GET'])
def search():
  query = request.args.get('search')
  if not query:
    data = None
    output_message = ''
  else:
    output_message = "Your search: " + query
    data = find_most_similar(query, 50)
  return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)



