# -*- coding: utf-8 -*-
from visual import color
from blobEntry import BlobEntry


lane_width = 25
left_lane_x = -lane_width * 0.5

class SpeedGate():
        
    def __init__(self, x, y, velocity):
        self.x = x
        self.y = y
        self.velocity = velocity
        self.visible = False
        # self.gate_obstacles = []
    
    def get_velocity(self):
        return self.velocity

    # def show(self):
    #     # for i in range(-11, -1, 2):
    #     #     blob = BlobEntry(i, i, self.y, 1, 1)
    #     #     blob.show()
    #     #     self.gate_obstacles.append(blob)
    #     # for i in range(3, 13, 2):
    #     #     blob = BlobEntry(i, i, self.y, 1, 1)
    #     #     self.gate_obstacles.append(blob)
    #     #     blob.show()
        
    #     self.visible = True
        
        
    # def hide(self):
    #     if self.visible:
    #         self.visible = False
    #         # for blob in self.gate_obstacles:
    #         #     blob.hide()
    
    # def isCollided(self, xcar, ycar, object_side):
    #     collided = False
    #     for blob in self.gate_obstacles:
    #         if abs(blob.y - ycar) < object_side and self.visible:
    #             xgap = abs(blob.x-xcar) - object_side
    #             if xgap < 0:
    #                 # blob.hide()
    #                 collided = True
    #         elif blob.y - ycar > object_side:
    #             break
    #         # print blob.x
    #     return collided