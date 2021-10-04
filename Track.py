# -*- coding: utf-8 -*-

from const import OVERVIEW_CENTER_PANE_WIDTH
from const import OVERVIEW_TRACK_BOX_HEIGHT
from const import TRACK_RIGHT_EXTEND
from const import OVERVIEW_TIME_STEP_WIDTH

from Sequence import Sequence

import tkinter as tk
import numpy as np

class Track(tk.Frame):
    
    def __init__(self, root, editMode):
        super().__init__(
            root,
            width=OVERVIEW_CENTER_PANE_WIDTH
            + TRACK_RIGHT_EXTEND,
            height=OVERVIEW_TRACK_BOX_HEIGHT,
            relief="raised",
            borderwidth=2
        )
        self.__data = np.zeros((0,), dtype='int')
        self.__editMode = editMode
        self.grid_propagate(0)
        self.__canvas = tk.Canvas(
            self,
            width=OVERVIEW_CENTER_PANE_WIDTH
            + TRACK_RIGHT_EXTEND - 4,
            height=OVERVIEW_TRACK_BOX_HEIGHT - 4,
            bg="red"
        )
        self.__canvas.grid(column=0, row=0)
        self.__canvas.bind("<Button-1>", self.__onClickLeft)
        self.__canvas.bind("<ButtonRelease-1>", self.__onReleaseLeft)
        self.__sequenceRectangles = []
        self.__sequences = []
        

    def __onClickLeft(self, event):
        timestep = event.x // OVERVIEW_TIME_STEP_WIDTH
        self.__startTimestep = timestep
        
    def __onReleaseLeft(self, event):
        print(self.__editMode.get())
        self.__endTimestep = event.x // OVERVIEW_TIME_STEP_WIDTH
        editMode = self.__editMode.get()
        if editMode == "create":
            self.__startTimestep = self.__nextFree(
                self.__startTimestep
            )
            self.__endTimestep = min(
                    self.__endTimestep,
                    self.__lastFreeAfter(self.__startTimestep)
            )
            if (self.__startTimestep < self.__endTimestep):
                self.__createSequence(self.__startTimestep, self.__endTimestep)
        elif editMode == "delete":
            self.__deleteSequence()
        elif editMode == "move":
            self.__move()
        self.__startTimestep = None
        self.__endTimestep = None
        
    def __nextFree(self, timestep):
        if (len(self.__data) <= timestep):
            result = timestep
        else:
            a = np.argwhere(self.__data[timestep:] == 0)
            if (len(a) == 0):
                result = len(self.__data)
            else:
                result = timestep + a[0][0]
        print("Next timestep: ", timestep, self.__data, result)
        return result
        
    def __lastFreeAfter(self, timestep):
        if (len(self.__data) <= timestep):
            result = np.inf
        else:
            a = np.argwhere(self.__data[timestep:] > 0)
            if (len(a) == 0):
                result = np.inf
            else:
                result = timestep + a[0][0]
        print("Last free after: ", timestep, self.__data, result)
        return result
    
    def __createSequence(self, startTimestep, endTimestep):
        self.__sequenceRectangles.append(
            self.__canvas.create_rectangle(
                startTimestep * OVERVIEW_TIME_STEP_WIDTH,
                2,
                endTimestep * OVERVIEW_TIME_STEP_WIDTH,
                OVERVIEW_TRACK_BOX_HEIGHT - 2,
                fill="green"
            )
        )
        self.__sequences.append(
            Sequence(startTimestep, endTimestep - startTimestep)
        )
        if (self.__data.shape[0] < endTimestep):
            newZeros = np.zeros((endTimestep - self.__data.shape[0],), dtype='int')
            self.__data = np.concatenate([self.__data, newZeros], 0)
        self.__data[startTimestep:endTimestep] = len(self.__sequences)
        print("length after createSequence: ", self.__data.shape[0])
        print("data after createSequence: ", self.__data)
        print("sequences:")
        for sequence in self.__sequences:
            print("    ", sequence.getStartTimestep(), " - ", sequence.getEndTimestep())
        
    def __deleteSequence(self):
        indexes = []
        for i in range(len(self.__sequences)):
            if self.__sequences[i].getStartTimestep() \
                <= self.__startTimestep \
                <= self.__sequences[i].getEndTimestep():
                indexes.append(i)
        print("delete: ", indexes)
        indexes.reverse()
        for i in indexes:
            self.__data[self.__sequences[i].getStartTimestep():self.__sequences[i].getEndTimestep()] = 0
            self.__data = np.where(self.__data > i, self.__data - 1, self.__data)
            self.__canvas.delete(self.__sequenceRectangles[i])
            del self.__sequenceRectangles[i]
            del self.__sequences[i]
        a = np.argwhere(self.__data > 0)
        if len(a) == 0:
            self.__data = np.zeros((0,), dtype='int')
        else:
            self.__data = self.__data[0:a[-1][0]+1]
        print("length after createSequence: ", self.__data.shape[0])
        print("data after createSequence: ", self.__data)

    def __move(self):
        index = self.__data[self.__startTimestep]
        startTimestepOfSequence = self.__sequences[index].getStartTimestep()
        endTimestepOfSequence = self.__sequences[index].getEndTimestep()
        
        
        