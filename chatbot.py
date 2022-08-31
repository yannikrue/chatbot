
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
intents = json.loads(open('intents.json').read())
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words,show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.75
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    if (len(return_list) == 0):
        return_list.append({"intent": "unsure", "probability": "unsure"})
    return return_list

def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
            result = random.choice(i['responses'])
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
    return result

def chatbot_response(msg):
    ints = predict_class(msg, model)
    print(ints)
    res = getResponse(ints, intents)
    return res


print("Jarvis, here to help\n")
while True:
    msg_input = input()
    if (msg_input == "quit"):
        break
    res = chatbot_response(msg_input)
    print(res)
