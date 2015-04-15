#!/usr/bin/python2

######################################################
#           NOOK/KINDLE DAILY DIGEST SCRIPT          #
######         by Aaron Fryklund, 2015          ######
######         aaron@aaronfryklund.com          ######
# This script creates an SVG image that
# contains information including:
#   -current date
#   -3-day weather forecast
#   -daily agenda (up to 3 appointments from google calendar)
#   -currently reading (via goodreads.com, 1st book on list)
#   -cover of current book (via goodreads.com)
#   -progress towards yearly book goal (via goodreads.com)
#   -cover of NewYorker (because I like to know when a new issue 
#    is available)
###
# The core of this script is based on Matthew Petroff's "Kindle
# Weather Display" from 2012. I modified the script (and the 
# included SVG file) by making the weather widget smaller and 
# further up and to the right to make room for a daily agenda
# and information about my current reading habits. From
# goodreads.com I pull data on how many books I've read toward
# my goal for the year, the book I'm currently reading, and the
# cover for that book. I also pull the latest New Yorker cover
# because I like to know when a new issue is available. 
#
# To access the google information, you will need to get 
# a client_id, client_secret, and developerKey. The calendar
# authentication script is in a separate file and is called from 
# this file. 
#
# The goodreads.com data is just pulled from the html page. To use
# this script as-is, you will need a goodreads.com account with 
# at least one book in your currently reading list and you will
# also need to be signed-up for the yearly book challenge. You may
# also wish to modify the script to fetch different data that
# is important to you. 
#
### HOW TO ADD YOUR CUSTOM INFORMATION
#
# Under the 'import' statements, you will see 2 goodreads.com urls that
# you will need to change to reflect your account. Your profile must be 
# set to public under the "My Account"->"Settings" tab. The url itself
# is simply your main profile page.
#
# To customize your location for the weather data, you must know your
# latitude and longitude. Add it into the 'weather_xml' definition line. 
#
# Change the 'calendarId' (in this file and in main.py) variable to your the email address associated with
# your google calendar. 
#
# You will also need to add your google dev info into google_calendar.py.
#
### BATCH FILE
#
# A windows batch file is included with this package. This batch file will:
#   1. Run this script and insert the data into the SVG template file
#   2. Run 'Inkscape' from the command line to convert the SVG file to png
#   3. Copy the resulting png file into a dropbox folder to sync with Nook
#
# I have not provided the equivalent programs for OSX or Linux, but a basic
# understanding of bash scripting should at least get you going in the right
# direction. 
#
### DEPENDENCIES
#
# In addition to the libraries you see listed here in the 'import' section,
# you will also need 'gflags', 'httplib2', and the libraries that google
# provides on their python developer page. You will see them when you sign
# up for your authentication credentials.
#
####

# Weather script based on "Kindle Weather Display"
# by Matthew Petroff (http://www.mpetroff.net/)
# September 2012

import urllib, urllib2
from xml.dom import minidom
import datetime
import codecs
import google_calendar
from lxml import html
import requests
import os
import re

print("Connecting to web services...")

# google id for calendar data
calendarId = 'afryklund@gmail.com'

page1 = requests.get('http://www.goodreads.com/user_challenges/123yourchallenge')
page2 = requests.get('http://www.goodreads.com/user/show/123-yourid')
page3 = requests.get('http://www.newyorker.com/magazine')
tree1 = html.fromstring(page1.text)
tree2 = html.fromstring(page2.text)
tree3 = html.fromstring(page3.text)
print("Fetching book data from Goodreads...")
bookCount = tree1.xpath('//div[@class="progressText"]/text()')
currentBook = tree2.xpath('//a[@class="bookTitle"]/text()')

stripped = bookCount[0].rstrip()
stripped = stripped.splitlines()

img1 = tree2.xpath('//div[@class="firstcol"]')
testString = ''
for child in img1[0]:
		testString += html.tostring(child)
coverUrl = re.search("(?P<url>https?://[^\"]+)", testString).group("url")

#print coverUrl
scriptDir = os.path.dirname(os.path.realpath(__file__))
urllib.urlretrieve(coverUrl, scriptDir + "\cover.jpg")

#FETCH NEWYORKER COVER [CLUNKY - MAY STOP WORKING IF WEB PAGE LAYOUT CHANGES]
img2 = tree3.xpath('//div[@class="cover-info module"]')

coverUrlString = img2[0].xpath('//img/@src')[3]
#print coverUrl2
coverUrl2 = re.search("(?P<url>https?://[^\"]+)", coverUrlString).group("url")
#print coverUrl
scriptDir = os.path.dirname(os.path.realpath(__file__))
urllib.urlretrieve(coverUrl2, scriptDir + "\NYcover.jpg")


# Fetch weather data (change lat and lon to desired location)
weather_xml = urllib2.urlopen('http://graphical.weather.gov/xml/SOAP_server/ndfdSOAPclientByDay.php?whichClient=NDFDgenByDay&lat=32.956&lon=-96.659&format=24+hourly&numDays=4&Unit=e').read()
dom = minidom.parseString(weather_xml)
print("Fetching weather data...")

# Parse dates
xml_day_one = dom.getElementsByTagName('start-valid-time')[0].firstChild.nodeValue[0:10]
day_one = datetime.datetime.strptime(xml_day_one, '%Y-%m-%d')
gTimeMin = '2015-01-12T00:00:00-06:00'
gTimeMax = '2015-01-12T23:59:59-06:00'
gTimeMin = str(day_one.year)+'-'+str(day_one.month)+'-'+str(day_one.day)+gTimeMin[10:]
gTimeMax = str(day_one.year)+'-'+str(day_one.month)+'-'+str(day_one.day)+gTimeMax[10:]

#Fetch next three calendar appointments from google calendar
print("Fetching calendar data...")
def getEvents(pageToken=None):
    events = google_calendar.service.events().list(
        calendarId=calendarId,
        singleEvents=True,
        maxResults=4,
        orderBy='startTime',
        timeMin=gTimeMin,
        timeMax=gTimeMax,
        pageToken=pageToken,
        ).execute()
    return events
events = getEvents()
event_time = [' ', ' ', ' ']
event_title = [' ', ' ', ' ']
event_number = 0
while True:
	for event in events['items']:
		if 'date' in event['start']:
#			print(event['start']['date'].encode('utf-8') + ' All Day')
			event_time[event_number] = "All Day"
		if 'dateTime' in event['start']:
			event_time[event_number] = event['start']['dateTime'].encode('utf-8')[11:16]
#			print(event['start']['dateTime'].encode('utf-8'))
		event_title[event_number] = event['summary'].encode('utf-8')
#		print(event['summary'].encode('utf-8'))
#		print('')
		event_number += 1
	page_token = events.get('nextPageToken')
	if page_token:
		events = getEvents(page_token)
	else:
		break


# Parse temperatures
xml_temperatures = dom.getElementsByTagName('temperature')
highs = [None]*4
lows = [None]*4
for item in xml_temperatures:
    if item.getAttribute('type') == 'maximum':
        values = item.getElementsByTagName('value')
        for i in range(len(values)):
            highs[i] = int(values[i].firstChild.nodeValue)
    if item.getAttribute('type') == 'minimum':
        values = item.getElementsByTagName('value')
        for i in range(len(values)):
            lows[i] = int(values[i].firstChild.nodeValue)

# Parse icons
xml_icons = dom.getElementsByTagName('icon-link')
icons = [None]*4
for i in range(len(xml_icons)):
    icons[i] = xml_icons[i].firstChild.nodeValue.split('/')[-1].split('.')[0].rstrip('0123456789')
    #print(icons[i])
print("Parsing data...")


# Open SVG to process
output = codecs.open('weather-script-preprocess.svg', 'r', encoding='utf-8').read()
print("Processing SVG...")

# Insert icons and temperatures
output = output.replace('ICON_ONE',icons[0]).replace('ICON_TWO',icons[1]).replace('ICON_THREE',icons[2]).replace('ICON_FOUR',icons[3])
output = output.replace('HIGH_ONE',str(highs[0])).replace('HIGH_TWO',str(highs[1])).replace('HIGH_THREE',str(highs[2])).replace('HIGH_FOUR',str(highs[3]))
output = output.replace('LOW_ONE',str(lows[0])).replace('LOW_TWO',str(lows[1])).replace('LOW_THREE',str(lows[2])).replace('LOW_FOUR',str(lows[3]))
print("...")

#Insert book info
output = output.replace('current_title',currentBook[0]).replace('reading_count',bookCount[0].strip())
output = output.replace('#LINK_ONE',scriptDir + "\cover.jpg").replace('#LINK_TWO',scriptDir + "\NYcover.jpg")

# Insert days of week
day_string = str(day_one)
one_day = datetime.timedelta(days=1)
days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
output = output.replace('Today:',days_of_week[(day_one).weekday()]+' '+day_string[:10]).replace('DAY_THREE',days_of_week[(day_one + 2*one_day).weekday()]).replace('DAY_FOUR',days_of_week[(day_one + 3*one_day).weekday()])
print("...")

output = output.replace('agenda1_date',event_time[0]).replace('agenda1_title',event_title[0]).replace('agenda2_date',event_time[1]).replace('agenda2_title',event_title[1]).replace('agenda3_date',event_time[2]).replace('agenda3_title',event_title[2])
print("...")

# Write output
codecs.open('weather-script-output.svg', 'w', encoding='utf-8').write(output)
print("Process complete.")
#Uncomment the next line to pause at the end of the script
#raw_input("Press Enter to close")