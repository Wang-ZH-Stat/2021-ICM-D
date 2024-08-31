import numpy as np
import os
import re
import pandas as pd
from sklearn.preprocessing import StandardScaler

influence_data = pd.read_csv('./data/influence_data.csv')
data_by_artist = pd.read_csv('./data/data_by_artist.csv')
artist_data = pd.read_csv('./data/artist_data.csv')

def get_diff(name, genre):
    influencer_feature = data_by_artist[data_by_artist['artist_name'] == name]
    influencer_id = influencer_feature['artist_id'].values[0]

    id_list = artist_data[artist_data['genre'] == genre]['id'].values
    genre_data = data_by_artist[data_by_artist['artist_id'].isin(id_list)]

    id_list = genre_data['artist_id'].values

    temp_df = influence_data[influence_data['influencer_name'] == name]
    if genre == 'R&B':
        followers_id = temp_df[temp_df['follower_main_genre'] == 'R&B;']['follower_id'].values
    else:
        followers_id = temp_df[temp_df['follower_main_genre'] == genre]['follower_id'].values

    for i in range(len(followers_id)):
        if followers_id[i] not in id_list:
            followers_id = np.delete(followers_id, i)
            break

    nonfollowers_id = []
    for id in id_list:
        if id not in followers_id:
            if id != influencer_id:
                nonfollowers_id.append(id)
    nonfollowers_id = np.array(nonfollowers_id)

    feature_list = ['danceability', 'energy', 'valence', 'tempo', 'loudness',
                                'key', 'acousticness', 'instrumentalness', 'liveness', 'speechiness']

    genre_data = genre_data[['artist_name', 'artist_id', 'danceability', 'energy', 'valence', 'tempo', 'loudness',
                                'key', 'acousticness', 'instrumentalness', 'liveness', 'speechiness']]

    genre_feature = genre_data[feature_list]

    sc = StandardScaler()
    genre_feature_sc = pd.DataFrame(data=sc.fit_transform(genre_feature), columns=feature_list)

    genre_data_sc = genre_data.copy()

    for feature in feature_list:
        genre_data_sc[feature] = genre_feature_sc[feature].values

    index = genre_data_sc[genre_data_sc['artist_id'] == influencer_id].index.tolist()[0]
    influencer_feature = genre_data_sc[genre_data_sc['artist_id'] == influencer_id]

    temp_df_sc = genre_data_sc[feature_list]

    diff_df = temp_df_sc - temp_df_sc.loc[index]

    diff_df = diff_df.abs()

    diff_genre_data_sc = genre_data_sc.copy()
    for feature in feature_list:
        diff_genre_data_sc[feature] = diff_df[feature].values

    dis = []
    for i in range(len(diff_genre_data_sc)):
        temp_fea = np.array(diff_genre_data_sc.iloc[i, ].tolist()[2:])
        temp_dis = np.sqrt(np.sum(temp_fea**2))
        dis.append(temp_dis)

    diff_genre_data_sc['distance'] = dis

    diff_genre_data_sc = diff_genre_data_sc[diff_genre_data_sc['distance'] > 0.001]

    action = []
    for i in range(len(diff_genre_data_sc)):
        id = diff_genre_data_sc.iloc[i, 1]
        if id in followers_id:
            action.append(1)
        else:
            action.append(0)

    diff_genre_data_sc['action'] = action

    diff_genre_data_sc.to_csv('./data/diff/diff_' + name + '.csv', encoding='utf-8', index=False)

get_diff('The Beatles', 'Pop/Rock')

get_diff('Marvin Gaye', 'R&B')

get_diff('Johnny Cash', 'Country')

get_diff('Kraftwerk', 'Electronic')

get_diff('Miles Davis', 'Jazz')
