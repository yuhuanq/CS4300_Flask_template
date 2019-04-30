#%%
import pickle 


entity_to_annotation_id = pickle.load(open("data/entity_to_annotation.pickle", 'rb'))


#%%

search = 'invisible'


if search in entity_to_annotation_id:
    print(search + ' is an enity')
else:
    print('no')

#%%
