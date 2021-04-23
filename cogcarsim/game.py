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
    def __init__(self, x_min=-13, y_min=0, x_max=13, y_max=24188, 
                 size=[12095, 13], path_score=0, blob_score=-10, adjacent_score=2):
        self.height = int(size[0])
        self.width = int(size[1])
        self.path_score = path_score
        self.blob_score = blob_score
        self.adjacent_score = adjacent_score
        self.gameGrid = path_score * np.ones((self.height+1, self.width))
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max
        self.x_range = (0.0, float(self.width)-1)
        self.y_range = (0.0, float(self.height)-1)
        self._isGoal = False
        # self.state = {}
        self.goal = (self.height-1, 6)
        self.available = []
        
    def __len__(self):
        return len(self.gameGrid)       
    
    def setTileScore(self, y, x, score):
        self.gameGrid[y][x] = score
        
    def setAdjacentScore(self, y, x):
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
        return self._isGoal
    
    def finished(self):
        self._isGoal = True
    
    @staticmethod
    def slidingWindow(self, overlap, carPos, velocity):
        # The visible lane length is 800
        # we want the window length is equal to the perceived lane length
        # so the window length will be lane_len/2
        windowSize = (lane_len//2, self.width-1)
        step = int(windowSize[0]*overlap)
        for y in range(0, self.height, step):
            yield (self[y:y+windowSize[0], 0:windowSize[1]], (y+windowSize[0], 6), velocity)  # yield the sliding window and its goal

def toMatrixCoords(x_range, y_range, x_min, x_max, y_min, y_max, obj):
    x_obj = obj.x
    y_obj = obj.y
    x = int(round((x_range[1]-x_range[0])*(x_obj-x_min)/(x_max-x_min), 0) + x_range[0])
    y = int(round((y_range[1]-y_range[0])*(y_obj-y_min)/(y_max-y_min), 0) + y_range[0])
    return y, x

def toGameCoords(x_range, y_range, x_min, x_max, y_min, y_max, y, x):
    x_obj = int(round((x-x_range[0])/(x_range[1]-x_range[0])*(x_max-x_min), 0) + x_min)
    y_obj = int(round((y-y_range[0])/(y_range[1]-y_range[0])*(y_max-y_min), 0) + y_min)
    return y_obj, x_obj 
    
class GameGraph():
    def __init__(self, blob_score):
        # self.max_depth = max_depth
        self.velocity = 1.6
        self.blob_score = blob_score
        # self.score = 0
        # self.past_score = 0
        self.G = nx.DiGraph()
        self.id = 0     # store the last id in the graph
        self.curID = 0  # store the current id (position of car) in the graph
        self.available = []
        # self.finished = False

    def expand(self, root_id, y, x, max_depth, velocity, grid):
        # add the root node
        self.velocity = velocity
        self.updateCurrentNode(root_id)
        parent_ids = []
        children_ids = []
        if (root_id not in self.G.nodes()):
            self.G.add_nodes_from([(root_id, {'weight': 0, 'location': (y, x), 'velocity': velocity, 'finished': False})])
        self.id += 1
        
        # compute the second layer of nodes
        if max_depth >= 2:
            if (x - 1 >= 0):
                self.G.add_nodes_from([(self.id, {'weight': 0, 'location': (y+leap, x-1), 'velocity': velocity, 'finished': False})])
                self.G.add_weighted_edges_from([(root_id, self.id, -edge_weight)])
                if grid[y+leap][x-1] == grid.blob_score:
                    self.setNodeWeight(self.id, (1/velocity) * self.blob_score)
                parent_ids.append(self.id)
            self.id += 1
            self.G.add_nodes_from([(self.id, {'weight': 0, 'location': (y+leap, x), 'velocity': velocity, 'finished': False})])
            self.G.add_weighted_edges_from([(root_id, self.id, 0)])
            if grid[y+leap][x] == grid.blob_score:
                    self.setNodeWeight(self.id, (1/velocity) * self.blob_score)
            parent_ids.append(self.id)
            self.id += 1
            if (x + 1 <= 12):
                self.G.add_nodes_from([(self.id, {'weight': 0, 'location': (y+leap, x+1), 'velocity': velocity, 'finished': False})])
                self.G.add_weighted_edges_from([(root_id, self.id, edge_weight)])
                if grid[y+leap][x+1] == grid.blob_score:
                    self.setNodeWeight(self.id, (1/velocity) * self.blob_score)
                parent_ids.append(self.id)
            self.id += 1
            
            # compute the rest
            for i in range(2, max_depth):
                y_temp = y + leap*i
                for x_temp in range(x-i, x+i+1):
                    if (x_temp < 0 or x_temp > 12):
                        self.id += 1
                        continue
                    self.G.add_nodes_from([(self.id, {'weight': 0, 'location': (y_temp, x_temp), 'velocity': velocity, 'finished': False})])
                    children_ids.append(self.id)
                    if grid[y_temp][x_temp] == grid.blob_score:
                        self.setNodeWeight(self.id, (1/velocity) * self.blob_score)
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
                        self.G.add_weighted_edges_from([(parent_id, mid_child, 15)])
                    if (right_child in children_ids):
                        self.G.add_weighted_edges_from([(parent_id, right_child, edge_weight)])
                parent_ids = children_ids
                children_ids = []
    
    def gameEvaluation(self, id):
        score = self.getNodeWeight(id) + self.getEdgeWeight(id)
        return score
    
    def setNodeWeight(self, id, score):
        self.G.nodes[id]['weight'] = score
        
    def getNodeWeight(self, id):
        return self.G.nodes[id]['weight']
        
    def setScore(self, score):
        self.score = score
        
    def getScore(self):
        return self.score
    
    def getEdgeWeight(self, id):
        return self.G.in_degree(id, weight='weight')
        
    def getNodeInfo(self, id):
        return self.G.nodes[id]
    
    def getParent(self, id):
        return self.G.predecessors(id)
    
    def updateCurrentNode(self, node_id):
        self.curID = node_id
        
    def finished(self, id):
        self.G.nodes[id]['finished'] = True
    
    def isFinish(self, id):
        return self.G.nodes[id]['finished']
    
    def getNodeGridPosition(self, id):
        y, x = self.G.nodes[id]['location']
        return y, x

    def getAvailable(self, id):
        self.available = sorted(list(self.G.successors(id)))
        return self.available

    def doMove(self, action, id):
        action = Actions.reverseDirection(action)
        posible_actions = self.getPosibleActions(id)
        if len(posible_actions) == 0:
            return 0
        if len(posible_actions) == 3:
            if action == Actions.LEFT:
                self.updateCurrentNode(self.available[0])
            if action == Actions.STRAIGHT:
                self.updateCurrentNode(self.available[1])
            if action == Actions.RIGHT:
                self.updateCurrentNode(self.available[2])
        elif len(posible_actions) == 2:
            if action == Actions.STRAIGHT:
                if (self.G.nodes[self.curID]['location'][1] == self.G.nodes[self.available[0]]['location'][1]):
                    self.updateCurrentNode(self.available[0])
                else:
                    self.updateCurrentNode(self.available[1])
            if action == Actions.LEFT:
                if (self.G.nodes[self.curID]['location'][1] - 1 == self.G.nodes[self.available[0]]['location'][1]):
                    self.updateCurrentNode(self.available[0])
            if action == Actions.RIGHT:
                if (self.G.nodes[self.curID]['location'][1] + 1 == self.G.nodes[self.available[1]]['location'][1]):
                    self.updateCurrentNode(self.available[1])
        return self.curID
    
    def getPosibleActions(self, id):
        # posibleActions = []
        self.getAvailable(id)
        if len(self.available) == 0:
            return []
        elif len(self.available) == 3:
            return [Actions.LEFT, Actions.STRAIGHT, Actions.RIGHT]
        else:
            if (self.G.nodes[self.curID]['location'][1] == self.G.nodes[self.available[0]]['location'][1]):
                return [Actions.STRAIGHT, Actions.RIGHT]
            if (self.G.nodes[self.curID]['location'][1] == self.G.nodes[self.available[1]]['location'][1]):
                return [Actions.STRAIGHT, Actions.LEFT]
                    
                    
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
    
    def directionToWheel(direction):
        action = Actions._directions[direction]
        return action * 500
    directionToWheel = staticmethod(directionToWheel)