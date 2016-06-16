# -*- coding: utf-8 -*-
"""
Created on Tue Jun 07 19:28:17 2016

@author: root
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Jun 06 18:54:04 2016

@author: PC-BRO
"""
from matplotlib import pyplot
import numpy as np
from matplotlib import mlab

time_tuple = (2016, 6 , 4, 17, 2 , 41, 0, 0, 0)

mainDir = '.\\Recordings\\sensors_logs\\'

time1_arr = []
time2_arr = []
time_event_arr = []
elevation1_arr = []
elevation2_arr = []
event_arr = []

data_events = open(mainDir + 'events.txt','r').readlines()
data_gem1 = open(mainDir + 'gem1.txt','r').readlines()
data_gem2 = open(mainDir + 'gem2.txt','r').readlines()

for line in data_gem1:
    #print line
    try:
        time1,elevation1 = line.split(' ')
        elevation1 = elevation1.rstrip().lstrip()
        time1_arr.append(float(time1.rstrip().lstrip()))
        elevation1_arr.append(float(elevation1))
    except:
        pass

for line in data_gem2:
    #print line
    try:
        time2,elevation2 = line.split(' ')
        elevation2 = elevation2.rstrip().lstrip()
        time2_arr.append(float(time2.rstrip().lstrip()))
        elevation2_arr.append(float(elevation2))
    except:
        pass

for line in data_events:
    #print line
    try:
        event_time,event = line.split(' ')
        event = event.rstrip().lstrip()
        time_event_arr.append(float(event_time.rstrip().lstrip()))
        event_arr.append(float(event))
    except:
        pass

time1_nparr = np.array(time1_arr)
elevation1_nparr = np.array(elevation1_arr)
time2_nparr = np.array(time2_arr)
elevation2_nparr = np.array(elevation2_arr)
event_time_nparr = np.array(time_event_arr)
event_nparr = np.array(event_arr)

#http://www.onlineconversion.com/unix_time.htm
timetag_start = 1464703482 # 1464703293 + 0  
timetag_stop =  1464703482 + 120 #1464703293 + 6


gem1_timeframe_index = [mlab.find(np.all([time1_nparr > timetag_start, time1_nparr <timetag_stop], axis=0))]
gem2_timeframe_index = [mlab.find(np.all([time2_nparr > timetag_start, time2_nparr <timetag_stop], axis=0))]
event_timeframe_index = [mlab.find(np.all([event_time_nparr > timetag_start, event_time_nparr <timetag_stop], axis=0))]

gem1_event_data = elevation1_nparr[gem1_timeframe_index]
gem1_time_data = time1_nparr[gem1_timeframe_index]

gem2_event_data = elevation2_nparr[gem2_timeframe_index]
gem2_time_data = time2_nparr[gem2_timeframe_index]

event_time_data = event_time_nparr[event_timeframe_index]
event_data = event_nparr[event_timeframe_index]

pyplot.close('all')

if len(gem1_time_data) > 0 and len(gem2_time_data) > 0:
    a = pyplot.figure()
    pyplot.ylim([0,180])
    pyplot.plot(gem1_time_data - timetag_start,gem1_event_data,'r')
    a.hold()
    pyplot.plot(gem2_time_data - timetag_start,gem2_event_data,'g')
    a.hold()
    pyplot.plot(event_time_data - timetag_start,event_data*40,'*')
    
    
    a.gca().invert_yaxis()
    pyplot.title('elevation')
    pyplot.show()
else :
    print len(gem1_event_data),len(gem2_event_data)