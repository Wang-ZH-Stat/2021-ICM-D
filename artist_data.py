import numpy as np
import os
import re
import pandas as pd

influence_data = pd.read_csv('./data/influence_data.csv')

influence_data['influencer_id'].value_counts()  # 3774
influence_data['follower_id'].value_counts()  # 5046

influencer_id = influence_data['influencer_id'].unique()
influencer_name = influence_data['influencer_name'].unique()
follower_id = influence_data['follower_id'].unique()
follower_name = influence_data['follower_name'].unique()

# 找出相同元素
def extra_same_elem(list1, list2):
    set1 = set(list1)
    set2 = set(list2)
    iset = set1.intersection(set2)
    return np.array(list(iset))

repeat_name = extra_same_elem(influencer_name, follower_name)  # 3219
repeat_id = extra_same_elem(influencer_id, follower_id)  # 3217

'''
influence_data[influence_data['influencer_name'] == repeat_name[25]]['influencer_id']
influence_data[influence_data['follower_name'] == repeat_name[25]]['follower_id']
'''

id = follower_id
for x in influencer_id:
    if x not in repeat_id:
        id = np.append(id, x)

len(id)  # 5603

id = list(id)

name = []
year = []
genre = []
for ID in id:
    if ID in influencer_id:
        name.append(influence_data[influence_data['influencer_id'] == ID]['influencer_name'].unique()[0])
        year.append(influence_data[influence_data['influencer_id'] == ID]['influencer_active_start'].unique()[0])

        genre_temp = influence_data[influence_data['influencer_id'] == ID]['influencer_main_genre'].unique()[0]
        genre_temp = genre_temp.replace(";", "")
        genre.append(genre_temp)

    else:
        name.append(influence_data[influence_data['follower_id'] == ID]['follower_name'].unique()[0])
        year.append(influence_data[influence_data['follower_id'] == ID]['follower_active_start'].unique()[0])

        genre_temp = influence_data[influence_data['follower_id'] == ID]['follower_main_genre'].unique()[0]
        genre_temp = genre_temp.replace(";", "")
        genre.append(genre_temp)

data_by_artist = pd.read_csv('./data/data_by_artist.csv')
artist_id = data_by_artist['artist_id'].unique()

for ID in artist_id:
    if ID not in id:
        id.append(ID)
        name.append(data_by_artist[data_by_artist['artist_id'] == ID]['artist_name'].unique()[0])
        year.append(None)
        genre.append(None)

artist_data = {'id': id, 'name': name, 'year': year, 'genre': genre}
artist_data = pd.DataFrame(artist_data)
artist_data.sort_values("year", inplace=True)

artist_data.to_csv('./data/artist_data.csv', encoding='utf-8', index=False)

