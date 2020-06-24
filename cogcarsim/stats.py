# -*- coding: utf-8 -*-

import os
import sqlite3
import os.path
import sys
import errno

version = "2012-11-20-A"

global results_dbfile
results_dbfile = str.replace(sys.argv[0], '.py', '.db', 1)
manual_speed = 1
auto_speed = 0
fixed_speed = 2

score_list_len = 10

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
    def save(dbfilename, date, path, blobs, participant, run, task, seed, start_velocity, collisions, speed_drops, description, level):
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
                          collisions, speed_drops, level, duration, distance, steps, version, description))
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
