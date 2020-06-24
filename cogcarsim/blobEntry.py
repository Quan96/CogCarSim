# -*- coding: utf-8 -*-

from visual import sphere, cone

object_side = 2.0    # length of cube side, sphere diameter, cone height etc.

class BlobEntry:
    def __init__(self, blob, x, y, shape, color):        
        self.blob = blob
        self.x = x
        self.y = y
        self.shape = shape
        self.color = color
        self.step_show = -1
        self.step_hide = -1
        self.step_near = -1
        self.xgap = 99999
        self.visible = False
        self.b = None
        
    def show(self):
        """
        Create and show the blob
        """
        c = (1, 0, 0) if self.color == 1 else (1, 0.5, 0) #change colors here: (1, 0, 0) for red, (1, 0.5, 0) for gold
        if self.shape == 1:
            blob = sphere(pos=(self.x, self.y, 0.0), 
                            radius=object_side/2, color=c)
        else:
            blob = cone(pos=(self.x, self.y, -object_side/2), 
                        axis=(0,0,object_side), radius=object_side/2, 
                        color=c)
        blob.visible = True
        self.b = blob
        self.visible = True
        
    def hide(self):
        """
        Hide the blob
        """
        if self.visible:
            self.b.visible = False
            # del(self.b)
            self.b = None
            self.visible = False
        
        