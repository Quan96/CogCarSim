import numpy as np
# from cogCarSim import wheel_sensitivity

lane_len = 800       #visible lane length

class Grid:
    def __init__(self, x_min=-13, y_min=0, x_max=13, y_max=24188, 
                 size=[12095, 13], path_score=0, blob_score=-10, adjacent_score=2):
        self.height = int(size[0])
        self.width = int(size[1])
        self.path_score = path_score
        # self.blob_score = blob_score
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
            
    def graph(self, carPos, velocity, max_depth):
        # Make a graph on the go
        for i in range(max_depth):
            

    @staticmethod
    def available(self):
        pass

    def do_move():
        pass

class DiGraph:
    class Node:
        def __init__(self, data, weight=0):
            self.data = data
            self.weight = 0
            self.links = []
            self.parent = None
            self.visited = False
            
        def getData(self):
            return self.data
        
        def setWeight(self, score):
            self.weight = score
            
        def isLeftNode(self):
            if (self.parent.getX > self.x):
                return True
            else:
                return False
        
        def isRightNode(self):
            if (self.parent.getX < self.x):
                return True
            else:
                return False
        
        def setParent(self, parent):
            self.parent = parent
            
        def add_edge(self, other, weight):
            self.links.append((other, weight))
    
    def __init__(self):
        self.nodes = []
        self.nodeCount = 0
        
    def newNode(self, data, weight):
        node = self.Node(data, weight)
        self.nodes.append(node)
        self.nodeCount += 1
        return node
        
        
        
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