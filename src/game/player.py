# Add class for player, e.g name, color, host/joiner, mode; use pickle to send object over socket

class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.wins = 0

    def getWins(self):
        return self.wins
    
    def addWin(self):
        self.wins += 1

    def getName(self):
        return self.name
    
    def getColor(self):
        return self.color
    
    def setName(self, newName):
        self.name = newName
    
    def setColor(self, newColor):
        self.color = newColor
