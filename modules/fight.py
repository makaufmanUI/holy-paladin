"""
⏩ modules/fight.py
~~~~~~~~~~~~~~~~~~~

TODO: Implement `eventConfigs` and `events` keys from the dictionary returned by `_get_data()`.
"""
import json
import requests
import datetime
# from modules.report import Report


WIPEFEST_REQUEST_HEADERS = {
    "authority": "api.wipefest.gg", "accept": "application/json, text/json", "accept-language": "en-US,en;q=0.9",
    "authorization": "Bearer 56c0497a5282843042fdeba04b9a661ce49832df25b3be8e5ef1efa15e19b69d", "origin": "https://www.wipefest.gg",
    "request-id": "^|232722f25a47453189ae70886c67fced.d53db694091f4b6e", "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google\"",
    "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": "\"Windows\"", "sec-fetch-dest": "empty", "sec-fetch-mode": "cors", "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36", "x-wipefest-game-version": "warcraft-classic"
}



GROUP_IDS = {
    "VoA": {
        "archavon the stone watcher": "772",  "archavon":   "772",
        "emalon the storm watcher":   "774",  "emalon":     "774",
        "koralon the flame watcher":  "776",  "koralon":    "776",
        "toravon the ice watcher":    "778",  "toravon":    "778",
    },
    "Onyxia": {
        "onyxia": "101084",  "onyxia'": "101084",  "onyxia's": "101084",  "onyxia's lair": "101084",
    },
    "Ulduar": {
        "fl":                   "744",   "flame leviathan":          "744",
        "ignis":                "745",   "ignis the furnace master": "745",
        "razorscale":           "746",
        "xt":                   "747",   "xt-002 deconstructor":     "747",   "xt-002":                "747",
        "iron council":         "748",   "the assembly of iron":     "748",   "assembly of iron":      "748",   "the iron council":       "748",
        "kologarn":             "749",
        "auriaya":              "750",
        "hodir":                "751",
        "thorim":               "752",
        "freya":                "753",
        "mimiron":              "754",
        "vezax":                "755",   "general vezax":            "755",
        "yogg":                 "756",   "yogg-saron":               "756",
        "alg":                  "757",   "algalon":                  "757",   "algalon the observer":  "757",
    },
    "ToC": {
        "beasts":               "629",   "northrend beasts":         "629",   "the northrend beasts":  "629",
        "jaraxxus":             "633",   "lord jaraxxus":            "633",
        "faction champs":       "637",   "faction champions":        "637",   "the faction champions": "637",
        "twins":                "641",   "twin val'kyr":             "641",   "the twin val'kyr":      "641",   "val'kyr twins": "641",
        "anub":                 "645",   "anub'arak":                "645",   "anubarak":              "645",
    }
}



def get_boss_id(name: str) -> str:
    """
    """
    try:
        boss_id = GROUP_IDS["Ulduar"][name.lower()]
    except KeyError:
        try:
            boss_id = GROUP_IDS["ToC"][name.lower()]
        except KeyError:
            try:
                boss_id = GROUP_IDS["VoA"][name.lower()]
            except KeyError:
                try:
                    boss_id = GROUP_IDS["Onyxia"][name.lower()]
                except KeyError:
                    raise KeyError(f"Boss name '{name}' not found.")
    return boss_id






class Fight:
    """
    """
    def __init__(self, 
                 report_code: str, boss_id: str|int, boss_percentage: int|float,
                 difficulty: int, end_time: int, fight_percentage: int|float, id: int|str,
                 kill: bool, boss_name: str, partial: int, size: int, start_time: int):
        self._report_code = report_code
        self._boss_id = str(boss_id) if isinstance(boss_id, int) else boss_id
        self._boss_percentage = boss_percentage
        self._difficulty = difficulty
        self._end_time = datetime.datetime.fromtimestamp(end_time//1000)
        self._fight_percentage = fight_percentage
        self._id = str(id) if isinstance(id, int) else id
        self._kill = kill
        self._boss_name = boss_name
        self._partial = partial
        self._size = size
        self._start_time = datetime.datetime.fromtimestamp(start_time//1000)
        
        self._data = self._get_data()
        # self._report_object: Report = None  # type: ignore

    def __repr__(self):
        return f"<Fight: {self._boss_name} (reportID {self._id}, bossID {self._boss_id})>"
    
    def __str__(self):
        return f"<Fight: {self._boss_name} (reportID {self._id}, bossID {self._boss_id})>"
    
    def __eq__(self, other: 'Fight'):
        return self._id == other._id
    
    def __hash__(self):
        return hash(self._id)
    

    @property
    def report_code(self) -> str:
        """
        The report code for the report this fight is from.
        """
        return self._report_code
    
    @property
    def boss_id(self) -> str:
        """
        The ID of the boss, as it appears on WCL, 𝒏𝒐𝒕 the fight ID.
        """
        return self._boss_id
    
    @property
    def boss_percentage(self) -> int|float:
        """
        Not sure what this is.
        """
        return self._boss_percentage
    
    @property
    def difficulty(self) -> int:
        """
        Not sure what this is.
        """
        return self._difficulty
    
    @property
    def end_time(self) -> datetime.datetime:
        """
        The end time of the fight, as a `datetime` object.
        """
        return self._end_time
    
    @property
    def fight_percentage(self) -> int|float:
        """
        Not sure what this is.
        """
        return self._fight_percentage
    
    @property
    def id(self, as_int: bool=False) -> int|str:
        """
        The ID of the fight, with respect to the report, 𝒏𝒐𝒕 what identifies the boss.
        """
        return int(self._id) if as_int else self._id

    @property
    def kill(self) -> bool:
        """
        Whether the fight was a kill or not.
        """
        return self._kill

    @property
    def boss_name(self) -> str:
        """
        The name of the boss.
        """
        return self._boss_name
    
    @property
    def partial(self) -> int:
        """
        Not sure what this is.
        """
        return self._partial
    
    @property
    def size(self) -> int:
        """
        The size of the raid group.
        """
        return self._size
    
    @property
    def start_time(self) -> datetime.datetime:
        """
        The start time of the fight, as a `datetime` object.
        """
        return self._start_time
    
    @property
    def duration(self) -> datetime.timedelta:
        """
        The duration of the fight, as a `timedelta` object.
        """
        return self.end_time - self.start_time
    
    @property
    def raid_info(self) -> dict:
        """
        Information about the raid composition.
        """
        return self._data["raid"]   # type: ignore
    

    def _get_data(self) -> dict[str,
            float |
            dict[ str,int|str|bool ] |
            list[ dict[str,int|str] ] |
            list[ dict[str,list|str|bool|int] ] |
            dict[ str,float|list[dict[str,int|float|str|dict[str,int|str|bool]]] ] |
            dict[ str,int|list[dict[str,int|str|bool]]|str|list[dict[str,int|str]] ] |
            list[ dict[str,int|float|dict[str,int|str]|list[dict[str,bool|float|str|int]]] ] |
            list[ dict[str,bool|str|list[int]|dict[str,list[str]|str|dict[str,list[int]]]|list[str]] ] |
            list[ dict[str,bool|list[dict[str,bool|str]]|dict[str,bool]|str|dict[str,bool|float|str]] ] |
            list[ dict[str,list[dict[str,int|list[dict[str,int|float|str]]]]|bool|list[dict[str,int|float|str]]|list|dict[str,int|str]|str|dict[str,int|list[dict[str,int|dict[str,int|str|list[dict[str,int]]]]]|list[int]|list[dict[str,int|str]]]|float] ]
        ]:
        """
        Gets raw data for the fight from the 𝘄𝗶𝗽𝗲𝗳𝗲𝘀𝘁.𝗴𝗴 API.

        The data has the following keys:
        - `abilities`
        - `eventConfigs`
        - `events`
        - `info`
        - `insightConfigs`
        - `insights`
        - `playerValues`
        - `percentile`
        - `raid`
        - `report`
        """
        # if len(self._data) == 0:
        url = f"https://api.wipefest.gg/report/{self._report_code}/fight/{self._id}"
        querystring = {"group":self._boss_id,"markupFormat":"Markup","insightsOnly":"false"}
        response = requests.request("GET", url, data="", headers=WIPEFEST_REQUEST_HEADERS, params=querystring)
        data = json.loads(response.text)
        self._data = data
        return self._data


    @property
    def percentile(self) -> float:
        """
        The raid as a whole's performance, as a percentile, in the fight.
        """
        return self._data["percentile"] # type: ignore


    @property
    def start_timestamp(self) -> int:
        """
        The timestamp of the start of the fight (as the number of milliseconds since the beginning of the report).
        """
        # print(self._data)
        try: return self._data['info']['start_time'] # type: ignore
        except: return 0
    
    @property
    def end_timestamp(self) -> int:
        """
        The timestamp of the end of the fight (as the number of milliseconds since the beginning of the report).
        """
        try: return self._data['info']['end_time'] # type: ignore
        except: return 999999999999
    

    def add_report_object(self, report):
        """
        Adds a reference to the `Report` object that this fight is from.
        """
        self._report_object = report


    def get_fight_duration(self) -> int:
        """
        Gets the duration of the fight, as an `int`.
        """
        return self.duration.seconds
        # count = 999999
        # events = []
        # timestamp = 0
        # while count != 0:
        #     url = f"https://classic.warcraftlogs.com/reports/summary-events/{self._report_code}/1/{timestamp}/9999999999/0/0/Any/0/-1.0.-1.-1/0"
        #     headers = {
        #         "authority": "classic.warcraftlogs.com",
        #         "accept": "application/json, text/javascript, */*; q=0.01",
        #         "accept-language": "en-US,en;q=0.9",
        #         "cookie": "usprivacy=1---; ad_clicker=false;",
        #         "referer": "https://classic.warcraftlogs.com/reports/J6yR7gnD4awCYztX",
        #         "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google\"",
        #         "sec-ch-ua-mobile": "?0",
        #         "sec-ch-ua-platform": "\"Windows\"",
        #         "sec-fetch-dest": "empty",
        #         "sec-fetch-mode": "cors",
        #         "sec-fetch-site": "same-origin",
        #         "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        #         "x-requested-with": "XMLHttpRequest"
        #     }
        #     response = requests.request("GET", url, headers=headers)
        #     data = json.loads(response.text)
        #     count = data['count']
        #     events += data['events']
        #     timestamp = events[-1]['timestamp']
        # return events[-1]['timestamp'] - events[0]['timestamp']