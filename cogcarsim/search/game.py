import numpy as np
# from cogCarSim import wheel_sensitivity
import networkx as nx
import matplotlib.pyplot as plt
import datetime
import math

lane_len = 800       #visible lane length
edge_weight = 3
leap = 3

collision_velocity_down = 0.102
nocollision_velocity_up = 0.0012

class Grid:
    """The grid representation of the game."""
    def __init__(self, x_min=-13, y_min=0, x_max=13, y_max=24188, 
                 path_score=0, blob_score=-10, adjacent_score=2):
        """Grid initialization.
        
        Args:
            x_min (int, optional): The min value of x in the game. Defaults to -13.
            y_min (int, optional): The min value of y in the game. Defaults to 0.
            x_max (int, optional): The max value of x in the game. Defaults to 13.
            y_max (int, optional): The max value of y in the game. Defaults to 24188.
            path_score (int, optional): The path score of the game. Defaults to 0.
            blob_score (int, optional): The blob score of the game. Defaults to -10.
            adjacent_score (int, optional): The score for adjacent tile to the blob. Defaults to 2.
        """
        self.height = int((y_max - y_min) // 2)     # the height of the grid
        self.width = int((x_max - x_min) // 2)      # the width of the grid
        self.path_score = path_score
        self.blob_score = blob_score
        self.adjacent_score = adjacent_score
        self.gameGrid = path_score * np.ones((self.height+1, self.width))
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max
        self.x_range = (0.0, float(self.width)-1)   # the horizontal range of the grid
        self.y_range = (0.0, float(self.height)-1)  # the vertical range of the grid
        self._isGoal = False
        # self.state = {}
        self.goal = (self.height-1, 6)              # the position of the goal
        # self.available = []
        
    def __len__(self):
        """Returns the dimensions of the gameGrid."""
        return len(self.gameGrid)       
    
    def setTileScore(self, y, x, score):
        """Set the score for given tile in the gameGrid.

        Args:
            y (int): The y coordinate.
            x (int): The x coordinate.
            score (float): The given score.
        """
        self.gameGrid[y][x] = score
        
    def setAdjacentScore(self, y, x):
        """Set the score for all adjacent tile of the blob.

        Args:
            y (int): The y grid coordinate of the blob.
            x (int): The x grid coordinate of the blob.
        """
        if self.gameGrid[y+1][x] == self.path_score:
            self.setTileScore(y+1, x, self.adjacent_score)    # up
        if self.gameGrid[y-1][x] == self.path_score:
            self.setTileScore(y-1, x, self.adjacent_score)    # down
        if self.gameGrid[y][x+1] == self.path_score:
            self.setTileScore(y, x+1, self.adjacent_score)    # right
        if self.gameGrid[y][x-1] == self.path_score:
            self.setTileScore(y, x-1, self.adjacent_score)    # left
    
    def __getitem__(self, key):
        return self.gameGrid[key]
    
    def isFinish(self):
        """Check if the game finished.

        Returns:
            boolean
        """
        return self._isGoal
    
    def finished(self):
        """Set the game state as finished."""
        self._isGoal = True

    def slidingWindow(self, overlap, carPos, velocity):
        # The visible lane length is 800
        # we want the window length is equal to the perceived lane length
        # so the window length will be lane_len/2
        windowSize = (lane_len//2, self.width-1)
        step = int(windowSize[0]*overlap)
        for y in range(0, self.height, step):
            yield (self[y:y+windowSize[0], 0:windowSize[1]], (y+windowSize[0], 6), velocity)  # yield the sliding window and its goal

def toGridCoords(x_range, y_range, x_min, x_max, y_min, y_max, obj):
    """Convert the game coordinates of an object into grid coordinates.

    Args:
        x_range (float tuple): The horizontal range of the grid.
        y_range (float tuple): he vertical range of the grid.
        x_min (int): The min value of x in the game.
        x_max (int): The max value of x in the game.
        y_min (int): The min value of y in the game.
        y_max (int): The max value of y in the game.
        obj (VPython object): The VPython object.

    Returns:
        int: The converted y and x grid coordinates
    """
    x_obj = obj.x
    y_obj = obj.y
    x = int(round((x_range[1]-x_range[0])*(x_obj-x_min)/(x_max-x_min), 0) + x_range[0])
    y = int(round((y_range[1]-y_range[0])*(y_obj-y_min)/(y_max-y_min), 0) + y_range[0])
    return y, x

def toGameCoords(x_range, y_range, x_min, x_max, y_min, y_max, y, x):
    """Convert the grid coordinates of object into game coordinate.

    Args:
        x_range (float tuple): The horizontal range of the grid.
        y_range (float tuple): The vertical range of the grid.
        x_min (int): The min value of x in the game.
        x_max (int): The max value of x in the game.
        y_min (int): The min value of y in the game.
        y_max (int): The max value of y in the game.
        y (int): The grid y coordinate of the object.
        x (int): The grid x coordinate of the object.

    Returns:
        float: the converted y and x game coordinates.
    """
    x_obj = int(round((x-x_range[0])/(x_range[1]-x_range[0])*(x_max-x_min), 0) + x_min)
    y_obj = int(round((y-y_range[0])/(y_range[1]-y_range[0])*(y_max-y_min), 0) + y_min)
    return y_obj, x_obj 
    
class GameGraph:
    """The graph representation of the game"""
    def __init__(self, blob_score):
        """The graph initialization.

        Args:
            blob_score (float): the blob score in the graph.
        """
        self.blob_score = blob_score
        self.G = nx.DiGraph()
        self.id = 0     # store the last id in the graph
        self.curID = 0  # store the current id (position of car) in the graph
        # self.available = [] # store the list of descendants of a node

    def expand(self, root_id, y, x, max_depth, velocity, grid):
        """Graph expansion based on the max_depth parameter.
        If max_depth reached but the last node is not grid.height
        The graph will continue to expand using a node in the last layer as new root

        Args:
            root_id (int): The id of the root node.
            y (int): The y grid coordinate of the root.
            x (int): The x grid coordinate of the root.
            max_depth (int): The max depth of the graph.
            velocity (float): The current velocity at root.
            grid (Grid): The game grid.
        """
        # add the root node
        last_y = grid.height - 1
        self.updateCurrentNode(root_id)
        parent_ids = []
        children_ids = []
        if (root_id not in self.G.nodes()):
            self.G.add_nodes_from([(root_id, {'weight': 0, 'location': (y, x), 'velocity': velocity, 'finished': False})])
        self.id += 1
        
        # compute the second layer of nodes
        if max_depth >= 2:
            # LEFT NODE
            if (x - 1 >= 0):
                self.G.add_nodes_from([(self.id, {'weight': 0, 'location': (y+leap, x-1), 'velocity': velocity, 'finished': False})])
                self.G.add_weighted_edges_from([(root_id, self.id, -edge_weight)])
                if grid[y+leap][x-1] == grid.blob_score:
                    self.setNodeWeight(self.id, (1/velocity) * self.blob_score)
                if y+leap >= last_y:
                    self.finished(self.id)
                parent_ids.append(self.id)
            self.id += 1
            # MIDDLE NODE
            self.G.add_nodes_from([(self.id, {'weight': 0, 'location': (y+leap, x), 'velocity': velocity, 'finished': False})])
            self.G.add_weighted_edges_from([(root_id, self.id, 0)])
            if grid[y+leap][x] == grid.blob_score:
                    self.setNodeWeight(self.id, (1/velocity) * self.blob_score)
            if y+leap >= last_y:
                self.finished(self.id)
            parent_ids.append(self.id)
            self.id += 1
            # RIGHT NODE
            if (x + 1 <= grid.width-1):
                self.G.add_nodes_from([(self.id, {'weight': 0, 'location': (y+leap, x+1), 'velocity': velocity, 'finished': False})])
                self.G.add_weighted_edges_from([(root_id, self.id, edge_weight)])
                if grid[y+leap][x+1] == grid.blob_score:
                    self.setNodeWeight(self.id, (1/velocity) * self.blob_score)
                if y+leap >= last_y:
                    self.finished(self.id)
                parent_ids.append(self.id)
            self.id += 1
            
            # compute the rest
            for i in range(2, max_depth):
                y_temp = y + leap*i
                for x_temp in range(x-i, x+i+1):
                    if (x_temp < 0 or x_temp > grid.width-1):
                        self.id += 1
                        continue
                    self.G.add_nodes_from([(self.id, {'weight': 0, 'location': (y_temp, x_temp), 'velocity': velocity, 'finished': False})])
                    children_ids.append(self.id)
                    if grid[y_temp][x_temp] == grid.blob_score:
                        self.setNodeWeight(self.id, (1/velocity) * self.blob_score)
                    if y_temp >= last_y:
                        self.finished(self.id)
                    self.id += 1
                step = 2*(i-1) + 1
                for parent_id in parent_ids:
                    # for child_id in children_ids:
                    # add edge for each parent with 3 other children
                    left_child = parent_id + step
                    mid_child = parent_id + step + 1
                    right_child = parent_id + step + 2
                    if (left_child in children_ids):
                        self.G.add_weighted_edges_from([(parent_id, left_child, -edge_weight)])
                    if (mid_child in children_ids):
                        self.G.add_weighted_edges_from([(parent_id, mid_child, 21)])
                    if (right_child in children_ids):
                        self.G.add_weighted_edges_from([(parent_id, right_child, edge_weight)])
                parent_ids = children_ids
                children_ids = []
    
    def gameEvaluation(self, id):
        """Get the node weight and edge weight of the given node id.

        Args:
            id (int): The node id.

        Returns:
            float: The sum of node weight and edge weight.
        """
        return self.getNodeWeight(id) + self.getEdgeWeight(id)
        # return score
    
    def setNodeWeight(self, id, score):
        """Set the node weight of the given node id.

        Args:
            id (int): The node id.
            score (float): the score to set.
        """
        self.G.nodes[id]['weight'] = score
        
    def getNodeWeight(self, id):
        """Returns the node weight of the node has given id.

        Args:
            id (int): The node id.

        Returns:
            float: The node weight.
        """
        return self.G.nodes[id]['weight']
        
    # def setScore(self, score):
    #     self.score = score
        
    # def getScore(self):
    #     return self.score
    
    def getEdgeWeight(self, id):
        """Returns the edge weight of the node has given id.

        Args:
            id (int): The node id.

        Returns:
            float: The weight of the node.
        """
        # return self.G.edges[parent_id, id]['weight']
        return self.G.in_degree(id, weight='weight')
        
    def getNodeInfo(self, id):
        """Returns all info of the node has given id.

        Args:
            id (int): The node id.

        Returns:
            dict: A dictionary contains node info.
        """
        return self.G.nodes[id]
    
    def getParent(self, id):
        """Returns the list of parents of the node has given id.

        Args:
            id (int): The node id.

        Returns:
            list: Parents of the node.
        """
        return self.G.predecessors(id)
    
    def updateCurrentNode(self, id):
        """Update the current id of the graph.

        Args:
            id (int): The up-to-date id.
        """
        self.curID = id
        
    def finished(self, id):
        """Set the state of the node has given id.

        Args:
            id (int): The node id.
        """
        self.G.nodes[id]['finished'] = True
    
    def isFinished(self, id):
        """Check the state of the node has the given id.

        Args:
            id (int): The node id.

        Returns:
            boolean: The state of the node.
        """
        return self.G.nodes[id]['finished']
    
    def getNodeGridPosition(self, id):
        """Return the position of the node has the given id in the Grid.

        Args:
            id (int): The node id.

        Returns:
            int tuple: The y and x coordinates of the node.
        """
        y, x = self.G.nodes[id]['location']
        return y, x

    def getAvailable(self, id):
        """Get the list of successors of the node has given id.

        Args:
            id (int): The node id.

        Returns:
            list: List of successors of the node.
        """
        available = sorted(list(self.G.successors(id)))
        return available

    def doMove(self, action):
        """Update the curID of the graph according to the given action.

        Args:
            action (Actions): The given action.

        Returns:
            int or None: Return None if the node has no possible action, curID otherwise.
        """
        posible_actions = self.getPossibleActions(self.curID)
        available = self.getAvailable(self.curID)
        if len(posible_actions) == 0:
            return
        # action = Actions.reverseDirection(action)
        if len(posible_actions) == 3:
            if action == Actions.LEFT:
                self.updateCurrentNode(available[0])
            if action == Actions.STRAIGHT:
                self.updateCurrentNode(available[1])
            if action == Actions.RIGHT:
                self.updateCurrentNode(available[2])
        elif len(posible_actions) == 2:
            if action not in posible_actions:
                action = Actions.STRAIGHT
            if action == Actions.STRAIGHT:
                if (self.G.nodes[self.curID]['location'][1] == self.G.nodes[available[0]]['location'][1]):
                    self.updateCurrentNode(available[0])
                else:
                    self.updateCurrentNode(available[1])
            elif action == Actions.LEFT:
                # if (self.G.nodes[self.curID]['location'][1] == self.G.nodes[available[0]]['location'][1]):
                self.updateCurrentNode(available[0])
            else:
                # if (self.G.nodes[self.curID]['location'][1] == self.G.nodes[available[1]]['location'][1]):
                self.updateCurrentNode(available[1])
    
    def generateSuccessors(self, action, id):
        """Get the successor of the node has given id according to the action.

        Args:
            action (Actions): The given action.
            id (int): The node id.

        Returns:
            int or None: None if the node has no successors, successorID otherwise.
        """
        # action = Actions.reverseDirection(action)
        posible_actions = self.getPossibleActions(id)
        available = self.getAvailable(id)
        successorID = id
        if len(posible_actions) == 0:
            return successorID
        if len(posible_actions) == 3:
            if action == Actions.LEFT:
                successorID = available[0]
            if action == Actions.STRAIGHT:
                successorID = available[1]
            if action == Actions.RIGHT:
                successorID = available[2]
        elif len(posible_actions) == 2:
            if action not in posible_actions:
                action = Actions.STRAIGHT
            if action == Actions.STRAIGHT:
                if (self.G.nodes[id]['location'][1] == self.G.nodes[available[0]]['location'][1]):
                    successorID = available[0]
                else:
                    successorID = available[1]
            elif action == Actions.LEFT:
                # if (self.G.nodes[id]['location'][1] == self.G.nodes[available[0]]['location'][1]):
                successorID = available[0]
            else:
                # if (self.G.nodes[id]['location'][1] == self.G.nodes[available[1]]['location'][1]):
                successorID = available[1]
        return successorID
            
    def getPossibleActions(self, id):
        """Get the possible action of the node has given id.

        Args:
            id (int): The node id.

        Returns:
            list: List of possible actions.
        """
        
        available = self.getAvailable(id)
        if len(available) == 0:
            return []
        elif len(available) == 3:
            return [Actions.LEFT, Actions.STRAIGHT, Actions.RIGHT]
        else:
            if (self.G.nodes[id]['location'][1] == self.G.nodes[available[0]]['location'][1]):
                return [Actions.STRAIGHT, Actions.RIGHT]
            if (self.G.nodes[id]['location'][1] == self.G.nodes[available[1]]['location'][1]):
                return [Actions.LEFT, Actions.STRAIGHT]
                    
    def printGraph(self):
        plt.figure()
        nx.draw(self.G)
        now = datetime.datetime.now()
        dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")        
        plt.savefig("logs/graph{date}.png".format(date=dt_string))
     
        
class Actions:
    LEFT = "Left"
    RIGHT = "Right"
    STRAIGHT = "Straight"
    
    _directions = {LEFT: -1, RIGHT: 1, STRAIGHT: 0}
    _directionsAsList = list(_directions.items())
    
    def reverseDirection(action):
        if action == Actions.LEFT:
            return Actions.RIGHT
        if action == Actions.RIGHT:
            return Actions.LEFT
        return action
    reverseDirection = staticmethod(reverseDirection)
    
    def directionToVector(direction, velocity=1.0):
        dx = Actions._directions[direction]
        return (velocity, dx * velocity)  # modified
    directionToVector = staticmethod(directionToVector)
    
    def radianToWheel(angle):
        wheelpos = 841.6*angle + 0.10986
        return wheelpos
    radianToWheel = staticmethod(radianToWheel)