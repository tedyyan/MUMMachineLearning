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
model.fit(X_train, Y_train, epochs = 10, batch_size=batch_size, verbose = 2)

validation_size = 1000

X_validate = X_test[-validation_size:]
Y_validate = Y_test[-validation_size:]
X_test = X_test[:-validation_size]
Y_test = Y_test[:-validation_size]

score,acc = model.evaluate(X_test, Y_test, verbose = 2, batch_size = batch_size)
print("score: %.2f" % (score))
print("acc: %.2f" % (acc))


''''''
# ## perdict
def get_result(sentiment):
    if(np.argmax(sentiment) == 0):
        print("negative")
        return "negative"
    elif (np.argmax(sentiment) == 1):
        print("positive")
        return "positive"
    

def predictLSTM(text):
    print(text)
    twt = [text]
    #vectorizing the tweet by the pre-fitted tokenizer instance
    twt = tokenizer.texts_to_sequences(twt)
    #padding the tweet to have exactly the same shape as `embedding_2` input
    twt = pad_sequences(twt, maxlen=28, dtype='int32', value=0)
    #print(model.summary())
    
    sentiment = model.predict(twt,batch_size=10,verbose = 2)[0]
    result = get_result(sentiment)
    return result

predictLSTM("I'll tell you the one good thing about #GOPDebates: candidates are tripping over themselves to outdo each other in sexism")

def test():
    perdict_text = "I'll tell you the one good thing about #GOPDebates: candidates are tripping over themselves to outdo each other in sexism"
    print(predictLSTM(perdict_text))

    perdict_text2 = "Meetings: Because none of us is as dumb as all of us. "
    print(predictLSTM(perdict_text2))

    perdict_text2 = "No *I* hate Planned Parenthood and women more! NO I HATE PLANNED PARENTHOOD AND WOMEN MORE!!!!! #GOPDebate "
    print(predictLSTM(perdict_text2))

if __name__ == '__main__':

    test()

