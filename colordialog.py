# Copyright (C) 2014-2021  Jesus Calvino-Fraga, jesuscf (at) gmail.com
# 
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2, or (at your option) any
# later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import globalvars as g
from globalvars import *
import sys
if sys.version_info[0] < 3:
    import Tkinter
    from Tkinter import *
    import tkColorChooser
    import tkSimpleDialog
else:
    import tkinter as Tkinter
    from tkinter import *
    from tkinter import colorchooser as tkColorChooser
    from tkinter import simpledialog as tkSimpleDialog

class colordialog(tkSimpleDialog.Dialog):

    def __init__(self, parent):
        self.mybuttons=[]
        self.mycolors=[]
        tkSimpleDialog.Dialog.__init__(self, parent, title="Color Settings")

    def mycb(self, r):
        colorTuple = tkColorChooser.askcolor(color=self.mycolors[r])
        if colorTuple[0]!='None':
            self.mycolors[r]=colorTuple[1]
            self.mybuttons[r].config(bg=colorTuple[1])

    def addrow(self, master, ltext, color, r):
        Label(master, text=ltext).grid(row=r, column=0)
        mybutton=Button(master, bg=color, width=10, command=lambda:self.mycb(r))
        mybutton.grid(row=r, column=1)
        return mybutton

    def body(self, master):
        b=self.addrow(master, "Background", g.bg_color, 0)
        self.mybuttons.append(b)
        self.mycolors.append(g.bg_color)
        
        b=self.addrow(master, "Symbol", g.symbol_color, 1)
        self.mybuttons.append(b)
        self.mycolors.append(g.symbol_color)
        
        b=self.addrow(master, "Grid", g.grid_color, 2)
        self.mybuttons.append(b)
        self.mycolors.append(g.grid_color)

        b=self.addrow(master, "Pin", g.pin_color, 3)
        self.mybuttons.append(b)
        self.mycolors.append(g.pin_color)

        b=self.addrow(master, "Wire", g.wire_color, 4)
        self.mybuttons.append(b)
        self.mycolors.append(g.wire_color)

        b=self.addrow(master, "Label", g.label_color, 5)
        self.mybuttons.append(b)
        self.mycolors.append(g.label_color)

        b=self.addrow(master, "Selection", g.select_color, 6)
        self.mybuttons.append(b)
        self.mycolors.append(g.select_color)

    def apply(self):
        g.setcolors(self.mycolors)
        #print 'Hello from color settings'

