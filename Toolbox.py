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
        self.__resizeLeft = tk.Button(
            self,
            text="resize left",
            command=lambda: self.__editMode.set("resize_left")
        )
        self.__resizeLeft.grid(column=3, row=0)
        self.__resizeRight = tk.Button(
            self,
            text="resize right",
            command=lambda: self.__editMode.set("resize_right")
        )
        self.__resizeRight.grid(column=4, row=0)
        self.__editMidi = tk.Button(
            self,
            text="edit",
            command=lambda: self.__editMode.set("edit_midi")
        )
        self.__editMidi.grid(column=5, row=0)