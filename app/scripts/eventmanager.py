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

import argparse,datetime,copy
import os, os.path, urllib.parse, sys, traceback

"try to import third party packages, but don't crash whole site if something is missing"
try:
    import httplib2
    from apiclient import discovery
    from oauth2client import file
    from oauth2client import client
    from oauth2client import tools
    import_errors=0
except ImportError as e:
    exc_type, exc_value, exc_traceback = sys.exc_info()

    import_errors=[str(e)]
    import_errors.extend(traceback.format_tb(exc_traceback))
    #import_errors.append("sys.path:")
    #import_errors.extend(["\t"+path for path in sys.path])

class EventManager():
    def __init__(self,verbose=0):
        self.verbose=verbose
        self.events=[]
        self.error_msgs=[]

        if import_errors:
            self.error_msgs=import_errors
            if verbose:
                print("\n".join(self.error_msgs))
            return

        self.set_service(verbose=verbose)
        if not self.service:
            if self.verbose:
                print("Failed to set service.")
            return

        self.set_events()
        self.clean_events()
        self.add_recurring_events()
        self.time_filter_events()
        self.sort_events()

    def set_events(self):
        self.events=[]
        page_token = None
        try:
            while True:
                service_events = self.service.events().list(calendarId='primary', pageToken=page_token).execute()
                for event in service_events['items']:
                    self.events.append(event)
                    if self.verbose:
                        print("EVENT:")
                        print(event)
                page_token = service_events.get('nextPageToken')
                if not page_token:
                    break
        except client.AccessTokenRefreshError:
            if self.verbose:
                print ("shyshycalendar.py fail: The credentials have been revoked or expired, please re-run"
                       "the application to re-authorize")

    def sort_events(self):
        self.events=sorted(self.events,key=lambda event: event["datetime"])

    def time_filter_events(self):
        cutoff=get_min_cutoff()

        self.events=[event for event in self.events if event["datetime"]>cutoff]

    def add_recurring_events(self,days_into_future=30):
        "recurring events only appear once. this makes copies of those events"
        min_cutoff=get_min_cutoff()
        max_cutoff=datetime.datetime.now()+datetime.timedelta(days=days_into_future)

        for event in self.events[:]:
            if ("recurrence" not in event or
                not len(event["recurrence"]) or
                "FREQ=WEEKLY" not in event["recurrence"][0]):
                continue

            new_event=0
            while not new_event or new_event["datetime"]<max_cutoff:
                if new_event:
                    self.events.append(new_event)
                else:
                    new_event=copy.deepcopy(event)
                new_event=copy.deepcopy(new_event)
                new_event["datetime"] += datetime.timedelta(days=7)
                set_pretty_date(new_event)
                if new_event["datetime"]<min_cutoff:
                    continue

    def clean_events(self):
        "adds entries to each event and exclude events that happened more than 12 hours ago"
        import dateutil.parser

        for event in self.events[:]:
            try:
                dt=dateutil.parser.parse(event["start"]["dateTime"])
                dt=dt.replace(tzinfo=None)
                event["datetime"]=dt
                set_pretty_date(event)
                event["url_safe_location"]=urllib.parse.quote(event["location"])
            except KeyError as e:
                self.events.remove(event)
                if self.verbose:
                    print("\nRemoved event because it failed to clean:")
                    print(event)


    def get_flow(self,verbose=0):
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

    def set_service(self,verbose=0):
        "sets self.service to a google api service object, authenticated and ready to go"
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
            flow=self.get_flow()
            credentials = tools.run_flow(flow, storage, flags)

        http = httplib2.Http()
        http = credentials.authorize(http)
        self.service = discovery.build('calendar', 'v3', http=http)

def get_min_cutoff():
    "no date earlier than this cutoff should ever appear in any list"
    return datetime.datetime.now()-datetime.timedelta(hours=12)


def set_pretty_date(event):
    "requires the 'datetime' key in event"
    dt=event["datetime"]
    pretty_date=dt.strftime("%A, %B %d %Y, %I:%M%p")
    pretty_date=pretty_date[:-2]+pretty_date[-2:].lower()
    event["pretty_date"]=pretty_date

if __name__=="__main__":
    for event in get_events():
        print(event)
