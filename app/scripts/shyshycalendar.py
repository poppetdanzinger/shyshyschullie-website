# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Command-line skeleton application for Calendar API.
Usage:
  $ python sample.py

You can also get help on all the command-line flags the program understands
by running:

  $ python sample.py --help

"""

import os

def get_events():
    try:
        import httplib2, dateutil.parser
        from apiclient import discovery
        from oauth2client import file
        from oauth2client import client
        from oauth2client import tools
        CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')
        FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
                                              scope=[
                                                  'https://www.googleapis.com/auth/calendar',
                                                  'https://www.googleapis.com/auth/calendar.readonly',
                                              ],
                                              message=tools.message_if_missing(CLIENT_SECRETS))

    except ImportError as e:
        print("ImportError in shyshycalendar. Are google calendar libraries installed?")
        print(e)
        return []

    storage = file.Storage('app/scripts/shyshy-storage.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(FLOW, storage, flags)

    http = httplib2.Http()
    http = credentials.authorize(http)
    service = discovery.build('calendar', 'v3', http=http)

    try:
        google_events=[]
        page_token = None
        while True:
            events = service.events().list(calendarId='primary', pageToken=page_token).execute()
            for event in events['items']:
                google_events.append(event)
                #print ("EVENT: %s"%event)
            page_token = events.get('nextPageToken')
            if not page_token:
                break
    except client.AccessTokenRefreshError:
        print ("shyshycalendar.py fail: The credentials have been revoked or expired, please re-run"
      "the application to re-authorize")

    clean=clean_events(google_events)
    for item in clean:
        print(item)
    return clean

def clean_events(google_events):
    for event in google_events:
        try:
            datetime=dateutil.parser.parse(event["end"]["dateTime"])
            pretty_date=datetime.strftime("%A, %B %d %Y, %I:%M%p")
            pretty_date=pretty_date[:-2]+pretty_date[-2:].lower()
            event["pretty_date"]=pretty_date
        except KeyError:
            pass
    return google_events

if __name__=="__main__":
    for event in get_events():
        print(event)
