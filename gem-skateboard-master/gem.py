from gemsdk import *
from Tkinter import *
import time
from Quaternion import Quat
import eulerangles
import time 
from thread import start_new_thread
from threading import Lock
import numpy as np
from matplotlib import mlab
import transformations
import serial
import struct

rad2deg = (180/3.141592653589793)
deg2rad = (3.141592653589793/180)

master = Tk()
canvas_center = 250
w = Canvas(master, width=canvas_center * 2, height=100)
w.pack()
w2 = Canvas(master, width=canvas_center * 2, height=100)
w2.pack()
w3 = Canvas(master, width=canvas_center * 2, height=100)
w3.pack()
w4 = Canvas(master, width=canvas_center * 2, height=100)
w4.pack()

def measures2elevation(roll,pitch,yaw):
    Re = transformations.euler_matrix(deg2rad*roll, deg2rad*pitch, deg2rad*yaw, 'rxyz')
    vecRot = np.matrix(Re[0:3,0:3].T) * np.matrix([1,0,0]).T
    return rad2deg*np.arctan2(np.sqrt(vecRot[0,0]**2 + vecRot[1,0]**2), vecRot[2,0])
    
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
    
    quat = Quat(quaternions[:4])
    
    gems_data_lock[0].acquire()
    try:
        gems_elev_data[0][gems_elev_data_counter[0]] = measures2elevation(quat.ra,quat.roll,quat.dec)
        gems_elev_data_counter[0] += 1  
        #print "1) ::: " ,gems_elev_data_counter[0]
    finally:
        gems_data_lock[0].release()

    

    gems_last_data_timestamps[0] = time.time()
    
    #euler_z,euler_y,euler_x = eulerangles.quat2euler(quat)
    
    #print quat[0],quat[1],quat[2],quat[3],euler_z,euler_y,euler_x,
    #print "1) %.3f"%time.time(),quat.ra,quat.roll,quat.dec,acceleration[0],acceleration[1],acceleration[2] #pitch,roll,yaw
    #print quat.ra,quat.dec,quat.roll
    #print quaternions[:4],acceleration[:3]
    w.delete(ALL)
    w.create_rectangle(canvas_center, 10, canvas_center + 100 * acceleration[0], 30, fill="red")
    w.create_rectangle(canvas_center, 40, canvas_center + 100 * acceleration[1], 60, fill="green")
    w.create_rectangle(canvas_center, 70, canvas_center + 100 * acceleration[2], 90, fill="blue")

    w2.delete(ALL)
    w2.create_rectangle(canvas_center, 10, canvas_center + (100.0/360.0) * (quat.ra-180), 30, fill="red")
    w2.create_rectangle(canvas_center, 40, canvas_center + (100.0/360.0) * (quat.roll-180), 60, fill="green")
    w2.create_rectangle(canvas_center, 70, canvas_center + (100.0/360.0) * quat.dec, 90, fill="blue")
		
	
    #print acceleration[0],acceleration[1],acceleration[2]
    return 0

def onCombinedData2(quaternions,acceleration):
    
    quat = Quat(quaternions[:4])
    
    gems_data_lock[1].acquire()
    try:
        gems_elev_data[1][gems_elev_data_counter[1]] = measures2elevation(quat.ra,quat.roll,quat.dec)
        gems_elev_data_counter[1] += 1  
        #print "2) ::: " ,gems_elev_data_counter[1]
    finally:
        gems_data_lock[1].release()
    gems_last_data_timestamps[1] = time.time()

    #euler_z,euler_y,euler_x = eulerangles.quat2euler(quat)
    
    #print quat[0],quat[1],quat[2],quat[3],euler_z,euler_y,euler_x,
    #print "2) %.3f"%time.time(),quat.ra,quat.roll,quat.dec,acceleration[0],acceleration[1],acceleration[2] #roll,pitch,yaw

    #print quat.ra,quat.dec,quat.roll
    #print quaternions[:4],acceleration[:3]
    w3.delete(ALL)
    w3.create_rectangle(canvas_center, 10, canvas_center + 100 * acceleration[0], 30, fill="red")
    w3.create_rectangle(canvas_center, 40, canvas_center + 100 * acceleration[1], 60, fill="green")
    w3.create_rectangle(canvas_center, 70, canvas_center + 100 * acceleration[2], 90, fill="blue")

    w4.delete(ALL)
    w4.create_rectangle(canvas_center, 10, canvas_center + (100.0/360.0) * (quat.ra-180), 30, fill="red")
    w4.create_rectangle(canvas_center, 40, canvas_center + (100.0/360.0) * (quat.roll-180), 60, fill="green")
    w4.create_rectangle(canvas_center, 70, canvas_center + (100.0/360.0) * quat.dec, 90, fill="blue")
		
	
    #print acceleration[0],acceleration[1],acceleration[2]
    return 0

gems = [None,None]
gems_last_data_timestamps = [0,0]
gems_elev_data = [range(0,200),range(0,200)]
gems_elev_data_counter = [0,0]
gems_data_lock = [Lock(),Lock()]

last_case = 0

HAND_DOWN = -1
HAND_UP = 1
HAND_UNKWON = 0

hands_trend = [0,0] # 1 - up, -1 - down, 0 - unkwon

EXPIRED_CONNECTION_TIMEOUT = 0.5
VECTOR_SIZE = 50
MAX_VECTOR_SIZE = 100
ELEVATION_THRESHOLD = 50.0
ELEVATION_TREND_PRECENT = 0.5

def CheckElevation(vec):
    #print vec
    vec_diff =  np.diff(np.array(vec))
    elChange = vec[-1] - vec[1];
    if (elChange > ELEVATION_THRESHOLD):
        #print 'DOWN'
        if (mlab.find(vec_diff > 0).size > VECTOR_SIZE*ELEVATION_TREND_PRECENT):
            return elChange,HAND_DOWN
    elif (elChange < -ELEVATION_THRESHOLD):
        #print 'UP'
        if (mlab.find(vec_diff < 0).size > VECTOR_SIZE*ELEVATION_TREND_PRECENT):
            return elChange,HAND_UP
    return 0,HAND_UNKWON


def main_thread_loop():
    last_case = 0
    
    while True:
        time.sleep(0.01)

        if gems_elev_data_counter[0] > MAX_VECTOR_SIZE:
            gems_data_lock[0].acquire()
            try:
                gems_elev_data[0][0:VECTOR_SIZE] = gems_elev_data[0][VECTOR_SIZE:MAX_VECTOR_SIZE]
                gems_elev_data_counter[0] = VECTOR_SIZE
            finally:
                gems_data_lock[0].release()
        
        if gems_elev_data_counter[1] > MAX_VECTOR_SIZE:
            gems_data_lock[1].acquire()
            try:
                gems_elev_data[1][0:VECTOR_SIZE] = gems_elev_data[1][VECTOR_SIZE:MAX_VECTOR_SIZE]
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

        print hands_trend, gems_elev_data[0][gems_elev_data_counter[0]-1],gems_elev_data[1][gems_elev_data_counter[1]-1]
        if last_case != 1 and hands_trend[0] == HAND_DOWN and hands_trend[1] == HAND_UNKWON and gems_elev_data[1][gems_elev_data_counter[1]-1] > 110:
            print 'CASE 1 ::: hand 1 down,hand 2 on the floor'
            last_case = 1
            ser.write(struct.pack('B'*8,255,254,100,1,1,150,150,0))
            ser.write(struct.pack('B'*8,255,254,100,1,1,150,150,0))
            ser.write(struct.pack('B'*8,255,254,100,1,1,150,150,0))
            ser.flush()
        elif last_case != 2 and hands_trend[1] == HAND_DOWN and hands_trend[0] == HAND_UNKWON and gems_elev_data[0][gems_elev_data_counter[0]-1] > 110:
            print 'CASE 2 ::: hand 2 down,hand 1 on the floor'
            last_case = 2
            ser.write(struct.pack('B'*8,255,254,100,1,1,150,150,0))
            ser.write(struct.pack('B'*8,255,254,100,1,1,150,150,0))
            ser.write(struct.pack('B'*8,255,254,100,1,1,150,150,0))
            ser.flush()
        elif last_case != 3 and hands_trend[0] == HAND_UP and hands_trend[1] == HAND_UNKWON and gems_elev_data[1][gems_elev_data_counter[1]-1] > 110:
            print 'CASE 3 ::: hand 1 up and hand 2 floor'
            last_case = 3
            ser.write(struct.pack('B'*8,255,254,100,1,1,150,150,0))
            ser.write(struct.pack('B'*8,255,254,100,1,1,150,150,0))
            ser.write(struct.pack('B'*8,255,254,100,1,1,150,150,0))
            ser.flush()
        elif last_case != 4 and hands_trend[1] == HAND_UP and hands_trend[0] == HAND_UNKWON and gems_elev_data[0][gems_elev_data_counter[0]-1] > 110:
            print 'CASE 4 ::: hand 2 up and hand 1 floor'
            last_case = 4
            ser.write(struct.pack('B'*8,255,254,100,1,1,150,150,0))
            ser.write(struct.pack('B'*8,255,254,100,1,1,150,150,0))
            ser.write(struct.pack('B'*8,255,254,100,1,1,150,150,0))            
            ser.flush()            
        else:
            lase_case = 0
ser = serial.Serial('COM10',baudrate=9600)
if __name__ == '__main__':
    gemMgr = GemManager()
    
    gems[0] = gemMgr.Gems.values()[0]
    res = gems[0].setCallbacks(onStatusUpdate,onCombinedData)
    gems[0].connect()
    
    if len(gemMgr.Gems) > 1:
        gems[1] = gemMgr.Gems.values()[1]
        gems[1].setCallbacks(onStatusUpdate2,onCombinedData2)        
        gems[1].connect()
    
    start_new_thread(main_thread_loop,())
    mainloop()
