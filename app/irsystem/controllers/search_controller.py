from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from datetime import datetime
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel #same as cosine similarity
from collections import Counter
from functools import reduce
import pickle
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')


project_name = "Song Finder"
net_id = "James Zhou: jlz44, Tristan Stone: tjs264, Dylan Hecht: dkh55, Yiwen Huang: yw385, Yuhuan Qiu: yq56"

#Global variables
annotation_to_song = {} # annotation_id as key and song_id as value
song_to_name = {} #song_id to name of song
annotation_to_text = {} #annotation_id to annotation text
annotation_to_fragment = {} #annotation_id to lyric fragment

with open('songs.json') as json_file:
    all_songs = json.load(json_file)
annotation_to_song = pickle.load( open( "annotation_to_song.p", "rb" ) )
song_to_name = pickle.load( open( "song_to_name.p", "rb" ) )
annotation_to_text = pickle.load( open( "annotation_to_text.p", "rb" ) )
annotation_to_fragment = pickle.load( open( "annotation_to_fragment.p", "rb" ) )


vectorizer = TfidfVectorizer(stop_words = "english",
                           max_df = 0.8,
                          norm = 'l2')
tf_idf = vectorizer.fit_transform(list(annotation_to_text.values()))
index_to_annotation = {i:v for i, v in enumerate(vectorizer.get_feature_names())}
index_to_id = {i:v for i, v in enumerate(list(annotation_to_text.keys()))}


def should_filter(start, end, artist, song_id):
    if artist and artist != "All":
        if not all_songs[song_id]["artists_names"] == artist:
            return True

    if start:
        start = datetime.strptime(start,"%Y-%m-%d")
    if end:
        end = datetime.strptime(end,"%Y-%m-%d")

    release_date_str = all_songs[song_id]["release_date"]

    if release_date_str:
        release_date = datetime.strptime(release_date_str,"%Y-%m-%d")

        #invalidate songs outside of date range
        if (start and release_date<start) or (end and release_date>end):
            return True
    else:
        return True

    return False

def find_most_similar(query,n_results, start = None, end = None, artist = None, relevance_feedback=True):
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

    if relevance_feedback:
        #psueodo-rel feedback take top 4 centroid
        top4_doc_ids = related_docs_indices[:4]
        for doc_id in top4_doc_ids:
            query_vector += tf_idf[doc_id] / len(top4_doc_ids)
        # do search again with transformed query
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
        song_id = annotation_to_song[annotation_id]
        if sim_score < 0.1 or should_filter(start, end, artist, song_id):
            continue
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

        song['score'] = round(.8 * similarity_sum_normalized + .2 * page_views_normalized, 2)

        result.append(song)

    result.sort(key = lambda x : x['score'], reverse = True)
    return result

def str2bool(v):
  if not v:
    return False
  return v.lower() in ("yes", "true", "t", "1")

@irsystem.route('/', methods=['GET'])
def search():
  query = request.args.get('search')
  start_year = request.args.get('date-start')
  end_year = request.args.get('date-end')
  relevance_feedback = str2bool(request.args.get('relevance_feedback'))
  artist = request.args.get('artist')
  artist_saved =  request.args.get('artist_saved')
  if not artist and artist_saved:
    artist = artist_saved
    print(artist)


  start = 1985
  end = 2019

  if not start_year:
    start_year = 1985
  if not end_year:
    end_year = 2019

  if not query:
    data = None
    output_message = ''
    query = ""
  else:
    output_message = "Your search: " + query

    if start_year:
      start = "{}-01-01".format(start_year)

    if end_year:
      end = "{}-12-31".format(end_year)

    print(start)
    print(end)
    data = find_most_similar(query, 50, start, end, artist, relevance_feedback)


  stops =  set(stopwords.words('english'))
  query_words = [query]
  if query:
    for word in query.split():
      if not word in stops:
          query_words.append(word)

  artist_full = artist
  if not artist:
    artist = "All"
  else:
    artist = artist.split()[0]

  return render_template('search.html', name=project_name, netid=net_id,
    output_message=output_message, data=data, query=query_words,
    date_start = start_year, date_end = end_year, artist = artist, artist_full = artist_full)



