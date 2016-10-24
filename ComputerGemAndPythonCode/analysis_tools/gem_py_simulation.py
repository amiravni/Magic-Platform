# -*- coding: utf-8 -*-
"""
Created on Thu Jun 16 19:17:15 2016

@author: root
"""
import os
import numpy as np
from matplotlib import mlab
from matplotlib import pyplot

log_folder = r"E:\ForBackUp\BlogStuff\MagicPlatform\gem-skateboard-master\analysis_tools\Recordings\\"

# 170133
#startTime = 1464703293
#interestingPoints = np.array([42,83,101.64])
# 170442
#startTime = 1464703482
#interestingPoints = np.array([14,24,34,48.7,62.8,78.9,82.8])
# 172723
#startTime = 1464704843
#interestingPoints = np.array([20.6,24,42,50,77,90,93,102,118,132,152,154,156,172,174])
# 173703
#startTime = 1464964626
#interestingPoints = np.array([58,92.5,111.7,201.7])
# 170241
startTime = 1465048960.5
interestingPoints = np.array([66,190,216.6,339,345.7,392,402.8])

allLogTimes = np.array(map(float,os.listdir(log_folder)))
indexFolderName = np.argmin(np.abs(startTime - allLogTimes))
    
log_time = str(allLogTimes[indexFolderName])
print "Folder Name:   " , log_time
EXPIRED_CONNECTION_TIMEOUT = 0.5
VECTOR_SIZE = 20
MAX_VECTOR_SIZE = 100
ELEVATION_THRESHOLD = 20.0
ELEVATION_TREND_PRECENT = 0.8
HAND_ON_FLOOR = 110

"""
EXPIRED_CONNECTION_TIMEOUT = 0.5
VECTOR_SIZE = 50
MAX_VECTOR_SIZE = 100
ELEVATION_THRESHOLD = 50.0
ELEVATION_TREND_PRECENT = 0.9
HAND_ON_FLOOR = 110
"""
HAND_DOWN = -1
HAND_UP = 1
HAND_UNKWON = 0
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


def check_for_events(hands_trend,last_gem1_sample,last_gem2_sample,last_case = [HAND_UNKWON]):
    if hands_trend[0] == HAND_DOWN and hands_trend[1] == HAND_UNKWON and last_gem2_sample > HAND_ON_FLOOR:
        if last_case[0] != 1:    
      #      print 'CASE 1 ::: hand 1 down,hand 2 on the floor'
            last_case[0] = 1
            return True
        last_case[0] = 1
    elif hands_trend[1] == HAND_DOWN and hands_trend[0] == HAND_UNKWON and last_gem1_sample > HAND_ON_FLOOR:
        if last_case[0] != 2:            
      #      print 'CASE 2 ::: hand 2 down,hand 1 on the floor'
            last_case[0] = 2
            return True
        last_case[0] = 2
    elif hands_trend[0] == HAND_UP and hands_trend[1] == HAND_UNKWON and last_gem2_sample > HAND_ON_FLOOR:
        if last_case[0] != 3:          
     #       print 'CASE 3 ::: hand 1 up and hand 2 floor'
            last_case[0] = 3
            return True
        last_case[0] = 3
    elif hands_trend[1] == HAND_UP and hands_trend[0] == HAND_UNKWON and last_gem1_sample > HAND_ON_FLOOR:
        if last_case[0] != 4:          
     #       print 'CASE 4 ::: hand 2 up and hand 1 floor'
            last_case[0] = 4  
            return True
        last_case[0] = 4            
    else:
        last_case[0] = 0    
    return False
def gem_stored_data_parse_line(gem_line):
    gem_line = gem_line.replace('[','')
    gem_line = gem_line.replace(']','')
    gem_line = gem_line.replace(',','')
    try:
        time,x,y,z,w,azm =  map(float, gem_line.split(' '))
    except:
        return -1,-1,-1,-1,-1,-1
    return time,x,y,z,w,azm
    
if __name__ == '__main__':
    
    pyplot.close('all')
    gem1_data = open(log_folder + log_time + "\gem1.txt").readlines()
    gem2_data = open(log_folder + log_time + "\gem2.txt").readlines()

    gem1_counter = 0
    gem2_counter = 0
    
    time1,x,y,z,w,azm = gem_stored_data_parse_line(gem1_data[0])
    time2,x,y,z,w,azm = gem_stored_data_parse_line(gem2_data[0])
    
    start_recording_time = min([time1,time2])
    sample_time = 0.01

    global_time = start_recording_time
    
        
    gem1_elevation_data = [0]
    gem2_elevation_data = [0]

    gem1_data_counter = 0
    gem2_data_counter = 0
    hands_trend = [HAND_UNKWON,HAND_UNKWON]
    
    while gem1_counter < len(gem1_data) and gem2_counter < len(gem2_data):
        
        while True:
            if gem1_counter >= len(gem1_data):
                break
            time,x,y,z,w,azm = gem_stored_data_parse_line(gem1_data[gem1_counter])
            if (time < global_time ) or time < 0:
                if azm != gem1_elevation_data[-1]:
                    gem1_elevation_data.append(azm)
                gem1_counter += 1
            else:
                break
        if len(gem1_elevation_data) > VECTOR_SIZE:
            gem1_elevation_data = gem1_elevation_data[-VECTOR_SIZE:]
        #print gem1_counter
        
        while True:
            
            if gem2_counter >= len(gem2_data):
                break
            
            time,x,y,z,w,azm = gem_stored_data_parse_line(gem2_data[gem2_counter])
            if (time < global_time  ) or time < 0:
                if azm != gem2_elevation_data[-1]:
                    gem2_elevation_data.append(azm)
                gem2_counter += 1
            else:
                break

        #print gem2_counter
        
        if len(gem2_elevation_data) > VECTOR_SIZE:
            gem2_elevation_data = gem2_elevation_data[-VECTOR_SIZE:]
            
        
        if gem1_counter > VECTOR_SIZE and gem2_counter > VECTOR_SIZE:
            hand1_elevation_deg,hand_trend1 = CheckElevation(gem1_elevation_data[:VECTOR_SIZE])
            hands_trend[0] = hand_trend1
            
            hand2_elevation_deg,hand_trend2 = CheckElevation(gem2_elevation_data[:VECTOR_SIZE])
            hands_trend[1] = hand_trend2
    
            ret = check_for_events(hands_trend,gem1_elevation_data[-1],gem2_elevation_data[-1])
            if ret and np.min(np.abs(startTime + interestingPoints - global_time )) < 2 :
                print global_time-startTime
            
            if np.min(np.abs(startTime + interestingPoints - global_time )) <= sample_time/2:
                print '---->',global_time-startTime            
                fig = pyplot.figure()
                pyplot.plot(gem1_elevation_data)
                fig.hold()
                pyplot.plot(gem2_elevation_data)                
                fig.gca().invert_yaxis()
                pyplot.title('elevation')
                

                #import pdb;pdb.set_trace()
        global_time += sample_time
    pyplot.show()