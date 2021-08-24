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
    import tkSimpleDialog
else:
    import tkinter as Tkinter
    from tkinter import *
    from tkinter import simpledialog as tkSimpleDialog
import vectortext
from vectortext import *

class label:
    Count = 0

    def __init__(self, canvas, parentsymbol, x, y, name, value, direction, visible, height=4):
        self.tag='LABEL_' + str(label.Count)
        self.tagtext='LABEL_' + str(label.Count) + "_TEXT"
        self.canvas=canvas
        self.x=x
        self.y=y
        self.zoom=get_zoom()
        self.name=name
        self.value=value
        self.direction=direction # 0:right, 1: up, 2:left, 3:down
        self.visible=visible # 0:nothing, 1:value, 2:name=value
        label.Count+=1
        self.rect=0
        self.height=height # in mm
        self.parentsymbol=parentsymbol
        self.draw()

    def clean(self):
        # Update the coordinates, in case a draw() command follows
        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        self.zoom=get_zoom()

        if self.direction==0:
            self.x=x1/self.zoom
            self.y=y1/self.zoom
        elif self.direction==1:
            self.x=x1/self.zoom
            self.y=y2/self.zoom
        elif self.direction==2:
            self.x=x2/self.zoom
            self.y=y2/self.zoom
        else:
            self.x=x2/self.zoom
            self.y=y1/self.zoom
        
        # Now delete everything
        self.canvas.delete(self.tag)
        
    def draw(self):
        self.zoom=get_zoom()
        if self.visible==2:
            text = "%s=%s" %(self.name, self.value)
        elif self.visible==1:
            text = "%s" %(self.value)
        else:
            text=''
        # Draw the sensing rectangle
        if text.__len__()>0:
            if self.direction==0:
                xlen=8*self.height*text.__len__()
                ylen=10*self.height
            elif self.direction==1:
                xlen=10*self.height
                ylen=-8*self.height*text.__len__()
            elif self.direction==2:
                xlen=-8*self.height*text.__len__()
                ylen=-10*self.height
            else:
                xlen=-10*self.height
                ylen=8*self.height*text.__len__()
        else:
            xlen=10*self.height
            ylen=10*self.height
      
        self.rect=self.canvas.create_rectangle(0, 0, xlen, ylen, outline='', width=1, tags=(self.tag), dash=(5,5))
        vectorstr(text, self.canvas, 0, 0, get_label_color(), self.tag, self.tagtext, self.direction, self.height)
        self.canvas.move(self.tag, self.x, self.y)
        self.canvas.scale(self.tag, 0, 0, self.zoom, self.zoom)
        self.canvas.itemconfigure(self.tag, width=self.zoom*3)

    def set_value(self, value):
        self.zoom=get_zoom()
        self.value=value
        self.clean()
        self.draw()

    def get_value(self):
        return self.value

    def get_name(self):
        return self.name

    def set_direction(self, direction):
        self.zoom=get_zoom()
        self.direction=direction
        self.clean()
        self.draw()

    def get_direction(self):
        return self.direction

    def set_visible(self, visible):
        self.zoom=get_zoom()
        self.visible=visible
        self.clean()
        self.draw()

    def get_visible(self):
        return self.visible

    def configure(self, x, y, value, direction, visible, height=4):
        self.x=x
        self.y=y
        self.value=value
        self.height=height
        self.direction=direction
        self.visible=visible
        self.zoom=get_zoom()
        self.clean()
        self.draw()
        
    def pointisin(self, x, y):
        try:
            x1, y1, x2, y2 = self.canvas.coords(self.rect)
            if (x>=x1) and (x<=x2) and (y>=y1) and (y<=y2):
                return 1
            else:
                return 0
        except:
            return 0

    def move(self, dx, dy):
        self.zoom=get_zoom()
        self.canvas.move(self.tag, dx, dy)
        self.x+=dx
        self.y+=dy

    def valueset(self, root, x, y):
        if self.visible==0: # there is still a minuscule rectangle for an invisible label, so
            return
        self.zoom=get_zoom()
        value= MyDialogString(root, self.name, self.value, self.height, x, y)

        if str(value.result)=='None':
            return
        self.value=value.result

        if str(value.height)=='None':
            return
        try:
            self.height=float(str(value.height))
        except:
            self.height==4

        self.clean()
        self.draw()
    
    # Rotate the label
    def rotate_ccw(self):
        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        cx=abs(x1+x2)/2-abs(y2-y1)/2
        cy=abs(y1+y2)/2+abs(x2-x1)/2
        allitems=self.canvas.find_withtag(self.tag)
        for figitem in allitems:
            points= self.canvas.coords(figitem)
            index=0
            while index < len(points):
                x=(points[index]-x1)
                y=(points[index+1]-y1)
                points[index]=y
                points[index+1]=-x
                index+=2
                self.canvas.coords(figitem, *points)
        self.canvas.move(self.tag, cx, cy)
        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        self.x=x1
        self.y=y1
        self.direction+=1
        if self.direction>3:
            self.direction=0

    def movetogrid(self):
        self.zoom=get_zoom() # this is actually a dummy function!

    def select(self, value):
        if value==True:
            if self.visible>0:
                self.canvas.itemconfig(self.rect, outline=g.select_color)
        else:
            self.canvas.itemconfig(self.rect, outline='')

class MyDialogString(tkSimpleDialog.Dialog):

    def __init__(self, parent, name, value, height, x, y):
        self.name=name
        self.value=value
        self.height=height
        self.x=x
        self.y=y
        self.entry1=0
        self.entry2=0
        tkSimpleDialog.Dialog.__init__(self, parent, title="Enter label value")

    # The default location assigned in tkSimpleDialog.py is not good, so:
    def geometry (self, position_str):
        tkSimpleDialog.Dialog.geometry(self, "+%d+%d" % (self.parent.winfo_rootx()+self.x, self.parent.winfo_rooty()+self.y))
       
    def body(self, master):

        Label(master, text=self.name).grid(row=0, column=0)

        self.entry1=Entry(master)
        self.entry1.delete(0, END)
        self.entry1.insert(0, self.value)
        self.entry1.grid(row=0, column=1)

        Label(master, text='size (mm)').grid(row=1, column=0)

        self.entry2=Entry(master)
        self.entry2.delete(0, END)
        self.entry2.insert(0, self.height)
        self.entry2.grid(row=1, column=1)       
            
        return self.entry1 # initial focus

    def apply(self):
        self.result=str(self.entry1.get())
        self.height=str(self.entry2.get())
