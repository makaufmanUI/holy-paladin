"""
source.py
~~~~~~~~~


"""
import os
import json
import datetime
import requests
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from rich.progress import track
from rich.traceback import install
from rich import print as richprint

install()
os.system("cls")
print("")

def rprint(*args, **kwargs):
    """Prints to console with time indicator."""
    richprint(f"[bold]>>[/bold]", *args, **kwargs)

from modules.fight import Fight
from modules.report import Report
from modules.player import Player

HEALING_TRANCE_SPELLID = 60513

WCL_BASE_URL = "https://classic.warcraftlogs.com/reports"

WCL_REQUEST_HEADERS = lambda fight: {
    "referer": f"https://classic.warcraftlogs.com/reports/{fight.report_code}",
    "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google\"",
    "authority": "classic.warcraftlogs.com", "x-requested-with": "XMLHttpRequest",
    "accept": "application/json, text/javascript, */*; q=0.01", "accept-language": "en-US,en;q=0.9",
    "cookie": "usprivacy=1---; ad_clicker=false; cookieconsent_status=dismiss; isAdBlocking=false;",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": "\"Windows\"", "sec-fetch-dest": "empty", "sec-fetch-mode": "cors", "sec-fetch-site": "same-origin"
}

WCL_REQUEST_URL = lambda endpoint, report_code, fight_id, start, end: f"{WCL_BASE_URL}/{endpoint}/{report_code}/{fight_id}/{start}/{end}"



def get_healing_trance_events(fight: Fight, player: Player) -> list[dict]:
    url = f"{WCL_REQUEST_URL('auras-events',fight.report_code,fight.id,fight.start_timestamp,fight.end_timestamp)}" + \
          f"/buffs/{HEALING_TRANCE_SPELLID}/{player.report_id}/{player.report_id}/0/0/source/0/-1.0.-1.-1/0/Any/Any/0"
    response = requests.request("GET", url, headers=WCL_REQUEST_HEADERS(fight))
    data = json.loads(response.text)
    return [{
            "timestamp": e["timestamp"],
            "timestamp_relative": e["timestamp"] - fight.start_timestamp,
            "time": datetime.timedelta(milliseconds=e["timestamp"] - fight.start_timestamp),
            "type": e["type"],
        } for e in [data["events"][i] for i in range(len(data["events"])) if len(data["events"][i]) > 0]]





def get_spell_cast_events(fight: Fight, player: Player) -> list[dict]:
    url = f"{WCL_REQUEST_URL('casts-graph',fight.report_code,fight.id,fight.start_timestamp,fight.end_timestamp)}" + \
          f"/{player.report_id}/0/Any/0/0/Any/0/ability/0/-1.0.-1.-1/0/2"
    response = requests.request("GET", url, headers=WCL_REQUEST_HEADERS(fight))
    data = json.loads(response.text)
    series = data['series']
    for s in series:
        for i in range(len(s['events'])):
            for j in range(len(s['events'][i])):
                if 'timestamp' in s['events'][i][j]:
                    s['events'][i][j]['timestamp_relative'] = s['events'][i][j]['timestamp'] - fight.start_timestamp
                    s['events'][i][j]['time'] = datetime.timedelta(milliseconds=s['events'][i][j]['timestamp'] - fight.start_timestamp)
    data = []
    for s in series:
        events = []
        for i in range(len(s['events'])):
            for j in range(len(s['events'][i])):
                if 'type' in s['events'][i][j]:
                    if s['events'][i][j]['type'] == 'cast':
                        events.append({
                            "timestamp": s['events'][i][j]['timestamp'],
                            "timestamp_relative": s['events'][i][j]['timestamp'] - fight.start_timestamp,
                            "time": datetime.timedelta(milliseconds=s['events'][i][j]['timestamp'] - fight.start_timestamp),
                            "ability": { "name": s['name'], "spell_id": s["guid"] }
                        })
        data.append({ "name": s['name'], "spell_id": s["guid"], "events": events })
    events = []
    for d in data:
        for e in d['events']:
            events.append(e)
    events = sorted(events, key=lambda k: k['timestamp'])
    return events





def get_mana_change_events(fight: Fight, player: Player) -> list[dict]:
    url = f"{WCL_REQUEST_URL('resources-graph',fight.report_code,fight.id,fight.start_timestamp,fight.end_timestamp)}" + \
          f"/100/0/{player.report_id}/0/-1.0.-1.-1/0/Any"
    response = requests.request("GET", url, headers=WCL_REQUEST_HEADERS(fight))
    data = json.loads(response.text)
    data = data['series'][0]
    data2 = []
    for i in range(len(data['currentValues'])):
        if 'timestamp' in data['events'][i]:
            data2.append({
                "timestamp": data['events'][i]['timestamp'],
                "timestamp_relative": data['events'][i]['timestamp'] - fight.start_timestamp,
                "time": datetime.timedelta(milliseconds=data['events'][i]['timestamp'] - fight.start_timestamp),
                "currentValue": data['currentValues'][i],
                "event": data['events'][i],
                "ability": data['events'][i]['ability'],
                "spent": data['currentValues'][i-1] - data['currentValues'][i] if i > 0 else 0
            })
    return data2
    
    # data = json.loads(response.text)
    # data = data['series'][0]
    # return [{
    #     "timestamp": data['events'][i]['timestamp'],
    #     "timestamp_relative": data['events'][i]['timestamp'] - fight.start_timestamp,
    #     "time": datetime.timedelta(milliseconds=data['events'][i]['timestamp'] - data.start_timestamp),
    #     "currentValue": data['currentValues'][i],
    #     "event": data['events'][i],
    #     "ability": data['events'][i]['ability'],
    #     "spent": data['currentValues'][i-1] - data['currentValues'][i] if i > 0 else 0
    # } for i in range(len(data['currentValues'])) if 'timestamp' in data['events'][i]]













# if __name__ == "__main__":
#     pass
