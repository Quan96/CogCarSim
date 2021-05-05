from game import GameGraph, Actions, Grid
import random

gameGraph = GameGraph(blob_score=10)
grid = Grid(-13, 0, 13, 100, [1000, 13], 0, 0, 0)
gameGraph.expand(root_id=0, y=0, x=0, max_depth=20, velocity=1.6, grid=grid)
while True:
    gameGraph.getAvailable(gameGraph.curID)
    print(len(gameGraph.available))
    gameGraph.doMove(Actions.STRAIGHT, gameGraph.curID)
    if len(gameGraph.available) == 0:
        # # print(gameGraph.curID)
        # # print(gameGraph.getNodeInfo(gameGraph.curID))
        # y, x = gameGraph.getNodeGridPosition(gameGraph.curID)
        # # print(y, x)
        # gameGraph.expand(root_id=gameGraph.curID, y=y, x=x, max_depth=5, velocity=2, grid=grid)
        # i += 1
        break

# gameGraph.printGraph()