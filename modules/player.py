"""
⏩ modules/player.py
~~~~~~~~~~~~~~~~~~~~


"""





class Player:
    def __init__(self, name: str, class_: str, guid: int, report_id: int):
        self._name = name
        self._guid = guid
        self._class = class_
        self._report_id = report_id

    def __repr__(self):
        return f"<Player: {self._name} (class {self._class})>"
    
    def __str__(self):
        return f"<Player: {self._name} (class {self._class})>"
    
    @property
    def name(self) -> str:
        """
        The name of the player.
        """
        return self._name
    
    @property
    def class_(self) -> str:
        """
        The class of the player (𝗣𝗮𝗹𝗮𝗱𝗶𝗻, 𝗪𝗮𝗿𝗹𝗼𝗰𝗸, 𝗠𝗮𝗴𝗲, 𝑒𝑡𝑐.).
        """
        return self._class
    
    @property
    def report_id(self) -> int:
        """
        The player's 𝒓𝒆𝒑𝒐𝒓𝒕 ID, in the context of the report they were parsed from, that identifies them in the report.
        """
        return self._report_id
    
    @property
    def guid(self) -> int:
        """
        The player's GUID, which is unique to the player and identifies them on WCL.
        """
        return self._guid
    

