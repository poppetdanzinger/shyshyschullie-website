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

import argparse,datetime
import os, os.path, urllib.parse

"try to import third party packages, but don't crash whole site if something is missing"
try:
    import httplib2
    from apiclient import discovery
    from oauth2client import file
    from oauth2client import client
    from oauth2client import tools
    import_error=0
except ImportError as e:
    import_error=e


def get_flow(verbose=0):
    "returns a configured google api flow object"
    secrets=os.path.join(os.path.dirname(__file__), "client_secrets.json")
    if not os.path.isfile(secrets):
        if verbose:
            print("Could not find file: \"%s\""%secrets)
        return 0

    flow = client.flow_from_clientsecrets(secrets,
                                          scope=[
                                              'https://www.googleapis.com/auth/calendar',
                                              'https://www.googleapis.com/auth/calendar.readonly',
                                          ],
                                          message=tools.message_if_missing(secrets))
    return flow

def get_service(verbose=0):
    "returns a google api service object, authenticated and ready to go"
    storage_path=os.path.join(os.path.dirname(__file__), "storage.dat")
    if not os.path.isfile(storage_path):
        storage_path="app/sripts/storage.dat"
    if not os.path.isfile(storage_path):
        if verbose:
            print("Could not find file: \"%s\""%storage_path)
        return 0
    storage = file.Storage(storage_path)
    credentials = storage.get()
    parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            parents=[tools.argparser])
    flags = parser.parse_args(list())
    if credentials is None or credentials.invalid:
        flow=get_flow()
        credentials = tools.run_flow(flow, storage, flags)

    http = httplib2.Http()
    http = credentials.authorize(http)
    service = discovery.build('calendar', 'v3', http=http)
    return service

def get_events(verbose=0):
    if import_error:
        if verbose:
            print(str(import_error))
        return []

    service=get_service(verbose=verbose)
    if not service:
        if verbose:
            print("Failed to get service.")
        return []

    events=[]
    page_token = None
    try:
        while True:
            service_events = service.events().list(calendarId='primary', pageToken=page_token).execute()
            for event in service_events['items']:
                events.append(event)
                if verbose:
                    print(event)
            page_token = service_events.get('nextPageToken')
            if not page_token:
                break
    except client.AccessTokenRefreshError:
        if verbose:
            print ("shyshycalendar.py fail: The credentials have been revoked or expired, please re-run"
                   "the application to re-authorize")
        return []

    events=get_clean_events(events,exclude_past=0)
    events=sorted(events,key=lambda event: event["datetime"])
    return events

def add_recurring_events(events,days_into_future=30):
    "recurring events only appear once. this makes copies of those events"
    for event in events:
        pass

def get_clean_events(events,exclude_past=0):
    "adds entries to each event and excludes events that happened more than 12 hours ago"
    import dateutil.parser
    cutoff=datetime.datetime.now()+datetime.timedelta(hours=12)

    for event in events:
        if exclude_past and event<cutoff:
            continue
        dt=dateutil.parser.parse(event["end"]["dateTime"])
        event["datetime"]=dt

        pretty_date=dt.strftime("%A, %B %d %Y, %I:%M%p")
        pretty_date=pretty_date[:-2]+pretty_date[-2:].lower()
        event["pretty_date"]=pretty_date
        event["url_safe_location"]=urllib.parse.quote(event["location"])

    return events

if __name__=="__main__":
    for event in get_events():
        print(event)
