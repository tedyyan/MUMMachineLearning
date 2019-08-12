#base on https://github.com/amirziai/sklearnflask
import sys
import os
import shutil
import time
import traceback

from flask import Flask, request, jsonify, render_template
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.externals import joblib
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn import model_selection
from twython import Twython
# from LSTM import predictLSTM
import json

from geopy.geocoders import Nominatim
import gmplot

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

from sklearn.feature_extraction.text import CountVectorizer
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense, Embedding, LSTM, SpatialDropout1D
from sklearn.model_selection import train_test_split
from keras.utils.np_utils import to_categorical
import re

#=======ltsm model init================================================
max_fatures = 2000

data = pd.read_csv('../Sentiment.csv')
# Keeping only the neccessary columns
data = data[['text','sentiment']]
data = data[data.sentiment != "Neutral"]
data['text'] = data['text'].apply(lambda x: x.lower())
data['text'] = data['text'].apply((lambda x: re.sub('[^a-zA-z0-9\s]','',x)))

for idx,row in data.iterrows():
    row[0] = row[0].replace('rt',' ')
    

tokenizer = Tokenizer(num_words=max_fatures, split=' ')
tokenizer.fit_on_texts(data['text'].values)
X = tokenizer.texts_to_sequences(data['text'].values)
X = pad_sequences(X)

Y = pd.get_dummies(data['sentiment']).values
X_train, X_test, Y_train, Y_test = train_test_split(X,Y, test_size = 0.3, random_state = 42)
print(X_train.shape,Y_train.shape)
print(X_test.shape,Y_test.shape)


# ## build model
embed_dim = 128
lstm_out = 196

model = Sequential()
model.add(Embedding(max_fatures, embed_dim, input_length = X.shape[1]))
model.add(SpatialDropout1D(0.4))
#model.add(LSTM(lstm_out, dropout=0.2, recurrent_dropout=0.2, return_sequences=True))
model.add(LSTM(lstm_out, dropout=0.2, recurrent_dropout=0.2))
model.add(Dense(2,activation='softmax'))
#model.add(TimeDistributed(Dense(2,activation='softmax')))

model.compile(loss = 'categorical_crossentropy', optimizer='adam',metrics = ['accuracy'])
print(model.summary())

# ## train mode

batch_size = 512
model.fit(X_train, Y_train, epochs = 1, batch_size=batch_size, verbose = 2)

validation_size = 1000

X_validate = X_test[-validation_size:]
Y_validate = Y_test[-validation_size:]
X_test = X_test[:-validation_size]
Y_test = Y_test[:-validation_size]

score,acc = model.evaluate(X_test, Y_test, verbose = 2, batch_size = batch_size)
print("score: %.2f" % (score))
print("acc: %.2f" % (acc))
# ## perdict
def get_result(sentiment):
    if(np.argmax(sentiment) == 0):
        print("negative")
    elif (np.argmax(sentiment) == 1):
        print("positive")

def predictLSTM(text):

    twt = [text]
    #vectorizing the tweet by the pre-fitted tokenizer instance
    twt = tokenizer.texts_to_sequences(twt)
    #padding the tweet to have exactly the same shape as `embedding_2` input
    twt = pad_sequences(twt, maxlen=28, dtype='int32', value=0)
    print(model.summary())
    model._make_predict_function()
    sentiment = model.predict(twt,batch_size=1,verbose = 2)[0]
    result = get_result(sentiment)
    return result

predictLSTM("good")

''''''

#====end lstm model==============================================================



app = Flask(__name__)
def drawMapPos(tweets):
    geolocator = Nominatim()

    # Go through all tweets and add locations to 'coordinates' dictionary
    coordinates = {'latitude': [], 'longitude': []}
    neg = {'latitude': [], 'longitude': []}
    for tweet in tweets:
        try:
            if analysisSentiment(tweet.get('text')) != "negative": 
                location = geolocator.geocode(tweet.get('location'))
        
                # If coordinates are found for location
                if location:
                    coordinates['latitude'].append(location.latitude)
                    coordinates['longitude'].append(location.longitude)
            '''
            else:
                location = geolocator.geocode(tweet.get('location'))
        
                # If coordinates are found for location
                if location:
                    neg['latitude'].append(location.latitude)
                    neg['longitude'].append(location.longitude)
            '''
        # If too many connection requests
        except:
            pass

    # Instantiate and center a GoogleMapPlotter object to show our map
    gmap = gmplot.GoogleMapPlotter(30, 0, 3)

    # Insert points on the map passing a list of latitudes and longitudes
    gmap.heatmap(coordinates['latitude'], coordinates['longitude'], radius=20)
    #            gradient =((200, 0, 0, 1),(100, 0, 0, 1),(50, 0, 0, 1)))
    #gmap.heatmap(neg['latitude'], neg['longitude'], radius=20,
    #            gradient =((0, 200, 200, 1),(0, 100, 100, 1),(0, 50, 50, 1)))


    # Save the map to html file
    gmap.draw("templates/python_heatmap.html")

def drawMapNeg(tweets):
    geolocator = Nominatim()

    # Go through all tweets and add locations to 'coordinates' dictionary
    coordinates = {'latitude': [], 'longitude': []}
    neg = {'latitude': [], 'longitude': []}
    #for count, user_loc in enumerate(tweets.location):
    for tweet in tweets:
        #try:
           
            if analysisSentiment(tweet.get('text')) != "positive":
                location = geolocator.geocode(tweet.get('location'))
        
                # If coordinates are found for location
                if location:
                    neg['latitude'].append(location.latitude)
                    neg['longitude'].append(location.longitude)
        # If too many connection requests
        #except:
        #    pass

    # Instantiate and center a GoogleMapPlotter object to show our map
    gmap = gmplot.GoogleMapPlotter(30, 0, 3)

    # Insert points on the map passing a list of latitudes and longitudes
    gmap.heatmap(neg['latitude'], neg['longitude'], radius=20)
                #gradient =((0, 200, 0, 0.6),(0, 100, 0, 0.3),(0, 50, 0, 0.3)))

    # Save the map to html file
    gmap.draw("templates/python_negheatmap.html")

def analysisSentiment(text):
    print(text)
    
    if predictLSTM(text) == 'Positive':  #len(text) > 80:
        return "positive"
    else:
        return "negative"

@app.route('/predict', methods=['POST'])
def predict():
    json_ = request.json
    #print("-------json---------",json_)
    #query = pd.get_dummies(pd.DataFrame(json_))
    
    print("-------query---------",json_["text"])
    
    return jsonify({"result":analysisSentiment(json_["text"])})

@app.route('/analysistext', methods=['GET'])
def analysistext():
    #json_ = request.json
    print(request.args.to_dict())
    gets = request.args.to_dict()
    yourtext = gets.get("yourtext")
    
    result = analysisSentiment(yourtext)
    return jsonify({"sentiment":result})

@app.route('/tweetLearning', methods=['GET'])
def tweetLearning():
    #json_ = request.json
    print(request.args.to_dict())
    gets = request.args.to_dict()
    keyword = gets.get("keyword")
    count = gets.get("count")
    result_type = gets.get("result_type")

    credentials = {}
    credentials['CONSUMER_KEY'] = "pyKBZeHhRb9w006Cv4Ituqi7E"
    credentials['CONSUMER_SECRET'] = "DwUyJXTzPF4FexqztrXKu6ij7tf9GHnH9EiGGh0FGtdgAejjux"
    credentials['ACCESS_TOKEN'] = "53697152-Nvdb7vmwGzPUI65duv6fkkA5ejvC8JSt0FtZncz3J"
    credentials['ACCESS_SECRET'] = "AlQ0boi3ePIY3muIH6DHylCidVyMkEtI56hI9cin2C7wx"
    python_tweets = Twython(credentials['CONSUMER_KEY'], credentials['CONSUMER_SECRET'])

    # Create our query
    query = {'q': keyword,
            'result_type': result_type,  #'popular' recent mixed
            'count': count,
            'lang': 'en',
            }

    # Search tweets
    #dict_ = {'user': [], 'date': [], 'text': [], 'favorite_count': []}
    

    positivecnt,negtivecnt = 0,0
    tweetsarr = []
    def process_tweet(tweet,positivecnt,negtivecnt):
        d = {}
        #d['hashtags'] = [hashtag['text'] for hashtag in tweet['entities']['hashtags']]
        d['text'] = tweet['text']
        d['user'] = tweet['user']['screen_name']
        d['location'] = tweet['user']['location']
        #d.get('favorite_count',list).append(tweet['favorite_count'])
        
        if analysisSentiment(status['text']) == "positive":
            positivecnt += 1
        else:
            negtivecnt += 1
        return d,positivecnt,negtivecnt
    
    for status in python_tweets.search(**query)['statuses']:
        ttt,positivecnt,negtivecnt = process_tweet(status,positivecnt,negtivecnt) 
        tweetsarr.append(ttt)
    
    tweets = pd.DataFrame(data=tweetsarr)
    

    drawMapPos(tweetsarr)
    drawMapNeg(tweetsarr)
    

    print("count",count,"Positive:",positivecnt,"Negtive:",negtivecnt)
    return jsonify({"count":count,"Positive:":positivecnt,"Negtive:":negtivecnt})


@app.route('/home')
def index():
    return render_template('home.html')

@app.route('/send')
def send():
    return render_template('send.html')

@app.route('/templatemap', methods=['GET'])
def templatemap():
    return render_template('python_heatmap.html')

@app.route('/templatemapneg', methods=['GET'])
def templatemapneg():
    return render_template('python_negheatmap.html')

if __name__ == '__main__':
    try:
        port = int(sys.argv[1])
    except Exception as e:
        port = 5000


    app.run(host='0.0.0.0', port=port, debug=True)

