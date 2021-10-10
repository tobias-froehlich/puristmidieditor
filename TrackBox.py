# -*- coding: utf-8 -*-

from const import OVERVIEW_LEFT_PANE_WIDTH
from const import OVERVIEW_TRACK_BOX_HEIGHT

import tkinter as tk
from IntEntry import IntEntry

class TrackBox(tk.Frame):
    def __init__(self, root, position, removeFunction, flipFunction):
        super().__init__(
            root,
            width=OVERVIEW_LEFT_PANE_WIDTH,
            height=OVERVIEW_TRACK_BOX_HEIGHT,
            relief="raised",
            borderwidth=2
        )
        self.__position = position
        self.__removeButton = tk.Button(
            self,
            text="x",
            command=lambda: removeFunction(self.__position)
        )
        self.__removeButton.grid(column=0, row=0, sticky='nw')
        self.__channel = IntEntry(self, init_value=1, from_=1, to=16)
        self.__channel.grid(column=1, row=0, sticky='nw')
        self.__upButton = tk.Button(
            self,
            text="up",
            command=lambda: flipFunction(self.__position - 1, self.__position)
        )
        self.__upButton.grid(column=2, row=0)
        self.__downButton = tk.Button(
            self,
            text="down",
            command=lambda: flipFunction(self.__position, self.__position + 1)
        )
        self.__downButton.grid(column=3, row=0)
    
        self.grid_propagate(0)
        
    def setPosition(self, position):
        self.__position = position
        
if __name__ == "__main__":
    root = tk.Tk();
    trackbox = TrackBox(root)
    trackbox.grid(column=0, row=0)
    
    root.mainloop()