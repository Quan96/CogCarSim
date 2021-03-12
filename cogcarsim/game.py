import numpy as np
# from cogCarSim import wheel_sensitivity
import networkx as nx

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
        self.G = None
        self.available = []
        
    def __len__(self):
        return len(self.gameGrid)
        
    def toMatrixCoords(self, obj):
        x_obj = obj.x
        y_obj = obj.y
        x = int(round((self.x_range[1]-self.x_range[0])*(x_obj-self.x_min)/(self.x_max-self.x_min), 0) + self.x_range[0])
        y = int(round((self.y_range[1]-self.y_range[0])*(y_obj-self.y_min)/(self.y_max-self.y_min), 0) + self.y_range[0])
        return y, x
    
    def toGameCoords(self, y, x):
        x_obj = int(round((x-self.x_range[0])/(self.x_range[1]-self.x_range[0])*(self.x_max-self.x_min), 0) + self.x_min)
        y_obj = int(round((y-self.y_range[0])/(self.y_range[1]-self.y_range[0])*(self.y_max-self.y_min), 0) + self.y_min)
        return y_obj, x_obj        
    
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
    
class GameGraph():
    def __init__(self, blob_score):
        # self.max_depth = max_depth
        # self.velocity = velocity
        self.blob_score = blob_score
        self.G = nx.DiGraph()
        self.id = 0
        self.available = []

    def expand(self, root_id, carPos, max_depth, velocity):
        # add the root node
        parent_ids = []
        children_ids = []
        if (root_id not in self.G.nodes()):
            self.G.add_nodes_from([(root_id, {'weight': 0, 'parents': [], 'location': (carPos.x, carPos.y), 'velocity': velocity})])
        self.id += 1
        # compute the second layer of nodes
        if (carPos.x - 1 >= 0):
            self.G.add_nodes_from([(self.id, {'weight': 0, 'parents': [root_id], 'location': (carPos.x - 1, carPos.y+4), 'velocity': velocity})])
            self.G.add_weighted_edges_from([(root_id, self.id, -edge_weight)])
            parent_ids.append(self.id)
            self.id += 1
        self.G.add_nodes_from([(self.id, {'weight': 0, 'parents': [root_id], 'location': (carPos.x, carPos.y+4), 'velocity': velocity})])
        self.G.add_weighted_edges_from([(root_id, self.id, 0)])
        parent_ids.append(self.id)
        self.id += 1
        if (carPos.x + 1 <= 12):
            self.G.add_nodes_from([(self.id, {'weight': 0, 'parents': [root_id], 'location': (carPos.x + 1, carPos.y+4), 'velocity': velocity})])
            self.G.add_weighted_edges_from([(root_id, self.id, edge_weight)])
            parent_ids.append(self.id)
            self.id += 1
        
        for i in xrange(2, max_depth):
            y = carPos.y + 4*i
            for x in xrange(carPos.x-i, carPos.x+i+1):
                if (x < 0 or x > 12):
                    self.id += 1
                    continue
                self.G.add_nodes_from([(self.id, {'weight': 0, 'parents': [], 'location': (x, y), 'velocity': velocity})])
                children_ids.append(self.id)
                self.id += 1
            step = 2*i + 1
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
    
    def setScore(self, id, score):
        self.G.nodes[id]['weight'] = score
        
    def setParent(self, id, parent_id):
        if (len(self.G.nodes[id]['parent']) < 3):
            self.G.nodes[id]['parents'].append(parent_id)
        else:
            print("Parents limitation is 3")

    @staticmethod
    def getAvailable(self, node_id):
        for adj_id, _ in self.G.adj[node_id].items():
            self.available.append(adj_id)
        return self.available

    @staticmethod
    def do_move(action):
        pass
            

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