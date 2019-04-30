#%%
import json
import numpy as np
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from spacy.pipeline import EntityRecognizer
import sys
import time
import pickle
import dill




nlp = spacy.load("en_core_web_lg")
def annotation_tokenizer(text):
    doc = nlp(text)
    for ent in doc.ents:
        text = text + " {}".format(ent)
    # tokenized_annotation = [token.lower_ for token in doc if not token.is_punct]
    tokenized_annotation = []
    for token in doc:
        if not token.is_punct and not token.is_stop:
            tokenized_annotation.append(token.lower_)
    #maybe make entities lowercase as well?
    ents = [ent.text for ent in doc.ents]
    tokenized_annotation = tokenized_annotation + ents
    return tokenized_annotation

def do_pickle():
    print("oh no")
    # with open('songs.json') as song_json:
    #     songs = json.load(song_json)

    dill.dump(annotation_tokenizer, open('annotation_tokenizer.dill', 'wb'))

    #build dicts
    # doc_id_to_ref_id = {} #index of tf_idf to annotation_id

    annotation_to_song = {} # annotation_id as key and song_id as value
    song_to_name = {} #song_id to name of song
    annotation_to_text = {} #annotation_id to annotation text
    annotation_to_fragment = {} #annotation_id to lyric fragment


    # ctr = 0
    # annotations = []
    # for song_id,v in songs.items():
    #     for r in v['referents']:
    #         for a in r['annotations']:
    #             doc_id_to_ref_id[ctr] = r['id']
    #             annotation_to_song[r['id']] = song_id
    #             song_to_name[song_id] = v['full_title']
    #             annotation_to_text[a['id']] = a['annotation']
    #             ctr +=1
    #             annotations.append(a['annotation'])
    



    #load song json file
    new_songs = {}
    with open('songs.json') as song_json: 
        songs = json.load(song_json)
    print(len(songs))
    
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

                if annotation_votes >= 15:
                    
                    if song_id not in new_songs:
                        new_songs[song_id] = song_data
                    
                    if song_id not in song_to_name:
                        song_to_name[song_id] = song_data["full_title"]
                        
                    if annotation_id not in annotation_to_song:
                        annotation_to_song[annotation_id] = song_id

                    if annotation_id not in annotation_to_text:
                        annotation_to_text[annotation_id] = annotation_text

                    if annotation_id not in annotation_to_fragment:
                        annotation_to_fragment[annotation_id] = lyric_fragment
                
    print("Processed {} annotations".format(len(annotation_to_text)))





    #%%
    #do sklearn stuff
    #this is really slow because of the tokenizer
    vectorizer = TfidfVectorizer(analyzer ='word', tokenizer=annotation_tokenizer)

    annotations = list(annotation_to_text.values())

    start = time.time()
    tf_idf = vectorizer.fit_transform(annotations)
    end = time.time()
    print("Time was {}".format(end-start))


    index_to_annotation = {i:v for i, v in enumerate(vectorizer.get_feature_names())}
    index_to_id = {i:v for i, v in enumerate(list(annotation_to_text.keys()))}

    pickle.dump(index_to_annotation, open('index_to_annotation.pickle', 'wb'))
    pickle.dump(index_to_id, open('index_to_id.pickle', 'wb'))

    pickle.dump(vectorizer.vocabulary_, open('vocabulary.pickle', 'wb'))
    pickle.dump(vectorizer.idf_, open('idf_.pickle', 'wb'))

    #%%
    #do pickling stuff
    #doc_id_pickle = open('doc_id_to_ref_id_p', 'wb')
    annotation_to_song_pickle = open('annotation_to_song_p', 'wb')
    song_to_name_pickle = open('song_to_name_p', 'wb')
    annotation_to_text_pickle = open('annotation_to_text_p', 'wb')
    annotation_to_fragment_pickle = open('annotation_to_fragment_p', 'wb')


    # pickle.dump(doc_id_to_ref_id, doc_id_pickle)
    # doc_id_pickle.close()

    pickle.dump(annotation_to_song, annotation_to_song_pickle)
    annotation_to_song_pickle.close()

    pickle.dump(song_to_name, song_to_name_pickle)
    song_to_name_pickle.close()

    pickle.dump(annotation_to_text, annotation_to_text_pickle)
    annotation_to_text_pickle.close()

    pickle.dump(annotation_to_fragment, annotation_to_fragment_pickle)
    annotation_to_fragment_pickle.close()


    tf_idf_pickle = open('tf_idf_p', 'wb')

    pickle.dump(tf_idf, tf_idf_pickle)
    tf_idf_pickle.close()


    vectorizer_pickle = open('vectorizer_p.dill', 'wb')

    dill.dump(vectorizer, vectorizer_pickle)
    vectorizer_pickle.close()

do_pickle()