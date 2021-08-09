# -*- coding: utf-8 -*-

from __future__ import print_function
from networkx.readwrite.graphml import GraphMLWriter
from visual import *
display.enable_shaders = False
import time
# import datetime 
import random
import json
import os
import errno
import wheel
import sys
import csv
# from math import ceil


from obstacles.blobEntry import *
from obstacles.speedGate import *
from obstacles.pathEntry import *
from search.game import *
# from search import *
from search.mcts import MCTSPlayer

refresh_rate = 60
default_start_velocity = 1.6

# Prop constants
distance_to_first_blob = 180
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
agent_speed = 4

# Display properties
scene_center = (0, -1.0, 4.0)
scene_forward = vector(0, 1.0, 0.0)
scene_range = (9.0, 9.0, 9.0)


left_lane_x = -lane_width * 0.5
right_lane_x = lane_width * 0.5
# lane_len = 800.0                        #visible lane length
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


# collision_velocity_down = 0.102
# nocollision_velocity_up = 0.0012

max_name_len = 20

score = 0.0
reinforce = False

# Level and map properties
random_gen = True                                           # check if user choose to randomly generated a map or not
current_level = 0                                           # keep track of current level for level up feature
levels = {1: "map1.json", 2:"map2.json", 3:"map3.json",     # a dict contains levels and maps name
          4:"map4.txt", 5:"map5.csv", 6:"map6.txt",
          7:"map7.txt"}

class CogCarSim:
    
    def generate_blobs_trad(self, nblobs, blob_seed, is_gate_on):
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
        id = 0
        y = distance_to_first_blob
        for i in range(nblobs//chunk):
            if is_gate_on and i != 0:
                y += blob_y_distance * 2
                speed_gate = SpeedGate(0, y, 1.6)
                for i in range(-11, -1, 2):
                    b = BlobEntry(id, i, y, 2, 2)
                    id += 1
                    self.blobs.append(b)
                for i in range(3, 13, 2):
                    b = BlobEntry(id, i, y, 2, 2)
                    id += 1
                    self.blobs.append(b)
                y += blob_y_distance * 4
                self.gates.append(speed_gate)
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
                b = BlobEntry(id, x, y, shape, color)
                id += 1
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
                id = 0
                if levels[level].endswith(".json"):
                    infor = json.load(file)
                    for data in infor["rows"]:
                        # print len(data)
                        if len(data) == 4:
                            x = float(data[0])
                            y = float(data[1])
                            shape = float(data[2])
                            color = float(data[3])
                            blob = BlobEntry(id, x, y, shape, color)
                            self.blobs.append(blob)
                            id += 1
                        elif len(data) == 3:
                            x = float(data[0])
                            y = float(data[1])
                            velocity = float(data[2])
                            speed_gate = SpeedGate(x, y, velocity)
                            for i in range(-11, int(x-1), 2):
                                b = BlobEntry(id, i, y, 2, 2)
                                id += 1
                                self.blobs.append(b)
                            for i in range(int(x+3), 13, 2):
                                b = BlobEntry(id, i, y, 2, 2)
                                id += 1
                                self.blobs.append(b)
                            y += blob_y_distance * 4
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
                            blob = BlobEntry(id, x, y, shape, color)
                            self.blobs.append(blob)
                            id += 1
                        elif len(data) == 3:
                            x = float(data[0])
                            y = float(data[1])
                            velocity = float(data[2])
                            speed_gate = SpeedGate(0, y, velocity)
                            for i in range(-11, int(x-1), 2):
                                b = BlobEntry(id, i, y, 2, 2)
                                id += 1
                                self.blobs.append(b)
                            for i in range(int(x+3), 13, 2):
                                b = BlobEntry(id, i, y, 2, 2)
                                id += 1
                                self.blobs.append(b)
                            y += blob_y_distance * 4
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
                            blob = BlobEntry(id, x, y, shape, color)
                            self.blobs.append(blob)
                            id += 1
                        elif len(row) == 3:
                            x = float(row[0])
                            y = float(row[1])
                            velocity = float(row[2])
                            speed_gate = SpeedGate(0, y, velocity)
                            for i in range(-11, int(x-1), 2):
                                b = BlobEntry(id, i, y, 2, 2)
                                id += 1
                                self.blobs.append(b)
                            for i in range(int(x+3), 13, 2):
                                b = BlobEntry(id, i, y, 2, 2)
                                id += 1
                                self.blobs.append(b)
                            y += blob_y_distance * 4
                            self.gates.append(speed_gate)
                file.close()
                return id
        except IOError as e:
            print(os.strerror(e.errno))
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
    
    def create_objects(self, nblobs, blob_seed, task, level, is_gate_on):   
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
        # car = box(pos=(0, initial_car_y, 0), length=object_side, height=object_side, width=object_side, color=color.blue)
        car = Agent(velocity=default_start_velocity)
        left_lane = cylinder(pos=(left_lane_x, lane_back_y, rail_height), axis=(0, 1, 0), radius=lane_radius, length=lane_len, color=color.gray(0.2))
        right_lane = cylinder(pos=(right_lane_x, lane_back_y, rail_height), axis=(0, 1, 0), radius=lane_radius, length=lane_len, color=color.gray(0.2))
        
        if isRandom():
            if task == manual_speed:
                self.generate_blobs_mani(nblobs, blob_seed, is_gate_on)
            else:
                self.generate_blobs_trad(nblobs, blob_seed, is_gate_on)
        else:
            self.load_level(level=level)
        self.first_visible_blob = 0
        self.n_visible_blobs = 0
        carPos = car.getPosition()
        self.reposition_blobs(carPos.y, 0)
        # self.gate_passed(car.pos.y)
        
        return car, left_lane, right_lane
    
    def create_grid(self, path_score=0.0, blob_score=10.0, adjacent_score=0.0, start_score=5.0, goal_score=100.0):
        """
        Create the matrix of the game to represent state space

        :param blob_score: [description], defaults to 1
        :type blob_score: int, optional
        :param adjacent_score: [description], defaults to 0
        :type adjacent_score: int, optional
        """
        last_y = self.blobs[-1].y + 2 * safe_back_y
        gameGrid = Grid(y_max=last_y, path_score=path_score, 
                        blob_score=blob_score, adjacent_score=adjacent_score)
        for blob in self.blobs:
            y, x = toGridCoords(gameGrid.x_range, gameGrid.y_range,
                                           gameGrid.x_min, gameGrid.x_max, 
                                           gameGrid.y_min, gameGrid.y_max, blob)
            gameGrid.setTileScore(y, x, blob_score) # set score for the blob position tile on the game grid
            gameGrid.setAdjacentScore(y, x) # set score for the blob position adjacent tiles on the game grid
        # initialize start and end point on grid
        gameGrid.setTileScore(0, (lane_width//2+1)//2, start_score) # the car start position at the center of grid
        last_row = range(0, lane_width//2+1)
        gameGrid.setTileScore(-1, last_row, goal_score) # every tile of the last row can be considered as goal
        return gameGrid
        
    def create_graph(self, blob_score=-10):
        """Create a graph representation of the game state

        :param blob_score: score of the blob, defaults to 10
        :type blob_score: int, optional
        :return: the graph representation
        """
        gameGraph = GameGraph(blob_score)
        return gameGraph

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
    
    def gate_passed(self, xcar, ycar, is_gate_on, control_velocity):
        """Check if the car passed the gate or not

        :param xcar: the horizontal coordinate of the car object
        :type xcar: float
        :param ycar: the vertical coordinate of the car object
        :type ycar: float
        :param is_gate_on: check if the player want to have gates
        :type is_gate_on: bool
        :param velocity: controlled velocity of the gate
        :type velocity: float
        :return: the controlled velocity if passed the gate
        :rtype: float
        """
        if len(self.gates) >= 1 and is_gate_on == True:     
            if self.gates[0].y < ycar - safe_back_y:
                if self.gates[0].x == int(xcar):
                    control_velocity = self.gates[0].get_velocity()
                del self.gates[0]
        return control_velocity
    
    def gridToLogFile(self, gameGrid, path_score, blob_score, adjacent_score, collision_score, car_score):
        """Create a log file to record the pathway of the car object

        :param gameGrid: the grid representation of the game
        :param path_score: score of the path
        :type path_score: float
        :param blob_score: score of the blob
        :type blob_score: float
        :param adjacent_score: score of adjacent tile to blob
        :type adjacent_score: float
        :param collision_score: penalty on collision
        :type collision_score: float
        :param car_score: the traverse path of the score set as car_score
        :type car_score: float
        """
        now = datetime.datetime.now()
        dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")
        file = 'logs/' + 'run' + dt_string + '.txt'
        line = ''
        with open(file, 'w') as f:
            for i in range(gameGrid.height):
                line+='|'
                for j in range(gameGrid.width):
                    if gameGrid[i][j] == path_score or gameGrid[i][j] == adjacent_score:
                        line+=' '
                    elif gameGrid[i][j] == blob_score:
                        line+='b'
                    elif gameGrid[i][j] == collision_score:
                        line+='x'
                    elif gameGrid[i][j] == car_score:
                        line+='c'
                line+='|\n'
            f.writelines(line)
            f.writelines('------------------------------------------\n')
            f.close()
    
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
        global score
        global reinforce
        
        self.define_display()
        display_rate = refresh_rate
        
        car, left_lane, right_lane = self.create_objects(total_blobs, blob_seed, task, level, is_gate_on)
       
        
        background_effect_left = 0 # how many rounds the collision effect (changed background color) will be in use
        last_collision = 0         # timestamp of the last collision
        collision_count = 0        # how many collisions so far
        collision_speed_drops = 0 # how many punished (speed decreasing) collisions
        debug_label = label(pos=car.getPosition(), height=20, border=6, box=0, opacity=0) # debug info text on the car
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
        actions = []
        step = 0
        max_velocity = velocity
        last_y = self.blobs[-1].y + 2 * safe_back_y
        carPos = car.getPosition()
        
        # set different score for different problem
        # actions_list = [Actions.LEFT, Actions.STRAIGHT, Actions.RIGHT]
        path_score = 1.0
        adjacent_score = -2.0
        start_score = 5.0
        blob_score = 10.0
        car_score = -50.0
        goal_score = -100.0
        collision_score = -1.0
        gameGrid = self.create_grid(path_score=path_score, blob_score=blob_score, adjacent_score=adjacent_score, 
                         start_score=start_score, goal_score=goal_score)
        max_depth = gameGrid.height // leap
        # print(max_depth)
        gameGraph = self.create_graph(blob_score=-99999)
        gameGraph.expand(0, 0, 6, max_depth, velocity, gameGrid)
        
        # memo = {}
        
        #input handling
        # print(actions)
        if task == agent_speed:
            # reinforce = True
            # windows = gameGrid.slidingWindow(0.5)     # 50% overlap
            # problem = ShortestPathProblem(grid=gameGrid, costFn=gameGrid.__getitem__)
            # actions, locations = aStarSearch(problem, manhattanHeuristic)
            # # for (window, window_goal) in windows:
            #     # pass
            #     # problem = ShortestPathProblem(grid=window, costFn=window.__getitem__)
            #     # actions, locations = aStarSearch(problem, manhattanHeuristic)
            
            # for location in locations:
            #     y = location[0]
            #     x = location[1]
            #     if gameGrid[y][x] == path_score:
            #         gameGrid.setTileScore(y, x, car_score)
            #     if gameGrid[y][x] == adjacent_score:
            #         gameGrid.setTileScore(y, x, car_score)
            #     if self.gameGrid[y][x] == blob_score:
            #         gameGrid.setTileScore(y, x, collision_score)
                
            # self.gridToLogFile(gameGrid, path_score, blob_score, adjacent_score, collision_score, car_score)
            reinforce = True
            MCTS_player = MCTSPlayer()
            MCTS_player.registerInitialState()  
                        
        while carPos.y < last_y and not reinforce:
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
            passed = self.reposition_blobs(carPos.y, step)
            
            # if controlled_velocity <> 0:
                # velocity = controlled_velocity
                        
            if replay:
                wheelpos = wheel_positions[step]
                throttlepos = throttle_positions[step]
            elif reinforce:
                y, x = toGridCoords(gameGrid.x_range, gameGrid.y_range,
                                              gameGrid.x_min, gameGrid.x_max, 
                                              gameGrid.y_min, gameGrid.y_max, carPos)
                if gameGrid[y][x] == path_score:
                    gameGrid.setTileScore(y, x, car_score)
                if gameGrid[y][x] == adjacent_score:
                    gameGrid.setTileScore(y, x, car_score)
                if gameGrid[y][x] == blob_score:
                    gameGrid.setTileScore(y, x, collision_score)
                
                available = gameGraph.getAvailable(gameGraph.curID)
                if len(available) == 0:
                    if (gameGrid.height == y):
                        gameGraph.finished(gameGraph.curID)
                    elif int((gameGrid.height - y) // leap) >= max_depth:
                        gameGraph.expand(gameGraph.curID, y, x, max_depth, velocity, gameGrid)     
                        # gameGraph.getAvailable(gameGraph.curID)
                    else:
                        depth = int((gameGrid.height - y) // leap)
                        gameGraph.expand(gameGraph.curID, y, x, depth, velocity, gameGrid)
                
                action = MCTS_player.get_action(gameGraph)
                gameGraph.doMove(action)
                cur_y, cur_x = gameGraph.getNodeGridPosition(gameGraph.curID)
                # print(cur_y, cur_x)
                y_dest, x_dest = toGameCoords(gameGrid.x_range, gameGrid.y_range,
                                              gameGrid.x_min, gameGrid.x_max, 
                                              gameGrid.y_min, gameGrid.y_max, cur_y, cur_x)
                duration = int(math.ceil((y_dest - carPos.y))/velocity)
                # print(y_dest, carPos.y, duration)
                # print(gameGraph.getNodeInfo(gameGraph.curID))
                # print(step)
                if duration != 0:
                    theta = math.atan((x_dest - carPos.x)/duration)
                    for _ in range(duration):
                        wheelpos = Actions.radianToWheel(theta)
                        throttlepos = 1000.0
            else:
                (w, t, b, c) = wheel.getprecise()
                wheelpos = w / 1000.0
                throttlepos = t / 1000.0
                brakepos = b / 1000.0
                clutchpos = c / 1000.0
                
                if autopiloting:
                    wheelpos = self.autopilot(carPos.x, carPos.y, velocity)  
                
            # Velocity changes here except collision effects
            if task == auto_speed or task == agent_speed:
                chosen_velocity = velocity # to be used in collision analyses
                velocity += passed * nocollision_velocity_up
                car.setVelocity(velocity)
                # velocity += nocollision_velocity_up
            elif task == manual_speed:
                throttle_ratio = 1.0*(throttlepos - pedal_neutral) / (pedal_down - pedal_neutral)
                velocity = sqrt((1.0-throttle_base)*velocity**2+2**throttle_multiply*throttle_base*throttle_ratio**throttle_power)
                chosen_velocity = velocity
            elif task == fixed_speed:
                chosen_velocity = start_velocity
            else:
                chosen_velocity = velocity
                
            if max_velocity < velocity:
                max_velocity = velocity
                
            # Steering
            xp, yp = car.move(wheelpos)
            
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
            carPos.x = xp
            carPos.y = yp
            debug_label.pos = carPos
            
            self.scene.center.x = xp
            self.scene.center.y = self.scene.center.y + velocity
            left_lane.pos.y = left_lane.pos.y + velocity
            right_lane.pos.y = right_lane.pos.y + velocity
            sys.setcheckinterval(old_interval)
            
            # Collision detection and handing
            
            car_y, car_x = toGridCoords(gameGrid.x_range, gameGrid.y_range,
                                                   gameGrid.x_min, gameGrid.x_max, 
                                                   gameGrid.y_min, gameGrid.y_max, carPos)            
            collision, collided_color = self.check_collision(carPos.x, carPos.y, step)
            # velocity = self.gate_passed(carPos.x, carPos.y, is_gate_on, velocity)
            if (collision):
                score -= gameGrid[car_y][car_x]
                collision_count = collision_count + 1
                if task == auto_speed or task == fixed_speed or task == agent_speed:
                    self.scene.background = (0.5, 0.5, 0.5)
                    background_effect_left += 5
                    if (step - last_collision > collision_grace_period):
                        if task == auto_speed or task == agent_speed:
                            velocity -= collision_velocity_down 
                            if (velocity < guaranteed_velocity):
                                velocity = guaranteed_velocity
                        collision_speed_drops = collision_speed_drops + 1
                        last_collision = step
                elif task == manual_speed:
                    penalty_time = collision_penalty_time[collided_color]
                    if self.penalty_box(carPos, penalty_time):
                        cheated = True
                    velocity = 0
            else:
                velocity = self.gate_passed(carPos.x, carPos.y, is_gate_on, velocity)
                    
            debug_label.text = 'Speed %.3f\nMaxSp %.3f\nSpeed drops %i\nCollisions %i\nBlobs %i\nGate %i ' % (velocity, max_velocity, collision_speed_drops, collision_count, self.first_visible_blob, len(self.gates))
            
            p = PathEntry()
            p.step = step
            p.x = carPos.x
            p.y = carPos.y
            p.collision = collision
            p.wheelpos = wheelpos
            p.throttlepos = throttlepos
            p.velocity = velocity
            p.chosen_velocity = chosen_velocity
            p.clock_begin = clock_begin
            p.time = datetime.datetime.fromtimestamp(time.time())
            path.append(p)
            step += 1
        
        # print(gameGrid.height)
        while carPos.y < last_y and reinforce:
            # if not batch:
            #     rate(display_rate)
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
            
            if play1:
                pause = True
                play1 = False
            elif pause:
                continue
            
            # blob housekeeping
            # passed = self.reposition_blobs(carPos.y, step)
            
            y, x = toGridCoords(gameGrid.x_range, gameGrid.y_range,
                                              gameGrid.x_min, gameGrid.x_max, 
                                              gameGrid.y_min, gameGrid.y_max, carPos)
            if gameGrid[y][x] == path_score:
                gameGrid.setTileScore(y, x, car_score)
            if gameGrid[y][x] == adjacent_score:
                gameGrid.setTileScore(y, x, car_score)
            if gameGrid[y][x] == blob_score:
                gameGrid.setTileScore(y, x, collision_score)
            
            available = gameGraph.getAvailable(gameGraph.curID)
            if len(available) == 0:
                if int((gameGrid.height - y) // leap) >= max_depth:
                    gameGraph.expand(gameGraph.curID, y, x, max_depth, velocity, gameGrid)     
                else:
                    depth = int((gameGrid.height - y) // leap)
                    gameGraph.expand(gameGraph.curID, y, x, depth, velocity, gameGrid)
            
            action = MCTS_player.get_action(gameGraph)
            gameGraph.doMove(action)
            dest_y, dest_x = gameGraph.getNodeGridPosition(gameGraph.curID)
            # print(cur_y, cur_x)
            y_dest, x_dest = toGameCoords(gameGrid.x_range, gameGrid.y_range,
                                            gameGrid.x_min, gameGrid.x_max, 
                                            gameGrid.y_min, gameGrid.y_max, dest_y, dest_x)
            duration = int(math.ceil((y_dest - carPos.y))/velocity)
            # print(duration)0
            # print(gameGraph.getNodeInfo(gameGraph.curID))
            # print(step)
            # print(action)
            if duration != 0:
                theta = math.atan((x_dest - carPos.x)/duration)
                for _ in range(duration):
                    rate(display_rate)
                    wheelpos = Actions.radianToWheel(theta)
                    throttlepos = 1000.0
                    
                    passed = self.reposition_blobs(carPos.y, step)
                    step += 1
                    chosen_velocity = velocity # to be used in collision analyses
                    velocity += passed * nocollision_velocity_up
                    car.setVelocity(velocity)
                    xp, yp = car.move(wheelpos)
                    
                    if (xp > right_lane_x - lane_margin):
                        xp = right_lane_x - lane_margin
                    if (xp < left_lane_x + lane_margin):
                        xp = left_lane_x + lane_margin
                    if max_velocity < velocity:
                        max_velocity = velocity
                    if (background_effect_left):
                        background_effect_left -= 1
                    if not background_effect_left:
                        self.scene.background = (0, 0, 0)    
                    
                    # All the movement happens here
                    old_interval = sys.getcheckinterval()
                    sys.setcheckinterval(100000)
                    carPos.x = xp
                    carPos.y = yp
                    debug_label.pos = carPos
            
                    self.scene.center.x = xp
                    self.scene.center.y = self.scene.center.y + velocity
                    left_lane.pos.y = left_lane.pos.y + velocity
                    right_lane.pos.y = right_lane.pos.y + velocity
                    sys.setcheckinterval(old_interval)
            
                    # Collision detection and handing
                    
                    # car_y, car_x = toGridCoords(gameGrid.x_range, gameGrid.y_range,
                    #                                     gameGrid.x_min, gameGrid.x_max, 
                    #                                     gameGrid.y_min, gameGrid.y_max, carPos)            
                    collision, collided_color = self.check_collision(carPos.x, carPos.y, step)
                    if (collision):
                        # score -= gameGrid[car_y][car_x]
                        collision_count = collision_count + 1
                        self.scene.background = (0.5, 0.5, 0.5)
                        background_effect_left += 5
                        if (step - last_collision > collision_grace_period):
                            velocity -= collision_velocity_down 
                            if (velocity < guaranteed_velocity):
                                velocity = guaranteed_velocity
                            collision_speed_drops = collision_speed_drops + 1
                            last_collision = step
                    else:
                        velocity = self.gate_passed(carPos.x, carPos.y, is_gate_on, velocity)
                            
                    debug_label.text = 'Speed %.3f\nMaxSp %.3f\nSpeed drops %i\nCollisions %i\nBlobs %i\nGate %i ' % (velocity, max_velocity, collision_speed_drops, collision_count, self.first_visible_blob, len(self.gates))
                    
                    p = PathEntry()
                    p.step = step
                    p.x = carPos.x
                    p.y = carPos.y
                    p.collision = collision
                    p.wheelpos = wheelpos
                    p.throttlepos = throttlepos
                    p.velocity = velocity
                    p.chosen_velocity = chosen_velocity
                    p.clock_begin = clock_begin
                    p.time = datetime.datetime.fromtimestamp(time.time())
                    path.append(p)
            else:
                break
            
            # print(gameGraph.getNodeInfo(gameGraph.curID))
                    
        # After while loop
        self.gridToLogFile(gameGrid, path_score, blob_score, adjacent_score, collision_score, car_score)
        clock_diff = path[-1].clock_begin - path[0].clock_begin
        step_diff = path[-1].step - path[0].step
        print("Time:", clock_diff)
        print("Average step duration:", clock_diff / step_diff)
        print("Steps per second", step_diff / clock_diff)
        print("Total steps", step_diff)
        print("End speed", velocity)
        print("Max speed", max_velocity)
        print("Collisions", collision_count)
        print("Collision speed drops", collision_speed_drops)
        
        start_label = label(pos=(carPos.x, carPos.y+40, carPos.z), height=24, border=10, opacity=1)
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
    elif task == agent_speed:
        s = "agent {:3.1f}".format(velocity)
    return s

class Agent:
    def __init__(self, velocity):
        self.car = box(pos=(0, initial_car_y, 0), length=object_side, height=object_side, width=object_side, color=color.blue)
        self.velocity = velocity
        
    def move(self, wheelpos):
        """Calculate the position of the car base on wheelpos

        :param wheelpos: [description]
        :type wheelpos: [type]
        :return: [description]
        :rtype: [type]
        """
        car_x = self.car.pos.x + wheelpos * self.velocity / wheel_sensitivity
        car_y = self.car.pos.y + self.velocity
        return car_x, car_y
        
    def getPosition(self):
        """Return the current position of the car object

        Returns:
            float tuple: current position of the car object
        """
        return self.car.pos
    
    # def updateVelocity(self, acceleration):
    #     """Update the velocity

    #     Args:
    #         acceleration (float): the acceleration
    #     """
    #     self.velocity += acceleration
        
    def setVelocity(self, new_velocity):
        """[summary]

        Args:
            new_velocity ([type]): [description]
        """
        self.velocity = new_velocity
        
    # def getLegalMove(self, wheelpos):
    #     legal = []
    #     car_x, _ = self.move(wheelpos)
    #     if car_x > right_lane_x - lane_margin:
    #         legal = ["Left", "Straight"]
    #         return legal
    #     if car_x < left_lane_x + lane_margin:
    #         legal = ["Right", "Straight"]
    #         return legal
    #     legal = ["Left", "Right", "Straight"]
    #     return legal