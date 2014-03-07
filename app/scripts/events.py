
import datetime, urllib.parse

dateformat="yyyy/mm/dd"

def get_events():
    with open("app/static/content/events.csv","r",encoding="utf-8") as f:
        data=f.read()

    lines=data.split("\n")
    columns=lines[0].split("\t")
    events=[]
    for line in lines[1:]:
        if not line.strip():
            continue

        event=get_event(line,columns)
        events.append(event)

    events=get_sorted_events(events)
    return events

def get_sorted_events(events):
    events=[e for e in events if dateformat in e]
    meta=[(e[dateformat],e) for e in events]
    meta.sort()
    return [item[1] for item in meta]

def get_event(line,columns):
    split=line.split("\t")

    event={}
    for i,item in enumerate(split):
        if not item.strip():
            continue
        event[columns[i].replace(" ","").lower()]=item.strip()

        if dateformat in event:
            d=get_formatted_date(event[dateformat])
            if d:
                event["date"]=d
        if "location" in event:
            event["url_safe_location"]=urllib.parse.quote(event["location"])

    return event

def get_formatted_date(datestring):
    split=datestring.split("/")
    try:
        year=int(split[0])
        month=int(split[1])
        day=int(split[2])
    except:
        return 0

    d=datetime.date(year,month,day)
    return d.strftime("%A %d. %B %Y")
