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
data = pd.read_csv('./Sentiment.csv')
# Keeping only the neccessary columns
data = data[['text','sentiment']]
data.head(5)


# ## texts to sequences

# In[25]:


data = data[data.sentiment != "Neutral"]
data['text'] = data['text'].apply(lambda x: x.lower())
data['text'] = data['text'].apply((lambda x: re.sub('[^a-zA-z0-9\s]','',x)))

print(data[ data['sentiment'] == 'Positive'].size)
print(data[ data['sentiment'] == 'Negative'].size)

for idx,row in data.iterrows():
    row[0] = row[0].replace('rt',' ')
    
max_fatures = 2000
tokenizer = Tokenizer(num_words=max_fatures, split=' ')
tokenizer.fit_on_texts(data['text'].values)
X = tokenizer.texts_to_sequences(data['text'].values)
X = pad_sequences(X)


# ## split data set

# In[3]:


Y = pd.get_dummies(data['sentiment']).values
X_train, X_test, Y_train, Y_test = train_test_split(X,Y, test_size = 0.3, random_state = 42)
print(X_train.shape,Y_train.shape)
print(X_test.shape,Y_test.shape)


# ## build model

# In[4]:


embed_dim = 128
lstm_out = 196

model = Sequential()
model.add(Embedding(max_fatures, embed_dim,input_length = X.shape[1]))
model.add(SpatialDropout1D(0.4))
#model.add(LSTM(lstm_out, dropout=0.2, recurrent_dropout=0.2, return_sequences=True))
model.add(LSTM(lstm_out, dropout=0.2, recurrent_dropout=0.2))
model.add(Dense(2,activation='softmax'))
#model.add(TimeDistributed(Dense(2,activation='softmax')))
model.compile(loss = 'categorical_crossentropy', optimizer='adam',metrics = ['accuracy'])
print(model.summary())


# ## train mode

# In[5]:


batch_size = 64
model.fit(X_train, Y_train, epochs = 6, batch_size=batch_size, verbose = 2)


# ## model evaluate

# In[6]:


validation_size = 1000

X_validate = X_test[-validation_size:]
Y_validate = Y_test[-validation_size:]
X_test = X_test[:-validation_size]
Y_test = Y_test[:-validation_size]

score,acc = model.evaluate(X_test, Y_test, verbose = 2, batch_size = batch_size)
print("score: %.2f" % (score))
print("acc: %.2f" % (acc))


# ## save model

# In[8]:


# model_json=model.to_json()
# with open('model.json','w') as f:
#     f.write(model_json)
# model.save_weights('model.h5')
from keras.models import load_model
model.save('model.h5')


# ## perdict

# In[45]:


def get_result(y_pred):
    if y_pred[0] > 0.5: 
        return 'Positive'
    elif y_pred[1] > 0.5:
        return 'Negative'
    else :
        return 'Neutral'


# In[46]:



def predict(text):
    predict_text = text.lower()
    predict_text = re.sub('[^a-zA-z0-9\s]','',perdict_text)

    predict_data = [predict_text]

    max_fatures = 2000
    tokenizer = Tokenizer(num_words=max_fatures, split=' ')
    tokenizer.fit_on_texts(predict_data)
    PX = tokenizer.texts_to_sequences(predict_data)
    PX = pad_sequences(PX, maxlen=X.shape[1])
    perdict_data
    y_pred = model.predict(PX,batch_size = 1)
    result = get_result(y_pred[0])
    return result


# In[47]:


perdict_text = "arcorubio came out of the gate like a true leader. I look forward to hearing more about his plans for a better America."
predict(perdict_text)


# In[48]:


perdict_text = "People who say they are #prolife are usually anti-social programs... They know that a society is a group of people right?"
predict(perdict_text)


# In[ ]:


if __name__ == '__main__':
    model=load_model('model.h5')
    model.compile(loss = 'categorical_crossentropy', optimizer='adam',metrics = ['accuracy'])

