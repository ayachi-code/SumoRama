

class GameState:
    def __init__(self, currentState):
        self.currentState = currentState
        self.playerType = None # Stores if the client is server or client at the beginning none
        self.socket = None
    def getCurrentState(self):
        return self.currentState
    def setCurrentState(self, newState):
        self.currentState = newState
    def getPlayerType(self):
        return self.playerType
    def setPlayerType(self, newRole):
        self.playerType = newRole
    def getSocket(self):
        return self.socket
    def setSocket(self, newSocket):
        self.socket = newSocket