from cogCarSim import *
from stats import *

def get_name():
    global current_level
    is_gate_on = True
    
    speed = default_start_velocity
    min_speed = 0.3
    max_speed = 4.0
    speed_increase = 0.1
    
    task = 0
    focus = 0
    
    tasknames = ["Auto", "Manual", "Fixed", "Fixed series",  "Agent"]
    speed_changable = [True, False, True, False, True]
    
    bc = tc = (1.0, 1.0, 1.0)
    angle = 0.01
    
    scene = display(title='CogCarSim', exit=1, fullscreen=True, width=1920, height=1080, background=(0,0,0), autoscale=False)
    scene.select()
    
    laatta1 = box(pos=(-6.5,0,0), size=(3,3,3), color=color.blue)
    laatta2 = box(pos=(6.5,0,0), size=(3,3,3), color=color.blue)
    
    title = label(pos=(0, 5.0, 0), text="CogCarSim", height=80, opacity=0, box=0)
    name_prompt = label(pos=(-2, 3, 0), text="Name", height=30, opacity=0, box=0)
    name = label(pos=(1.5, 3, 0), height=30, width=100, linecolor=bc, color=tc)
    task_prompt = label(pos=(-2,1.5,0), text="Game", height=30, linecolor=tc, opacity=0, box=0)
    task_label = label(pos=(1.5,1.5,0), height=30, border=10, opacity=0, linecolor=bc, color=tc, box=0) 
    speed_prompt = label(pos=(-2,0,0), text="Speed", height=30, linecolor=tc, opacity=0, box=0)
    speed_label = label(pos=(1.5,0,0), height=30, border=10, opacity=1, linecolor=bc, color=tc, box=0)
    gate_prompt = label(pos=(-2,-1.5,0), text="Gate", height=30, linecolor=tc, opacity=0, box=0)
    gate_label = label(pos=(1.5,-1.5,0), text="On", height=30, border=10, opacity=1, linecolor=bc, color=tc, box=0)
    level_prompt = label(pos=(-2, -3, 0), text="Level", height=30, opacity=0, box=0)
    level = label(pos=(1.5, -3, 0), height=30, width=50, linecolor=bc, color=tc, box=0)
    next_level = label(pos=(4.5, -3, 0), text="Next_level", height=30, box=0)
    
    start_label = label(pos=(0,-4.5 ,0), height=24, border=10, opacity=1, box=0, linecolor=color.blue) 
    start_label.text = 'Please type in your name\nPress enter to start'
    
    fields = [name, task_label, speed_label, gate_label, level, next_level]
    key = ''
    while 1:
        rate(50)
        task_label.text = tasknames[task]
        speed_label.text = "{:3.1f}".format(speed)
        laatta1.rotate(angle=angle, axis=(1, 1, 1))
        laatta2.rotate(angle=-angle, axis=(1, 1, 1))
        if scene.kb.keys:
            key = scene.kb.getkey()
            if key == "escape":
                break
            if key == '\n' or key == 'f1' or key =='f2':
                break
            elif len(key) == 1 and focus == 0:
                if len(name.text) < max_name_len:
                    name.text += key    # append new character
            elif len(key) == 1 and focus == 4:
                if key.isdigit():
                    if int(key) <= len(levels):
                        level.text += key
            elif (key == 'backspace' or key == 'delete'):
                if len(name.text) > 0 and focus == 0:
                    name.text = name.text[:-1] # erase 1 letter
                if len(level.text) > 0 and focus == 4:
                    level.text = level.text[:-1]
            elif key == "right" and focus == 3:
                is_gate_on = not is_gate_on
                if is_gate_on:
                    gate_label.text = "On"
                else:
                    gate_label.text = "Off"
            elif key == "shift+delete":
                if focus == 0:
                    name.text = ''
                if focus == 4:
                    level.text = ''
            elif key == 'left':
                if focus == 0:
                    pass
                elif focus == 1:
                    task = task - 1 if task > 0 else len(tasknames)-1
                # elif focus == 2 and speed_changable[task]:
                #     speed = speed - speed_increase if speed > min_speed else min_speed
            elif key == 'right' or key == ' ':
                if focus == 0:
                    pass
                elif focus == 1:
                     task = task + 1 if task < len(tasknames)-1 else 0
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
            
        speed_label.color = (0.2, 0.2, 0.2) if task != auto_speed and task != fixed_speed and task != agent_speed else (1.0, 1.0, 1.0)
        speed_label.linecolor = (0.2, 0.2, 0.2) if task != auto_speed and task != fixed_speed and task != agent_speed  else (1.0, 1.0, 1.0)
        
    name = name.text
    level_text = level.text
    scene.visible = False
    if name == "":
        name = "Anonymous"
    if task != auto_speed and task != fixed_speed and task != agent_speed:
        speed = 0.0
    if level_text == "" and focus <> 5:
        setRandom(True)
        # setCurrentLevel(0)
        current_level = 0
    else:
        setRandom(False)
        if focus == 5:
            current_level += 1
        else:
            current_level = int(level_text)
    return name, key, task, speed, current_level, is_gate_on

def show_fame(titletext, current, subtitle, results):
    scene = display(title="CogCarSim", exit=1, fullscreen=True, width=1920, height=1080, autoscale=False)
    scene.select()
    fame_x = -1
    fame_y = 1.5
    fame_yd = 0.8
    own_x = -1
    own_y = 5
    title = label(pos=(own_x+0.8,own_y+0.8,0), text=titletext, height=50, box=0)
    ownspeed = label(pos=(own_x+0.8,own_y-1.0,0), text=current, height=100, box=0)
    l = []
    fametitle = label(pos=(fame_x+0.8, fame_y+1.0, 0), text=subtitle, height=50, box=0)
    for i in range(len(results)):
        name, result = results[i]
        append(l, label(pos=(fame_x-3.0,fame_y-i*fame_yd,0), text="%i"%(i+1), height = 30, box=0))
        append(l, label(pos=(fame_x-1.0,fame_y-i*fame_yd,0), text=result, height = 30, box=0))
        append(l, label(pos=(fame_x+3.6,fame_y-i*fame_yd,0), text=name, height = 30, box=0))
    laataa1 = box(pos=(-8.5,0,0), size=(3,3,3), color=color.blue)
    laataa2 = box(pos=(8.5,0,0), size=(3,3,3), color=color.blue)
    a = 0.02
    while 1:
        laataa1.rotate(angle=a, axis=(1,1,1))
        laataa2.rotate(angle=-a, axis=(1,1,1))
        rate(20)
        if scene.kb.keys:
            key = scene.kb.getkey()
            if key == '\n':
                scene.visible = False
                test_run()  # go to next run
            else:
                break
                scene.visible =  False

def task_string(task, velocity):
    if task == auto_speed:
        s = "auto {:3.1f}".format(velocity)
    elif task == manual_speed:
        s = "manual"
    elif task == fixed_speed:
        s = "fix {:3.1f}".format(velocity)
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
    
    if task == auto_speed or task == agent_speed:
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
    name, key, game, vel, level, is_gate_on = get_name()
    
    if key == 'f1':
        if game <= fixed_speed:
            show_high(name=None, task=game, selected_velocity=vel, collisions=None, duration=None, speed_drop=None, end_velocity=None)
        return
    
    if not game in {manual_speed, auto_speed, fixed_speed, agent_speed}:
        blob_seed, nblobs, task, selected_velocity, description = get_test_details(name, game)
    else:
        task = game
        blob_seed = random.randint(1, 10000000)
        description = "Individual"
        selected_velocity = vel
        
    sim = CogCarSim()
    if not isRandom():
        nblobs = sim.load_level(level=level)
    else:
        nblobs = number_of_blobs
    path, blobs, cheated, collisions, speed_drops, end_velocity = sim.run(start_velocity=selected_velocity, task=task,
                                                                         blob_seed=blob_seed, total_blobs=nblobs, level=level, is_gate_on=is_gate_on)
    
    if len(path) > 0:
        duration = path[-1].clock_begin - path[0].clock_begin
        if cheated:
            name = "Cheater"
    run = Stats.get_last_run_number(results_dbfile)+1
    t = time.localtime()
    date = str(datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec))
    Stats.save(dbfilename=results_dbfile, path=path, blobs=blobs, description = description,
                participant=name, run=run, task=task, seed=blob_seed, level=current_level, 
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
if len(sys.argv) == 1:
    test_run()
elif sys.argv[1] == "replay":
    if len(sys.argv) == 3:
        replay(sys.argv[2])
    else:
        replay()
               
    