import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
def getDGRecommends():
    df1=pd.read_csv('tmdb_5000_credits.csv')
    df2=pd.read_csv('tmdb_5000_movies.csv')

    df1.columns = ['id','tittle','cast','crew']
    df2= df2.merge(df1,on='id')

    C= df2['vote_average'].mean()


    m= df2['vote_count'].quantile(0.9)

    q_movies = df2.copy().loc[df2['vote_count'] >= m]
    #q_movies.shape

    def weighted_rating(x, m=m, C=C):
        v = x['vote_count']
        R = x['vote_average']
        # Calculation based on the IMDB formula
        return (v/(v+m) * R) + (m/(m+v) * C)

    # Define a new feature 'score' and calculate its value with `weighted_rating()`
    q_movies['score'] = q_movies.apply(weighted_rating, axis=1)

    #Sort movies based on score calculated above
    q_movies = q_movies.sort_values('score', ascending=False)

    #Print the top 15 movies
    q_movies[['id','title', 'vote_count', 'vote_average', 'score']].head(10)

    #pop= df2.sort_values('popularity', ascending=False)
    return q_movies[['title']].head(10)
    
    '''
    plt.figure(figsize=(12,4))

    plt.barh(pop['title'].head(6),pop['popularity'].head(6), align='center',
            color='skyblue')
    plt.gca().invert_yaxis()
    plt.xlabel("Popularity")
    plt.title("Popular Movies")
    '''

if __name__ == '__main__':
    items = getDGRecommends()
    print(items)
    items2 = items.values
    for it in items2:
        print(it[0])
        print(it[1])
    #print(getDGRecommends())