# MAIN
import os
import json
import bottle
from bottle import HTTPResponse
# SUB
from tAssist import *
from VEnv import VEnv
from Agent import Agent

Name = 'Jinx'
Author = 'MareShae'
SnakeAgent = None
LogFile = 'Log.txt'


def DList2List(DList: list[dict]):
    List = []
    for Dict in DList:
        List += [[Dict['y'], Dict['x']]]
    return List


#    # # # # # # # #  MAIN-PROCESS # # # # # # # # # # # # # # # # # # # # #
@bottle.route("/")
def index():
    return "New Game. WHO DIS!?"


@bottle.get("/")
def ping():
    """
    Used by the BattleSnake Engine to make sure your snake is still working.
    """
    response = {"apiversion": '1', "version": '7',
                "head": 'evil', "tail": 'bwc-flake',
                "author": Author, "color": '#736CCB'}
    return HTTPResponse(status=200, body=json.dumps(response),
                        headers={"Content-Type": "application/json"})


@bottle.post("/start")
def start():
    global SnakeAgent
    """
    Called every time a new BattleSnake game starts and your snake is in it.
    Your response will control how your snake is displayed on the board.
    """
    # START
    START = bottle.request.json

    # Create Agent
    Board = START['board']
    Body = DList2List(START['you']['body'])
    Shape = (Board['height'], Board['width'])
    SnakeAgent = Agent(Name, Shape, Body)

    # Snake Vision
    for snake in Board['snakes']:
        if snake['name'] != SnakeAgent.Name:
            SnakeAgent.Snake[snake['name']] = Random(-0.2, -0.29)

    # Print
    print('START:', START['game']['id'], '\n',
          'Number of Snakes: ', len(Board['snakes']))

    return HTTPResponse(status=200)


@bottle.post("/move")
def move():
    """
    Called when the BattleSnake Engine needs to know your next move.
    The data parameter will contain information about the board.
    Your response must include your move of up, down, left, or right.
    """
    # MOVE
    MOVE = bottle.request.json
    # print("MOVE:", MOVE)

    # Parameters
    Snakes = {}
    Board = MOVE['board']
    Food = DList2List(Board['food'])
    for snake in Board['snakes']:
        Snakes[snake['name']] = DList2List(snake['body'])

    # Update Snake:
    SnakeAgent.Update(DList2List(MOVE['you']['body']),
                      Divide(MOVE['you']['health'], 100))

    # Move
    Tiles = {'food': Food, 'snakes': Snakes}
    Move = SnakeAgent.Move(Tiles)

    # Shouts are not displayed on the game board.
    # Shouts are messages sent to all the other snakes in the game.
    SHOUT = ["Sk Sk Sk!"]
    RESPONSE = {"move": Move, "shout": Choice(SHOUT)}

    # DUMPGlobal()  # Convert to JSON
    # RETURN RESPONSE
    return HTTPResponse(status=200, body=json.dumps(RESPONSE),
                        headers={"Content-Type": "application/json"})


@bottle.post("/end")
def end():
    """
    Called every time a game with your snake in it ends.
    """
    END = bottle.request.json
    print('END: ', END['game']['id'], '\n',
          'Turn: ', END['turn'], '\n',
          'Health: ', END['you']['health'], '\n',
          'Snakes Left: ', len(END['board']['snakes']))

    return HTTPResponse(status=200)


def main():
    bottle.run(
        application,
        host=os.getenv("IP", "0.0.0.0"),
        port=os.getenv("PORT", "8080"),
        debug=os.getenv("DEBUG", True),
    )


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == "__main__":
    main()
