# -*- coding: utf-8 -*-

from visual import *
display.enable_shaders = False
import time
import datetime
import random
import json
import os
import errno
import wheel
import sys
import csv

from blobEntry import *
from speedGate import *
from pathEntry import *

refresh_rate = 60
default_start_velocity = 1.6

# Prop constants
distance_to_first_blob = 200
number_of_blobs = 2000
blob_y_distance = 12.0
blobs_per_patch = 100
inter_patch_distance = 100
blob_x_values = range(-11,11+1,2)
chunk = 50  # the number of blobs in a chunk

# Prop Probabilites
prob_red_cone = 0.4                #probabilities for blob types (target is all 1 minus all the others)
prob_red_ball = 0.4
prob_gold_ball = 0.1

manual_speed = 1
auto_speed = 0
fixed_speed = 2

# Display properties
scene_center = (0, -1.0, 4.0)
scene_forward = vector(0, 1.0, 0.0)
scene_range = (9.0, 9.0, 9.0)


left_lane_x = -lane_width * 0.5
right_lane_x = lane_width * 0.5
lane_len = 800.0                        #visible lane lenght
rail_height = 0.5
lane_radius = 0.1                       #lane border radius
lane_back_y = -20
                     
initial_car_y = 0.0                     #initial car y position
safe_back_y = 5.0                       #safe backward distance where objects no longer need to be visible
lane_margin = object_side / 2 + lane_radius 
blob_x_values = range(-11,11+1,2)

collision_grace_period = 100            # immunity time after collision (while no speed drop)
guaranteed_velocity = 0.3               # floor of the felocity no matter how many collisions
collision_penalty_time = [0, 5, 20]

left_button = 7
right_button = 6
left_paddle = 5
right_paddle = 4

wheel_sensitivity = 800.0
full_brake_deceleration = 0.01
full_throttle_speed = 4.0
pedal_neutral = 1000
pedal_down = -1000

throttle_base = 0.002
throttle_multiply = 4
throttle_power = 5


collision_velocity_down = 0.102
nocollision_velocity_up = 0.0012

max_name_len = 20

# Level and map properties
random_gen = True                                           # check if user choose to randomly generated a map or not
current_level = 0                                           # keep track of current level for level up feature
levels = {1: "map1.json", 2:"map2.json", 3:"map3.json",     # a dict contains levels and maps name
          4:"map4.txt", 5:"map5.csv"}     

class CogCarSim:
    
    def generate_blobs_trad(self, nblobs, blob_seed):
        """
        Randomly generates blob color and shape
        then add blob to the list

        :param nblobs: total number of blobs
        :type nblobs: int
        :param blob_seed: random seed number
        :type blob_seed: int
        """
        blob_random = random.Random()
        blob_random.seed(blob_seed)
        self.blobs = []
        self.gates = []
        y = distance_to_first_blob
        for i in range(nblobs//chunk):
            for j in range(chunk):
                x = blob_random.choice(blob_x_values)
                r = blob_random.random()
                if r < prob_red_ball:
                    shape = 1
                    color = 1
                elif r < prob_red_ball + prob_gold_ball:
                    shape = 1
                    color = 2
                elif r < prob_red_ball + prob_gold_ball + prob_red_cone:
                    shape = 2
                    color = 1
                else:
                    shape = 2
                    color = 2
                b = BlobEntry(j, x, y, shape, color)
                self.blobs.append(b)
                y += blob_y_distance
            y += blob_y_distance * 2
            speed_gate = SpeedGate(y, 1.6)
            y += blob_y_distance * 10
            self.gates.append(speed_gate)
    
    def generate_blobs_mani(self, nblobs, blob_seed):
        """
        Randomly generates blob color and shape
        then add blob to the list

        :param nblobs: total number of blobs
        :type nblobs: int
        :param blob_seed: random seed number
        :type blob_seed: int
        """

        blob_random = random.Random()
        blob_random.seed(blob_seed)
        self.blobs = []
        y = distance_to_first_blob
        bc = blobs_per_patch
        # blob_id = 0
        color = blob_random.choice([1,2])
        for i in range(nblobs):
            x = blob_random.choice(blob_x_values)
            shape = 1 if blob_random.random() < 0.5 else 2
            blob = BlobEntry(i, x, y, shape, color)
            self.blobs.append(blob)
            y += blob_y_distance
            # ib += 1
            bc -= 1
            if bc == 0:
                color = 2 if color == 1 else 1
                bc = blobs_per_patch
                y += inter_patch_distance
            
    def load_level(self, path='maps', level=1, random=True):
        """
        Load the pre-defined map or generate random map
        Assume that pre-defined map written in json file
        having the format: x-coord,y-coord,shape,color

        :param path: path the maps file, defaults to './maps'
        :type path: str, optional
        :param level: map level, defaults to 0
        :type level: int, optional
        :raises FileNotFoundError
        :return: the current_map level and the number of blobs
        :rtype: int
        """
        
        self.blobs = []
        self.gates = []
        try:
            with open(path + os.sep + levels[level]) as file:
                lines = 0
                if levels[level].endswith(".json"):
                    infor = json.load(file)
                    for data in infor["rows"]:
                        # print len(data)
                        if len(data) == 4:
                            x = float(data[0])
                            y = float(data[1])
                            shape = float(data[2])
                            color = float(data[3])
                            blob = BlobEntry(lines, x, y, shape, color)
                            self.blobs.append(blob)
                            lines += 1
                        elif len(data) == 2:
                            y = float(data[0])
                            velocity = float(data[1])
                            speed_gate = SpeedGate(y, velocity)
                            self.gates.append(speed_gate)
                elif levels[level].endswith(".txt"):
                    infor = file.readline()
                    while infor:
                        data = infor.split(',')
                        if len(data) == 4:
                            x = float(data[0])
                            y = float(data[1])
                            shape = float(data[2])
                            color = float(data[3])
                            blob = BlobEntry(lines, x, y, shape, color)
                            self.blobs.append(blob)
                            lines += 1
                        elif len(data) == 2:
                            y = float(data[0])
                            velocity = float(data[1])
                            speed_gate = SpeedGate(y, velocity)
                            self.gates.append(speed_gate)
                        infor = file.readline()
                elif levels[level].endswith(".csv"):
                    infor = csv.reader(file, delimiter=",")
                    next(infor)
                    for row in infor:
                        if len(row) == 4:
                            x = float(row[0])
                            y = float(row[1])
                            shape = float(row[2])
                            color = float(row[3])
                            blob = BlobEntry(lines, x, y, shape, color)
                            self.blobs.append(blob)
                            lines += 1
                        elif len(row) == 2:
                            y = float(row[0])
                            velocity = float(row[1])
                            speed_gate = SpeedGate(y, velocity)
                            self.gates.append(speed_gate)
                file.close()
                return lines
        except IOError as e:
            print os.strerror(e.errno)
            return number_of_blobs
        
    def define_display(self):
        """
        Define the display
        """
        
        self.scene = display(title='CogCarSim', exit=1, fullscreen=True, width=1920, height=1080, center=scene_center, background=(0,0,0), autoscale=False)
        self.scene.range = scene_range
        self.scene.forward = scene_forward
        
        self.scene.select()
        self.scene.show_rendertime = 0
    
    def create_objects(self, nblobs, blob_seed, task, level):   
        """
        Create the car object and 2 lanes

        :param total_blobs: total number of blobs
        :type total_blobs: int
        :param blob_seed: random seed number
        :type blob_seed: int
        :param task: manual, auto speed or fixed speed
        :type task: int
        :return: the car object and 2 lanes
        :rtype: VPython object
        """
        car = box(pos=(0, initial_car_y, 0), length=object_side, height=object_side, width=object_side, color=color.blue)
        left_lane = cylinder(pos=(left_lane_x, lane_back_y, rail_height), axis=(0, 1, 0), radius=lane_radius, length=lane_len, color=color.gray(0.2))
        right_lane = cylinder(pos=(right_lane_x, lane_back_y, rail_height), axis=(0, 1, 0), radius=lane_radius, length=lane_len, color=color.gray(0.2))
        
        if isRandom():
            if task == manual_speed:
                self.generate_blobs_mani(nblobs, blob_seed)
            else:
                self.generate_blobs_trad(nblobs, blob_seed)
        else:
            self.load_level(level=level)
        self.first_visible_blob = 0
        self.n_visible_blobs = 0
        self.reposition_blobs(car.pos.y, 0)
        # self.gate_passed(car.pos.y)
        
        return car, left_lane, right_lane

    def autopilot(self, xcar, ycar, velocity):
        """
        Autopilot mode

        :param xcar: the x-coordinate of the car object
        :type xcar: float
        :param ycar: the y-coordinate of the car object
        :type ycar: float
        :param velocity: the current speed of the car object
        :type velocity: float
        :return: [description]
        :rtype: int
        """
        bstep = 0
        bwp = 0
        for awp in [0, -50, 50, -100, 100, -200, 200, -1000, 1000]:
            maxstep = 30
            sight = -1
            for astep in range(maxstep):
                axp = xcar + astep * awp * velocity / wheel_sensitivity
                if axp > right_lane_x - lane_margin:
                    axp = right_lane_x - lane_margin
                if axp < left_lane_x + lane_margin:
                    axp = left_lane_x + lane_margin
                ayp = ycar + astep * velocity
                acol = False
                for i in range(self.first_visible_blob, self.first_visible_blob + self.n_visible_blobs):
                    b = self.blobs[i]
                    if (b.y > ayp + object_side):
                        break
                    if abs(b.x - axp) < object_side and abs(b.y - ayp) < object_side and b.visible:
                            acol = True
                            break
                if acol:
                    break
                else:
                    sight = astep
            if sight > bstep:
                bstep = sight
                bwp = awp
                if sight == maxstep - 1:
                    break
        return bwp

    def wait_start(self, description):
        start_label = label(pos=(0, 40, 0), height=24, border=10, opacity=1) 
        start_label.text = 'Press wheel button to start'
        while True:
            rate(75)
            if wheel.getbttn(left_button):
                break
            elif wheel.getbttn(right_button):
                break
            elif wheel.getbttn(left_paddle):
                break
            elif wheel.getbttn(right_paddle):
                break
        
        start_label.visible = False

    def reposition_blobs(self, ycar, step):
        """
        Show new blobs as the car go
        and hide passed blob

        :param ycar: y-coordinate of the car object
        :type ycar: float
        :param step: [description]
        :type step: int
        :return: number of blobs passed
        :rtype: int
        """
        blob_passed = 0
        created = 0
        for i in range(self.first_visible_blob, self.first_visible_blob + self.n_visible_blobs):
            if self.blobs[i].y < ycar - safe_back_y:
                self.blobs[i].hide()
                self.blobs[i].step_hide = step
                self.first_visible_blob += 1
                self.n_visible_blobs -= 1
                blob_passed += 1
            else:
                break
        for i in range(self.first_visible_blob + self.n_visible_blobs, len(self.blobs)):
            if self.blobs[i].y - ycar < lane_len:
                self.blobs[i].show()
                self.blobs[i].step_show = step
                self.n_visible_blobs += 1
                created += 1
            else:
                break
        return blob_passed
    
    def gate_passed(self, ycar, is_gate_on):
        velocity = 0
        if len(self.gates) >= 1 and is_gate_on == True:
            if self.gates[0].y < ycar - safe_back_y:
                velocity = self.gates[0].get_velocity()
                self.gates[0].hide()
                del self.gates[0]
            
            # if self.gates[0].y - ycar < lane_len:
                # self.gates[0].show()
        return velocity
    
    
    def check_collision(self, xcar, ycar, step):
        """
        Check if the blobs has collided with the car

        :param xcar: x-coordinate of the car object
        :type xcar: float
        :param ycar: y-coordinate of the car object
        :type ycar: float
        :param step: [description]
        :type step: int
        :return: True if collided and the color of the colided object, otherwise false and 0
        :rtype: bool and int
        """
        collision = False
        color = 0
        for i in range(self.first_visible_blob, self.first_visible_blob + self.n_visible_blobs):
            b = self.blobs[i]
            if abs(b.y - ycar) < object_side and b.visible:
                xgap = abs(b.x - xcar) - object_side
                self.blobs[i].xgap = xgap
                self.blobs[i].step_near = step  
                if xgap < 0:
                    b.hide()
                    collision = True
                    color = b.color
            elif b.y - ycar > object_side:
                break
        return collision, color
        

    def penalty_box(self, carpos, penalty):
        cheated = False
        x,y,z = carpos
        t0 = time.clock()
        t1 = t0 + penalty
        collision_label = label(pos=(x,y+40,z), height=24, border=10, opacity=1)
        collision_label.visible = True
        while time.clock() < t1:
            t = t1 - time.clock()
            collision_label.text = 'Collision penalty left: {:5.0f}'.format(t)
            rate(refresh_rate)
            if self.scene.kb.keys:
                cheated = True
                break
        collision_label.visible = False
        return cheated
    
    def run(self, task, start_velocity, total_blobs, blob_seed, 
                    replay = False, wheel_positions=None, throttle_positions=None, level=1, is_gate_on=True):
        """
        The main loop of the program

        :param task: [description]
        :type task: [type]
        :param start_velocity: velocity when game start
        :type start_velocity: float
        :param total_blobs: total number of blobs
        :type total_blobs: int
        :param blob_seed: random seed number
        :type blob_seed: int
        :param replay: [description], defaults to False
        :type replay: bool, optional
        :param wheel_positions: positions of the wheel, defaults to None
        :type wheel_positions: float, optional
        :param throttle_positions: [description], defaults to None
        :type throttle_positions: [type], optional
        :return: the run information
        """
        
        self.define_display()
        display_rate = refresh_rate
        
        car, left_lane, right_lane = self.create_objects(total_blobs, blob_seed, task, level)
        
        background_effect_left = 0 # how many rounds the collision effect (changed background color) will be in use
        last_collision = 0         # timestamp of the last collision
        collision_count = 0        # how many collisions so far
        collision_speed_drops = 0 # how many punished (speed decreasing) collisions
        debug_label = label(pos=car.pos, height=20, border=6, box=0, opacity=0) # debug info text on the car
        debug_label.visible = False
        
        debug = False
        autopiloting = False
        cheated = False
        batch = False
        pause = False
        play1 = False
        
        wheel.initx()
        task_description = task_string(task, start_velocity)
        self.wait_start(task_description)
        velocity = start_velocity
        
        path = []
        step = 0
        max_velocity = velocity
        last_y = self.blobs[-1].y + 2 * safe_back_y
        #input handling
        while car.y < last_y:
            if not batch:
                rate(display_rate)
            clock_begin = time.clock()
            
            if self.scene.kb.keys:
                cheated = True
                key = self.scene.kb.getkey()
                if key == 'q':
                    self.scene.visible = False
                    return None
                elif key == 'p':
                    pause = not pause
                elif key == ' ':
                    play1 = True
                    self.scene.center.z = 2*self.scene.center.z
                    self.scene.center.z = self.scene.center.z / 2
                elif key == "+":
                    display_rate *= 2
                elif key == '-':
                    display_rate /= 2
                    if display_rate == 0:
                        display_rate = 1
                elif key == 'd':
                    debug = not debug
                    debug_label.visible = debug
                elif key == 'a':
                    autopiloting = not autopiloting
                elif key == 'b':
                    batch = not batch
                    
            if play1:
                pause = True
                play1 = False
            elif pause:
                continue
            
            # blob housekeeping
            passed = self.reposition_blobs(car.pos.y, step)
            
            controlled_velocity = self.gate_passed(car.pos.y, is_gate_on)
            
            if controlled_velocity <> 0:
                velocity = controlled_velocity
                        
            if replay:
                wheelpos = wheel_positions[step]
                throttlepos = throttle_positions[step]
            else:
                (w, t, b, c) = wheel.getprecise()
                wheelpos = w / 1000.0
                throttlepos = t / 1000.0
                brakepos = b / 1000.0
                clutchpos = c / 1000.0
                
                if autopiloting:
                    wheelpos = self.autopilot(car.pos.x, car.pos.y, velocity)
                
            # Velocity changes here except collision effects
            if task == auto_speed:
                chosen_velocity = velocity # to be used in collision analyses
                velocity += passed * nocollision_velocity_up
            elif task == manual_speed:
                throttle_ratio = 1.0*(throttlepos - pedal_neutral) / (pedal_down - pedal_neutral)
                velocity = sqrt((1.0-throttle_base)*velocity**2+2**throttle_multiply*throttle_base*throttle_ratio**throttle_power)
                chosen_velocity = velocity
            else:
                chosen_velocity = velocity
                
            if max_velocity < velocity:
                max_velocity = velocity
                
            # Steering
            xp = car.pos.x + wheelpos * velocity / wheel_sensitivity
            
            if (xp > right_lane_x - lane_margin):
                xp = right_lane_x - lane_margin
            if (xp < left_lane_x + lane_margin):
                xp = left_lane_x + lane_margin
                
            if (background_effect_left):
                background_effect_left -= 1
                if not background_effect_left:
                    self.scene.background = (0, 0, 0)
                    
            # All the movement happens here
            old_interval = sys.getcheckinterval()
            sys.setcheckinterval(100000)
            car.pos.x = xp
            car.pos.y = car.pos.y + velocity
            debug_label.pos = car.pos
            
            self.scene.center.x = xp
            self.scene.center.y = self.scene.center.y + velocity
            left_lane.pos.y = left_lane.pos.y + velocity
            right_lane.pos.y = right_lane.pos.y + velocity
            sys.setcheckinterval(old_interval)
            
            # Collision detection and handing
            
            collision, collided_color = self.check_collision(car.pos.x, car.pos.y, step)
            if (collision):
                collision_count = collision_count + 1
                if task == auto_speed or task == fixed_speed:
                    self.scene.background = (0.5, 0.5, 0.5)
                    background_effect_left += 5
                    if (step - last_collision > collision_grace_period):
                        if task == auto_speed:
                            velocity -= collision_velocity_down 
                            if (velocity < guaranteed_velocity):
                                velocity = guaranteed_velocity
                        collision_speed_drops = collision_speed_drops + 1
                        last_collision = step
                elif task == manual_speed:
                    penalty_time = collision_penalty_time[collided_color]
                    if self.penalty_box(car.pos, penalty_time):
                        cheated = True
                    velocity = 0
                    
            debug_label.text = 'Speed %.3f\nMaxSp %.3f\nSpeed drops %i\nCollisions %i\nBlobs %i\nGate %i ' % (velocity, max_velocity, collision_speed_drops, collision_count, self.first_visible_blob, len(self.gates))
            
            p = PathEntry()
            p.step = step
            p.x = car.pos.x
            p.y = car.pos.y
            p.collision = collision
            p.wheelpos = wheelpos
            p.throttlepos = throttlepos
            p.velocity = velocity
            p.chosen_velocity = chosen_velocity
            p.clock_begin = clock_begin
            p.time = datetime.datetime.fromtimestamp(time.time())
            path.append(p)
            step += 1
            
        # After while loop
        
        clock_diff = path[-1].clock_begin - path[0].clock_begin
        step_diff = path[-1].step - path[0].step
        print "Time:", clock_diff
        print "Average step duration:", clock_diff / step_diff
        print "Steps per second", step_diff / clock_diff
        print "Total steps", step_diff
        print "End speed", velocity
        print "Max speed", max_velocity
        print "Collisions", collision_count
        print "Collision speed drops", collision_speed_drops
        
        start_label = label(pos=(car.pos.x, car.pos.y+40, car.pos.z), height=24, border=10, opacity=1)
        start_label.text = 'Run finished'
        start_label.visible = True
        time.sleep(2)
        self.scene.visible = 0
        
        #cheated = False
        return path, self.blobs, cheated, collision_count, collision_speed_drops, velocity
    
    def __del__(self):
        wheel.releasex()
        

                          
                    
def isRandom():
    return random_gen

def setRandom(state):
    global random_gen
    random_gen = state
    
# def setCurrentLevel(level):
#     global current_level
#     current_level = level
    
def task_string(task, velocity):
    if task == auto_speed:
        s = "auto {:3.1f}".format(velocity)         
    elif task == manual_speed:
        s = "manual" 
    elif task == fixed_speed:
        s = "fixed {:3.1f}".format(velocity)
    return s