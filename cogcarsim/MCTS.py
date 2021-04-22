# import logging
# import copy
from decimal import Decimal
import numpy as np
from operator import itemgetter
from game import Actions

# def rollout_policy_fn(game):
#     """
#     a coarse , fast version of policy_fn used in the rollout phase
#     """
#     action_probs = np.random.len(game.available)
#     return zip(game.available, action_probs)

# def policy_value_fn(game):
#     """
#     A function that takes in a state and outputs a list of (action, probability)
#     tuples and a score for the state
#     """
#     action_probs = np.ones(len(game.available))
#     return zip(game.available, action_probs), 0
    
# class TreeNode(object):
#     """
#     A node in the MCTS tree. Each node keeps track of its own value Q,
#     prior probability P, and its visit-count-adjusted prior score u
#     """
#     def __init__(self, parent, prior_prob):
#         self._parent = parent
#         self._children = {}     # a map from action to TreeNode
#         self._n_visits = 0
#         self._Q = 0
#         self._u = 0
#         self._P = prior_prob
        
#     def expand(self, action_priors):
#         """
#         Expand the tree by creating new children

#         :param action_priors: a list of tuples of actions and their prior probability
#             according to the policy function
#         :type action_priors: list of tuples
#         """
#         for action, prob in action_priors:
#             if action not in self._children:
#                 self._children[action] = TreeNode(self, prob)
    
#     def select(self, c_puct):
#         """
#         Select action among children that gives maximum action value 
#         plus bonus u(P)

#         :param c_puct: [description]
#         :type c_puct: [type]
#         :return: A tuple of (action, nextNode)
#         """
#         return max(self._children.items(), key=lambda act_node: act_node[1].get_value(c_puct))
    
#     def update(self, value):
#         """
#         Update node values from leaf evaluation

#         :param value: the value of subtree evaluation from the current perspective
#         :type value: int
#         """
#         # Increase the visit value
#         self._n_visits += 1
#         # Update Q, a running average of values for all visits
#         self._Q += 1.0*(value - self._Q) / self._n_visits
        
#     def backpropagate(self, value):
#         """
#         Call the update on all ancestor
#         """
#         if self._parent:
#             self._parent.backpropagate(-value)
#         self.update(value)
    
#     def get_value(self, c_puct):
#         """
#         Calculate and return the value for a node.
#         It is a combination of leaf evaluation Q, and the node's prior
#         adjusted for its visit count, u.
        
#         :param c_puct: a number in (0, inf) controlling the relative impact of value Q
#             and prior probability P, on the node's score
#         :type c_puct: int
#         """
#         self._u = (c_puct*self._P*np.sqrt(self._parent._n_visits) / (1+self._n_visits))
#         return self._Q + self._u

#     def is_leaf(self):
#         """
#         Check if leaf node
#         """
#         return self._children == {}

#     def is_root(self):
#         return self._parent is None
    
# class MCTS(object):

#     def __init__(self, policy_value_fn, c_puct=5, n_playout=10000):
#         """

#         :param policy_value_fn: a function that takes in game state 
#             and output a list of (action, probability) tuples and alse a score in [-1, 1]
#         :param c_puct: a number in (0, inf) that controls 
#             how quickly exploration converges to the maximum-value policy.
#             A higher value means relying on the prior more.
#             defaults to 5
#         :type c_puct: int, optional
#         :param n_playout: [description], defaults to 10000
#         :type n_playout: int
#         """
#         self._root = TreeNode(None, 1.0)
#         self._policy = policy_value_fn
#         self._c_puct = c_puct
#         self._n_playout = n_playout
        
#     def _playout(self, state):
#         """
#         Run a single playout from the root to the leaf, getting a value at
#         the leaf and propagating it back through its parents.
#         State is modified in-place, so a copy must be provided.

#         :param state: [description]
#         :type state: [type]
#         """
#         node = self._root
#         while(1):
#             if node.is_leaf():
#                 break
#             action, node  = node.select(self._c_puct)
#             state.do_move(action)
        
#         action_probs, _ = self._policy(state)
#         end = state.isFinish()
#         if not end:
#             node.expand(action_probs)
        
#         leaf_value = self._evaluate_rollout(state)
#         node.backpropagate(-leaf_value)
        
#     def _evaluate_rollout(self, state, limit=1000):
#         """
#         Use the rollout policy to play until the end of the game,

#         :param state: [description]
#         :type state: [type]
#         :param limit: [description], defaults to 1000
#         :type limit: int, optional
#         """
#         return 0
    
#     def get_move(self, state):
#         """
#         Run all playouts sequentially and returns the most visited action

#         :param state: the current game state
#         :type state: Game
#         """
#         for i in range(self._n_playout):
#             state_copy = copy.deepcopy(state)
#             self._playout(state_copy)
#         return max(self._root._children.items(),
#                    key=lambda act_node: act_node[1]._n_visits)[0]
        
#     def update_with_move(self, last_move):
#         """
#         Step forward in the tree, keeping everything we already know
#         about the subtree.
#         """
#         if last_move in self._root._children:
#             self._root = self._root._children[last_move]
#             self._root._parent = None
#         else:
#             self._root = TreeNode(None, 1.0)
    
#     def __str__(self):
#         return "MCTS"

# class MCTSPlayer(object):
#     """
#     AI player based on MCTS
#     """
#     def __init__(self, c_puct=5, n_playout=2000):
#         self.mcts = MCTS(policy_value_fn, c_puct, n_playout)
        
#     def get_action(self, game):
#         moves = game.getPosibleActions
#         if moves is not None:
#             move = self.mcts.get_move(game)
#             self.mcts.update_with_move(-1)
#             return move
#         else:
#             print("No available move")
    
#     def __str__(self):
#         return "AI CogCarSim"

import random
import math

class Node(object):
    def __init__(self, state, parent, actionList, children, visited, score, action):
        self.state = state
        self.parent = parent
        self.actionList = actionList
        self.children = children
        self.visited = visited
        self.score = score
        self.action = action
    
class MCTSPlayer(object):
    total = 0
    
    def traverse(self, node, game):
        len_actionList = len(node.actionList)
        if len_actionList == 0:
            return
        r = random.randint(0, len_actionList - 1)
        random_choice = node.actionList[r]
        node.actionList.pop(r)
        child_state = game.doMove(random_choice, node.state[0])
        # child_state = game.getAvailable(node.state[0])
        if game.isFinish(child_state):
            child_actionList = []
        else:
            child_actionList = game.getPosibleActions(game.curID)
        s = node.state
        s.append(game.curID)
        # s.doMove(random_choice)
        child = Node(s, node, child_actionList, [], 1, 1, random_choice)
        child.score = self.rollout(child, child_state, game)
        
        self.update(child)
        node.children.append(child)
        return
    
    def rollout(self, node, current_state, game):
        possible = node.actionList
        # maximum_value = -1 * float('inf')
        for i in range(5):
            if len(possible) > 1:
                current_state = game.doMove(possible[random.randint(0, len(possible)-1)], current_state)
            # for state in states:
            elif len(possible) == 1:
                current_state = game.doMove(possible[0], current_state)
            if current_state == 0 or game.isFinish(current_state):
                return 0
            else:
                possible = game.getPosibleActions(current_state)
                score = game.gameEvaluation(current_state)
        return score
    
    def update(self, node):
        while node.parent is not None:
            node = node.parent
            node.visited += 1
            node.score += node.score
            self.total = node.visited
    
    def compare(self, node):
        c = 2
        max_value = -1 * float('inf')
        if len(node.children) > 0:
            for i in node.children:
                val = (i.score / i.visited) + c * math.sqrt(2*math.log(self.total)/i.visited)
                if val > max_value:
                    max_value = val
                    selected_child = i
            return selected_child
        return None
    
    def get_action(self, state):
        # state_copy = copy.deepcopy(state)
        node = Node([state.curID], None, state.getPosibleActions(state.curID), [], 0, 0, Actions.STRAIGHT)
        root = node
        flag = 0
        
        while True:
            if node is None:
                flag = 1
                break
            if len(node.actionList) > 0:
                while len(node.actionList) > 0:
                    self.traverse(node, state)
                flag = 2
            else:
                node = self.compare(node)
                
            if flag == 2:
                # node = root
                flag = 0
                break
                
        max_value = 0
        for i in root.children:
            if i.visited >= max_value:
                max_value = i.visited
        
        ans = []
        for i in root.children:
            if i.visited == max_value:
                ans.append(i.action)
                
        if len(ans) > 0:
            return ans[random.randint(0, len(ans) - 1)]
        
        return Actions.STRAIGHT
    
        
                