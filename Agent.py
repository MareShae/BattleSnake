from tAssist import *
from VEnv import VEnv

Main = 'genome.txt'
Genome = ReadGenome(Main)
class Agent:
    def __init__(self, name, envShape, body):
        # AGENT DETAILS
        self.Name = name
        self.width, self.height = envShape
        self.body, self.head = body, body[0]
        self.Network = NeuralNetwork(Genome)  #
        self.hypotenuse = Divide(Add(envShape), math.sqrt(2))  # Longest possible distance

        # ACTIVITY DETAILS
        self.orientation = [-1, 0]
        self.stamina, self.holdStamina = 1, 1
        self.angles = [0, 15, 30, 45, 60, 75,
                       90, 105, 120, 135, 150,
                       -150, -135, -120, -105,
                       -90, -75, -60, -45, -30, -15]  # Octagon

        # MEMORY
        self.Snake = {self.Name: -0.20000}
        self.Food, self.Boundary = -0.1, -0.3

    def Update(self, body, stamina):
        self.stamina = stamina
        self.body, self.head = body, body[0]

    def CheckBoard(self, YXAbs, Board):
        Food, Snakes = Board['food'], Board['snakes']
        if YXAbs in Food:
            return self.Food
        for name in Snakes:
            if YXAbs in Snakes[name]:
                return self.Snake[name]
        return None

    def Move(self, Board: dict) -> str:
        # NETWORK:
        NeuralInput = self.See(Board) + [self.stamina, self.holdStamina]
        self.Network.ForwardPass(NeuralInput)

        # STAMINA:
        self.holdStamina = self.stamina

        # MOVEMENTS:
        confidence = RoundList(self.Network.ReadOutput())
        if confidence == [0, 1]:
            self.orientation = RoundList(RotMat(90, self.orientation))  # ClockWise: 90 deg
        elif confidence == [1, 0]:
            self.orientation = RoundList(RotMat(-90, self.orientation))  # ClockWise: -90 deg

        if self.orientation == [-1, 0]:
            return 'up'  # Forward/Repeat: 0 deg
        elif self.orientation == [0, 1]:
            return 'right'  # ClockWise: 90 deg
        elif self.orientation == [0, -1]:
            return 'left'  # ClockWise: -90 deg
        elif self.orientation == [1, 0]:
            return 'down'  # ClockWise: 180 deg

        return response

    def See(self, Board: dict) -> list:
        # Searches VEnvironment for:
        vFeat, vDist = [], []  # Features and Their distance
        YPov, XPov = self.head

        for theta in self.angles:
            y, x = YPov, XPov  # ...
            route = RotMat(theta, self.orientation)  # ...
            y, x = Add([y, route[0]]), Add([x, route[1]])  # ...
            YAbs, XAbs = Round(y), Round(x)  # Look in 21 directions
            while True:
                dist = abs(YPov - YAbs) + abs(XAbs - XPov)
                if not 0 <= YAbs < self.height or not 0 <= XAbs < self.width:
                    vDist.append(Divide(dist, self.hypotenuse))
                    vFeat.append(self.Boundary)
                    break
                tile = self.CheckBoard([YAbs, XAbs], Board)
                if tile:
                    vDist.append(Divide(dist, self.hypotenuse))
                    vFeat.append(tile)
                    break
                y, x = Add([y, route[0]]), Add([x, route[1]])  # ...
                YAbs, XAbs = Round(y), Round(x)  # and Keep looking

        return vFeat + vDist
