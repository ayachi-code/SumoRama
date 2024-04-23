

class GameState:
    def __init__(self, currentState):
        self.currentState = currentState
    def getCurrentState(self):
        return self.currentState
    def setCurrentState(self, newState):
        self.currentState = newState