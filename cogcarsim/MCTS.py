# import logging
# import copy
from decimal import Decimal
from os import stat_result
import numpy as np
from operator import itemgetter
from game import Actions

import random
import math

# class Node(object):
#     def __init__(self, state, parent, actionList, children, visited, score, action):
#         self.state = state
#         self.parent = parent
#         self.actionList = actionList
#         self.children = children
#         self.visited = visited
#         self.score = score
#         self.action = action
    
# class MCTSPlayer(object):
#     # total = 0
#     def registerInitialState(self):
#         self.root = None
#         return
    
#     def expand(self, node, game):
#         len_actionList = len(node.actionList)
#         if len_actionList == 0:
#             return
#         r = random.randint(0, len_actionList - 1)
#         random_choice = node.actionList[r]
#         node.actionList.pop(r)
#         child_state = game.generateSuccessors(random_choice, node.state[0])
#         # child_state = game.getAvailable(node.state[0])
#         if game.isFinished(child_state):
#             child_actionList = []
#         else:
#             child_actionList = game.getPossibleActions(child_state)
#         s = node.state
#         s.append(child_state)
#         # s.doMove(random_choice)
#         child = Node(s, node, child_actionList, [], 1, 1, random_choice)
#         child.score = self.rollout(child, child_state, game)
        
#         self.update(child, child.score)
#         node.children.append(child)
#         return
    
#     def rollout(self, node, current_state, game):
#         possible = node.actionList
#         # maximum_value = -1 * float('inf')
#         for i in range(5):
#             if len(possible) > 0:
#                 current_state = game.generateSuccessors(possible[random.randint(0, len(possible)-1)], current_state)

#             if current_state == None or game.isFinished(current_state):
#                 return 0
#             else:
#                 possible = game.getPossibleActions(current_state)
#                 score = game.gameEvaluation(current_state)
#         return score
    
#     def update(self, node, score):
#         while node.parent is not None:
#             node.visited += 1
#             node.score += score
#             node = node.parent
    
#     def select(self, node):
#         c = 2
#         maximum_value= -1 * float('inf')
#         # if len(node.children) > 0:
#         for i in node.children:
#             val = (i.score/i.visited) + c * math.sqrt(2*math.log(node.visited)/i.visited)
#             if abs(val) > maximum_value:
#                 maximum_value = abs(val)
#                 selected_child = i
#         return selected_child
#         # return None
        
#     def get_action(self, game):
#         # state_copy = copy.deepcopy(state)
#         node = Node([game.curID], None, game.getPossibleActions(game.curID), [], 1, 0, Actions.STRAIGHT)
#         root = node
#         flag = 0
        
#         while True:
#             if node is None:
#                 # print(0)
#                 flag = 1
#                 break
#             if len(node.actionList) > 0:
#                 # print(1)
#                 while len(node.actionList) > 0:
#                     self.expand(node, game)
#                     # print(1)
#                 flag = 2
#             else:
#                 # print(2)
#                 node = self.select(node)
                
#             if flag == 2:
#                 # print(3)
#                 node = root
#                 flag = 0
#                 # break
                
#         max_value = 0
#         for i in root.children:
#             if i.visited >= max_value:
#                 max_value = i.visited
        
#         ans = []
#         for i in root.children:
#             if i.visited == max_value:
#                 ans.append(i.action)
                
#         if len(ans) > 0:
#             return ans[random.randint(0, len(ans) - 1)]
        
#         return Actions.STRAIGHT
                  
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
