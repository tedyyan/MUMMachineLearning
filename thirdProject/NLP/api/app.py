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
from LSTM import predict
import json

from geopy.geocoders import Nominatim
import gmplot


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
    if len(text) > 80:
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
    
    print("yourtext",yourtext)
    return jsonify({"yourtext":yourtext})

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
