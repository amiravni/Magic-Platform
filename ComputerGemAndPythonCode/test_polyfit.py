# -*- coding: utf-8 -*-
"""
Created on Mon Jul 04 19:00:03 2016

@author: PC-BRO
"""

import numpy as np
from matplotlib import pylab

def createElevationVectorAfterPolyfit(x,y):
    f = np.polyfit(x,y,1)
    return  np.polyval(f,x)
    
x = [1,2,3,4,5,6,7]
y = [1,4,9,16,25,36,49]
new_y = createElevationVectorAfterPolyfit(x,y)
#print new_y

a = pylab.figure()
pylab.plot(x,y)
a.hold()
pylab.plot(x,new_y)

pylab.show()