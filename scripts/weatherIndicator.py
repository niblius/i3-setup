# -*- coding: utf-8 -*-
import geocoder
import json
import locale
import os
import requests
import pandas as pd
import urllib

class weatherIndicator:

    def __init__(self):
        # forecast.io api key:
        f = open('/home/christoph/.config/forecast-io-key')
        key = f.readline().rstrip()
        f.close()

        # Get current longitude and latitude based on IP address:
        ip = requests.get('http://ipinfo.io/ip').text.rstrip()
        loc = geocoder.freegeoip(ip)
        self.city = loc.locality
        if self.city == None:
            self.city = geocoder.google([loc.lat, loc.lng], \
                    method='reverse').city

        # Get weather info:
        root_url = 'https://api.forecast.io/forecast/'
        weather = requests.get(root_url + key + '/' + str(loc.lat) + ',' + \
                str(loc.lng))
        weather = json.loads(weather.text)

        # Convert temperature to Celcius:
        self.temperature = round((weather['currently']['temperature']-32) * 5/9)

        # Get current weather condition:
        condition = weather['currently']['summary']

        # Translate city when approriate:
        cdict = dict({'Boston': {'ga': 'Bostún'},
            'Dublin': {'ga': 'Baile Átha Cliath'}})

        language = locale.getlocale()[0]
        if language == 'ga_IE':
            try:
                self.city = cdict[self.city]['ga']
            except KeyError:
                self.city = self.city
        elif language == 'de_DE':
            try:
                self.city = cdict[self.city]['de']
            except KeyError:
                self.city = self.city

        # Get weather translation and icon:
        df = pd.read_csv(os.path.expanduser('~/') + '.config/i3/scripts/weather.csv')
        df = df[df.en == condition]

        if df.shape[0] == 0:
            self.icon = ''
            self.weather = condition
        else:
            self.icon = df.icon.values[0]
            self.icon = bytes(self.icon, 'ascii').decode('unicode-escape')
            if language == 'de_DE':
                self.weather = df.de.values[0]
            elif language == 'ga_IE':
                self.weather = df.ga.values[0]
            else:
                self.weather = condition

    def shortWeather(self):
        print(self.icon + str(self.temperature) + '°C')

    def longWeather(self):
        print(self.icon + '-' + self.city + ': ' + self.weather + ', ' + \
                str(self.temperature) + '°C')
