# -*- coding: utf-8 -*-

import tkinter as tk

class Toolbox(tk.Frame):
    
    def __init__(self, root, editMode):
        super().__init__(root)
        self.__editMode = editMode
        self.__createSequence = tk.Button(
            self,
            text="create",
            command=lambda: self.__editMode.set("create")
        )
        self.__createSequence.grid(column=0, row=0)
        self.__deleteSequence = tk.Button(
            self,
            text="delete",
            command=lambda: self.__editMode.set("delete")
        )
        self.__deleteSequence.grid(column=1, row=0)
        self.__moveSequence = tk.Button(
            self,
            text="move",
            command=lambda: self.__editMode.set("move")
        )
        self.__moveSequence.grid(column=2, row=0)
        