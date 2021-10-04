# class Scrollcanvas
# ------------------
#
# Child class of tk.Frame.
# Has an entry box for entering integers only.
# The integer value only changes when the enter
# key is pressed, not during typing.
# Background and foreground colors are inverted
# during typing.


import tkinter as tk

class IntEntry(tk.Frame):

    def __init__(self, master,
                 width=3,
                 bg_color="white", fg_color="black",
                 init_value=0, from_=0, to=99):
        super().__init__(master)
        self.__from_ = from_
        self.__to = to
        self.__bg_color = bg_color
        self.__fg_color = fg_color
        self.__value = init_value
        self.__text = tk.StringVar()
        self.__text.set(str(init_value))
        self.__entry = tk.Entry(self,
            width=width,
            textvariable=self.__text,
            insertbackground=bg_color
        )
        self.__entry.bind(
            "<Return>", self.__on_return
        )
        self.__entry.bind(
            "<Button-1>", self.__on_mouse_down
        )
        self.__entry.bind(
            "<FocusOut>", self.__on_return
        )
        self.__on_return(None)
        self.__entry.pack(side="left")

    def __on_return(self, event):
        self.__entry.config(bg=self.__bg_color)
        self.__entry.config(fg=self.__fg_color)
        string = self.__text.get()
        
        try:
            value = int(string)
            if self.__from_ <= value <= self.__to:
                self.__value = value
        except:
            pass
        self.__text.set(str(self.__value))
        self.focus()

    def __on_mouse_down(self, event):
        self.__entry.config(bg=self.__fg_color)
        self.__entry.config(fg=self.__bg_color)

    def get(self):
        return self.__value

   

if __name__ == "__main__":
    root = tk.Tk()
    intentry = IntEntry(
        root,
        bg_color="green",
        fg_color="red",
        init_value=5,
        from_=-10
    )
    intentry.pack()
    def loop():
        print(intentry.get())
        root.after(1000, loop)

    root.after(0, loop)
    root.mainloop()




