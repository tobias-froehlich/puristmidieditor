# -*- coding: utf-8 -*-

import numpy as np
from const import MAX_POLY

class Sequence():
    
    def __init__(self, startTimestep, length):
        self.__startTimestep = startTimestep
        self.__length = length
        self.__data = np.zeros(
                (length, MAX_POLY, 3),
                dtype='int'
        ) # 1. dimension: timestep, 2. dimension: poly, 3. dimension: note_on/off, midicode, velocity
        
    def setStartTimestep(self, startTimestep):
        self.__startTimestep = startTimestep
        
    def getStartTimestep(self):
        return self.__startTimestep
    
    def resizeLeft(self, change):
        if change < 0:
            self.__data = np.concatenate([
                np.zeros((-change, MAX_POLY, 3), dtype='int'),
                self.__data
            ])
        elif change > 0:
            self.__data = self.__data[change:]
        self.__length -= change
        self.__startTimestep += change
    
    def resizeRight(self, change):
        if change > 0:
            self.__data = np.concatenate([
                self.__data,
                np.zeros((change, MAX_POLY, 3), dtype='int')
            ])
        elif change < 0:
            self.__data = self.__data[:change]
        self.__length += change
    
    def getEndTimestep(self):
        return self.__startTimestep + self.__length
    
    def addNote(self, midicode, velocity, startTimestep, endTimestep):
        if self.__data[startTimestep, -1, 0] > 0 \
            or self.__data[endTimestep, -1, 0] > 0:
            return False
        if (startTimestep == endTimestep):
            if self.__data[startTimestep, -2, 0] > 0:
                return False
        if np.any(self.__data[startTimestep:endTimestep+1,:,1] == midicode):
            return False
        i = 0
        while self.__data[startTimestep, i, 0] > 0:
            i += 1
        self.__data[startTimestep, i, 0] = 1
        self.__data[startTimestep, i, 1] = midicode
        self.__data[startTimestep, i, 2] = velocity
        i = 0
        while self.__data[endTimestep, i, 0] > 0:
            i += 1
        self.__data[endTimestep, i, 0] = 2
        self.__data[endTimestep, i, 1] = midicode
        self.__data[endTimestep, i, 2] = 0
        print("note added. data: ", self.__data)
        return True