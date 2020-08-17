import numpy as np

class Grid:
    def __init__(self, x_min=-13, y_min=0, x_max=13, y_max=24188, size=[13, 12095]):
        self.width = size[0]
        self.height = size[1]
        self.gameGrid = np.zeros((self.width, self.height))
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max
        self.x_range = (0, size[0])
        self.y_range = (0, size[1])
        
    def toMatrixCoords(self, blob):
        x_blob = blob.x
        y_blob = blob.y
        x = (self.x_range[1]-self.x_range[0])*((x_blob - self.x_min)/(self.x_max - self.x_min)) + self.x_range[0]
        y = (self.y_range[1]-self.y_range[0])*((y_blob - self.y_min)/(self.y_max - self.y_min)) + self.y_range[0]
        return (x, y)
    
    def setTileScore(self, x, y, score):
        self.gameGrid[x][y] = score
        
    def setAdjacentScore(self, x, y, score):
        self.setTileScore(x+1, y, score)
        self.setTileScore(x-1, y, score)
        self.setTileScore(x, y+1, score)
        self.setTileScore(x, y-1, score)