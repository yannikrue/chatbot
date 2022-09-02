
from glob import glob
from operator import ne
import pickle
from time import time
from xmlrpc.client import FastMarshaller
import numpy as np
import json
import random
import webbrowser
import time

import nltk
from nltk.stem import WordNetLemmatizer

from keras.models import load_model

import webscraping

model = load_model('chatbot_model.h5')


lemmatizer = WordNetLemmatizer()
intents_json = json.loads(open('intents.json').read())
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))

stocks = False
news = False
weather = False

def clean_up_sentence(sentence):
    sen_words = nltk.word_tokenize(sentence)
    sen_words = [lemmatizer.lemmatize(word.lower()) for word in sen_words]
    return sen_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sen_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)
    for s in sen_words:
        for i,w in enumerate(words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict(sentence, model):
    # filter out low p cases
    p = bow(sentence, words,show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.75
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by p
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    if (len(return_list) == 0):
        return_list.append({"intent": "unsure", "probability": "unsure"})
    return return_list

def getResponse(ints, ints_json):
    global stocks, weather, news
    tag = ints[0]['intent']
    list_of_intents = ints_json['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
            info = ""
            res = random.choice(i['responses'])
            break
    if tag == "stocks":
        stocks = True
    elif tag == "weather":
        weather = True
        info = webscraping.get_weather() + "\n\n"
    elif tag == "news":
        news = True
        info = webscraping.get_news() + "\n\n"
    return info + res

def chatbot_response(msg):
    global stocks, weather, news
    res = "Anything else I can do for you?"
    print(msg)
    if msg == "y\n":
        if stocks:
            webbrowser.open('https://app.parqet.com/p/6231ddc2ca76350dff004bf0')
        elif weather:
            webbrowser.open("https://www.srf.ch/meteo")
        elif news:
            webbrowser.open("https://www.srf.ch/")
        stocks = False
        weather = False
        news = False
        return res
    elif msg == "n\n":
        stocks = False
        weather = False
        news = False
        return res
    else:
        ints = predict(msg, model)
        res = getResponse(ints, intents_json)
        return res
