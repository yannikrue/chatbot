
import pickle
from time import time
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
    tag = ints[0]['intent']
    list_of_intents = ints_json['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
            res = random.choice(i['responses'])
            break
    if tag == "stocks":
        i = input("Do you want me to open Parqet, the portfolio visualizer? y/n \n")
        if (i == "y"):
            time.sleep(3)
            webbrowser.open('https://app.parqet.com/p/6231ddc2ca76350dff004bf0')
    elif tag == "weather":
        weather = webscraping.get_weather()
        print(weather)
        i = input("Should I open the weather app for more detailed weather forecast? y/n \n")
        if i == "y":
            webbrowser.open("https://www.srf.ch/meteo")
    elif tag == "news":
        news = webscraping.get_news()
        print(news)
        i = input("Should I open the news app for more detailed information? y/n \n")
        if i == "y":
            webbrowser.open("https://www.srf.ch/")
    return res

def chatbot_response(msg):
    ints = predict(msg, model)
    res = getResponse(ints, intents_json)
    return res


print("Jarvis, here to help\n")
while True:
    msg_input = input()
    if (msg_input == "quit"):
        break
    res = chatbot_response(msg_input)
    print(res)