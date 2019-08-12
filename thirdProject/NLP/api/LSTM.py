#!/usr/bin/env python
# coding: utf-8

# In[16]:



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
from keras.models import load_model

model = Sequential()
max_fatures = 2000

def load_data():
    data = pd.read_csv('./Sentiment.csv')
    # Keeping only the neccessary columns
    data = data[['text','sentiment']]
    data = data[data.sentiment != "Neutral"]
    data['text'] = data['text'].apply(lambda x: x.lower())
    data['text'] = data['text'].apply((lambda x: re.sub('[^a-zA-z0-9\s]','',x)))

    print(data[ data['sentiment'] == 'Positive'].size)
    print(data[ data['sentiment'] == 'Negative'].size)

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
    return X_train, X_test, Y_train, Y_test, X, Y

def trian():
    
    # load_data
    X_train, X_test, Y_train, Y_test, X, Y = load_data()

    # ## build model
    embed_dim = 128
    lstm_out = 196

    # model = Sequential()
    model.add(Embedding(max_fatures, embed_dim, input_length = X.shape[1]))
    model.add(SpatialDropout1D(0.4))
    #model.add(LSTM(lstm_out, dropout=0.2, recurrent_dropout=0.2, return_sequences=True))
    model.add(LSTM(lstm_out, dropout=0.2, recurrent_dropout=0.2))
    model.add(Dense(2,activation='softmax'))
    #model.add(TimeDistributed(Dense(2,activation='softmax')))
    model.compile(loss = 'categorical_crossentropy', optimizer='adam',metrics = ['accuracy'])
    print(model.summary())


    # ## train mode

    batch_size = 64
    model.fit(X_train, Y_train, epochs = 7, batch_size=batch_size, verbose = 2)


    # ## model evaluate
    validation_size = 1000

    X_validate = X_test[-validation_size:]
    Y_validate = Y_test[-validation_size:]
    X_test = X_test[:-validation_size]
    Y_test = Y_test[:-validation_size]


    score,acc = model.evaluate(X_test, Y_test, verbose = 2, batch_size = batch_size)
    print("score: %.2f" % (score))
    print("acc: %.2f" % (acc))

    # ## save model
    # model_json=model.to_json()
    # with open('model.json','w') as f:
    #     f.write(model_json)
    # model.save_weights('model.h5')
    
    model.save('model.h5')


# ## perdict
def get_result(y_pred):
    if y_pred[0] >= 0.5: 
        return 'Positive'
    else :
        return 'Negative'


def predict(text):
    predict_text = text.lower()
    predict_text = re.sub('[^a-zA-z0-9\s]','',predict_text)

    predict_data = [predict_text]

    max_fatures = 2000
    tokenizer = Tokenizer(num_words=max_fatures, split=' ')
    tokenizer.fit_on_texts(predict_data)
    PX = tokenizer.texts_to_sequences(predict_data)
    PX = pad_sequences(PX, maxlen=28)
    
    
    if model == None:
        print("load_model!!!")
    # print(model.summary())

    y_pred = model.predict(PX, batch_size = 1)
    print(y_pred)
    result = get_result(y_pred[0])
    return result


def test():
    perdict_text = "I'll tell you the one good thing about #GOPDebates: candidates are tripping over themselves to outdo each other in sexism"
    print(predict(perdict_text))

    perdict_text2 = "bad"
    print(predict(perdict_text2))

if __name__ == '__main__':

    trian()
    # load()
    test()
