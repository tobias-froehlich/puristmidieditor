# -*- coding: utf-8 -*-

import numpy as np

class Sequence():
    
    def __init__(self, startTimestep, length):
        self.__startTimestep = startTimestep
        self.__length = length
        self.__data = np.zeros(
                (length, 3),
                dtype='int'
        ) # 1. dimension: timestep, 2. dimension: note_on/off, midicode, velocity
        
    def setStartTimestep(self, startTimestep):
        self.__startTimestep = startTimestep
        
    def getStartTimestep(self):
        return self.__startTimestep
    
    def setLength(self, length):
        self.__length = length
    
    def getEndTimestep(self):
        return self.__startTimestep + self.__length