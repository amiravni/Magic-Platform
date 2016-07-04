#misc
import os
import serial
import struct
import time
#Threads
from thread import start_new_thread
from threading import Lock
#Math and plots
import numpy as np
from matplotlib import mlab
import matplotlib.pyplot as plt
#Our includes
from gemsdk import *
from Quaternion2 import Quaternion2
from myVideoWriter import myVideoWriter
from platform_communication_handler import platformCommunicationHandler as pch

workingFlag = 0

def createElevationVectorAfterPolyfit(x,y):
    f = np.polyfit(x,y,1)
    return  np.polyval(f,x)
    

def get_elevation(quat):
    x, y, z = np.eye(3)
    rots = [Quaternion2.from_v_theta(x, theta) for theta in (np.pi / 2, -np.pi / 2)]
    rots += [Quaternion2.from_v_theta(y, theta) for theta in (np.pi / 2, -np.pi / 2)]
    rots += [Quaternion2.from_v_theta(y, theta) for theta in (np.pi, 0)]        
    one_face = np.array([[1, 1, 1], [1, -1, 1], [-1, -1, 1], [-1, 1, 1]])

    Rs = [(quat * rot).as_rotation_matrix() for rot in rots]
    faces = [np.dot(one_face, R.T) for R in Rs]
    vecNew = np.sum(faces[2].T,1)/4 # XZY
    elevationNew = (180/np.pi)*np.arctan2(np.sqrt(vecNew[0]**2 + vecNew[2]**2), vecNew[1])
    return elevationNew 


def onStatusUpdate(st):
    if st!=1:
        gems[0].connect()
    print "1) status update",st
    return 0

def onStatusUpdate2(st):
    if st!=1:
        gems[1].connect()
    print "2) status update",st
    return 0

def onCombinedData(quaternions,acceleration):
 #   tic = time.time()
        
    gems_data_lock[0].acquire()
    try:
        gems_elev_data[0][gems_elev_data_counter[0]] = get_elevation(Quaternion2.from_xyzw(quaternions[:4]))
        gems_elev_data_time[0][gems_elev_data_counter[0]] = time.time()
        if gems_last_data[0] != gems_elev_data[0][gems_elev_data_counter[0]]:
            gems_last_data[0] = gems_elev_data[0][gems_elev_data_counter[0]]
            gems_elev_data_counter[0] += 1  
        else:
            print "DEBUG: Duplicate data, ignoring..."
    finally:
        gems_data_lock[0].release()

    gem1_data_time = time.time()
    print >> gem_1_fd,gem1_data_time ,quaternions[:4],gems_elev_data[0][gems_elev_data_counter[0]-1]
    gems_last_data_timestamps[0] = gem1_data_time 
    gem_1_fd.flush()
 #   print "1: %.5f"%((time.time() - tic)   )
    return 0

def onCombinedData2(quaternions,acceleration):
 #   tic = time.time()
    gems_data_lock[1].acquire()
    try:
        gems_elev_data[1][gems_elev_data_counter[1]] = get_elevation(Quaternion2.from_xyzw(quaternions[:4]))
        gems_elev_data_time[1][gems_elev_data_counter[1]] = time.time()
        if gems_last_data[1] != gems_elev_data[0][gems_elev_data_counter[1]]:
            gems_last_data[1] = gems_elev_data[1][gems_elev_data_counter[1]]
            gems_elev_data_counter[1] += 1  
        else:
            print "DEBUG: Duplicate data, ignoring..."            
        #print "2) ::: " ,gems_elev_data_counter[1]
    finally:
        gems_data_lock[1].release()
        
    gem2_data_time = time.time()
    print >> gem_2_fd,gem2_data_time ,quaternions[:4],gems_elev_data[1][gems_elev_data_counter[1]-1]
    gems_last_data_timestamps[1] = gem2_data_time
    gem_2_fd.flush()
 #   print "2: %.5f"%((time.time() - tic)   )
    return 0

gems = [None,None]
gems_last_data = [0,0]
gems_last_data_timestamps = [0,0]
gems_elev_data = [range(0,200),range(0,200)]
gems_elev_data_counter = [0,0]
gems_data_lock = [Lock(),Lock()]

gems_elev_data_time = [range(0,200),range(0,200)]

workingFlag = 0
last_case = 0

HAND_DOWN = -1
HAND_UP = 1
HAND_UNKWON = 0

hands_trend = [0,0] # 1 - up, -1 - down, 0 - unkwon

EXPIRED_CONNECTION_TIMEOUT = 0.5
VECTOR_SIZE = 20
MAX_VECTOR_SIZE = 100
ELEVATION_THRESHOLD = 20.0
ELEVATION_TREND_PRECENT = 0.8
HAND_ON_FLOOR = 110
HAND_ON_FLOOR_MAX = 160
def CheckElevation(vec):
    #print vec
    step = 1.0/len(vec)
    vec_after_polyfit = createElevationVectorAfterPolyfit(mlab.frange(0,1-step,step),vec)
    vec_diff =  np.diff(np.array(vec_after_polyfit))
    elChange = vec_after_polyfit[-1] - vec_after_polyfit[1];
    if (elChange > ELEVATION_THRESHOLD):
        #print 'DOWN'
        if (mlab.find(vec_diff >= 0).size > VECTOR_SIZE*ELEVATION_TREND_PRECENT):
            return elChange,HAND_DOWN
    elif (elChange < -ELEVATION_THRESHOLD):
        #print 'UP'
        if (mlab.find(vec_diff <= 0).size > VECTOR_SIZE*ELEVATION_TREND_PRECENT):
            return elChange,HAND_UP
    return 0,HAND_UNKWON


def main_thread_loop():
    global workingFlag
    global last_case
    led_tic = time.time()
    dup_gem1_vec = []
    dup_gem2_vec = []
    dup_gem1_counter = []
    dup_gem2_counter = []
    dup_gem1_last_timestamp = 0
    dup_gem2_last_timestamp = 0
    
    while True:
        #tic = time.time()    
        time.sleep(0.01)
        
        if  time.time() - led_tic > 10:
            platform_controller.turn_leds_on()
            led_tic = time.time()
            print >> events_fd,time.time(),"sent LED"
            events_fd.flush()

    
        gems_data_lock[0].acquire()
        try:
            if gems_elev_data_counter[0] > MAX_VECTOR_SIZE:
                gems_elev_data[0][0:VECTOR_SIZE] = gems_elev_data[0][MAX_VECTOR_SIZE - VECTOR_SIZE:MAX_VECTOR_SIZE]
                gems_elev_data_time[0][0:VECTOR_SIZE] = gems_elev_data_time[0][MAX_VECTOR_SIZE - VECTOR_SIZE:MAX_VECTOR_SIZE]                
                gems_elev_data_counter[0] = VECTOR_SIZE
            dup_gem1_vec = gems_elev_data[0][:]
            dup_gem1_counter = gems_elev_data_counter[0]
            dup_gem1_last_timestamp = gems_last_data_timestamps[0]
        finally:
            gems_data_lock[0].release()
            
        gems_data_lock[1].acquire()
        try:
            if gems_elev_data_counter[1] > MAX_VECTOR_SIZE:
                gems_elev_data[1][0:VECTOR_SIZE] = gems_elev_data[1][MAX_VECTOR_SIZE - VECTOR_SIZE:MAX_VECTOR_SIZE]
                gems_elev_data_time[1][0:VECTOR_SIZE] = gems_elev_data_time[1][MAX_VECTOR_SIZE - VECTOR_SIZE:MAX_VECTOR_SIZE]
                gems_elev_data_counter[1] = VECTOR_SIZE
            dup_gem2_vec = gems_elev_data[1][:]
            dup_gem2_counter = gems_elev_data_counter[1]
            dup_gem2_last_timestamp = gems_last_data_timestamps[0]
        finally:
            gems_data_lock[1].release()

        if gems[0] is None or gems[1] is None:
            continue

        if (time.time() - dup_gem1_last_timestamp >  EXPIRED_CONNECTION_TIMEOUT ) or (time.time() - dup_gem2_last_timestamp > EXPIRED_CONNECTION_TIMEOUT):
           continue
       
        if dup_gem1_counter < VECTOR_SIZE or dup_gem2_counter < VECTOR_SIZE:
            continue
        
        #print "gems_elev_data_counter[0]-VECTOR_SIZE+1",gems_elev_data_counter[0]-VECTOR_SIZE,gems_elev_data_counter[0]
        hand1_elevation_deg,hand_trend1 = CheckElevation(dup_gem1_vec[dup_gem1_counter-VECTOR_SIZE+1:dup_gem1_counter-1])
        hands_trend[0] = hand_trend1
        
        hand2_elevation_deg,hand_trend2 = CheckElevation(dup_gem2_vec[dup_gem2_counter-VECTOR_SIZE+1:dup_gem2_counter-1])
        hands_trend[1] = hand_trend2

#        print last_case,hands_trend, gems_elev_data[0][gems_elev_data_counter[0]-1],gems_elev_data[1][gems_elev_data_counter[1]-1]
        if hands_trend[0] == HAND_DOWN and hands_trend[1] == HAND_UNKWON and dup_gem2_vec[dup_gem2_counter-1] > HAND_ON_FLOOR and dup_gem1_vec[dup_gem1_counter-1] < HAND_ON_FLOOR_MAX:
            if last_case != 1:    
                print >> events_fd,time.time(), 'CASE 1 ::: hand 1 down,hand 2 on the floor'
             #   print "Was something 1"                
                events_fd.flush()
                platform_controller.move_forward()
            last_case = 1
            
        elif hands_trend[1] == HAND_DOWN and hands_trend[0] == HAND_UNKWON and dup_gem1_vec[dup_gem1_counter-1] > HAND_ON_FLOOR and dup_gem2_vec[dup_gem2_counter-1] < HAND_ON_FLOOR_MAX:
            if last_case != 2:            
                print >> events_fd,time.time(), 'CASE 2 ::: hand 2 down,hand 1 on the floor'
             #   print "Was something 2"                
                events_fd.flush()
                platform_controller.move_forward()  
            last_case = 2
            
        elif hands_trend[0] == HAND_UP and hands_trend[1] == HAND_UNKWON and dup_gem2_vec[dup_gem2_counter-1] > HAND_ON_FLOOR and dup_gem1_vec[dup_gem1_counter-1] < HAND_ON_FLOOR_MAX:
            if last_case != 3:          
                print >> events_fd,time.time(), 'CASE 3 ::: hand 1 up and hand 2 floor'
             #   print "Was something 3"                
                events_fd.flush()
                platform_controller.move_forward() 
            last_case = 3
            
        elif hands_trend[1] == HAND_UP and hands_trend[0] == HAND_UNKWON and dup_gem1_vec[dup_gem1_counter-1] > HAND_ON_FLOOR and dup_gem2_vec[dup_gem2_counter-1] < HAND_ON_FLOOR_MAX:
            if last_case != 4:          
                print >> events_fd,time.time(), 'CASE 4 ::: hand 2 up and hand 1 floor'
            #    print "Was something 4"
                events_fd.flush()
                platform_controller.move_forward() 
            last_case = 4            
        else:
            last_case = 0
        #print "Lock: %.5f"%((time.time() - tic)   )

def figure_thread_loop():   
    global workingFlag
    global last_case
    plt.figure(2)
    mngr = plt.get_current_fig_manager()
    mngr.window.setGeometry(250,250,650, 650)
    plt.ion()    
    plt.gca().invert_yaxis()
    plt.figure(3)
    mngr = plt.get_current_fig_manager()
    mngr.window.setGeometry(1050,250,650, 650)    
    plt.ion()    
    plt.gca().invert_yaxis()
   # xList = range(1,VECTOR_SIZE-1)
    
    while True:
        if gems_elev_data_counter[0] < VECTOR_SIZE or gems_elev_data_counter[1] < VECTOR_SIZE:
            continue
        print "Ready!"
        return
        plt.figure(2)
        plt.clf()
        try: 
            xList = range(1,VECTOR_SIZE-1) #gems_elev_data_time[0][gems_elev_data_counter[0]-VECTOR_SIZE+1:gems_elev_data_counter[0]-1] - np.ones(VECTOR_SIZE - 2) * gems_elev_data_time[0][gems_elev_data_counter[0]-VECTOR_SIZE+1]
        except:
            print "continueing...."
            continue
        vec = gems_elev_data[0][gems_elev_data_counter[0]-VECTOR_SIZE+1:gems_elev_data_counter[0]-1]
        step = 1.0/len(vec)
        vec_after_polyfit = createElevationVectorAfterPolyfit(mlab.frange(0,1-step,step),vec)       
#print gems_elev_data_counter[0], gems_elev_data_time[0][gems_elev_data_counter[0]-VECTOR_SIZE+1],gems_elev_data_time[0][gems_elev_data_counter[0]-1]       
        if last_case == 0:
            if gems_elev_data[0][gems_elev_data_counter[0]-1] > HAND_ON_FLOOR:
                plt.scatter(xList,vec_after_polyfit ,c='r')
            else:
                plt.scatter(xList, vec_after_polyfit,c='b')
        else:
            plt.scatter(xList, vec_after_polyfit,c='r',s=80, marker='x')
            plt.scatter(xList, vec,c='r',s=80)
        #plt.axis([-0.1, 1.1, 0, 180])
        plt.axis([0, VECTOR_SIZE, 0, 180])   
        plt.gca().invert_yaxis()
        plt.draw() 
        
        plt.figure(3)
        plt.clf()   
        xList = range(1,VECTOR_SIZE-1) #gems_elev_data_time[1][gems_elev_data_counter[1]-VECTOR_SIZE+1:gems_elev_data_counter[1]-1] - np.ones(VECTOR_SIZE - 2) * gems_elev_data_time[1][gems_elev_data_counter[1]-VECTOR_SIZE+1]
        vec = gems_elev_data[1][gems_elev_data_counter[1]-VECTOR_SIZE+1:gems_elev_data_counter[1]-1]
        step = 1.0/len(vec)
        vec_after_polyfit = createElevationVectorAfterPolyfit(mlab.frange(0,1-step,step),vec)       
        if last_case == 0:
            if gems_elev_data[1][gems_elev_data_counter[1]-1] > HAND_ON_FLOOR:
                plt.scatter(xList, vec_after_polyfit,c='r')
            else:
                plt.scatter(xList, vec_after_polyfit,c='b')
        else:
            plt.scatter(xList, vec_after_polyfit,c='r',s=80, marker='x') 
            plt.scatter(xList, vec,c='r',s=80)
        #plt.axis([-0.1, 1.1, 0, 180])   
        plt.axis([0, VECTOR_SIZE, 0, 180])   

        plt.gca().invert_yaxis()
        plt.draw() 
            
        plt.pause(0.00001)        

      
platform_controller = pch('COM4')

session_name = str(time.time())

gem_1_fd = None
gem_2_fd = None
events_fd = None

if __name__ == '__main__':

    
    os.mkdir(session_name)
    gem_1_fd = open(session_name+"/gem1.txt",'w')    
    gem_2_fd = open(session_name+"/gem2.txt",'w')
    events_fd = open(session_name+"/events.txt",'w')

    mvw = myVideoWriter()
    mvw.init(0,session_name+"/video.avi")
    mvw.startCapture()   

    gemMgr = GemManager()
    
    gems[0] = gemMgr.Gems.values()[0]
    res = gems[0].setCallbacks(onStatusUpdate,onCombinedData)
    gems[0].connect()
    
    if len(gemMgr.Gems) > 1:
        gems[1] = gemMgr.Gems.values()[1]
        gems[1].setCallbacks(onStatusUpdate2,onCombinedData2)        
        gems[1].connect()
    
    start_new_thread(main_thread_loop,())
    start_new_thread(figure_thread_loop,())

    while True:
        time.sleep(0.01)
