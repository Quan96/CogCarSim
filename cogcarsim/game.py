import numpy as np
# from cogCarSim import wheel_sensitivity
import networkx as nx
import matplotlib.pyplot as plt
import datetime

lane_len = 800       #visible lane length
edge_weight = 1

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
            
    # def graph(self, carPos, max_depth, velocity=0):
    #     # Make a graph on the go
    #     self.G = nx.DiGraph()
    #     root = self.G.newNode((carPos.x, carPos.y), 0)
    #     parents = [root]
    #     self.available = []
    #     children = []
    #     for i in range(1, max_depth):
    #         y = carPos.y + 4*i
    #         for x in range(carPos.x-i, carPos.x+i+1):
    #             if (x < 0 or x > 12):
    #                 continue
    #             if (self.gameGrid[y][x] == self.blob_score):
    #                 new_node = self.G.newNode((x, y), weight = self.blob_score)
    #             else:
    #                 new_node = self.G.newNode((x, y), weight = 0)
    #             children.append(new_node)
    #         for parent in parents:
    #             for child in children:
    #                 if (abs(child.data[0] - parent.data[0]) <= 1):
    #                     if (child.isLeftNode(parent)):
    #                         parent.addEdge(child, -edge_weight)
    #                         child.setParent(parent, edge_weight)
    #                     elif(child.isRightNode(parent)):
    #                         parent.addEdge(child, edge_weight)
    #                         child.setParent(parent, -edge_weight)
    #                     else:
    #                         parent.addEdge(child, 0)
    #                         child.setParent(parent, 0)
    #         parents = children   
    #         children = []
    #     return self.G

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
        # self.velocity = velocity
        self.blob_score = blob_score
        self.score = 0
        self.G = nx.DiGraph()
        self.id = 0     # store the last id in the graph
        self.curID = 0  # store the current id (position of car) in the graph
        self.available = []
        self.finished = False

    def expand(self, root_id, y, x, max_depth, velocity, grid):
        # add the root node
        self.updateCurrentNode(root_id)
        parent_ids = []
        children_ids = []
        if (root_id not in self.G.nodes()):
            self.G.add_nodes_from([(root_id, {'weight': 0, 'parents': [], 'location': (y, x), 'velocity': velocity})])
        self.id += 1
        
        # compute the second layer of nodes
        if (x - 1 >= 0):
            self.G.add_nodes_from([(self.id, {'weight': 0, 'parents': [root_id], 'location': (y+4, x - 1), 'velocity': velocity})])
            self.G.add_weighted_edges_from([(root_id, self.id, -edge_weight)])
            if grid[y][x] == grid.blob_score:
                self.setNodeWeight(self.id, self.blob_score)
            parent_ids.append(self.id)
            self.id += 1
        self.G.add_nodes_from([(self.id, {'weight': 0, 'parents': [root_id], 'location': (y+4, x), 'velocity': velocity})])
        self.G.add_weighted_edges_from([(root_id, self.id, 0)])
        if grid[y][x] == grid.blob_score:
                self.setNodeWeight(self.id, self.blob_score)
        parent_ids.append(self.id)
        self.id += 1
        if (x + 1 < 12):
            self.G.add_nodes_from([(self.id, {'weight': 0, 'parents': [root_id], 'location': (y+4, x + 1), 'velocity': velocity})])
            self.G.add_weighted_edges_from([(root_id, self.id, edge_weight)])
            if grid[y][x] == grid.blob_score:
                self.setNodeWeight(self.id, self.blob_score)
            parent_ids.append(self.id)
            self.id += 1
        
        for i in range(2, max_depth):
            y = y + 3*i
            for x in range(x-i, x+i+1):
                if (x < 0 or x > 12):
                    self.id += 1
                    continue
                self.G.add_nodes_from([(self.id, {'weight': 0, 'parents': [], 'location': (y, x), 'velocity': velocity})])
                children_ids.append(self.id)
                if grid[y][x] == grid.blob_score:
                    self.setNodeWeight(self.id, self.blob_score)
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
                    self.setParent(left_child, parent_id)
                if (mid_child in children_ids):
                    self.G.add_weighted_edges_from([(parent_id, mid_child, 0)])
                    self.setParent(mid_child, parent_id)
                if (right_child in children_ids):
                    self.G.add_weighted_edges_from([(parent_id, right_child, edge_weight)])
                    self.setParent(right_child, parent_id)
            parent_ids = children_ids
            children_ids = []
    
    def setNodeWeight(self, id, score):
        self.G.nodes[id]['weight'] = score
        
    def setScore(self, score):
        self.score = score
        
    def getScore(self):
        return self.score
        
    def getNodeInfo(self, id):
        return self.G.nodes[id]
        
    def setParent(self, id, parent_id):
        if (len(self.G.nodes[id]['parents']) < 3):
            self.G.nodes[id]['parents'].append(parent_id)
        else:
            print("Parents limitation is 3")
    
    def updateCurrentNode(self, node_id):
        self.curID = node_id
        
    def isFinish(self):
        return self.finished
    
    def getNodeGridPosition(self, id):
        y, x = self.G.nodes[id]['location']
        return y, x

    def getAvailable(self):
        self.available = []
        for adj_id, _ in self.G.adj[self.curID].items():
            self.available.append(adj_id)
        return self.available.sort()

    def doMove(self, action):
        action = Actions.reverseDirection(action)
        self.getAvailable()
        if len(self.available) == 0:
            return
        elif len(self.available) == 3:
            if action == Actions.LEFT:
                self.updateCurrentNode(self.available[0])
            if action == Actions.STRAIGHT:
                self.updateCurrentNode(self.available[1])
            if action == Actions.RIGHT:
                self.updateCurrentNode(self.available[2])
        else:
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
    
    def getPosibleActions(self):
        # posibleActions = []
        self.getAvailable()
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
     
     
# class DiGraph:
#     link_count = 0
#     class Node:
#         def __init__(self, data, weight=0):
#             self.data = data
#             self.weight = 0
#             self.links = []
#             self.pastLink = None
#             self.parents = []
#             self.visited = False
                      
#         def getData(self):
#             return self.data
        
#         def setWeight(self, score):
#             self.weight = score
            
#         def isLeftNode(self, other):
#             if (other.data[0] > self.data[0]):
#                 return True
#             else:
#                 return False
        
#         def isRightNode(self, other):
#             if (other.data[0] < self.data[0]):
#                 return True
#             else:
#                 return False
        
#         def setParent(self, parent, weight):
#             self.parents.append((parent, weight))
            
#         def addEdge(self, other, weight):
#             self.links.append((other, weight))
#             DiGraph.link_count += 1
    
#     def __init__(self):
#         self.nodes = []
#         self.node_count = 0
        
#     def newNode(self, data, weight):
#         node = self.Node(data, weight)
#         self.nodes.append(node)
#         self.node_count += 1
#         return node
        
        
        
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
        return action * 400
    directionToWheel = staticmethod(directionToWheel)