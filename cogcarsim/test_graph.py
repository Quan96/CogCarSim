from game import GameGraph, Actions
import random

gameGraph = GameGraph(blob_score=10)
gameGraph.expand(root_id=0, y=0, x=0, max_depth=3, velocity=1.6)
i = 0
# print(gameGraph.curID)
# gameGraph.getAvailable()
# print(gameGraph.available)
# gameGraph.doMove(Actions.STRAIGHT)
# print(gameGraph.curID)
# gameGraph.getAvailable()
# print(gameGraph.available)
# gameGraph.setNodeWeight(1, 5)
# print(gameGraph.getNodeInfo(1))
# # gameGraph.doMove(Actions.STRAIGHT)
# # print(gameGraph.curID)
# # gameGraph.getAvailable()
# # print(gameGraph.available)
# # gameGraph.doMove(Actions.RIGHT)
# # print(gameGraph.curID)
# gameGraph.printGraph()
while i != 2:
    gameGraph.doMove(Actions.STRAIGHT)
    gameGraph.getAvailable()
    if len(gameGraph.available) == 0:
        # print(gameGraph.curID)
        # print(gameGraph.getNodeInfo(gameGraph.curID))
        y, x = gameGraph.getNodeGridPosition(gameGraph.curID)
        # print(y, x)
        gameGraph.expand(root_id=gameGraph.curID, y=y, x=x, max_depth=3, velocity=2)
        i += 1

gameGraph.printGraph()