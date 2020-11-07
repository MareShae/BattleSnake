from tAssist import *

class VEnv:
    def __init__(self, shape):
        # BOARD INFO
        self.envRecord = []  # Record the state of the environment
        self.width, self.height = shape  # Size of the environment
        self.env = numpy.zeros(shape=[self.height, self.width])  # Constructing the environment
        self.hypotenuse = Divide(self.width + self.height, math.sqrt(2))  # Longest possible distance

        # BOARD POINTS
        self.empty = []  # The empty tiles
        self.turns, self.score = 0, 0
        for y in range(self.height):
            for x in range(self.width):
                self.empty.append((y, x))
        self.food = []  # Where food is spawned

    def show(self):
        print(self.env)

    def record(self):
        self.envRecord += [self.env]

    def reset(self):
        self.turns = 0
        self.score = 0
        self.empty = []  # The empty tiles
        for y in range(self.height):
            for x in range(self.width):
                self.empty.append((y, x))
        self.food = []  # Where food is spawned
        self.envRecord = []  # Record the state of the environment
        self.env = numpy.zeros(shape=[self.height, self.width])  # Constructing the environment

    def spawnFood(self):
        for _ in range(FoodLimit - len(self.food)):
            tile = Choice(self.empty)
            self.env[tile] = Food
            self.food.append(tile)
            self.empty.remove(tile)

    def resetTile(self, tile):
        if self.env[tile] == Food:
            self.food.remove(tile)
        self.env[tile] = Empty
        self.empty.append(tile)

    def setTile(self, tile, feature):
        if tile in self.empty:
            self.empty.remove(tile)
        self.env[tile] = feature
