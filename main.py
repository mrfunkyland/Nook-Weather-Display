calendarId = 'the-name-of-your-calendar'

import google_calendar
import pprint

def getEvents(pageToken=None):
    events = google_calendar.service.events().list(
        calendarId=calendarId,
        singleEvents=True,
        maxResults=4,
        orderBy='startTime',
        timeMin='2015-01-12T00:00:00-08:00',
        timeMax='2015-01-12T23:59:00-08:00',
        pageToken=pageToken,
        ).execute()
    return events

def main():
    events = getEvents()
    while True:
        for event in events['items']:
            if 'date' in event['start']:
			    print(event['start']['date'].encode('utf-8') + ' All Day')
            if 'dateTime' in event['start']:
			    print(event['start']['dateTime'].encode('utf-8'))
            print(event['summary'].encode('utf-8'))
            print('')
        page_token = events.get('nextPageToken')
        if page_token:
            events = getEvents(page_token)
        else:
            break

if __name__ == '__main__':
    main()