#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
openweathermap.py - Openweathermap module for jenni/phenny irc bot, in german and 
specific to german and austrian zip codes.

Copyright 2015 TF (https://github.com/re-src/)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni-misc: https://github.com/freeboson/jenni-misc/
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
'''

import re
import web

appid = 'bd82977b86bf27fb59a04b61b657fb6f' # this appid is the currently available public key, but should probably be replaced by a personal appid

'''Patterns to search for in the resulting xml file'''
map_city = re.compile('<location><name>(.*?)</name>|<city id=".*?" name="(.*?)"')
map_country = re.compile('<country>(.*?)</country>')
map_humidity = re.compile('<humidity value="(.+?)" unit')
map_clouds = re.compile('<clouds value=".*?" all="(.*?)" unit|clouds value="(.*?)"')
map_temp_day = re.compile('<temperature day="(.*?)"|<temperature value="(.*?)"')
map_temp_min = re.compile('min="(.*?)"')
map_temp_max = re.compile('max="(.*?)"')
map_temp_morn = re.compile('morn="(.*?)"')
map_temp_eve = re.compile('eve="(.*?)"')
map_temp_night = re.compile('night="(.*?)"')
map_sunrise = re.compile('sun rise="(.*?)"')
map_sunset = re.compile('set="(.*?)"')
map_forecast = re.compile('<symbol number=".*?" name="(.*?)"')
map_pressure = re.compile('<pressure unit="hPa" value="(.*?)"|<pressure value="(.*?)"')
map_day = re.compile('<time day="(.*?)">')
map_windspeed = re.compile('windSpeed mps="(.*?)"|<wind><speed value="(.*?)"')
map_winddirection = re.compile('windDirection deg=".*?" code="(.*?)"|<direction value=".*?" code="(.*?)"')
map_weather = re.compile('<weather number=".*?" value="(.*?)" icon=".*?"')
map_lastupdate = re.compile('<lastupdate value="(.*?)"')
map_coord = re.compile('<coord lon="(.*?)" lat="(.*?)"|latitude="(.*?)" longitude="(.*?)"')

'''Main method'''
def openweathermap(jenni, input):
    '''.wetter -- Weather via openweathermap.org '''
    text = input.group().split()

    if len(text) > 1 and '-h' not in text:
        get_daily(jenni, input)
 
    else:
        get_help(jenni)

openweathermap.commands = ['wetter', 'w', 'openweathermap']
openweathermap.priority = 'low'

'''Help method'''
def get_help(jenni):
    jenni.say(" <Ortsnamen>: Suche nach Wetterdaten mittels Openweathermap, <PLZ>: Suche nach PLZ in DE/AT, -v <Anzahl><Ortsnamen>: Vorhersage (nur für Ortsnamen, nicht PLZ")

'''Get the weather'''
def get_daily(jenni, input):
    global appid
    text = input.group().split()
    text.remove(text[0])
    if isint(text[0]):
        if len(text[0]) == 4:
            url = "http://api.openweathermap.org/data/2.5/weather?zip=" + text[0] + ",at&mode=xml&units=metric&lang=de"
        elif len(text[0]) == 5:
            url = "http://api.openweathermap.org/data/2.5/weather?zip=" + text[0] + ",de&mode=xml&units=metric&lang=de"
    else:
        if '-v' in input:
            count = 3
            query = ''
            url = 'http://api.openweathermap.org/data/2.5/forecast/daily?q='
            for i in range (0, len(text)):
                if text[i] == '-v' and isint(text[i+1]):               
                    count = text[i+1]
                    text.remove(text[i+1])
                    text.remove(text[i])
                    break
            for i in range (0, len(text)):
                if not isint(text[i]) and text[i] != '-v':
                    if query == '':
                        query = text[i].encode('utf-8')
                    else:
                        query += '+' + text[i].encode('utf-8')
            url += query + '&mode=xml&units=metric&cnt=' + str(count) + '&lang=de'

        else:
            url = "http://api.openweathermap.org/data/2.5/weather?q=" + text[0].encode('utf-8')
            text.remove(text[0])
            for t in text:
                url += '+' + t.encode('utf-8')
            url += "&mode=xml&units=metric&lang=de"

    url += '&APPID=' + appid
    page = web.get(url)
    city = map_city.findall(page)
    country = map_country.findall(page)
    humidity = map_humidity.findall(page)
    clouds = map_clouds.findall(page)
    temp_day = map_temp_day.findall(page)
    temp_min = map_temp_min.findall(page)
    temp_max = map_temp_max.findall(page)
    temp_morn = map_temp_morn.findall(page)
    temp_eve = map_temp_eve.findall(page)
    temp_night = map_temp_night.findall(page)
    sunrise = map_sunrise.findall(page)
    sunset = map_sunset.findall(page)
    forecast = map_forecast.findall(page)
    pressure = map_pressure.findall(page)
    day = map_day.findall(page)
    windspeed = map_windspeed.findall(page)
    winddirection = map_winddirection.findall(page)
    weather = map_weather.findall(page)
    lastupdate = map_lastupdate.findall(page)
    coord = map_coord.findall(page)

    for i in range(0, len(temp_day)):
        if city[0][0]:
            info = "[Vorhersage] \x02" + city[0][0] + "\x0F, " + country[0]
        elif city[0][1]:
            info = "[Aktuell] \x02" + city[0][1] + "\x0F, " + country[0]
        if coord:
            if coord[0][1]:
                info += " (" + coord[0][1]
            if coord[0][0]:
                info += ", " + coord[0][0] + ")"
            if coord[0][2]:
                info += " (" + '%.2f' % round(float(coord[0][2]), 2)
            if coord[0][3]:
                info += ", " + '%.2f' % round(float(coord[0][3]), 2)
                info += ")"
        if day:
            dayelements = day[i].split("-")
            info += " am \x02" + dayelements[2] + "." + dayelements[1] + "." + dayelements[0] + "\x0F"
        elif lastupdate:
            dateelements = lastupdate[0].split("-")
            dayelements = dateelements[2].split('T')
            lastupdatedayelem = dayelements[1].split(":")
            lastupdateh = int(lastupdatedayelem[0])+2
            info += " um \x02" + str(lastupdateh) + ":" + lastupdatedayelem[1] + "\x0F"
        if temp_day[i][0]:
            td = "%.1f" % float(temp_day[i][0])
            td = td.replace(".", ",")
            info += ': Tagsüber \x02' + td + '\x0F°'
        elif temp_day[i][1]:
            td = "%.1f" % float(temp_day[i][1])
            td = td.replace(".", ",")
            info += ': Derzeit \x02' + td + '\x0F°'
        if temp_min:
            tmin = "%.1f" % float(temp_min[i])
            tmin = tmin.replace(".", ",")
            info += ' (' + tmin
        if temp_max:
            tmax = "%.1f" % float(temp_max[i])
            tmax = tmax.replace(".", ",")
            info += ' bis ' + tmax + '°)'
        if weather:
            info += ", \x02" + weather[0] + "\x0F"
        if temp_morn:
            tmorn = "%.1f" % float(temp_morn[i])
            tmorn = tmorn.replace(".", ",")
            info += ' morgens ' + tmorn + '°/'
        if temp_eve:
            te = "%.1f" % float(temp_eve[i])
            te = te.replace(".", ",")
            info += 'abends ' + te + '°/'
        if temp_night:
            tn = "%.1f" % float(temp_night[i])
            tn = tn.replace(".", ",")
            info += 'nachts ' + tn + '° -'
        if forecast:
            info += " \x02" + forecast[i] + "\x0F"
        if clouds[i][0]:
            info += ", Bewölkung: " + clouds[i][0] + '%,'
        elif clouds[i][1]:
            info += ", Bewölkung: " + clouds[i][1] + '%,'
        if humidity:
            info += ' Luftfeuchtigkeit: ' + humidity[i] + '%,'
        if pressure[i][0]:
            p = "%.0f" % float(pressure[i][0])
            info += " Luftdruck: " + p + ' hPa,'
        elif pressure[i][1]:
            p = "%.0f" % float(pressure[i][1])
            info += " Luftdruck: " + p + ' hPa,'
        if windspeed[i][0]:
            ws = float(windspeed[i][0]) * 3.6
            ws = "%.1f" % ws
            ws = str(ws).replace(".", ",")
            info += " Wind: " + str(ws) + " km/h "
        elif windspeed[i][1]:
            ws = float(windspeed[i][1]) * 3.6
            ws = "%.1f" % ws
            ws = str(ws).replace(".", ",")
            info += " Wind: " + str(ws) + " km/h "
        if winddirection[i][0]:
            info += "aus Richtung " + getdirection(winddirection[i][0])
        elif winddirection[i][1]:
            info += "aus Richtung " + getdirection(winddirection[i][1])
        if not (i > 0):
            sunrisetime = sunrise[0].split("T")
            sunrisetimeelements = sunrisetime[1].split(":")
            sunriseh = int(sunrisetimeelements[0]) + 2
            info += ', Sonnenauf/-untergang: ' + str(sunriseh) + ":" + sunrisetimeelements[1]
            sunsettime = sunset[0].split("T")
            sunsettimeelements = sunsettime[1].split(":")
            sunseth = int(sunsettimeelements[0]) + 2 
            info += "/" + str(sunseth) + ":" + sunsettimeelements[1] + " Uhr"
        info += "."
        jenni.say(info)

'''Maps the abbreviations to german words for the wind directions'''
winddirection_table = {
    "NNE": "Nordnordost",
    "ENE": "Ostnordost",
    "ESE": "Ostsüdost",
    "SSE": "Südsüdost",
    "SSW": "Südsüdwest",
    "WSW": "Westsüdwest",
    "WNW": "Westnordwest",
    "NNW": "Nordnordwest",
    "NW": "Nordwest",
    "SW": "Südwest",
    "NE": "Nordost",
    "SE": "Südost",
    "N": "Nord",
    "S": "Süd",
    "E": "Ost",
    "W": "West"
}

'''Get the word from the winddirection_table for an abbreviation'''
def getdirection(text):
    for i, j in winddirection_table.iteritems():
        if i == text:
            text = text.replace(i, j)
    return text

'''Helper method to determine wether a variable is an integer or not, should be moved to a helper file usually'''
def isint(value):
  try:
    int(value)
    return True
  except:
    return False

if __name__ == '__main__':
    print __doc__.strip()
