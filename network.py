import numpy as np
import os
import re
import pandas as pd

dynamic_influence = pd.read_csv('./data/dynamic_influence.csv')
artist_data = pd.read_csv('./data/artist_data.csv')
influencer_data = pd.read_csv('./data/influencer_data.csv')
'''
top = 500
top_dynamic_influence = dynamic_influence.iloc[:top, ]

influencer_id = top_dynamic_influence['influencer_id'].unique()
influencer_name = top_dynamic_influence['influencer_name'].unique()
follower_id = top_dynamic_influence['follower_id'].unique()
follower_name = top_dynamic_influence['follower_name'].unique()


id_list = influencer_id
for x in follower_id:
    if x not in id_list:
        id_list = np.append(id_list, x)

name_list = []
genre_list = []
for id in id_list:
    temp_df = artist_data[artist_data['id'] == id]
    name_list.append(temp_df['name'].values[0])
    genre_list.append(temp_df['genre'].values[0])

entity = pd.DataFrame({'id': name_list, 'label': genre_list})
entity.to_csv('./data/entity.csv', encoding='utf-8', index=False)

Source = []
Target = []
Type = []
Weight = []
for i in range(len(top_dynamic_influence)):
    Source.append(top_dynamic_influence.iloc[i, 1])
    Target.append(top_dynamic_influence.iloc[i, 3])
    Type.append('Directed')
    Weight.append(top_dynamic_influence.iloc[i, 5])

relationship = pd.DataFrame({'Source': Source, 'Target': Target, 'Type': Type, 'Weight': Weight})
relationship.to_csv('./data/relationship.csv', encoding='utf-8', index=False)
'''

id_list = influencer_data.iloc[:100, ]['influencer_id'].values

Source = []
Target = []
Type = []
Weight = []
for i in range(len(id_list)):
    for j in range(len(id_list)):
        if i != j:
            temp_f = dynamic_influence[dynamic_influence['influencer_id'] == id_list[i]]
            if id_list[j] in temp_f['follower_id'].values:
                Source.append(temp_f[temp_f['follower_id'] == id_list[j]]['influencer_name'].values[0])
                Target.append(temp_f[temp_f['follower_id'] == id_list[j]]['follower_name'].values[0])
                Type.append('Directed')
                Weight.append(temp_f[temp_f['follower_id'] == id_list[j]]['dynamic_influence'].values[0])

relationship = pd.DataFrame({'Source': Source, 'Target': Target, 'Type': Type, 'Weight': Weight})
relationship.to_csv('./data/relationship.csv', encoding='utf-8', index=False)

name_list = list(set(Source)|set(Target))

entity = pd.DataFrame({'id': name_list, 'label': name_list})
entity.to_csv('./data/entity.csv', encoding='utf-8', index=False)


