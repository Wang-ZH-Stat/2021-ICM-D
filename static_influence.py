import numpy as np
import os
import re
import pandas as pd
import scipy.stats
from collections import Counter

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
id_list = follower_id
for x in influencer_id:
    if x not in repeat_id:
        id = np.append(id_list, x)

len(id_list)  # 5603
id_list = list(id_list)

def truncation(x, a, b):
    if x > b:
        x = b
    if x < a:
        x = a
    return x


def logistic(x):
    return 1/(1+np.exp(-x))

def IOU(list1, list2):
    intersection = list(set(list1) & set(list2))
    union = list(set(list1) | set(list2))
    # len(intersection)/(min(len(list1), len(list2)))
    return len(intersection)/len(union)

def get_richness(influence_data, id):
    influencer_id = influence_data['influencer_id'].unique()
    if id not in influencer_id:
        return None, None

    else:
        followers_data = influence_data[influence_data['influencer_id'] == id]
        year = followers_data['influencer_active_start'].unique()[0]

        followers_year = followers_data['follower_active_start'].values
        # 纠正更早的被影响者
        for i in range(len(followers_year)):
            if followers_year[i] < year:
                followers_year[i] = year
        year_unique, year_count = np.unique(followers_year, return_counts=True)
        if(len(year_count)>3):
            cul_count = 0
            for i in range(3, len(year_count)):
                cul_count += year_count[i]
            year_count[3] = cul_count
            year_count = year_count[:4]
            year_unique = year_unique[:4]
        KL_year = scipy.stats.entropy(np.ones(len(year_unique),) / len(year_unique), year_count/sum(year_count))
        if KL_year > 1:
            KL_year = 1

        followers_genre = followers_data['follower_main_genre'].values
        genre_unique, genre_count = np.unique(followers_genre, return_counts=True)
        genre_count = -np.sort(-genre_count)
        if(len(genre_count)>=2):
            cul_count = 0
            for i in range(1, len(genre_count)):
                cul_count += genre_count[i]
            genre_count[1] = cul_count
            genre_count = genre_count[:2]
            KL_genre = scipy.stats.entropy(np.array([0.5, 0.5]), genre_count / sum(genre_count))

            if KL_genre > 1:
                KL_genre = 1

        else:
            KL_genre = 1

        return KL_year, KL_genre

def get_affinity(influence_data, id):

    def neighbor_list(id):
        followers_data = influence_data[influence_data['influencer_id'] == id]
        influencers_data = influence_data[influence_data['follower_id'] == id]
        followers_id_list = followers_data['follower_id'].values
        influencers_id_list = influencers_data['influencer_id'].values
        neighbor_id_list = list(set(followers_id_list) | set(influencers_id_list))

        return neighbor_id_list

    IOU_list = []
    neighbor_id_list = neighbor_list(id)
    for id2 in neighbor_id_list:
        neighbor_neighbor_list = neighbor_list(id2)
        IOU_list.append(IOU(neighbor_id_list, neighbor_neighbor_list))

    affinity = np.mean(np.array(IOU_list))
    affinity = logistic(affinity)
    # affinity = truncation(affinity, 0.1, 1)

    return affinity

def get_strength(influence_data, id):
    followers_data = influence_data[influence_data['influencer_id'] == id]
    year = followers_data['influencer_active_start'].unique()[0]

    year_data = influence_data[influence_data['influencer_active_start'] == year]
    year_influencer_count = len(year_data['influencer_id'].unique())

    strength = np.sqrt(len(followers_data)) * np.log(year_influencer_count)

    return strength

def get_width(kl1, kl2):
    # delta = logistic(1) - logistic(0)
    # width = ((logistic(1-kl1) - logistic(0)) / delta) * ((logistic(1-kl2) - logistic(0)) / delta)
    width = logistic(1-kl1) * logistic(1-kl2)

    return width

def get_rank(influence_data, influencer_id):
    genre_list = []
    follow_num_list = []
    for id in influencer_id:
        followers_data = influence_data[influence_data['influencer_id'] == id]
        genre = followers_data['influencer_main_genre'].unique()[0]
        genre_list.append(genre)
        follow_num = len(followers_data)
        follow_num_list.append(follow_num)

    df = pd.DataFrame({'id': influencer_id, 'genre': genre_list, 'follow_num': follow_num_list})
    rank_list = df.groupby(["genre"])["follow_num"].rank(ascending=False)

    proportion = []
    res = Counter(genre_list)
    for i in range(len(rank_list)):
        pop = rank_list[i] / (res[genre_list[i]] + 0.5)
        proportion.append(1 - pop)

    return follow_num_list, rank_list, proportion

def get_static_influence(width, affinity, strength, genre_rank):
    static_influence = []
    for i in range(len(width)):
        influence = width[i] * affinity[i] * strength[i] / np.sqrt(genre_rank[i])
        static_influence.append(influence)

    return static_influence

name = []
year = []
genre = []
kl_year = []
kl_genre = []
width = []
affinity = []
strength = []
for id in influencer_id:
    name.append(influence_data[influence_data['influencer_id'] == id]['influencer_name'].unique()[0])
    year.append(influence_data[influence_data['influencer_id'] == id]['influencer_active_start'].unique()[0])

    genre_temp = influence_data[influence_data['influencer_id'] == id]['influencer_main_genre'].unique()[0]
    genre_temp = genre_temp.replace(";", "")
    genre.append(genre_temp)

    kl1, kl2 = get_richness(influence_data, id)
    kl_year.append(kl1)
    kl_genre.append(kl2)
    width.append(get_width(kl1, kl2))

    affinity.append(get_affinity(influence_data, id))
    strength.append(get_strength(influence_data, id))

followers_num, genre_rank, _ = get_rank(influence_data, influencer_id)

static_influence = get_static_influence(width, affinity, strength, genre_rank)


influencer_data = {'influencer_id': influencer_id, 'influencer_name': name, 'year': year, 'genre': genre,
                   'followers_num': followers_num, 'genre_rank': genre_rank, 'kl_year': kl_year,
                   'kl_genre': kl_genre, 'width': width, 'affinity': affinity, 'strength': strength,
                   'static_influence': static_influence}
influencer_data = pd.DataFrame(influencer_data)
influencer_data.sort_values("static_influence", inplace=True, ascending=False)

influencer_data.to_csv('./data/influencer_data.csv', encoding='utf-8', index=False)

