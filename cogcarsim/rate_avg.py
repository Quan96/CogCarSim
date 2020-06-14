from visual import *
import random
import datetime
import time
import wheel
import sys
import sqlite3
import os.path

prerounds=1
rounds = 1000
target = 75
scene = display(title='CogCarSim', exit=1, fullscreen=False, background=(0,0,0), autoscale=False)
laatta1 = box(pos=(0,0,0), size=(3,3,3), color=color.blue)
for i in range(prerounds):
    rate(target)
t1 = time.clock()
for i in range(rounds):
    wheel.rate(target)
    for j in range(100000):
        pass
           
t2 = time.clock()
print rounds / (t2-t1)
scene.visible=False
            
