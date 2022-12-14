import nltk
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')
from nltk.stem import WordNetLemmatizer

import json
import pickle
import random

import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.optimizers import SGD

lemmatizer = WordNetLemmatizer()

words=[]
classes = []
documents = []

ignore_words = ['?', '!']
data_file = open('intents.json').read()
intents = json.loads(data_file)


for intent in intents['intents']:
    for pattern in intent['patterns']:

        # take string and tokenize it
        w = nltk.word_tokenize(pattern)
        words.extend(w)
        # adding to documents
        documents.append((w, intent['tag']))

        # adding tags to our class list
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

#stem and normalize every word
words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]
words = sorted(list(set(words)))
classes = sorted(list(set(classes)))

#safe words and classes in pickle
pickle.dump(words,open('words.pkl','wb'))
pickle.dump(classes,open('classes.pkl','wb'))

# initializing training data
train_data = []
output_empty = [0] * len(classes)

for document in documents:
    # initializing bag of words
    bag = []
    # token list for the pattern
    pattern_words = document[0]
    # normalize words - ai can recognize similar words
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]
    # replace 0 with 1 for every match
    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)

    # output is 0 for each tag and 1 for current tag (for each pattern)
    output_row = list(output_empty)
    output_row[classes.index(document[1])] = 1

    train_data.append([bag, output_row])

# shuffle our features and turn into np.array
random.shuffle(train_data)
train_data = np.array(train_data)
# create train and test lists. X - patterns, Y - intents
train_x = list(train_data[:,0])
train_y = list(train_data[:,1])
print("Training data created")


# 3 layers. 1st 128 neurons,  2nd 64 neurons and output layer contains number of neurons
# equal to number of intents to predict output intent with softmax
nn = Sequential()
nn.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
nn.add(Dropout(0.5))
nn.add(Dense(64, activation='relu'))
nn.add(Dropout(0.5))
nn.add(Dense(len(train_y[0]), activation='softmax'))

# Compile neural net
sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
nn.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

#saving and fitting neural net as model
hist = nn.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)
nn.save('chatbot_model.h5', hist)

print("model saved in chatbot_model.h5")