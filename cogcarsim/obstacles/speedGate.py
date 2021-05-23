# -*- coding: utf-8 -*-
from visual import color
# from blobEntry import BlobEntry


lane_width = 25
left_lane_x = -lane_width * 0.5

class SpeedGate:
        
    def __init__(self, x, y, velocity):
        self.x = x
        self.y = y
        self.velocity = velocity
        self.visible = False
        # self.gate_obstacles = []
    
    def get_velocity(self):
        """Return the controlled velocity of the gate.

        Returns:
            int: controlled velocity
        """
        return self.velocity
