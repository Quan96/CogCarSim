import numpy as np
from math import ceil

class Grid:
    def __init__(self, x_min=-13, y_min=0, x_max=13, y_max=24188, size=[12095, 13]):
        self.height = int(size[0])
        self.width = int(size[1])
        self.gameGrid = np.zeros((self.height, self.width))
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max
        self.x_range = (0.0, float(self.width-1))
        self.y_range = (0.0, float(self.height-1))
        
    def __len__(self):
        return len(self.gameGrid)
        
    def toMatrixCoords(self, blob):
        x_blob = blob.x
        y_blob = blob.y
        x = int(round((self.x_range[1]-self.x_range[0])*(x_blob - self.x_min)/(self.x_max - self.x_min), 0) + self.x_range[0])
        y = int(round((self.y_range[1]-self.y_range[0])*(y_blob - self.y_min)/(self.y_max - self.y_min), 0) + self.y_range[0])
        return x, y
    
    def setTileScore(self, y, x, score):
        self.gameGrid[y][x] = score
        
    def setAdjacentScore(self, y, x, score):
        self.setTileScore(y+1, x, score)    # up
        self.setTileScore(y-1, x, score)    # down
        self.setTileScore(y, x+1, score)    # right
        self.setTileScore(y, x-1, score)    # left

    
    def __getitem__(self, key):
        return self.gameGrid[key]
    