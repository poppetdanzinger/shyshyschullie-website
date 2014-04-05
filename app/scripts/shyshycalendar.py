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

import argparse
import os, os.path

def get_events():
    path=os.path.join(os.path.dirname(__file__), "client_secrets.json")
    if not os.path.isfile(path):
        print("Could not find file: \"%s\""%path)
        return []

    try:
        import httplib2
        from apiclient import discovery
        from oauth2client import file
        from oauth2client import client
        from oauth2client import tools
        FLOW = client.flow_from_clientsecrets(path,
                                              scope=[
                                                  'https://www.googleapis.com/auth/calendar',
                                                  'https://www.googleapis.com/auth/calendar.readonly',
                                              ],
                                              message=tools.message_if_missing(path))

    except ImportError as e:
        print("ImportError in shyshycalendar. Are google calendar libraries installed?")
        print(e)
        return []

    storage = file.Storage('app/scripts/storage.dat')
    credentials = storage.get()
    parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            parents=[tools.argparser])
    flags = parser.parse_args(list())
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
            import dateutil.parser
            datetime=dateutil.parser.parse(event["end"]["dateTime"])
            pretty_date=datetime.strftime("%A, %B %d %Y, %I:%M%p")
            pretty_date=pretty_date[:-2]+pretty_date[-2:].lower()
            event["pretty_date"]=pretty_date
        except KeyError:
            pass
        except ImportError:
            print("clean_events failed to import dateutil.parser")
    return google_events

if __name__=="__main__":
    for event in get_events():
        print(event)
