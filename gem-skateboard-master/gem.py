from gemsdk import *
from Tkinter import *
import time
#from Quaternion import Quat
#import eulerangles
from thread import start_new_thread
from threading import Lock
import numpy as np
from matplotlib import mlab
import transformations
import serial
import struct
import matplotlib.pyplot as plt
from Quaternion2 import Quaternion2
#from myVideoWriter import myVideoWriter

rad2deg = (180/3.141592653589793)
deg2rad = (3.141592653589793/180)
workingFlag = 0

master = Tk()
#canvas_center = 250
#w = Canvas(master, width=canvas_center * 2, height=100)
#w.pack()
#w2 = Canvas(master, width=canvas_center * 2, height=100)
#w2.pack()
#w3 = Canvas(master, width=canvas_center * 2, height=100)
#w3.pack()
#w4 = Canvas(master, width=canvas_center * 2, height=100)
#w4.pack()
def write2arduino(ser):
    ser.write(struct.pack('B'*8,255,254,100,1,1,150,150,0))
    ser.write(struct.pack('B'*8,255,254,100,1,1,150,150,0))
    ser.write(struct.pack('B'*8,255,254,100,1,1,150,150,0))
    ser.flush()


def measures2elevation(roll,pitch,yaw):
    Re = transformations.euler_matrix(deg2rad*0, deg2rad*(pitch-90), deg2rad*0, 'rxyz')
    vecRot = np.matrix(Re[0:3,0:3].T) * np.matrix([1,0,0]).T
    return rad2deg*np.arctan2(np.sqrt(vecRot[0,0]**2 + vecRot[1,0]**2), vecRot[2,0])

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
    
#    quat = Quat(quaternions[:4])
    
    gems_data_lock[0].acquire()
    try:
        gems_elev_data[0][gems_elev_data_counter[0]] = get_elevation(Quaternion2.from_xyzw(quaternions[:4]))
        gems_elev_data_time[0][gems_elev_data_counter[0]] = time.time()
        if gems_last_data[0] != gems_elev_data[0][gems_elev_data_counter[0]]:
            gems_last_data[0] = gems_elev_data[0][gems_elev_data_counter[0]]
            gems_elev_data_counter[0] += 1  
        else:
            print "DEBUG: Duplicate data, ignoring..."
        #print "1) ::: " ,gems_elev_data_counter[0]
    finally:
        gems_data_lock[0].release()

    

    gems_last_data_timestamps[0] = time.time()
    
    #euler_z,euler_y,euler_x = eulerangles.quat2euler(quat)
    
    #print quat[0],quat[1],quat[2],quat[3],euler_z,euler_y,euler_x,
    #print "1) %.3f"%time.time(),quat.ra,quat.roll,quat.dec,acceleration[0],acceleration[1],acceleration[2] #pitch,roll,yaw
    #print quat.ra,quat.dec,quat.roll
    #print quaternions[:4],acceleration[:3]
    
    
#    w.delete(ALL)
#    w.create_rectangle(canvas_center, 10, canvas_center + 100 * acceleration[0], 30, fill="red")
#    w.create_rectangle(canvas_center, 40, canvas_center + 100 * acceleration[1], 60, fill="green")
#    w.create_rectangle(canvas_center, 70, canvas_center + 100 * acceleration[2], 90, fill="blue")
#
#    w2.delete(ALL)
#    w2.create_rectangle(canvas_center, 10, canvas_center + (100.0/360.0) * (quat.ra-180), 30, fill="red")
#    w2.create_rectangle(canvas_center, 40, canvas_center + (100.0/360.0) * (quat.roll-180), 60, fill="green")
#    w2.create_rectangle(canvas_center, 70, canvas_center + (100.0/360.0) * quat.dec, 90, fill="blue")
#		
	
    #print acceleration[0],acceleration[1],acceleration[2]
    return 0

def onCombinedData2(quaternions,acceleration):
    global ax
#    quat = Quat(quaternions[:4])
#    if 90 - np.abs(quat.dec) < 5:
    #quat = Quat([0,-quat.dec,0]) * Quat(quaternions[:4])
    #print quat.roll, quat.ra, quat.dec
    
    
    
    
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
    gems_last_data_timestamps[1] = time.time()
    #euler_z,euler_y,euler_x = eulerangles.quat2euler(quat)
    
    #print quat[0],quat[1],quat[2],quat[3],euler_z,euler_y,euler_x,
    #print "2) %.3f"%time.time(),quat.ra,quat.roll,quat.dec,acceleration[0],acceleration[1],acceleration[2] #roll,pitch,yaw

    #print quat.ra,quat.dec,quat.roll
    #print quaternions[:4],acceleration[:3]

#    w3.delete(ALL)
#    w3.create_rectangle(canvas_center, 10, canvas_center + 100 * acceleration[0], 30, fill="red")
#    w3.create_rectangle(canvas_center, 40, canvas_center + 100 * acceleration[1], 60, fill="green")
#    w3.create_rectangle(canvas_center, 70, canvas_center + 100 * acceleration[2], 90, fill="blue")
#
#    w4.delete(ALL)
#    w4.create_rectangle(canvas_center, 10, canvas_center + (100.0/360.0) * (quat.ra-180), 30, fill="red")
#    w4.create_rectangle(canvas_center, 40, canvas_center + (100.0/360.0) * (quat.roll-180), 60, fill="green")
#    w4.create_rectangle(canvas_center, 70, canvas_center + (100.0/360.0) * quat.dec, 90, fill="blue")
#		
	
    #print acceleration[0],acceleration[1],acceleration[2]
    return 0

gems = [None,None]
gems_last_data = [0,0]
gems_last_data_timestamps = [0,0]
gems_elev_data = [range(0,200),range(0,200)]
gems_elev_data_counter = [0,0]
gems_data_lock = [Lock(),Lock()]

gems_elev_data_time = [range(0,200),range(0,200)]

global workingFlag
global last_case
workingFlag = 0
last_case = 0

HAND_DOWN = -1
HAND_UP = 1
HAND_UNKWON = 0

hands_trend = [0,0] # 1 - up, -1 - down, 0 - unkwon

EXPIRED_CONNECTION_TIMEOUT = 0.5
VECTOR_SIZE = 50
MAX_VECTOR_SIZE = 100
ELEVATION_THRESHOLD = 50.0
ELEVATION_TREND_PRECENT = 0.9
HAND_ON_FLOOR = 110

def CheckElevation(vec):
    #print vec
    vec_diff =  np.diff(np.array(vec))
    elChange = vec[-1] - vec[1];
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
    
    while True:
        time.sleep(0.01)
        
        if  time.time() - led_tic > 10:
            ser.write(struct.pack('B'*8,255,254,100,1,6,150,150,0))
            ser.write(struct.pack('B'*8,255,254,100,1,6,150,150,0))
            ser.write(struct.pack('B'*8,255,254,100,1,6,150,150,0))
            led_tic = time.time()
            print "sent LED"
        if gems_elev_data_counter[0] > MAX_VECTOR_SIZE:
            gems_data_lock[0].acquire()
            try:
                gems_elev_data[0][0:VECTOR_SIZE] = gems_elev_data[0][VECTOR_SIZE:MAX_VECTOR_SIZE]
                gems_elev_data_time[0][0:VECTOR_SIZE] = gems_elev_data_time[0][VECTOR_SIZE:MAX_VECTOR_SIZE]                
                gems_elev_data_counter[0] = VECTOR_SIZE
            finally:
                gems_data_lock[0].release()
        
        if gems_elev_data_counter[1] > MAX_VECTOR_SIZE:
            gems_data_lock[1].acquire()
            try:
                gems_elev_data[1][0:VECTOR_SIZE] = gems_elev_data[1][VECTOR_SIZE:MAX_VECTOR_SIZE]
                gems_elev_data_time[1][0:VECTOR_SIZE] = gems_elev_data_time[1][VECTOR_SIZE:MAX_VECTOR_SIZE]
                gems_elev_data_counter[1] = VECTOR_SIZE
            finally:
                gems_data_lock[1].release()


        if gems[0] is None or gems[1] is None:
            continue

        if (time.time() - gems_last_data_timestamps[0] >  EXPIRED_CONNECTION_TIMEOUT ) or (time.time() - gems_last_data_timestamps[1] > EXPIRED_CONNECTION_TIMEOUT):
           continue
       
        if gems_elev_data_counter[0] < VECTOR_SIZE or gems_elev_data_counter[1] < VECTOR_SIZE:
            continue
        
        #print "gems_elev_data_counter[0]-VECTOR_SIZE+1",gems_elev_data_counter[0]-VECTOR_SIZE,gems_elev_data_counter[0]
        hand1_elevation_deg,hand_trend1 = CheckElevation(gems_elev_data[0][gems_elev_data_counter[0]-VECTOR_SIZE+1:gems_elev_data_counter[0]-1])
        hands_trend[0] = hand_trend1
        
        hand2_elevation_deg,hand_trend2 = CheckElevation(gems_elev_data[1][gems_elev_data_counter[1]-VECTOR_SIZE+1:gems_elev_data_counter[1]-1])
        hands_trend[1] = hand_trend2

#        print last_case,hands_trend, gems_elev_data[0][gems_elev_data_counter[0]-1],gems_elev_data[1][gems_elev_data_counter[1]-1]
        if hands_trend[0] == HAND_DOWN and hands_trend[1] == HAND_UNKWON and gems_elev_data[1][gems_elev_data_counter[1]-1] > HAND_ON_FLOOR:
            if last_case != 1:    
                print 'CASE 1 ::: hand 1 down,hand 2 on the floor'
                write2arduino(ser)
                workingFlag = 1
            else:
                workingFlag = 0
            last_case = 1
        elif hands_trend[1] == HAND_DOWN and hands_trend[0] == HAND_UNKWON and gems_elev_data[0][gems_elev_data_counter[0]-1] > HAND_ON_FLOOR:
            if last_case != 2:            
                print 'CASE 2 ::: hand 2 down,hand 1 on the floor'
                write2arduino(ser)  
                workingFlag = 2
            else:
                workingFlag = 0                
            last_case = 2
        elif hands_trend[0] == HAND_UP and hands_trend[1] == HAND_UNKWON and gems_elev_data[1][gems_elev_data_counter[1]-1] > HAND_ON_FLOOR:
            if last_case != 3:          
                print 'CASE 3 ::: hand 1 up and hand 2 floor'
                write2arduino(ser) 
                workingFlag = 3
            else:
                workingFlag = 0                
            last_case = 3
        elif hands_trend[1] == HAND_UP and hands_trend[0] == HAND_UNKWON and gems_elev_data[0][gems_elev_data_counter[0]-1] > HAND_ON_FLOOR:
            if last_case != 4:          
                print 'CASE 4 ::: hand 2 up and hand 1 floor'
                write2arduino(ser) 
                workingFlag = 4
            else:
                workingFlag = 0                
            last_case = 4            
        else:
            last_case = 0
            

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
        plt.figure(2)
        plt.clf()
        try: 
            xList = gems_elev_data_time[0][gems_elev_data_counter[0]-VECTOR_SIZE+1:gems_elev_data_counter[0]-1] - np.ones(VECTOR_SIZE - 2) * gems_elev_data_time[0][gems_elev_data_counter[0]-VECTOR_SIZE+1]
        except:
            print "continueing...."
            continue
        
        #print gems_elev_data_counter[0], gems_elev_data_time[0][gems_elev_data_counter[0]-VECTOR_SIZE+1],gems_elev_data_time[0][gems_elev_data_counter[0]-1]       
        if last_case == 0:
            if gems_elev_data[0][gems_elev_data_counter[0]-1] > HAND_ON_FLOOR:
                plt.scatter(xList, gems_elev_data[0][gems_elev_data_counter[0]-VECTOR_SIZE+1:gems_elev_data_counter[0]-1],c='r')
            else:
                plt.scatter(xList, gems_elev_data[0][gems_elev_data_counter[0]-VECTOR_SIZE+1:gems_elev_data_counter[0]-1],c='b')
        else:
            plt.scatter(xList, gems_elev_data[0][gems_elev_data_counter[0]-VECTOR_SIZE+1:gems_elev_data_counter[0]-1],c='r',s=80, marker='x')
        plt.axis([-0.1, 1.1, 0, 180])
        plt.gca().invert_yaxis()
        plt.draw() 
        
        plt.figure(3)
        plt.clf()   
        xList = gems_elev_data_time[1][gems_elev_data_counter[1]-VECTOR_SIZE+1:gems_elev_data_counter[1]-1] - np.ones(VECTOR_SIZE - 2) * gems_elev_data_time[1][gems_elev_data_counter[1]-VECTOR_SIZE+1]
        if last_case == 0:
            if gems_elev_data[1][gems_elev_data_counter[1]-1] > HAND_ON_FLOOR:
                plt.scatter(xList, gems_elev_data[1][gems_elev_data_counter[1]-VECTOR_SIZE+1:gems_elev_data_counter[1]-1],c='r')
            else:
                plt.scatter(xList, gems_elev_data[1][gems_elev_data_counter[1]-VECTOR_SIZE+1:gems_elev_data_counter[1]-1],c='b')
        else:
            plt.scatter(xList, gems_elev_data[1][gems_elev_data_counter[1]-VECTOR_SIZE+1:gems_elev_data_counter[1]-1],c='r',s=80, marker='x')       
        plt.axis([-0.1, 1.1, 0, 180])   
        plt.gca().invert_yaxis()
        plt.draw() 
            
        plt.pause(0.00001)        
            
#def figure_thread_loop():   
#    global workingFlag
#    global last_case
#    plt.figure(1)
#    mngr = plt.get_current_fig_manager()
#    mngr.window.setGeometry(250,250,650, 650)
#    plt.axis([-100, 100, 0, 180])
#    plt.ion()    
#    plt.figure(2)
#    mngr = plt.get_current_fig_manager()
#    mngr.window.setGeometry(1050,250,650, 650)    
#    plt.axis([-100, 100, 0, 180])
#    plt.ion()    
#    iii = 0    
#    lastValue0 = 0
#    lastValue1 = 0
#    
#    while True:
#        plt.figure(1)
##        print lastValue0 , gems_elev_data[0][gems_elev_data_counter[0]-1]
#        for jjj in range(0,9):
#            val = lastValue0 + ( gems_elev_data[0][gems_elev_data_counter[0]-1] - lastValue0 ) * (jjj/10.0)
#            plt.scatter(iii-1+jjj/10.0, val ,c='k',s=3)
#        if last_case == 0:
#            plt.scatter(iii, gems_elev_data[0][gems_elev_data_counter[0]-1],c='b')
#        else: 
#            plt.scatter(iii, gems_elev_data[0][gems_elev_data_counter[0]-1],c='r',s=80, marker='x')
#          
#        plt.figure(2)
#        for jjj in range(0,9):
#            val = lastValue1 + ( gems_elev_data[1][gems_elev_data_counter[1]-1] - lastValue1 ) * (jjj/10.0)
#            plt.scatter(iii-1+jjj/10.0, val ,c='k',s=3)        
#        if last_case == 0:
#            plt.scatter(iii, gems_elev_data[1][gems_elev_data_counter[1]-1],c='b')
#        else: 
#            plt.scatter(iii, gems_elev_data[1][gems_elev_data_counter[1]-1],c='r',s=80, marker='x')
#
#
#        plt.figure(1)
#        plt.axis([iii - 30, iii + 10, 0, 180])            
#        plt.draw()    
#        plt.figure(2)
#        plt.axis([iii - 30, iii + 10, 0, 180])            
#        plt.draw()    
#
#
#        iii += 1   
#        if gems_elev_data[0][gems_elev_data_counter[0]-1] != lastValue0:
#            lastValue0 = gems_elev_data[0][gems_elev_data_counter[0]-1]
#        if gems_elev_data[1][gems_elev_data_counter[1]-1] != lastValue1:
#            lastValue1 = gems_elev_data[1][gems_elev_data_counter[1]-1]                                 
#        plt.pause(0.00001)        
         

ser = serial.Serial('COM10',baudrate=9600)
ser.timeout = 0.01
ax = None

if __name__ == '__main__':

    gemMgr = GemManager()
    
    gems[0] = gemMgr.Gems.values()[2]
    res = gems[0].setCallbacks(onStatusUpdate,onCombinedData)
    gems[0].connect()
    
    if len(gemMgr.Gems) > 1:
        gems[1] = gemMgr.Gems.values()[1]
        gems[1].setCallbacks(onStatusUpdate2,onCombinedData2)        
        gems[1].connect()
    
    start_new_thread(main_thread_loop,())
    start_new_thread(figure_thread_loop,())
    
#    mvw = myVideoWriter()
#    mvw.init(0,'test.avi')
#    mvw.startCapture()   

    mainloop()
