# import logging
# import copy
# from decimal import Decimal
# from os import stat_result
# import numpy as np
# from operator import itemgetter
from game import Actions

import random
import math
                  
class Node:
    score = visitnumber = 0
    childList = []
    expanded = False
    lastAction = None
    
    def __init__(self, lastAction, parent):
        self.score = 0
        self.childList = []
        self.visitnumber = 1
        self.expanded = False
        self.lastAction = lastAction
        self.parent = parent
        
    def createChild(self, action):
        newNode = Node(action, self)
        self.childList.append(newNode)
        return newNode

class MCTSPlayer:
    def registerInitialState(self):
        self.root = None
        return
    
    def expand(self, node, game):
        nodeSet = actionList = []
        tempNode = node
        
        while tempNode.parent is not None:
            nodeSet.append(tempNode)
            tempNode = tempNode.parent
        
        nodeSet.reverse()
        tempState = game.curID
        
        for i in nodeSet:
            prevState = tempState
            tempState = game.generateSuccessors(i.lastAction, tempState)
            if tempState is None:
                self.backpropagate(i, game.gameEvaluation(tempState))
                return None
            elif game.isFinished(tempState):
                self.backpropagate(i, game.gameEvaluation(tempState))
                return
        
        for i in node.childList:
            actionList.append(i.lastAction)
        
        legal = game.getPossibleActions(tempState)
        # childNode = Node(None, None)
        for action in legal:
            if action not in actionList:
                childNode = node.createChild(action)
                return childNode
                break
        if len(node.childList) == len(legal):
            node.expanded = True
        
        return
                      
                
    def backpropagate(self, node, score):
        while node is not self.root:
            node.visitnumber += 1
            node.score += score
            node = node.parent

    def select(self, node):
        curMax = -1 * float('inf')
        c = 2
        bestChild = []
        for i in node.childList:
            result = (i.score/i.visitnumber) + c*math.sqrt((2*math.log(node.visitnumber))/i.visitnumber)
            if result == curMax:
                bestChild.append(i)
            if result > curMax:
                curMax = result
                bestChild = []
                bestChild.append(i)
        return bestChild[random.randint(0, len(bestChild) - 1)]
    
    def treePolicy(self, game):
        node = self.root
        while True:
            if not node.expanded:
                return self.expand(node, game)
            else:
                node = self.select(node)
                
    def defaultPolicy(self, node, game):
        nodeSet = []
        tempNode = node
        
        while tempNode.parent is not None:
            nodeSet.append(tempNode)
            tempNode = tempNode.parent
        
        nodeSet.reverse()
        tempState = game.curID
        for i in nodeSet:
            prevState = tempState
            tempState = game.generateSuccessors(i.lastAction, tempState)            
            if tempState is None:
                self.backpropagate(i, game.gameEvaluation(tempState))
                return None
            elif game.isFinished(tempState):
                self.backpropagate(i, game.gameEvaluation(tempState))
                return
        
        for j in range(0, 5):
            if not game.isFinished(tempState):
                legal = game.getPossibleActions(tempState)
                if not legal:
                    break
                prevState = tempState
                tempState = game.generateSuccessors(random.choice(legal), tempState)
                if tempState is None:
                    return None
            else:
                break
            
        return game.gameEvaluation(tempState)

    def get_action(self, game):
        bestActions = []
        rootChildList = []
        self.root = Node(None, None)
        
        while True:
            expandedNode = self.treePolicy(game)
            if expandedNode == None:
                break
            score = self.defaultPolicy(expandedNode, game)
            if score == None:
                break
            self.backpropagate(expandedNode, score)
            
        for node in self.root.childList:
            rootChildList.append(node.visitnumber)
        
        rootChildList.sort(reverse=True)
        
        for node in self.root.childList:
            if node.visitnumber == rootChildList[0]:
                bestActions.append(node.lastAction)
                
        if len(bestActions) == 0:
            return Actions.STRAIGHT
        return bestActions[random.randint(0, len(bestActions) - 1)]
