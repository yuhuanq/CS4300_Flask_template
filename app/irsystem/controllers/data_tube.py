#%%
import json
import numpy as np
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from spacy.pipeline import EntityRecognizer
import sys
import time




annotation = "This line includes an allusion to  Ralph Ellison\u2019s Invisible Man; the unnamed narrator is walking down the streets of New York City when he smells yams, triggering memories of his hometown in the South. The yam is used as a symbol of authenticity; the protagonist famously declares, \u201cI yam what I am.\u201d Here Kendrick is declaring his own authenticity, unlike the rappers he disses in the rest of the verse.\n\nYams are a key ingredient in African cuisine and have significance in some parts of Africa as a sign of social status. In his novel Things Fall Apart, Chinua Achebe begins by documenting how a man\u2019s worth in Igbo society was largely determined by his yearly yam yield. When Kendrick says he \u201cgot the yams,\u201d he means he has attained money, power and prestige.\n\nBig butts on healthy ladies and balloons filled with drugs (particularly heroin)  are also colloquially known as \u201cyams.\u201d"
#print(annotation)
#%%

nlp = spacy.load("en_core_web_lg")

# ner = nlp.create_pipe("ner")
# nlp.add_pipe(ner)
# entity = Entity(keywords_list=['books'])
# nlp.add_pipe(entity, last=True)



# merge_ents = nlp.create_pipe("merge_entities")
# nlp.add_pipe(merge_ents)

#%%
doc = nlp(annotation)
#%%

print([token.text for token in doc])

#%%
test = annotation
doc1 = nlp(test)
print([token for token in doc1])

for ent in doc1.ents:
    print(ent.text, ent.start_char, ent.end_char, ent.label_)



#%%


#%%
nlp = spacy.load("en_core_web_lg")
with open('songs.json') as song_json:
    songs = json.load(song_json)

#%%

#%%
annotation_ctr = 1
def annotation_tokenizer(text):
    doc = nlp(text)
    for ent in doc.ents:
        text = text + " {}".format(ent)
    tokenized_annotation = [token.lower_ for token in doc if not token.is_punct]
    #maybe make entities lowercase as well?
    ents = [ent.text for ent in doc.ents]
    tokenized_annotation = tokenized_annotation + ents
    print(annotation_ctr)
    annotation_ctr+=1
    return tokenized_annotation

#%%
print(annotation_tokenizer(annotation))
#%%
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
vectorizer = TfidfVectorizer(analyzer ='word', tokenizer=annotation_tokenizer)

#%%
print(len(annotations))
print(sys.getsizeof(annotations))
for a in annotations:
    print(a)
    
#%%
start = time.time()
tf_idf = vectorizer.fit_transform(annotations)
end = time.time()
print("Time was {}".format(end-start))

#%% do the pickling



#%%
def search(query, n_results):
    query_vector = vectorizer.transform([query])

    cosine_sim =  cosine_similarities = linear_kernel(query_vector, tf_idf).flatten()
    related_docs_indices = cosine_similarities.argsort()[-n_results:]

