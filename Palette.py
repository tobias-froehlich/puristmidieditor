import tkinter as tk

class Palette(tk.Frame):

    def __init__(self, root, tracks):
        super().__init__(root, relief="raised", borderwidth=2)
        self.__editingWindow = root
        self.__buttons = []
        for track in tracks:
            self.__buttons.append(tk.Button(
                self,
                bg=track.getColor(),
                activebackground=track.getColor(),
                fg=track.getColor(),
                borderwidth=4,
                command=(lambda position: lambda : self.__onButton(position))(track.getPosition())
            ))
        for button in self.__buttons:
            button.pack(side="top")
        self.__onButton(0)

    def getPosition(self):
        return self.__position

    def __onButton(self, position):
        for button in self.__buttons:
            button.config(relief="raised")
        self.__buttons[position].config(relief="sunken")
        self.__position = position
        self.__editingWindow.initForbiddenRegions(position)
        
