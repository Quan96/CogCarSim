# -*- coding: utf-8 -*-

from visual import *
display.enable_shaders = False
import random
import datetime
import time
import wheel
import sys
import sqlite3
import os.path
import errno

# Global constants

version = "2012-11-20-A"

refresh_rate = 60
default_start_velocity = 1.6

blob_y_distance = 12.0      
number_of_blobs = 2000      # total number of blobs
blobs_per_patch = 100
inter_patch_distance = 100
distance_to_first_blob = 200

prob_red_cone = 0.4                #probabilities for blob types (target is all 1 minus all the others)
prob_red_ball = 0.4
prob_gold_ball = 0.1

manual_speed = 1
auto_speed = 0
fixed_speed = 2

score_list_len = 10


# Classic-versio
#scene_center = (0,-1.0, 1.0)
#scene_forward = vector(0, 0.97, -0.17)
#scene_range = (10.0, 10.0, 10.0)

# Matala kulma, kuutio alalaidassa kohtuullisen kokoisena
scene_center = (0, -1.0, 4.0)
scene_forward = vector(0, 1.0, 0.0)
scene_range = (9.0, 9.0, 9.0)


lane_width = 25
left_lane_x = -lane_width * 0.5
right_lane_x = lane_width * 0.5
lane_len = 800.0                        #visible lane lenght
rail_height = 0.5
lane_radius = 0.1                       #lane border radius
lane_back_y = -20                       #lane start point

object_side = 2.0                       #length of cube side, sphere diameter, cone height etc.
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

random_gen = True
levels = {1: "map1.txt", 2:"map2.txt"}
current_level = 0

class CogCarSim:

    class PathEntry:
        
        def __init__(self):
            self.step = None
            self.clock_begin = None
            self.time = None
            self.x = None
            self.y = None
            self.collision = None
            self.wheelpos = None
            self.throttlepos = None
            self.velocity = None
            self.chosen_velocity = None

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
        y = distance_to_first_blob
        for i in range(nblobs):
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
            b = self.BlobEntry(i, x, y, shape, color)
            self.blobs.append(b)
            y += blob_y_distance


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
        ib = 0
        color = blob_random.choice([1,2])
        for b in range(nblobs):
            x = blob_random.choice(blob_x_values)
            shape = 1 if blob_random.random() < 0.5 else 2
            blob = self.BlobEntry(ib, x, y, shape, color)
            self.blobs.append(blob)
            y += blob_y_distance
            ib += 1
            bc -= 1
            if bc == 0:
                color = 2 if color == 1 else 1
                bc = blobs_per_patch
                y += inter_patch_distance
                
    def load_level(self, path='.\\maps', level=1):
        """
        Load the pre-defined map or generate random map
        Assume that pre-defined map written in text file
        having the format: x-coord,y-coord,shape,color

        :param path: path the maps file, defaults to './maps'
        :type path: str, optional
        :param level: map level, defaults to 0
        :type level: int, optional
        :raises FileNotFoundError
        :return: the current map level, 0 if map randomly generated
        :rtype: int
        """
        # global random_gen
        global current_level
        global number_of_blobs

        self.blobs = []
        try:
            with open(path + os.sep + levels[level]) as file:
                line = file.readline()
                lines = 0
                while line:
                    line_components = line.split(',')
                    x = float(line_components[0])
                    y = float(line_components[1])
                    shape = int(line_components[2])
                    color = int(line_components[3])
                    blob = self.BlobEntry(lines, x, y, shape, color)
                    self.blobs.append(blob)
                    lines+=1
                    line = file.readline()
                number_of_blobs = lines
                file.close()
                return True
        except IOError as e:
            print os.strerror(e.errno)
            return False
        current_level = 0

    def load_next_level(self):
        """
        Load next level in the map stack

        :param level: map level, defaults to 1
        :type level: int, optional
        """
        global current_level

        next_level = current_level + 1
        self.load_level(level=next_level)
        current_level = next_level

    def define_display(self):
        # Define the display

        self.scene = display(title='CogCarSim', exit=1, fullscreen=True, width=1920, height=1080, center=scene_center, background=(0,0,0), autoscale=False)       
        self.scene.range = scene_range
        self.scene.forward = scene_forward 

        self.scene.select()
        # self.scene.cursor.visible = 0
        self.scene.show_rendertime = 0
        

    def create_objects(self, total_blobs, blob_seed, task):
        """
        Create the car object and 2 lanes

        :param total_blobs: total number of blobs
        :type total_blobs: int
        :param blob_seed: random seed number
        :type blob_seed: int
        :param task: manual or auto speed
        :type task: int
        :return: the car object and 2 lanes
        :rtype: VPython object
        """
        car = box(pos=(0,initial_car_y,0), length=object_side, height=object_side, width=object_side, color=color.blue)
        left_lane = cylinder(pos=(left_lane_x, lane_back_y, rail_height), axis=(0, 1, 0), radius=lane_radius, length=lane_len, color=color.gray(0.2))
        right_lane = cylinder(pos=(right_lane_x, lane_back_y, rail_height), axis=(0, 1, 0), radius=lane_radius, length=lane_len, color=color.gray(0.2))

        # global current_level
        # global random_gen

        if random_gen:
            if task == manual_speed:
                self.generate_blobs_mani(total_blobs, blob_seed)
            else:
                self.generate_blobs_trad(total_blobs, blob_seed)
        else:
            self.load_level(level=current_level)
        self.first_visible_blob = 0
        self.n_visible_blobs = 0
        self.reposition_blobs(car.pos.y, 0)
        
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
        passed = 0
        created = 0
        for i in range(self.first_visible_blob, self.first_visible_blob + self.n_visible_blobs):
            if self.blobs[i].y < ycar - safe_back_y:
                self.blobs[i].hide()
                self.blobs[i].step_hide = step
                self.first_visible_blob += 1
                self.n_visible_blobs -= 1
                passed += 1
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
        return passed
                
            

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
                    replay = False, wheel_positions=None, throttle_positions=None, level=0):
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

        car, left_lane, right_lane = self.create_objects(total_blobs, blob_seed, task)


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
        # input handling
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
               # elif key == 'up':
                    self.scene.center.z = 2*self.scene.center.z
               # elif key == 'down':
                    self.scene.center.z = self.scene.center.z / 2
                elif key == '+':
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
                    
            if (max_velocity < velocity):
                max_velocity = velocity
        
            # Steering
            xp = car.pos.x + wheelpos * velocity / wheel_sensitivity
            
            if xp > right_lane_x - lane_margin:
                xp = right_lane_x - lane_margin
            if xp < left_lane_x + lane_margin:
                xp = left_lane_x + lane_margin
                
            if background_effect_left:
                background_effect_left -= 1
                if not background_effect_left:
                    self.scene.background = (0,0,0)

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
                  
            # Collision detection and handling

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

            debug_label.text = 'Speed %.3f\nMaxSp %.3f\nSpeed drops %i\nCollisions %i\nBlobs %i' % (velocity, max_velocity, collision_speed_drops, collision_count, self.first_visible_blob)

            p = CogCarSim.PathEntry()
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

        # after while loop
        
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
        # print current_level
        
        start_label = label(pos=(car.pos.x, car.pos.y+40, car.pos.z), height=24, border=10, opacity=1)
        start_label.text = 'Run finished'
        start_label.visible = True
        time.sleep(2)
        self.scene.visible = 0

        #cheated = False
        return path, self.blobs, cheated, collision_count, collision_speed_drops, velocity
    
    def __del__(self):
        wheel.releasex()


class Stats:


    @staticmethod
    def pathinfo(path):
        if len(path) > 0:
            min_velocity = max_velocity = path[-1].velocity
            sum = 0.0
            for p in path:
                if p.velocity > max_velocity:
                    max_velocity = p.velocity
                if p.velocity < min_velocity:
                    min_velocity = p.velocity
                sum = sum + p.velocity
            avg_velocity = sum / len(path)
            return min_velocity, max_velocity, avg_velocity
        else:
            return 0,0,0
    
    

    @staticmethod
    def save(dbfilename, date, path, blobs, participant, run, task, seed, start_velocity, collisions, speed_drops, description):
        if len(path) > 0:
            p2 = path[-1]
            p1 = path[0]
            duration = p2.clock_begin - p1.clock_begin
            distance = p2.y - p1.y
            steps = p2.step - p1.step
            end_velocity = p2.velocity
            min_velocity, max_velocity, avg_velocity = Stats.pathinfo(path)
        else:
            return

        try:
            conn = None
            if not os.path.exists(dbfilename):
                conn = sqlite3.connect(dbfilename)
                conn.execute('''create table run (run integer, participant text, date text, task integer, totalblobs integer, 
                                                    seed integer, min_velocity real, max_velocity real, 
                                                    start_velocity real, end_velocity real, avg_velocity real, collisions integer,
                                                    speed_drops integer, level integer,
                                                    duration real, distance real, steps integer, version string, description string)''')
                conn.execute('''create table blob (blob integer, run integer, x real, y real, shape integer, color integer, 
                                                    step_show integer, step_hide integer, step_near integer, xgap real)''')
                conn.execute('''create table step (step integer, run integer, clock_begin real, time real,
                                                    x real, y real, collision integer, 
                                                    wheelpos real, throttlepos real, velocity real, chosenvel real)''')
            else:
                conn = sqlite3.connect(dbfilename)
            conn.execute('''insert into run (run, participant, date, task, totalblobs, seed, 
                                               min_velocity, max_velocity, start_velocity, end_velocity, 
                                               avg_velocity, collisions, speed_drops, level, duration, distance, steps, version, description) 
                                               values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                         (run, participant, date, task, len(blobs), seed,  
                          min_velocity, max_velocity, start_velocity, end_velocity, avg_velocity, 
                          collisions, speed_drops, current_level, duration, distance, steps, version, description))
            for b in blobs:
                conn.execute('''insert into blob (blob, run, x, y, shape, color, step_show, step_hide, step_near, xgap) 
                                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                             (b.blob, run, b.x, b.y, b.shape, b.color, b.step_show, b.step_hide, b.step_near, b.xgap))
            for p in path:
                conn.execute('''insert into step (step, run, clock_begin, time, x, y, collision, 
                                wheelpos, throttlepos, velocity, chosenvel) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                             (p.step, run, p.clock_begin, p.time, p.x, p.y, p.collision, 
                            p.wheelpos, p.throttlepos, p.velocity, p.chosen_velocity))
            conn.commit()
        except e:
            raise e
        finally:
            # This will be always executed. Even if except reraises the exception.
            if conn:
                conn.close()



    @staticmethod
    def print_runs(dbfilename=None):
        try:
            conn = None
            if not os.path.exists(dbfilename):
                print "No database %s file found" %dbfilename
                return

            conn = sqlite3.connect(dbfilename)
            cur = conn.cursor()
            print "Existing runs in database %s:" %dbfilename
            cur.execute('''select run, participant, date from run order by run''')
            lastp = -1
            print '{0:3} {1:15} {2:15}'.format("Run", "Participant", "Date")
            for row in cur:
                r, p, d = row
                print '{0:3} {1:15} {2:15}'.format(r, p, d)
            print
            conn.commit()
        except e:
            raise e
        finally:
            # This will be always executed. Even if except reraises the exception.
            if conn:
                conn.close()

    @staticmethod
    def get_earlier_count(participant, task, speed):
        conn = None
        if not os.path.exists(results_dbfile):
            return 0

        conn = sqlite3.connect(results_dbfile)
        cur = conn.cursor()
        cur.execute('''select count (*) from run where participant=? and task=? and start_velocity=? ''', (participant, task, speed))
        t = cur.fetchone()
        conn.close()
        return t[0]
    

    @staticmethod
    def get_last_run_number(dbfilename):
        try:
            conn = None
            if not os.path.exists(dbfilename):
                return 0

            conn = sqlite3.connect(dbfilename)
            cur = conn.cursor()
            #cur.execute("select max (run) from run where participant=?", (participant,))
            cur.execute("select max (run) from run")
            t = cur.fetchone()
            conn.commit()
            if t[0] == None:
                return 0
            else:
                return t[0]
        except e:
            raise e
        finally:
            # This will be always executed. Even if except reraises the exception.
            if conn:
                conn.close()


    @staticmethod
    def get_control_positions(dbfilename, run):
        try:
            conn = None
            if not os.path.exists(dbfilename):
                print "No database %s file found" %dbfilename
                return

            conn = sqlite3.connect(dbfilename)
            cur = conn.cursor()
            cur.execute('''select wheelpos, throttlepos from step
                                where run=? order by step''',(run,))
            w = []
            t = []
            for i in cur:
                w.append(i[0])
                t.append(i[1])
            conn.commit()
            return w,t
        except e:
            raise e
        finally:
            # This will be always executed. Even if except reraises the exception.
            if conn:
                conn.close()


    @staticmethod
    def get_run_info(dbfilename, run):
        try:
            conn = None
            if not os.path.exists(dbfilename):
                print "No database %s file found" %dbfilename
                return

            conn = sqlite3.connect(dbfilename)
            cur = conn.cursor()
            cur.execute('''select seed, totalblobs, task, start_velocity  from run 
                                where run=? ''',(run,))
            conn.commit()
            row = cur.fetchone()
            seed = row[0]
            totalblobs = row[1]
            task = row[2]
            start_velocity = row[3]
            
            return seed, totalblobs, task, start_velocity
        except e:
            raise e
        finally:
            # This will be always executed. Even if except reraises the exception.
            if conn:
                conn.close()


    @staticmethod
    def get_scores(name,dbfilename, task, speed):
        nscores = 10
        try:
            conn = None
            if not os.path.exists(dbfilename):
                print "No database %s file found" %dbfilename
                return
            conn = sqlite3.connect(dbfilename)
            cur = conn.cursor()
            if task == fixed_speed:
                cur.execute('''select participant, collisions from run 
                               where task=? and participant <> "Cheater" and abs(start_velocity - ?) < 0.01
                               order by collisions asc, date asc limit ?''',(task,speed, score_list_len))
                results = []
                for r in cur:
                    p,c = r
                    results.append((p,"{}".format(c)))
                    if len(results) == nscores:
                        break
            elif task == auto_speed:
                cur.execute('''select participant, duration, collisions from run 
                               where task=? and participant <> "Cheater" and abs(start_velocity - ?) < 0.01
                               order by duration asc, collisions asc, date asc''',(task,speed))
                results = []
                for r in cur:
                    p,d,c = r
                    m, s = divmod(d,60)
                    if p.startswith(name[:3]): # only own scores visible + name parameter first 3 characters
                        results.append((p,"{:.0f} min {:.0f} s ({})".format(m, s, c)))
                    if len(results) == nscores:
                        break
            else:
                cur.execute('''select participant, duration, collisions from run 
                               where task=? and participant <> "Cheater" and abs(start_velocity - ?) < 0.01
                               order by duration asc, date asc limit ?''',(task,speed, score_list_len))
                results = []
                for r in cur:
                    p,d,c = r
                    results.append((p,"{:.3f} ({})".format(d, c)))
                    if len(results) == nscores:
                        break
                
            return results            
        except e:
            raise e
        finally:
            # This will be always executed. Even if except reraises the exception.
            if conn:
                conn.close()




def get_name():
    global current_level
    global random_gen
    
    speed = default_start_velocity
    min_speed = 0.3
    max_speed = 4.0
    speed_increase = 0.1

    task = 0
    focus = 0

    tasknames = ["Auto", "Manual", "Fixed", "Fixed series"]
    speed_changable =[True, False, True, False]

    bc = tc = (1.0, 1.0, 1.0)
    angle = 0.01
        
    scene = display(title='CogCarSim', exit=1, fullscreen=True, width=1920, height=1080, background=(0,0,0), autoscale=False)
    scene.select()

    laatta1 = box(pos=(-6.5,0,0), size=(3,3,3), color=color.blue)
    laatta2 = box(pos=(6.5,0,0), size=(3,3,3), color=color.blue)

    title = label(pos=(0,4.0,0), text="CogCarSim", height=80, opacity=0, box=0)
    name_prompt = label(pos=(-2,1.5,0), text="Name", height=30, opacity=0, box=0)
    name = label(pos=(1.5,1.5,0), height=30, width=100,linecolor=bc, color=tc) # initially blank text
    task_prompt = label(pos=(-2,0.0,0), text="Game", height=30, linecolor=tc, opacity=0, box=0)
    task_label = label(pos=(1.5,0.0,0), height=30, border=10, opacity=0, linecolor=bc, color=tc, box=0) 
    speed_prompt = label(pos=(-2,-1.5,0), text="Speed", height=30, linecolor=tc, opacity=0, box=0)
    speed_label = label(pos=(1.5,-1.5,0), height=30, border=10, opacity=1, linecolor=bc, color=tc, box=0)
    level_prompt = label(pos=(-2, -3, 0), text="Level", height=30, opacity=0, box=0)
    level = label(pos=(1.5, -3, 0), height=30, width=50, linecolor=tc, color=tc, box=0)
    
    start_label = label(pos=(0,-4.5 ,0), height=24, border=10, opacity=1, box=0, linecolor=color.blue) 
    start_label.text = 'Please type in your name\nPress enter to start'

    fields = [name, task_label, speed_label, level]
    key = ''
    while 1:
        rate(50)
        task_label.text = tasknames[task]
        speed_label.text = "{:3.1f}".format(speed)
        laatta1.rotate(angle=angle, axis = (1,1,1))
        laatta2.rotate(angle=-angle, axis = (1,1,1))
        if scene.kb.keys: # is there an event waiting to be processed?
            key = scene.kb.getkey() # obtain keyboard information
            if key == 'escape':
                break
            if key == '\n' or key == 'f1' or key == 'f2':
                break
            elif len(key) == 1 and focus == 0:
                if len(name.text) < max_name_len:
                    name.text += key # append new character
            elif len(key) == 1 and focus == 3:
                if key.isdigit():
                    if int(key) <= len(levels):
                        level.text += key
            elif (key == 'backspace' or key == 'delete'): 
                if len(name.text) > 0 and focus == 0:
                    name.text = name.text[:-1] # erase one letter
                if len(level.text) > 0 and focus == 3:
                    level.text = level.text[:-1]    
            elif key == 'shift+delete':
                if focus == 0: 
                    name.text = '' # erase all the text
                if focus == 3:
                    level.text = ''
            elif key == 'left': 
                if focus == 0:
                    pass
               # elif focus == 1:
               #     task = task - 1 if task > 0 else len(tasknames)-1
               # elif focus == 2 and speed_changable[task]:
               #     speed = speed - speed_increase if speed > min_speed else min_speed
            elif key == 'right' or key == ' ': 
                if focus == 0:
                    pass
               # elif focus == 1:
               #      task = task + 1 if task < len(tasknames)-1 else 0
               # elif focus == 2 and speed_changable[task]:
               #      speed = speed + speed_increase if speed < max_speed else max_speed
            elif key == 'down': 
                fields[focus].box=0
                focus = focus + 1 if focus < len(fields)-1 else 0
                fields[focus].box=1
            elif key == 'up': 
                fields[focus].box=0
                focus = focus - 1 if focus > 0 else len(fields)-1
                fields[focus].box=1
            elif key == 'end-of-line':
                break
        speed_label.color = (0.2, 0.2, 0.2) if task != auto_speed and task != fixed_speed else (1.0, 1.0, 1.0)
        speed_label.linecolor = (0.2, 0.2, 0.2) if task != auto_speed and task != fixed_speed  else (1.0, 1.0, 1.0)

    name = name.text
    level = level.text
    scene.visible = False
    if name == "":
        name = "Anonymous"
    if task != auto_speed and task != fixed_speed:
        speed = 0.0
    if level == "":
        random_gen = True
        current_level = 0
    else:
        random_gen = False
        current_level = int(level)
    return name, key, task, speed, current_level


def show_fame(titletext, current, subtitle, results):
    scene = display(title='CogCarSim', exit=1, fullscreen=True, width=1920, height=1080, background=(0,0,0), autoscale=False)
    scene.select()
    fame_x = -1
    fame_y = 1.5
    fame_yd = 0.8
    own_x = -1
    own_y = 5
    title = label(pos=(own_x+0.8,own_y+0.8,0), text=titletext, height = 50, box=0)
    ownspeed = label(pos=(own_x+0.8,own_y-1.0,0), text=current, height = 100, box=0)
    l = []
    fametitle = label(pos=(fame_x+0.8,fame_y+1,0), text=subtitle, height = 50, box=0)
    for i in range(len(results)):
        name, result = results[i]
        append(l, label(pos=(fame_x-3.0,fame_y-i*fame_yd,0), text="%i"%(i+1), height = 30, box=0))
        append(l, label(pos=(fame_x-1.0,fame_y-i*fame_yd,0), text=result, height = 30, box=0))
        append(l, label(pos=(fame_x+3.6,fame_y-i*fame_yd,0), text=name, height = 30, box=0))
    laatta1 = box(pos=(-8.5,0,0), size=(3,3,3), color=color.blue)
    laatta2 = box(pos=(8.5,0,0), size=(3,3,3), color=color.blue)
    a = 0.02
    while 1:
        laatta1.rotate(angle=a, axis = (1,1,1))
        laatta2.rotate(angle=-a, axis = (1,1,1))
        rate(20)
        if scene.kb.keys:
            key = scene.kb.getkey() # obtain keyboard information
            if key == '\n':
                scene.visible = False
                test_run() # go to next run
            else:
                break
                scene.visible = False
    
def task_string(task, velocity):
    if task == auto_speed:
        s = "auto {:3.1f}".format(velocity)         
    elif task == manual_speed:
        s = "manual" 
    elif task == fixed_speed:
        s = "fixed {:3.1f}".format(velocity)
    return s
    
    
def show_high(name, task, selected_velocity, duration, collisions, speed_drops, end_velocity):
    if name == None:
        name = "ZZZZZ"
        collisions = 99
        speed_drops = 99
        duration = 999.999
        end_velocity = 0.0
        
    results = Stats.get_scores(name,results_dbfile, task, selected_velocity)
    subtitle = "High Scores"
    m, s = divmod(duration, 60)    
    
    if task == auto_speed:
        show_fame(titletext = "{}'s time (collisions)".format(name), 
                  current = "{:.0f} min {:.0f} s ({})".format(m, s, collisions), # show elapsed time and collisions
                  subtitle = subtitle,
                  results = results)    
    elif task == manual_speed:
        show_fame(titletext = "{}'s time".format(name), 
                  current = "{:.3f} ({})".format(duration, collisions),
                  subtitle = subtitle,
                  results = results)    
    elif task == fixed_speed:
        show_fame(titletext = "{}'s collisions".format(name), 
                  current = "{}".format(collisions), 
                  subtitle = subtitle,
                  results = results)


def get_next_series_velocity(name, description):
    start_velocity = 1.0
    velocity_step = 0.2
    
    conn = None
    if not os.path.exists(results_dbfile):
        return start_velocity

    conn = sqlite3.connect(results_dbfile)
    cur = conn.cursor()
    cur.execute('''select max(start_velocity) from run where participant=? and description=? and collisions = 0 ''', (name, description))
    b, = cur.fetchone()
    conn.close()
    return b + velocity_step if b != None else start_velocity
    

def get_test_details(name, game):
    if game == 3:
        task = fixed_speed
        description = "Fixed series"
        nblobs = number_of_blobs
        selected_velocity = get_next_series_velocity(name, description)
        blob_seed = int(10*selected_velocity)+100*task+1000*Stats.get_earlier_count(name, task, selected_velocity)
    else:
        assert(False)
    return blob_seed, nblobs, task, selected_velocity, description
    
def test_run():
    name, key, game, vel, current_level = get_name()
    
    if key == 'f1': 
        if game <= fixed_speed:
            show_high(name=None, task=game, selected_velocity=vel, collisions=None, duration = None, end_velocity = None, speed_drops = None)
        return
    
    if not game in {manual_speed, auto_speed, fixed_speed}:
        blob_seed, nblobs, task, selected_velocity, description = get_test_details(name, game)
    else:
        task = game
        blob_seed = random.randint(1, 10000000)
        nblobs = number_of_blobs
        description = "Individual"
        selected_velocity = vel
       
    sim = CogCarSim()
    path, blobs, cheated, collisions, speed_drops, end_velocity = sim.run(start_velocity = selected_velocity, task = task, 
                blob_seed = blob_seed, total_blobs = nblobs, level=current_level)
    if len(path) > 0:
        duration = path[-1].clock_begin - path[0].clock_begin
    if cheated:
        name = "Cheater"
    run = Stats.get_last_run_number(results_dbfile)+1
    t = time.localtime()
    date = str(datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec))
    Stats.save(dbfilename=results_dbfile, path=path, blobs=blobs, description = description,
                participant=name, run=run, task=task, seed=blob_seed, 
                date = date, start_velocity = selected_velocity, collisions = collisions, speed_drops = speed_drops)
    show_high(name, task, selected_velocity, duration, collisions, speed_drops, end_velocity)


def verify(run, steps, blobs, collisions, speed_drops, end_velocity):
    conn = sqlite3.connect(results_dbfile)
    cur = conn.cursor()
    
    cur.execute(''' select collisions, speed_drops, end_velocity from run where run = ? ''',(run,))
    row = cur.fetchone()
    c, s, e = row
    if collisions <> c:
        print "Mismatch in run fields, run:", run
        print "collisions", c, collisions
    if speed_drops <> s:
        print "Mismatch in run fields, run:", run
        print "speed drops", s, speed_drops
    if end_velocity <> e:
        print "Mismatch in run fields, run:", run
        print "end velocity", e, end_velocity
        
        
    cur.execute(''' select step, x, y, collision, wheelpos, throttlepos, \
                    velocity from step where run = ? order by step ''',(run,))
    i = 0
    rows = cur.fetchall()
    if len(rows) <> len(steps):
        print "Mismatch in step list length, run:", run
        return
        
    for row in rows:
        step, x, y, collision, wheelpos, throttlepos, velocity = row
        s = steps[i]
        i += 1
        if  (s.step <> step or
            s.x <> x or
            s.y <> y or
            s.collision <> collision or
            s.wheelpos <> wheelpos or
            s.throttlepos <> throttlepos or
            s.velocity <> velocity):
                print "Mismatch in step fields, run:", run
                print "step", s.step, step
                print "x", s.x, x
                print "y", s.y, y
                print "collision", s.collision, collision
                print "wheelpos", s.wheelpos, wheelpos
                print "throttlepos", s.throttlepos, throttlepos
                print "velocity", s.velocity, velocity
                
    cur.execute(''' select blob, x, y from blob where run = ? order by blob ''',(run,))
    i = 0
    rows = cur.fetchall()
    if len(rows) <> len(blobs):
        print "Mismatch in blob list length, run:", run
    
    for row in rows:
        blob,x,y = row
        b = blobs[i]
        i += 1
        if b.x <> x or b.y <> y:
                print "Mismatch in blob fields, run:", run
                print "x", b.x, x
                print "y", b.y, y
    print "Verification of db record finished"


def replay(text=None):
    if not text:
        Stats.print_runs(results_dbfile)    
        print "No changes will be made to the database during replay"
        text = raw_input('Give the run number for replay [0=last, Enter=Quit]:')
    if text != "":
        run = int(text)
    else:
        return
    if run == 0:
        run = Stats.get_last_run_number(results_dbfile)
    if run == 0:
        return
    wp, tp = Stats.get_control_positions(results_dbfile, run)
    seed, total_blobs, task, start_speed  = Stats.get_run_info(results_dbfile, run)
    sim = CogCarSim()
    path, blobs, cheated, collisions, speed_drops, end_velocity = sim.run(start_velocity = start_speed, blob_seed = seed, task = task,
                                        total_blobs = total_blobs, replay = True, wheel_positions = wp, throttle_positions = tp, level=current_level)
    verify(run, path, blobs, collisions, speed_drops, end_velocity)
    raw_input('Press Enter to Exit')
    

#Main
global results_dbfile
results_dbfile = str.replace(sys.argv[0], '.py', '.db', 1)
if len(sys.argv) == 1:
    test_run()
elif sys.argv[1] == "replay":
    if len(sys.argv) == 3:
        replay(sys.argv[2])
    else:
        replay()
