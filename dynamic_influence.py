import numpy as np
import os
import re
import pandas as pd

influencer_data = pd.read_csv('./data/influencer_data.csv')
influence_data = pd.read_csv('./data/influence_data.csv')
artist_data = pd.read_csv('./data/artist_data.csv')

influencer_id = influence_data['influencer_id'].unique()
follower_id = influence_data['follower_id'].unique()

id = follower_id
for x in influencer_id:
    if x not in id:
        id = np.append(id, x)
id_list = list(id)

influencer_id_list = []
follower_id_list = []
influencer_name_list = []
follower_name_list = []
action = []
for i in range(len(influencer_id)):
    followers_id = influence_data[influence_data['influencer_id'] == influencer_id[i]]['follower_id'].unique()
    for id_f in followers_id:
        influencer_id_list.append(influencer_id[i])
        follower_id_list.append(id_f)
        influencer_name = artist_data[artist_data['id'] == influencer_id[i]]['name'].values[0]
        follower_name = artist_data[artist_data['id'] == id_f]['name'].values[0]
        influencer_name_list.append(influencer_name)
        follower_name_list.append(follower_name)
        action.append(1)

df_action = pd.DataFrame({'influencer_id': influencer_id_list, 'influencer_name': influencer_name_list,
                          'follower_id': follower_id_list, 'follower_name': follower_name_list,
                          'action': action})

dynamic_influence = []
for i in range(len(df_action)):
    id_i = df_action.iloc[i, 0]
    id_f = df_action.iloc[i, 2]
    static_influence = influencer_data[influencer_data['influencer_id'] == id_i]['static_influence'].values[0]
    year_i = influencer_data[influencer_data['influencer_id'] == id_i]['year'].values[0]
    year_f = influence_data[influence_data['follower_id'] == id_f]['follower_active_start'].values[0]
    if year_f < year_i:
        year_f = year_i

    influence_num = len(influence_data[influence_data['follower_id'] == id_f])

    dy_influence = static_influence / (np.log(influence_num + 1) + np.log(1 + (year_f-year_i)/10))
    dynamic_influence.append(dy_influence)

df_action['dynamic_influence'] = dynamic_influence
df_action.sort_values("dynamic_influence", inplace=True, ascending=False)

df_action.to_csv('./data/dynamic_influence.csv', encoding='utf-8', index=False)

