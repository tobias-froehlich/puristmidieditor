# -*- coding: utf-8 -*-

from const import OVERVIEW_LEFT_PANE_WIDTH
from const import OVERVIEW_TRACK_BOX_HEIGHT

import tkinter as tk
from IntEntry import IntEntry

class TrackBox(tk.Frame):
    def __init__(self, root):
        super().__init__(
            root,
            width=OVERVIEW_LEFT_PANE_WIDTH,
            height=OVERVIEW_TRACK_BOX_HEIGHT,
            relief="raised",
            borderwidth=2
        )
        self.__channel = IntEntry(self, init_value=1, from_=1, to=16)
        self.__channel.grid(column=0, row=0, sticky='nw')
        self.grid_propagate(0)
        
        
if __name__ == "__main__":
    root = tk.Tk();
    trackbox = TrackBox(root)
    trackbox.grid(column=0, row=0)
    
    root.mainloop()