# class Scrollcanvas
# ------------------
#
# Child class of tk.Frame.
# Has a tk.Canvas and Scrollbars.
#
# Mouse events can be bound by
#
#     scrollcanvas.bind(button, func)
#
# where func is a function with one
# argument (event).
# The event coordinates are
# automatically transformed to 
# the scrollregion.
#
# Rectangles and lines can be drawn using
#
#     scrollcanvas.createRectangle(*args, **kwargs)
#     scrollcanvas.createLine(*args, **kwargs)
#
# with the same arguments as the functions of
# tk.Canvas. Add the tag "scrollcanvas" if the
# scrollregion shall take it into account. The
# id of the drawn object is returned.
# When the id is known, the coordinates can
# be read and changed by
# 
#    coords = scrollcanvas.coords(id)
#    > some code that changes coords <
#    scrollcanvas.coords(id, *coords)
#
# The drawn object can be deleted by
#
#     scrollcanvas.delete(id)
#
# The scrollregion is adjusted by 
#
#     scrollcanvas.refresh()
#
# so that all drawn elements that
# have the tag "scrollcanvas" are
# within the scrollregion.
#
# If there shall not be a scrollbar, create the
# instance with
#
#    scrollcanvas = Scrollcanvas(
#        root, height, width, xscroll="none"
#    )
# resp.
#    scrollcanvas = Scrollcanvas(
#        root, height, width, yscroll="none"
#    )
#
# Two or more instances of Scrollcanvas can
# share a scrollbar. The scrollbar appears
# only at one of them, the master. The other
# one (slave) gets the master instance as
# argument when created. Example:
#
#    master_scrollcanvas(root, height, width)
#    slave_scrollcanvas(
#        root, height, width,
#        xscroll=scrollcanvas,
#        yscroll="none"
#    )

import tkinter as tk

def function_sequence(f, g):
    # returns a function that first calls f then g
    # with the same arguments.
    def help(f, g, *args, **kwargs):
        f(*args, **kwargs)
        g(*args, **kwargs)
    return lambda *args, **kwargs: help(f, g, *args, **kwargs)


class Scrollcanvas(tk.Frame):

    def __init__(self, root, width, height,
                 xscroll="master", yscroll="master"):
        super().__init__(
            root,
        )
        self.__makeCanvasAndScrollbars(
            width, height, xscroll, yscroll
        )
        self.xview = lambda *args, **kwargs : None
        self.yview = lambda *args, **kwargs : None
        self.__bindCanvasWithScrollbars()


    def __makeCanvasAndScrollbars(self,
                                   width, height,
                                   xscroll, yscroll):
        if xscroll == "master":
            self.__xscrollbar = tk.Scrollbar(
                self,
                orient="horizontal"
            )
            self.__xscrollbar.grid(
                row=1, column=0, sticky="ew"
            )
            self.__xscrollmaster = None
            self.__xscrollmode = "master"
        elif isinstance(xscroll, Scrollcanvas):
            self.__xscrollmaster = xscroll
            self.__xscrollbar = xscroll.xscrollbar
            self.__xscrollmode = "slave"
        elif xscroll == "none":
            self.__xscrollmaster = None
            self.__xscrollmode = "none"

        if yscroll == "master":
            self.__yscrollbar = tk.Scrollbar(
                self,
                orient="vertical"
            )
            self.__yscrollbar.grid(
                row=0, column=1, sticky="ns"
            )
            self.__yscrollmaster = None
            self.__yscrollmode = "master"
        elif isinstance(yscroll, Scrollcanvas):
            self.__yscrollmaster = yscroll
            self.__yscrollbar = yscroll.yscrollbar
            self.__yscrollmode = "slave"
        elif yscroll == "none":
            self.__yscrollmaster = None
            self.__yscrollmode = "none"

        self.__canvas = tk.Canvas(
            self,
            width=width,
            height=height,
            bg="green",
        )
        self.__canvas.grid(row=0, column=0)


    @property
    def xscrollbar(self):
        return self.__xscrollbar


    @property
    def yscrollbar(self):
        return self.__yscrollbar

    
    @property
    def canvas(self):
        return self.__canvas

    
    def addXViewFunc(self, func):
        self.xview = function_sequence(
            self.xview,
            func
        )
        self.__xscrollbar.config(
            command=self.xview
        )
    
    def addYViewFunc(self, func):
        self.yview = function_sequence(
            self.yview,
            func
        )
        self.__yscrollbar.config(
            command=self.yview
        )


    def __bindCanvasWithScrollbars(self):
        if self.__xscrollmode != "none":
            self.__canvas.config(
                xscrollcommand=self.__xscrollbar.set
            )
        if self.__xscrollmode == "master":
            self.addXViewFunc(self.__canvas.xview)
        elif self.__xscrollmode == "slave":
            self.__xscrollmaster.addXViewFunc(
                self.__canvas.xview
            )

        if self.__yscrollmode != "none":
            self.__canvas.config(
                yscrollcommand=self.__yscrollbar.set
            )
        if self.__yscrollmode == "master":
            self.addYViewFunc(self.__canvas.yview)
        elif self.__yscrollmode == "slave":
            self.__yscrollmaster.addYViewFunc(
                self.__canvas.yview
            )
 
    def getXScrollregion(self):
        if self.__xscrollmode == "master":
            bbox = self.__canvas.bbox("scrollcanvas")
            if bbox:
                (xmin, ymin, xmax, ymax) = bbox
            else:
                (xmin, xmax) = (0, 0)
            xmin = min(xmin, 0)
            xmax = max(
                xmax,
                int(self.__canvas["width"])
            )
            return (xmin, xmax)
        elif self.__xscrollmode == "slave":
            return self.__xscrollmaster.getXScrollregion()
        elif self.__xscrollmode == "none":
            return (0, int(self.__canvas["width"]))

    def getYScrollregion(self):
        if self.__yscrollmode == "master":
            bbox = self.__canvas.bbox("scrollcanvas")
            if bbox:
                (xmin, ymin, xmax, ymax) = bbox
            else:
                (ymin, ymax) = (0, 0)
            ymin = min(ymin, 0)
            ymax = max(
                ymax,
                int(self.__canvas["height"])
            )
            return (ymin, ymax)
        elif self.__yscrollmode == "slave":
            return self.__yscrollmaster.getYScrollregion()
        elif self.__yscrollmode == "none":
            return (0, int(self.__canvas["height"]))

    def refresh(self):
        (xmin, xmax) = self.getXScrollregion()
        (ymin, ymax) = self.getYScrollregion()
        self.__canvas.config(
            scrollregion=(xmin, ymin, xmax, ymax)
        )

    def createRectangle(self, *args, **kwargs):
        return self.__canvas.create_rectangle(
            *args, **kwargs
        )

    def createLine(self, *args, **kwargs):
        return self.__canvas.create_line(
            *args, **kwargs
        )

    def coords(self, id, *args):
        if args:
            self.__canvas.coords(id, *args)
            return None
        else:
            return self.__canvas.coords(id)

    def itemconfig(self, id, *args, **kwargs):
        if args or kwargs:
            self.__canvas.itemconfig(
                id,
                *args, **kwargs
            )
            return None
        else:
            return self.__canvas.itemconfig(id)

    def delete(self, id):
        self.__canvas.delete(id)

    def __windowPosToScrollregPos(self, x, y):
        (xmin, xmax) = self.getXScrollregion()
        (ymin, ymax) = self.getYScrollregion()
        if self.__xscrollmode != "none":
            xscr = self.__xscrollbar.get()[0]
        else:
            xscr = 0
        if self.__yscrollmode != "none":
            yscr = self.__yscrollbar.get()[0]
        else:
            yscr = 0
        width = xmax - xmin
        height = ymax - ymin
        x += xscr*width + xmin
        y += yscr*height + ymin
        return (x, y)


    def bind(self, button, func):
        def f(event):
            (event.x, event.y) = \
                self.__windowPosToScrollregPos(
                    event.x, event.y
                )
            return func(event)
        self.__canvas.bind(button, f)
        
    def lift(self, id):
        self.__canvas.lift(id)

if __name__ == "__main__":
    root = tk.Tk()
    scrollcanvas = Scrollcanvas(root, 600, 400)
    scrollcanvas.grid(row=0, column=1)

    scrollcanvas.createRectangle(
        -10, -20, 30, 40,
        width=0,
        fill="blue"
    )

    scrollcanvas.createLine(
        110, 120, 130, 140,
        width=1,
        fill="blue"
    )

    scrollcanvas.createRectangle(
        1010, 1120, 1130, 1140,
        width=0,
        fill="yellow"
    )

    scrollcanvas2 = Scrollcanvas(
        root, 50, 400, 
        xscroll="none", yscroll=scrollcanvas
    )
    scrollcanvas2.grid(row=0, column=0, sticky="nw")
    scrollcanvas2.createRectangle(
        30, 30, 40, 40, width=0, fill="yellow"
    )

    scrollcanvas3 = Scrollcanvas(
        root,
        600, 50,
        xscroll=scrollcanvas, yscroll="master"
    )
    scrollcanvas3.grid(row=1, column=1, sticky="se")
    scrollcanvas3.createRectangle(
        30, 30, 40, 40, width=0, fill="yellow"
    )
    scrollcanvas3.createRectangle(
        100, 100, 110, 110, width=0, fill="yellow",
        tag="scrollcanvas"
    )
    scrollcanvas3.refresh()

    def make_point(event):
        scrollcanvas.createRectangle(
            event.x, event.y, event.x+100, event.y+100,
            width=0,
            fill="red",
            tag="scrollcanvas"
        )
        scrollcanvas.refresh()
        scrollcanvas2.refresh()
        scrollcanvas3.refresh()

    scrollcanvas.bind("<Button-1>", make_point)

    scrollcanvas.refresh()

    root.mainloop()

