import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import re
from sklearn.feature_extraction.text import CountVectorizer
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense, Embedding, LSTM, SpatialDropout1D
from sklearn.model_selection import train_test_split
from keras.utils.np_utils import to_categorical
from keras.layers import Dropout
from keras.layers import GRU
from keras.layers import Activation, Dense
from keras.activations import sigmoid
from keras.models import load_model

from keras.backend import clear_session

max_features = 2000

def load_data():
    data = pd.read_csv('../Sentiment.csv')
    # Keeping only the neccessary columns
    data = data[['text','sentiment']]

    data = data[data.sentiment != "Neutral"]
    data['text'] = data['text'].apply(lambda x: x.lower())
    data['text'] = data['text'].apply((lambda x: re.sub('[^a-zA-z0-9\s]','',x)))

    #print(data[ data['sentiment'] == 'Positive'].size)
    #print(data[ data['sentiment'] == 'Negative'].size)

    for idx,row in data.iterrows():
        row[0] = row[0].replace('rt',' ')

    tokenizer = Tokenizer(num_words=max_features, split=' ')
    tokenizer.fit_on_texts(data['text'].values)
    X = tokenizer.texts_to_sequences(data['text'].values)
    X = pad_sequences(X)
    
    embed_dim = 128
    model = Sequential()
    model.add(Embedding(max_features, embed_dim,input_length = X.shape[1]))
    model.add(Dropout(0.2))
    model.add(GRU(32))
    model.add(Dense(2,activation='softmax'))
    model.add(Dropout(0.2))
    #model.add(Dense(1,activation='sigmoid'))
    model.compile(loss = 'categorical_crossentropy', optimizer='adam',metrics = ['accuracy'])
    #print(model.summary())
    
    Y = pd.get_dummies(data['sentiment']).values
    X_train, X_test, Y_train, Y_test = train_test_split(X,Y, test_size = 0.33, random_state = 42)
    #print(X_train.shape,Y_train.shape)
    #print(X_test.shape,Y_test.shape)
    
    batch_size = 32
    model.fit(X_train, Y_train, epochs = 7, batch_size=batch_size, verbose = 2)
    model.save('GRU_model.h5')
    del model
    

def twt_GRU(twt):
    tokenizer = Tokenizer(num_words=max_features, split=' ')
    twt = tokenizer.texts_to_sequences(twt)
    #padding the tweet to have exactly the same shape as `embedding_2` input
    twt = pad_sequences(twt, maxlen=28, dtype='int32', value=0)
    #print(twt)
    clear_session()
    model = load_model('GRU_model.h5')
    sentiment = model.predict(twt,batch_size=1,verbose = 2)[0]
    if(np.argmax(sentiment) == 0):
        res="negative"
    elif (np.argmax(sentiment) == 1):
        res="positive"
    return res