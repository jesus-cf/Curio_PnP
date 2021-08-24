# Copyright (C) 2020-2021  Jesus Calvino-Fraga, jesuscf (at) gmail.com
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
import vectortext
import label
import symbol

import sys
if sys.version_info[0] < 3:
    import Tkinter
    from Tkinter import *
    import tkSimpleDialog
else:
    import tkinter as Tkinter
    from tkinter import *
    from tkinter import simpledialog as tkSimpleDialog

class sym(symbol.symbol):
    Count = 0

    def __init__(self, canvas, x, y):
        self.tag='CONFIGURATION_' + str(sym.Count)
        self.tag_fill='CONFIGURATION_' + str(sym.Count) + '_fill'
        self.tag_outline='CONFIGURATION_' + str(sym.Count) + '_outline'
        self.canvas=canvas
        self.x=x
        self.y=y
        self.zoom=get_zoom()
        self.direction=0
        self.mirrorv=0
        self.mirrorh=0
        sym.Count+=1
        self.label_list=[]
        self.pin_list=[]
        self.rect=0
        self.draw()
        self.add_to_grid_mat()

    def draw(self):
        self.zoom=get_zoom()
        self.rect=self.canvas.create_rectangle(0, 0, 160, 160, outline='', width=1, tags=(self.tag, self.tag_outline), dash=(5,5))
        self.canvas.create_rectangle(0, 0, 160, 160, outline= get_symbol_color(), tags=(self.tag, self.tag_outline))
        self.canvas.create_line(80, 100, 80, 150, fill = get_symbol_color(), tags=(self.tag, self.tag_fill))
        self.canvas.create_line(80, 60, 80, 10, fill = get_symbol_color(), tags=(self.tag, self.tag_fill))
        self.canvas.create_line(100, 80, 150, 80, fill = get_symbol_color(), tags=(self.tag, self.tag_fill))
        self.canvas.create_line(60, 80, 10, 80, fill = get_symbol_color(), tags=(self.tag, self.tag_fill))
        self.canvas.move(self.tag, self.x, self.y)
        self.canvas.scale(self.tag, 0, 0, self.zoom, self.zoom)
        self.addlabel(160, 0, 'Name', 'Settings', 0, 0)
        self.addlabel(160, 40, 'Use big tray', '0', 0, 0)
        self.addlabel(160, 80, 'Hide wires', '0', 0, 0)
        self.addlabel(160, 120, 'X offset (mm)', '0.0', 0, 0)
        self.addlabel(160, 160, 'Y offset (mm)', '0.0', 0, 0)
        self.addlabel(160, 200, 'ton delay (ms)', '300', 0, 0)
        self.addlabel(160, 240, 'toff delay (ms)', '300', 0, 0)
        self.addlabel(160, 280, 'servo delay (ms)', '300', 0, 0)
        self.addlabel(160, 320, 'servo max (ms)', '2.2', 0, 0)
        self.addlabel(160, 360, 'servo min (ms)', '0.5', 0, 0)
        self.canvas.itemconfigure(self.tag, width=self.zoom)

