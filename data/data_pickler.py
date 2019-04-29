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




nlp = spacy.load("en_core_web_lg")
with open('songs.json') as song_json:
    songs = json.load(song_json)


def annotation_tokenizer(text):
    doc = nlp(text)
    for ent in doc.ents:
        text = text + " {}".format(ent)
    tokenized_annotation = [token.lower_ for token in doc if not token.is_punct]
    #maybe make entities lowercase as well?
    ents = [ent.text for ent in doc.ents]
    tokenized_annotation = tokenized_annotation + ents
    return tokenized_annotation



#build dicts
doc_id_to_ref_id = {} #index of tf_idf to annotation_id

annotation_to_song = {} # annotation_id as key and song_id as value
song_to_name = {} #song_id to name of song
annotation_to_text = {} #annotation_id to annotation text
annotation_to_fragment = {} #annotation_id to lyric fragment


ctr = 0
annotations = []
for song_id,v in songs.items():
    for r in v['referents']:
        for a in r['annotations']:
            doc_id_to_ref_id[ctr] = r['id']
            annotation_to_song[r['id']] = song_id
            song_to_name[song_id] = v['full_title']
            annotation_to_text[a['id']] = r['lyric']
            ctr +=1
            annotations.append(a['annotation'])
  

#%%
#do sklearn stuff
#this is really slow because of the tokenizer
vectorizer = TfidfVectorizer(analyzer ='word', tokenizer=annotation_tokenizer)

start = time.time()
tf_idf = vectorizer.fit_transform(annotations)
end = time.time()
print("Time was {}".format(end-start))



#%%
#do pickling stuff
doc_id_pickle = open('doc_id_to_ref_id_p', 'wb')
annotation_to_song_pickle = open('annotation_to_song_p', 'wb')
song_to_name_pickle = open('song_to_name_p', 'wb')
annotation_to_text_pickle = open('annotation_to_text_p', 'wb')
annotation_to_fragment_pickle = open('annotation_to_fragment_p', 'wb')


pickle.dump(doc_id_to_ref_id, doc_id_pickle)
doc_id_pickle.close()

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


vectorizer_pickle = open('vectorizer_p', 'wb')

pickle.dump(vectorizer, vectorizer_pickle)
vectorizer_pickle.close()
