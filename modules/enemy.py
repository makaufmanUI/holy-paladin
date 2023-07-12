"""
⏩ modules/enemy.py
~~~~~~~~~~~~~~~~~~~


"""




class Enemy:
    def __init__(self, name: str, type_: str, guid: int, report_id: int):
        self._name = name
        self._guid = guid
        self._type = type_
        self._report_id = report_id

    def __repr__(self):
        return f"<Enemy: {self._name} (type {self._type})>"
    
    def __str__(self):
        return f"<Enemy: {self._name} (type {self._type})>"
    
    @property
    def name(self) -> str:
        """
        The name of the enemy unit.
        """
        return self._name
    
    @property
    def type_(self) -> str:
        """
        The type of the enemy unit (𝒆.𝒈. NPC).
        """
        return self._type
    
    @property
    def report_id(self) -> int:
        """
        The enemy unit's 𝒓𝒆𝒑𝒐𝒓𝒕 ID, in the context of the report it was parsed from, that identifies it in the report.
        """
        return self._report_id
    
    @property
    def guid(self) -> int:
        """
        The enemy unit's GUID, which is unique to the unit and is used to classify bosses, etc.
        """
        return self._guid
    



