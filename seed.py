import numpy as np
import os
import re
import pandas as pd

influencer_data = pd.read_csv('./data/influencer_data.csv')
dynamic_influence = pd.read_csv('./data/dynamic_influence.csv')
influence_data = pd.read_csv('./data/influence_data.csv')
followers_id = list(influence_data['follower_id'].unique())
influencers_id = list(influence_data['influencer_id'].unique())

top = 200
top_influencers_id = list(dynamic_influence.sort_values("dynamic_influence", inplace=False, ascending=False)\
                              ['influencer_id'].unique()[:top])


def get_total_influence(dynamic_influence, influences_id_list, follower_id):
    influencers_data = dynamic_influence[dynamic_influence['follower_id'] == follower_id]
    total_influence = 0
    for i in range(len(influencers_data)):
        if influencers_data.iloc[i, 0] in influences_id_list:
            total_influence += influencers_data.iloc[i, 5]

    return total_influence

def difference(list1, list2):
    if len(list2) == 0:
        return list1
    else:
        list3 = []
        for x in list1:
            if x not in list2:
                list3.append(x)

        return list3

def get_influence_spread(influences_id_list, id_i):
    sigma_S = 0
    diff_S = difference(followers_id, influences_id_list)
    for id in diff_S:
        action_num = len(dynamic_influence[dynamic_influence['follower_id'] == id])
        sigma_S += get_total_influence(dynamic_influence, influences_id_list, id) / action_num

    sigma_S_x = 0
    influences_id_list.append(id_i)
    diff_S_x = difference(followers_id, influences_id_list)
    for id in diff_S_x:
        action_num = len(dynamic_influence[dynamic_influence['follower_id'] == id])
        sigma_S_x += get_total_influence(dynamic_influence, influences_id_list, id) / action_num

    influence_spread = sigma_S_x - sigma_S

    return influence_spread

k = 50
S = []
temp_influencers_id = top_influencers_id
for i in range(k):
    print(i)

    Q = []
    for j in range(len(temp_influencers_id)):
        id = temp_influencers_id[j]
        temp_data = dynamic_influence[dynamic_influence['influencer_id'] == id]

        width = influencer_data[influencer_data['influencer_id'] == id]['width'].values[0]

        influence_spread = 0
        for p in range(len(temp_data)):
            if temp_data.iloc[p, 2] not in S:
                influence_spread += temp_data.iloc[p, 5] * width

        Q.append(influence_spread)

    idx = Q.index(max(Q))
    S.append(temp_influencers_id[idx])
    temp_influencers_id.pop(idx)

seed_data = influencer_data[influencer_data['influencer_id'] == S[0]]
for seed_id in S[1:len(S)]:
    temp_df = influencer_data[influencer_data['influencer_id'] == seed_id]
    seed_data = seed_data.append(temp_df)

seed_data['genre'].value_counts()

seed_data.to_csv('./data/seed_data.csv', encoding='utf-8', index=False)

