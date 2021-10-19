# -*- coding: utf-8 -*-

import numpy as np
from const import MAX_POLY

class Sequence():
    
    def __init__(self, startTimestep, length):
        self.__startTimestep = startTimestep
        self.__length = length
        self.__data = np.zeros(
                (length, MAX_POLY, 2, 2),
                dtype='int'
        ) + 128 # 1. dimension (None): timestep, 2. dimension(MAX_POLY): poly, 3. dimension(2): note_on/off, 4. dimension(2): midicode, velocity
        
    def setStartTimestep(self, startTimestep):
        self.__startTimestep = startTimestep
        
    def getStartTimestep(self):
        return self.__startTimestep
    
    def resizeLeft(self, change):
        if change < 0:
            self.__data = np.concatenate([
                np.zeros((-change, MAX_POLY, 2, 2), dtype='int') + 128,
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
                np.zeros((change, MAX_POLY, 2, 2), dtype='int') + 128
            ])
        elif change < 0:
            self.__data = self.__data[:change]
        self.__length += change
    
    def getEndTimestep(self):
        return self.__startTimestep + self.__length
    
    def addNote(self, midicode, velocity, startTimestep, endTimestep):
        if np.any(self.__data[startTimestep, -1, :] != 128) \
            or np.any(self.__data[endTimestep, -1, :] != 128):
            return False
        if np.any(self.__data[startTimestep:endTimestep+1,:,:,0] == midicode):
            return False
        i = 0
        while np.any(self.__data[startTimestep, i, 0, :] != 128):
            i += 1
        self.__data[startTimestep, i, 0, 0] = midicode
        self.__data[startTimestep, i, 0, 1] = velocity
        i = 0
        while np.any(self.__data[endTimestep, i, 1, :] != 128):
            i += 1
        self.__data[endTimestep, i, 1, 0] = midicode
        self.__data[endTimestep, i, 1, 1] = 0
        print("note added. data: ", self.__data)
        return True
    
    def getNotes(self, startTimestep, endTimestep):
        notes = []
        if endTimestep < self.getStartTimestep() \
            or startTimestep >= self.getEndTimestep():
            return notes
        startedNotes = np.zeros((128,), dtype='int')
        startTimes = np.zeros((128,), dtype='int')
        for t in range(startTimestep - self.getStartTimestep(), endTimestep - self.getStartTimestep()):
            if 0 <= t < self.__length:
                for p in range(MAX_POLY):
                    if np.any(self.__data[t, p, 0, :] != 128):
                        midicode = self.__data[t, p, 0, 0]
                        velocity = self.__data[t, p, 0, 1]
                        startedNotes[midicode] = velocity
                        startTimes[midicode] = t + self.getStartTimestep()
                for p in range(MAX_POLY):
                    if np.any(self.__data[t, p, 1, :] != 128):
                        midicode = self.__data[t, p, 1, 0]
                        startTime = startTimes[midicode]
                        endTime = t + self.getStartTimestep()
                        velocity = startedNotes[midicode]
                        notes.append((midicode, velocity, startTime, endTime))
                        startedNotes[midicode] = 0
                        startTimes[midicode] = 0
        return notes
    
    def deleteNote(self, startTimestep, endTimestep, midicode):
        for p in range(MAX_POLY):
            if self.__data[startTimestep - self.__startTimestep, p, 0, 0] == midicode:
                self.__data[startTimestep - self.__startTimestep, p:-1, 0, :] = self.__data[startTimestep - self.__startTimestep, p+1:, 0, :]
                self.__data[startTimestep - self.__startTimestep, -1, 0, :] = 128
        for p in range(MAX_POLY):
            if self.__data[endTimestep - self.__startTimestep, p, 1, 0] == midicode:
                self.__data[endTimestep - self.__startTimestep, p:-1, 1, :] = self.__data[endTimestep - self.__startTimestep, p+1:, 1, :]
                self.__data[endTimestep - self.__startTimestep, -1, 1, :] = 128
                
        print("noteDeleted. data: ", self.__data)
            
    