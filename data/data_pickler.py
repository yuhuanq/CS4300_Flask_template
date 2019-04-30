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
from itertools import chain, combinations





nlp = spacy.load("en_core_web_lg")
def annotation_tokenizer(text):
    doc = nlp(text)
    # for ent in doc.ents:
    #     text = text + " {}".format(ent)
    # tokenized_annotation = [token.lower_ for token in doc if not token.is_punct]
    tokenized_annotation = []
    for token in doc:
        if not token.is_punct and not token.is_stop:
            tokenized_annotation.append(token.lower_)
    #maybe make entities lowercase as well?
    ents = [ent.text.lower() for ent in doc.ents]
    tokenized_annotation = tokenized_annotation + ents
    return tokenized_annotation, ents

# def tokenized_annotations(annotations):
#     accum = []#list of lists
#     for annotation in annotations:
#         tokenized_annotation, ents = annotation_tokenizer(annotation)
#         accum.append(tokenized_annotation)
#     return accum

def get_ents_and_tokenize(annotation_to_text):
    entity_to_annotation_id = {} #entity as key, annotation_id value
    accum = []
    for an_id, annotation in annotation_to_text.items():
        tokenized_annotation, ents = annotation_tokenizer(annotation)
        accum.append(tokenized_annotation)
        if len(ents) > 0:
            for entity in ents:
                # print(entity)
                if entity not in entity_to_annotation_id:
                    entity_to_annotation_id[entity] = [an_id]
                else:
                    entity_to_annotation_id[entity].append(an_id)
    return (accum, entity_to_annotation_id)

def nothing(text):
    return text

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
    start = time.time()
    vectorizer = TfidfVectorizer(tokenizer=nothing, preprocessor=nothing,)

    # annotations = tokenized_annotations(list(annotation_to_text.values()))
    annotations, entity_to_annotation_id = get_ents_and_tokenize(annotation_to_text)

    if 'kanye' in entity_to_annotation_id:
        print("yesssssssssssssssssssssssssssss")
    else:
        print("fuckkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")

    
    tf_idf = vectorizer.fit_transform(annotations)
    end = time.time()
    print("Time was {}".format(end-start))

    pickle.dump(entity_to_annotation_id, open("entity_to_annotation.pickle", 'wb'))

    # for k,v in entity_to_annotation_id.items():
    #     print(k, v)
    #     break

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


# nlp = spacy.load("en_core_web_sm")
# def query_tokenizer(text):
#     doc = nlp(text)
#     for ent in doc.ents:
#         text = text + " {}".format(ent)
#     tokenized_annotation = [token.lower_ for token in doc if not token.is_punct]
#     #maybe make entities lowercase as well?
#     ents = [ent.text for ent in doc.ents]
#     for ent in ents:
#         print("this is an entity!: {}".format(ent))
#     tokenized_annotation = tokenized_annotation + ents
#     # print(type(tokenized_annotation))
#     # print(tokenized_annotation)
#     # for thing in tokenized_annotation:
#     #     print(thing)
#     # print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
#     return tokenized_annotation

# def powerset(iterable):
#     "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
#     s = list(iterable)
#     return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

# def boolean_search(query):
#     tokens = query_tokenizer(query)
#     power_set = powerset(tokens)
#     for thing in power_set:
#         print(thing)
#         print(len(thing))
#         accum = ""
#         for t in thing:
#             print(t)
#             accum = accum + ' ' + t
#             print(accum)

# boolean_search('invisible man')
#%%
