# -*- coding: utf-8 -*-
from visual import cylinder, color

lane_width = 25
left_lane_x = -lane_width * 0.5

class SpeedGate:
        
    def __init__(self, y, velocity):
        self.y = y
        self.velocity = velocity
        self.visible = False
        self.g = None
    
    def get_velocity(self):
        return self.velocity

    def show(self):
        gate = cylinder(pos=(left_lane_x, self.y, 1), axis=(1,0,0), radius=0.4, length=lane_width, color=color.yellow(0.02))
        gate.visible = True
        self.g = gate
        self.visible = True
        
        
    def hide(self):
        if self.visible:
            self.g.visible = False
            self.visible = False
            self.g = None