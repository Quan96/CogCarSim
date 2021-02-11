import logging
import copy
import numpy as np
from operator import itemgetter

def rollout_policy_fn(game):
    """
    a coarse , fast version of policy_fn used in the rollout phase
    """
    action_probs = np.random.len(game.width)
    return zip(game.available, action_probs)

def policy_value_fn(game):
    """
    A function that takes in a state and outputs a list of (action, probability)
    tuples and a score for the state
    """
    action_probs = np.one(len(game.width))/len(game.width)
    return zip(game.available, action_probs), 0
    
class TreeNode(object):
    """
    A node in the MCTS tree. Each node keeps track of its own value Q,
    prior probability P, and its visit-count-adjusted prior score u
    """
    def __init__(self, parent, prior_prob):
        self._parent = parent
        self._children = {}     # a map from action to TreeNode
        self._n_visits = 0
        self._Q = 0
        self._u = 0
        self._P = prior_prob
        
    def expand(self, action_priors):
        """
        Expand the tree by creating new children

        :param action_priors: a list of tuples of actions and their prior probability
            according to the policy function
        :type action_priors: list of tuples
        """
        for action, prob in action_priors:
            if action not in self._children:
                self._children[action] = TreeNode(self, prob)
    
    def select(self, c_puct):
        """
        Select action among children that gives maximum action value 
        plus bonus u(P)

        :param c_puct: [description]
        :type c_puct: [type]
        :return: A tuple of (action, nextNode)
        """
        return max(self._children.items(), key=lambda act_node: act_node[1].get_value(c_puct))
    
    def update(self, value):
        """
        Update node values from leaf evaluation

        :param value: the value of subtree evaluation from the current perspective
        :type value: int
        """
        # Increase the visit value
        self._n_visits += 1
        # Update Q, a running average of values for all visits
        self._Q += 1.0*(value - self._Q) / self._n_visits
        
    def backpropagate(self, value):
        """
        Call the update on all ancestor
        """
        if self._parent:
            self._parent.backpropagate(-value)
        self.update(value)
    
    def get_value(self, c_puct):
        """
        Calculate and return the value for a node.
        It is a combination of leaf evaluation Q, and the node's prior
        adjusted for its visit count, u.
        
        :param c_puct: a number in (0, inf) controlling the relative impact of value Q
            and prior probability P, on the node's score
        :type c_puct: int
        """
        self._u = (c_puct*self.P*np.sqrt(self._parent._n_visits) / (1+self._n_visits))
        return self._Q + self._u

    def is_leaf(self):
        """
        Check if leaf node
        """
        return self._children == {}

    def is_root(self):
        return self._parent is None
    
class MCTS(object):

    def __init__(self, policy_value_fn, c_puct=5, n_playout=10000):
        """

        :param policy_value_fn: a function that takes in game state 
            and output a list of (action, probability) tuples and alse a score in [-1, 1]
        :param c_puct: a number in (0, inf) that controls 
            how quickly exploration converges tot the maximum-value policy.
            A higher value means relying on the prior more.
            defaults to 5
        :type c_puct: int, optional
        :param n_playout: [description], defaults to 10000
        :type n_playout: int
        """
        self._root = TreeNode(None, 1.0)
        self._policy = policy_value_fn
        self._c_puct = c_puct
        self._n_playout = n_playout
        
    def _playout(self, state):
        """
        Run a single playout from the root to the leaf, getting a value at
        the leaf and propagating it back through its parents.
        State is modified in-place, so a copy must be provided.

        :param state: [description]
        :type state: [type]
        """
        node = self._root
        while(1):
            if node.is_leaf():
                break
            action, node  = node.select(self._c_puct)
            state.do_move(action)
        
        action_probs, _ = self._policy(state)
        end = state.isFinish()
        if not end:
            node.expand(action_probs)
        
        leaf_value = self._evaluate_rollout(state)
        node.backpropagate(-leaf_value)
        
    def _evaluate_rollout(self, state, limit=1000):
        """
        Use the rollout policy to play until the end of the game,

        :param state: [description]
        :type state: [type]
        :param limit: [description], defaults to 1000
        :type limit: int, optional
        """
        return 0
    
    def get_move(self, state):
        """
        Run all playouts sequentially and returns the most visited action

        :param state: the current game state
        :type state: Game
        """
        for i in range(self._n_playout):
            state_copy = copy.deepcopy(state)
            self._playout(state_copy)
        return max(self._root._children.items(),
                   key=lambda act_node: act_node[1]._n_visits)[0]
        
    def update_with_move(self, last_move):
        """
        Step forward in the tree, keeping everything we already know
        about the subtree.
        """
        if last_move in self._root._children:
            self._root = self._root._children[last_move]
            self._root._parent = None
        else:
            self._root = TreeNode(None, 1.0)
    
    def __str__(self):
        return "MCTS"

class MCTSPlayer(object):
    """
    AI player based on MCTS
    """
    def __init__(self, c_puct=5, n_playout=2000):
        self.mcts = MCTS(policy_value_fn, c_puct, n_playout)
        
    def get_action(self, game):
        moves = game.available
        if len(moves) > 0:
            move = self.mcts.get_move(game)
            self.mcts.update_with_move(-1)
            return move
        else:
            print("No available move")
    
    def __str__(self):
        return "AI CogCarSim"