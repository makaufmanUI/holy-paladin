"""
⏩ modules/report.py
~~~~~~~~~~~~~~~~~~~~


"""
import time
import json
import datetime
import requests
import concurrent.futures
from bs4 import BeautifulSoup
from modules.enemy import Enemy
from modules.player import Player
from modules.fight import Fight, WIPEFEST_REQUEST_HEADERS




# class Report:
#     def __init__(self, report_code: str):
#         self._report_code = report_code
#         self._fight_information = self._get_fight_information()

#     def _get_fight_information(self):










class Report:
    """
    """
    def __init__(self, code: str):
        self._code = code
        self._data = self._get_data()
        self._fights = self._get_fights()
        self._cached_fight_data = {}
        self._players = self._get_players()
        self._num_players = len(self._players)
        self._enemies = self._get_enemies()
        self._num_enemies = len(self._enemies)
        self._url = f"https://classic.warcraftlogs.com/reports/{self._code}"
        for fight in self._fights:
            fight.add_report_object(self)
        

    def __repr__(self):
        return f"Report: {self._code}"
    def __str__(self):
        return f"Report: {self._code}"
    def __eq__(self, other: 'Report'):
        return self._code == other._code
    def __hash__(self):
        return hash(self._code)
    
    def _get_data(self) -> dict:
        """
        Returns
        -------
        ```
        a
        ```
        """
        url = f"https://api.wipefest.gg/report/{self._code}"
        response = requests.request("GET", url, data="", headers=WIPEFEST_REQUEST_HEADERS)
        report_data = json.loads(response.text)
        return report_data
    
    def _get_fights(self) -> list['Fight']:
        """
        Gets a list of fights in the report.

        Returns
        -------
        - List of fights, each as a `Fight` class object, in the report.
        """
        # url = f"https://api.wipefest.gg/report/{self._code}"
        # response = requests.request("GET", url, data="", headers=WIPEFEST_REQUEST_HEADERS)
        # report_data = json.loads(response.text)
        fights = []
        report_fights = self._data['fights']
        for f in report_fights:
            if f['boss'] is not None:
                fights.append(Fight(self._code, str(f['boss']), f['bossPercentage'], f['difficulty'], f['end_time'], f['fightPercentage'], str(f['id']), True if f['kill'] == 1 else False, f['name'], f['partial'], f['size'], f['start_time']))
        return fights
    
    def _get_players(self) -> list['Player']:
        """
        Gets a list of players in the report.

        Returns
        -------
        - List of players, each as a `Player` class object, in the report.
        """
        players = []
        friendlies = self._data['friendlies']
        for friend in friendlies:
            if friend['type'] in ['Warrior','Paladin','Hunter','Rogue','Priest','DeathKnight','Shaman','Mage','Warlock','Druid']:
                players.append(Player(friend['name'], friend['type'], friend['guid'], friend['id']))
        return players
    
    def _get_enemies(self) -> list['Enemy']:
        """
        Gets a list of enemy NPCs in the report.

        Returns
        -------
        - List of enemy NPCs, each as a `Enemy` class object, in the report.
        """
        enemies = []
        enemyNPCs = self._data['enemies']
        for enemy in enemyNPCs:
            enemies.append(Enemy(enemy['name'], enemy['type'], enemy['guid'], enemy['id']))
        return enemies



    @property
    def owner(self) -> str:
        """
        The owner of / account that uploaded the report.
        """
        return self._data["owner"]  # type: ignore
    
    @property
    def title(self) -> str:
        """
        The title/description of the report.
        """
        return self._data["title"]  # type: ignore
    
    @property
    def start_time(self) -> datetime.datetime:
        """
        The date/time of the first event in the report.
        """
        return datetime.datetime.fromtimestamp(self._data['start']//1000)
    
    @property
    def end_time(self) -> datetime.datetime:
        """
        The date/time of the last event in the report.
        """
        return datetime.datetime.fromtimestamp(self._data['end']//1000)

    @property
    def duration(self) -> datetime.timedelta:
        """
        The duration of the report.
        """
        return self.end_time - self.start_time

    @property
    def fights(self) -> list['Fight']:
        """
        A list of fights in the report.
        """
        return self._fights
    
    @property
    def players(self) -> list['Player']:
        """
        A list of players in the report.
        """
        return self._players
    

    def get_fight_by_report_id(self, fight_id: str) -> Fight:
        """
        Gets a fight from the report.

        Parameters
        ----------
        - `fight_id`: The report ID of the fight to get.

        Returns
        -------
        - The fight with the given ID, as a `Fight` class object.
        """
        if isinstance(fight_id, int):
            fight_id = str(fight_id)
        for fight in self._fights:
            if fight.id == fight_id:
                return fight
        raise ValueError(f"Fight with ID {fight_id} not found in report {self._code}")
    

    def get_fight_by_boss_name(self, boss_name: str) -> Fight:
        """
        Gets a fight from the report.

        Parameters
        ----------
        - `boss_name`: The name of the boss of the fight to get.

        Returns
        -------
        - The fight with the given boss name, as a `Fight` class object.
        """
        matches = []
        for fight in self._fights:
            if fight.boss_name.lower()[:4] == boss_name.lower()[:4] and fight.kill:
                matches.append(fight)
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            return max(matches, key=lambda f: f.duration)
        raise ValueError(f"Fight with boss name {boss_name} not found in report {self._code}")
    

    def get_fight_by_boss_id(self, boss_id: str) -> Fight:
        """
        Gets a fight from the report.

        Parameters
        ----------
        - `boss_id`: The ID of the boss of the fight to get.

        Returns
        -------
        - The fight with the given boss ID, as a `Fight` class object.
        """
        if isinstance(boss_id, int):
            boss_id = str(boss_id)
        for fight in self._fights:
            if fight.boss_id == boss_id:
                return fight
        raise ValueError(f"Fight with boss ID {boss_id} not found in report {self._code}")
    

    def get_player_by_name(self, name: str) -> Player:
        """
        Gets a player from the report.

        Parameters
        ----------
        - `name`: The name of the player to get.

        Returns
        -------
        - The player with the given name, as a `Player` class object.
        """
        for player in self._players:
            if player.name.lower() == name.lower():
                return player
        raise ValueError(f"Player with name {name} not found in report {self._code}")
    

    def get_player_by_guid(self, guid: str) -> Player:
        """
        Gets a player from the report.

        Parameters
        ----------
        - `guid`: The GUID of the player to get.

        Returns
        -------
        - The player with the given GUID, as a `Player` class object.
        """
        if isinstance(guid, str):
            guid = int(guid)
        for player in self._players:
            if player.guid == guid:
                return player
        raise ValueError(f"Player with GUID {guid} not found in report {self._code}")
    

    def get_player_by_report_id(self, report_id: str) -> Player:
        """
        Gets a player from the report.

        Parameters
        ----------
        - `report_id`: The report ID of the player to get.

        Returns
        -------
        - The player with the given report ID, as a `Player` class object.
        """
        if isinstance(report_id, str):
            report_id = int(report_id)
        for player in self._players:
            if player.report_id == report_id:
                return player
        raise ValueError(f"Player with report ID {report_id} not found in report {self._code}")
    

    def get_players_by_class(self, class_: str) -> list['Player']:
        """
        Gets players from the report.

        Parameters
        ----------
        - `class_`: The class of the players to get.

        Returns
        -------
        - The players with the given class, as a list of `Player` class objects.
        """
        players = []
        for player in self._players:
            if player.class_.lower() == class_.lower():
                players.append(player)
        return players
    

    def get_enemy_by_name(self, name: str) -> Enemy:
        """
        Gets an enemy NPC from the report.

        Parameters
        ----------
        - `name`: The name of the enemy to get.

        Returns
        -------
        - The enemy NPC with the given name, as an `Enemy` class object.
        """
        for enemy in self._enemies:
            if enemy.name.lower() == name.lower():
                return enemy
        raise ValueError(f"Enemy NPC with name {name} not found in report {self._code}")
    

    def get_enemy_by_guid(self, guid: str) -> Enemy:
        """
        Gets an enemy NPC from the report.

        Parameters
        ----------
        - `guid`: The GUID of the enemy to get.

        Returns
        -------
        - The enemy NPC with the given GUID, as an `Enemy` class object.
        """
        if isinstance(guid, str):
            guid = int(guid)
        for enemy in self._enemies:
            if enemy.guid == guid:
                return enemy
        raise ValueError(f"Enemy NPC with GUID {guid} not found in report {self._code}")
    

    def get_enemy_by_report_id(self, report_id: str) -> Enemy:
        """
        Gets an enemy NPC from the report.

        Parameters
        ----------
        - `report_id`: The report ID of the enemy to get.

        Returns
        -------
        - The enemy NPC with the given report ID, as an `Enemy` class object.
        """
        if isinstance(report_id, str):
            report_id = int(report_id)
        for enemy in self._enemies:
            if enemy.report_id == report_id:
                return enemy
        raise ValueError(f"Enemy NPC with report ID {report_id} not found in report {self._code}")
