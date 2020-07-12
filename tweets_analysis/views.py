from django.shortcuts import render

import tweepy
import random
import pandas as pd
import preprocessor as p
import string
from textblob import TextBlob
import json
import os

def removePunc(sent):
    punc = [i for i in string.punctuation]
    punc.remove("'")
    for val in punc:
        sent = sent.replace(val, '')
    return sent

def isThere(loc, reference):
    for word in loc.split(','):
        if word.strip().capitalize() in reference.keys():
            return (True, word.strip().capitalize())
    return (False, None)

def getKey(country):
    key = random.choice(list(country))
    if len(country[key]) > 0:
        return key
    else:
        return getKey(country)

# Create your views here.
def analyse(request):

    consumer_key = '6AeMJZFppnlP1PbBxHu1KLBqG'
    consumer_secret = 'cqjZ0Pl3YHx0FSh7sYnZzwYePNscZO3QLLpHqD5hiY2TjzaavA'
    access_token = '1274225074304770049-bRxYBaB1YY8aA0pIYQiUlo7PZBpwWS'
    access_token_secret = 'w36rkKzDlbo4z0tYiYomqxdLHxlzyvYXgvkTnky70PQqA'
    callback_uri = 'oob'
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback_uri)
    auth.set_access_token(access_token, access_token_secret)

    module_dir = os.path.dirname(__file__)
    with open(os.path.join(module_dir, 'cities.json')) as f:
        cities = json.load(f)
    with open(os.path.join(module_dir, 'states.json')) as f:
        states = json.load(f)
    with open(os.path.join(module_dir, 'countries.json')) as f:
        countries = json.load(f)

    api = tweepy.API(auth)
    query = '#covid-19 #coronavirus #CoronavirusPandemic'
    statuses = list()
    for i, status in enumerate(tweepy.Cursor(api.search, q=query, lang='en').items(100)):
        if status not in statuses:
            statuses.append(status)
    tweets = {'text':[], 'location':[], 'polarity':[]}
    i = 1
    for status in statuses:
        text = removePunc(p.clean(status.text)).strip()
        if status.user.location not in ['', 'online', 'Pressing you against the pages', "EVERYWHERE GRIND'N"] and text not in tweets['text']:
            tweets['text'].append(text)
            tweets['location'].append(status.user.location)
            tweets['polarity'].append(TextBlob(text).sentiment.polarity)
            i += 1
    df = pd.DataFrame(tweets)

    # with open('coordinates.json') as f:
    #     big_coord = json.load(f)

    latitude = []
    longitude = []
    place = []
    for d in df['location']:
        city_chk = isThere(d, cities)
        state_chk = isThere(d, states)
        country_chk = isThere(d, countries)
        if city_chk[0]:
            latitude.append(cities[city_chk[1]][0])
            longitude.append(cities[city_chk[1]][1])
            place.append(city_chk[1])
        elif state_chk[0]:
            lat, long = states[state_chk[1]][random.randrange(0, len(states[state_chk[1]]))]
            latitude.append(lat)
            longitude.append(long)
            place.append(state_chk[1])
        elif country_chk[0]:
            lat, long = countries[country_chk[1]][random.randrange(0, len(countries[country_chk[1]]))]
            latitude.append(lat)
            longitude.append(long)
            place.append(country_chk[1])
        else:
            key = getKey(countries)
            lat, long = countries[key][random.randrange(0, len(countries[key]))]
            latitude.append(lat)
            longitude.append(long)
            place.append(key)

    df['latitude'] = latitude
    df['longitude'] = longitude
    df['place'] = place

    country_polar = {}
    for index in df.index:
        if df['place'][index] not in country_polar:
            country_polar[df['place'][index]] = {'positive' : 0, 'negative' : 0, 'neutral' : 0, 'latitude':df['latitude'][index], 'longitude':df['longitude'][index]}
        if df['polarity'][index] > 0:
            country_polar[df['place'][index]]['positive'] += 1
        elif df['polarity'][index] < 0:
            country_polar[df['place'][index]]['negative'] += 1
        else:
            country_polar[df['place'][index]]['neutral'] += 1

    data = list(zip(df['text'], df['polarity']))
    positive = []
    negative = []
    neutral = []

    for text, polarity in data:
        if polarity > 0:
            positive.append(text)
        if polarity == 0:
            neutral.append(text)
        if polarity < 0:
            negative.append(text)

    positive = " ".join(positive)
    negative = " ".join(negative)
    neutral = " ".join(neutral)

    pos_list = set()
    for word in positive.split():
        sent = TextBlob(word)
        if sent.sentiment.polarity > 0:
            pos_list.add((word.lower(), positive.lower().count(word.lower())))
    pos_list = [p[0] for p in pos_list]

    neg_list = set()
    for word in negative.split():
        sent = TextBlob(word)
        if sent.sentiment.polarity < 0:
            neg_list.add((word.lower(), negative.lower().count(word.lower())))
            
    neg_list = [n[0] for n in neg_list]
    
    neut_list = set()
    for word in neutral.split():
        sent = TextBlob(word)
        if sent.sentiment.polarity == 0:
            neut_list.add((word.lower(), neutral.lower().count(word.lower())))
    neut_list = set(filter(lambda x : x[1] > 1, neut_list))
    neut_list = [neu[0] for neu in neut_list]

    return render(request, "dashboard.html", {'country' : country_polar, 'positive' : pos_list, 'negative' : neg_list, 'neutral' : neut_list})
    