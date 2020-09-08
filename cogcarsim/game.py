import numpy as np
from math import ceil

class Grid:
    def __init__(self, x_min=-13, y_min=0, x_max=13, y_max=24188, 
                 size=[12095, 13], path_score=0, goal_score=100.0, start_score=5.0):
        self.height = int(size[0])
        self.width = int(size[1])
        self.gameGrid = path_score * np.ones((self.height+1, self.width))
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max
        self.x_range = (0.0, float(self.width)-1)
        self.y_range = (0.0, float(self.height)-1)
        self._isGoal = False
        
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
        
    def setAdjacentScore(self, y, x, score):
        self.setTileScore(y+1, x, score)    # up
        self.setTileScore(y-1, x, score)    # down
        self.setTileScore(y, x+1, score)    # right
        self.setTileScore(y, x-1, score)    # left

    
    def __getitem__(self, key):
        return self.gameGrid[key]
    
    def isFinish(self):
        return self._isGoal
    
    def finished(self):
        self._isGoal = True
    
class Actions:
    _directions = {"FastLeft" : -100, "SlowLeft" : -50, 
                  "FastRight":  100, "SlowRight":  50, 
                  "Straight" :  0}
    _directionsAsList = list(_directions.items())
    
    def reverseDirection(action):
        if action == "FastLeft":
            return _directions["FastRight"]
        if action == "SlowLeft":
            return _directions["SlowRight"]
        if action == "FastRight":
            return _directions["FastLeft"]
        if action == "SlowRight":
            return _directions["SlowLeft"]
        return action
    reverseDirection = staticmethod(reverseDirection)