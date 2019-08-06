import pandas as pd
from surprise import SVD
from surprise import Dataset, Reader
from surprise.model_selection import cross_validate, train_test_split
from collections import defaultdict
from surprise import NMF

def get_top_n(predictions, n=10):
    # First map the predictions to each user.
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est))

    # Then sort the predictions for each user and retrieve the k highest ones.
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]

    return top_n

def get_title(top_n):
    df = pd.read_csv('ratings_small.csv').drop(['timestamp'],axis=1)
    movie_titles = pd.read_csv('movies_metadata.csv', usecols=['id', 'title'])
    movie_titles = movie_titles.rename(columns={'id': 'movieId'})
    movie_titles['movieId'] = pd.to_numeric(movie_titles['movieId'], errors='coerce')
    df = pd.merge(df,movie_titles,on='movieId')

    for uid, user_ratings in top_n.items():
        if(uid == userid):
            print(uid, [iid for (iid, _) in user_ratings])


def predict_VSD(userid):

    df = pd.read_csv('ratings_small.csv').drop(['timestamp'],axis=1)
    reader = Reader(rating_scale=(1, 5))

    #使用reader格式从文件中读取数据
    data = Dataset.load_from_df(df[['userId', 'movieId', 'rating']], reader=reader)

    #拆分训练集与测试集，75%的样本作为训练集，25%的样本作为测试集
    trainset, testset = train_test_split(data, test_size=.25)

    model = SVD(n_factors=100)
    model.fit(trainset)

    predictions = model.test(testset)
    top_n = get_top_n(predictions, n=30)

    movie_titles = pd.read_csv('movies_metadata.csv', usecols=['id', 'title'])
    movie_titles = movie_titles.rename(columns={'id': 'movieId'})
    movie_titles['movieId'] = pd.to_numeric(movie_titles['movieId'], errors='coerce').fillna(0)
    movie_titles['movieId'] = movie_titles['movieId'].astype('int')
    movie_titles.drop_duplicates()

    for uid, user_ratings in top_n.items():
        if(uid == userid):
            title_list = [iid for (iid, _) in user_ratings]
            #print(uid, [iid for (iid, _) in user_ratings])
            #print(title_list)
            #print(uid, title_list)

    titles = movie_titles[movie_titles.movieId.isin(title_list)]
    print(titles[2:])
    return titles[2:]

def predict_NMF(userid):
    df = pd.read_csv('ratings_small.csv').drop(['timestamp'],axis=1)
    reader = Reader(rating_scale=(1, 30))

    #使用reader格式从文件中读取数据
    data = Dataset.load_from_df(df[['userId', 'movieId', 'rating']], reader=reader)

    #拆分训练集与测试集，75%的样本作为训练集，25%的样本作为测试集
    trainset, testset = train_test_split(data, test_size=.25)

    #使用NMF
    algo = NMF()
    algo.fit(trainset)
    pred_nmf = algo.test(testset)
    top_nmf_n = get_top_n(pred_nmf, n=5)

    movie_titles = pd.read_csv('movies_metadata.csv', usecols=['id', 'title'])
    movie_titles = movie_titles.rename(columns={'id': 'movieId'})
    movie_titles['movieId'] = pd.to_numeric(movie_titles['movieId'], errors='coerce').fillna(0)
    movie_titles['movieId'] = movie_titles['movieId'].astype('int')
    movie_titles.drop_duplicates()

    for uid, user_ratings in top_nmf_n.items():
        if(uid == userid):
            #print(uid, [iid for (iid, _) in user_ratings])
            title_list = [iid for (iid, _) in user_ratings]

    titles = movie_titles[movie_titles.movieId.isin(title_list)]
    print(titles[2:])
    return titles[2:]
