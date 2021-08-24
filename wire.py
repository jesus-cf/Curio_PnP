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
else:
    import tkinter as Tkinter
    from tkinter import *
import vectortext
from vectortext import *
import math
import label
import symbol

class wire(symbol.symbol):
    Count = 0

    def __init__(self, canvas, x0, y0, x1, y1, nodename):
        self.tag='WIRE_' + str(wire.Count)
        self.tag2='WIRE_' + str(wire.Count) + '_B'
        self.canvas=canvas
        self.x0=x0
        self.y0=y0
        self.x1=x1
        self.y1=y1
        self.x=x0
        self.y=y0
        self.label_list=[]
        self.zoom=get_zoom()
        self.nodename=nodename
        wire.Count+=1
        self.bubble0=0
        self.bubble1=0
        self.circle0=0
        self.circle1=0
        self.rect=0
        self.line=0
        self.move0=False
        self.move1=False
        self.cs1=4
        self.cs2=5
        self.tape_angle=0 # Updated before pick and place
        self.part_angle=0 # Updated before pick and place
        self.draw()
        self.add_to_grid_mat()

    def roundtoint(self, x0, y0, x1, y1):
        return int(x0+0.5), int(y0+0.5), int(x1+0.5), int(y1+0.5)

    def add_to_grid_mat(self):
        self.points=[]
        a,b,c,d=self.canvas.coords(self.line)
        z=get_zoom()
        x0,y0,x1,y1=self.roundtoint(a/z,b/z,c/z,d/z)
        if(x0>=0) and (x0<g.canvas_xsize) and (y0>=0) and (y0<g.canvas_ysize):
            ix=int((x0+0.5)/10)
            iy=int((y0+0.5)/10)
            self.points.append(ix)
            self.points.append(iy)
            g.grid_mat[ix][iy]+=1
        if(x1>=0) and (x1<g.canvas_xsize) and (y1>=0) and (y1<g.canvas_ysize):
            ix=int((x1+0.5)/10)
            iy=int((y1+0.5)/10)
            self.points.append(ix)
            self.points.append(iy)
            g.grid_mat[ix][iy]+=1

    def remove_from_grid_mat(self):
        if self.points:
            index=0
            while index < len(self.points):
                x=(self.points[index])
                y=(self.points[index+1])
                g.grid_mat[x][y]-=1
                index+=2
            self.points=[]

    def setmove(self, a, b):
        self.move0=a
        self.move1=b

    def printmove(self):
        if (self.move0==False) and (self.move1==False) :
            print ('False False')
        if (self.move0==False) and (self.move1==True) :
            print ('False True')
        if (self.move0==True) and (self.move1==False) :
            print ('True False')
        if (self.move0==True) and (self.move1==True) :
            print ('True True')
        
    
    def select(self, value):
        if (self.move0==True) and (self.move1==False) :
            if value==True:
                self.canvas.itemconfig(self.circle0, outline=g.select_color)
            else:
                self.canvas.itemconfig(self.circle0, outline='')
            self.canvas.itemconfig(self.circle1, outline='')
            self.canvas.itemconfig(self.rect, fill='')
        elif (self.move0==False) and (self.move1==True) :
            if value==True:
                self.canvas.itemconfig(self.circle1, outline=g.select_color)
            else:
                self.canvas.itemconfig(self.circle1, outline='')
            self.canvas.itemconfig(self.circle0, outline='')
            self.canvas.itemconfig(self.rect, fill='')
        else:
            if value==True:
                self.canvas.itemconfig(self.rect, fill=g.select_color)
            else:
                self.canvas.itemconfig(self.rect, fill='')            
            self.canvas.itemconfig(self.circle0, outline='')
            self.canvas.itemconfig(self.circle1, outline='')
            self.move0==False
            self.move1==False

    def clean(self):
        self.remove_from_grid_mat()
        #Delete all the labels of this wire and remove them from the global list of labels
        for item in self.label_list: # For all the labels in the local list...
            g.label_list.remove(item)
            item.clean()
            del item        
        self.canvas.delete(self.tag)

    def calculate_rect(self, x0, y0, x1, y1, isnew):
        if isnew==True: # It will be scalled shortly
            xx=3
        else:
            xx=3*get_zoom()
        if x0==x1:
            p0x=x0-xx
            p0y=y0
            p1x=x0+xx
            p1y=y0
            p2x=x1+xx
            p2y=y1
            p3x=x1-xx
            p3y=y1
        elif y0==y1:
            p0x=x0
            p0y=y0-xx
            p1x=x1
            p1y=y0-xx
            p2x=x1
            p2y=y1+xx
            p3x=x0
            p3y=y1+xx
        else:
            # For a perpendicular line we need the minus reciprocal of the wire slope:
            m=-1.0*(float(x1-x0)/float(y1-y0))
            dx=xx/math.sqrt((m*m)+1)
            dy=m*dx
            p0x=int(x0-dx)
            p0y=int(y0-dy)
            p1x=int(x0+dx)
            p1y=int(y0+dy)
            p2x=int(x1+dx)
            p2y=int(y1+dy)
            p3x=int(x1-dx)
            p3y=int(y1-dy)

        return p0x, p0y, p1x, p1y, p2x, p2y, p3x, p3y, p0x, p0y

    def addlabel(self, x, y, name, value, orientation, display, height=4):
        self.zoom=get_zoom()
        newlabel=label.label(self.canvas, self, self.x+x, self.y+y, name, value, orientation, display, height)
        self.label_list.append(newlabel)
        g.label_list.append(newlabel)
         
    def draw(self):
        self.zoom=get_zoom()

        # Since wires can be in an angle, create a rectangle using line segments
        self.rect=self.canvas.create_line(self.calculate_rect(self.x0, self.y0, self.x1, self.y1, True), fill ='', width=1, tags=(self.tag, "wires", "wirebox"), dash=(5,5))

        self.bubble0=self.canvas.create_oval(self.x0-self.cs1, self.y0-self.cs1, self.x0+self.cs1, self.y0+self.cs1, outline = get_wire_color(), tags=(self.tag, "wires", "wirebuble"))
        self.bubble1=self.canvas.create_polygon(self.x1-self.cs1, self.y1-self.cs1, self.x1+self.cs1, self.y1-self.cs1, self.x1+self.cs1, self.y1+self.cs1, self.x1-self.cs1, self.y1+self.cs1, outline = get_wire_color(), tags=(self.tag, "wires", "wirebuble"), fill='')

        self.circle0=self.canvas.create_oval(self.x0-self.cs2, self.y0-self.cs2, self.x0+self.cs2, self.y0+self.cs2, outline = '', tags=(self.tag, "wires", "wirebuble"))
        #self.circle1=self.canvas.create_oval(self.x1-self.cs2, self.y1-self.cs2, self.x1+self.cs2, self.y1+self.cs2, outline = '', tags=(self.tag, "wires", "wirebuble"))
        self.circle1=self.canvas.create_polygon(self.x1-self.cs2, self.y1-self.cs2, self.x1+self.cs2, self.y1-self.cs2, self.x1+self.cs2, self.y1+self.cs2, self.x1-self.cs2, self.y1+self.cs2, outline = get_wire_color(), tags=(self.tag, "wires", "wirebuble"), fill='')

        self.line=self.canvas.create_line(self.x0, self.y0, self.x1, self.y1, fill = get_wire_color(),
                                          tags=(self.tag, self.tag2, "wires", "wireline"))
        self.canvas.scale(self.tag, 0, 0, self.zoom, self.zoom)
        self.canvas.itemconfigure(self.tag, width=self.zoom*3)
        self.addlabel(0, 10, 'Name', 'PNP wire', 0, 0)
        self.addlabel(0, 50, 'Rotation', '0', 0, 0)
        
    def bubble_onoff(self, n, onoff):
        if onoff==1:
            if n==0:
                self.canvas.itemconfigure(self.bubble0, outline = get_wire_color())
            else:
                self.canvas.itemconfigure(self.bubble1, outline = get_wire_color())
        else:
            if n==0:
                self.canvas.itemconfigure(self.bubble0, outline = '')
            else:
                self.canvas.itemconfigure(self.bubble1, outline = '')

    def set_nodename(self, nodename):
        self.nodename=nodename

    def get_nodename(self):
        return self.nodename
    
    def move(self, dx, dy):
        if (self.move0==True) and (self.move1==False) :
            x0, y0, x1, y1=self.canvas.coords(self.line)
            x0+=dx
            y0+=dy
            self.canvas.coords(self.line, x0, y0, x1, y1)
            self.canvas.move(self.bubble0, dx, dy)
            self.canvas.move(self.circle0, dx, dy)
            x0, y0, x1, y1=self.canvas.coords(self.line)
            self.canvas.coords(self.rect, self.calculate_rect(x0, y0, x1, y1,False))
        elif (self.move0==False) and (self.move1==True) :
            x0, y0, x1, y1=self.canvas.coords(self.line)
            x1+=dx
            y1+=dy
            self.canvas.coords(self.line, x0, y0, x1, y1)
            self.canvas.move(self.bubble1, dx, dy)
            self.canvas.move(self.circle1, dx, dy)
            x0, y0, x1, y1=self.canvas.coords(self.line)
            self.canvas.coords(self.rect, self.calculate_rect(x0, y0, x1, y1,False))
        else:
            self.canvas.move(self.tag, dx, dy)
            self.move0==False
            self.move1==False
            for item in self.label_list: # For all the labels in the local list...
               item.move(dx, dy)

    # from http://stackoverflow.com/questions/849211/shortest-distance-between-a-point-and-a-line-segment
    def dist_to_point(self, x1,y1, x2,y2, x3,y3): # x3,y3 is the point
        px = x2-x1
        py = y2-y1

        something = px*px + py*py

        if something>0:
            u =  ((x3 - x1) * px + (y3 - y1) * py) / float(something)

            if u > 1:
                u = 1
            elif u < 0:
                u = 0

            x = x1 + u * px
            y = y1 + u * py

            dx = x - x3
            dy = y - y3

            dist = math.sqrt(dx*dx + dy*dy)
            return dist
        else:
            return 100000

    def pointisin(self, x, y):
        x1, y1, x2, y2 = self.canvas.coords(self.line)
        if self.dist_to_point(x1, y1, x2, y2, x, y)<=(5*get_zoom()):
            return True
        else:
            return False

    def nearP1(self, x, y):
        x1, y1, x2, y2 = self.canvas.coords(self.line)
        if (abs(x1-x))<=(3*get_zoom()) and (abs(y1-y))<=(5*get_zoom()):
            return True
        else:
            return False

    def nearP2(self, x, y):
        x1, y1, x2, y2 = self.canvas.coords(self.line)
        if (abs(x2-x))<=(3*get_zoom()) and (abs(y2-y))<=(5*get_zoom()):
            return True
        else:
            return False

    def move_xy_to_grid(self, x, y):
        gridsize=(get_zoom()*10)
        nx=int(((x+0.000001)+gridsize/2)/gridsize) # Sometimes moving parts and wires results in different offsets.  
        ny=int(((y+0.000001)+gridsize/2)/gridsize) # The 0.000001 added here seems to help somehow.
        nx*=gridsize
        ny*=gridsize
        return nx, ny

    def movetogrid(self):
        self.remove_from_grid_mat()
        z=get_zoom()
        gridsize=int(z*10)
        x0, y0, x1, y1 = self.canvas.coords(self.line)
        #x0, y0=self.move_xy_to_grid(x0, y0) #TEST
        #x1, y1=self.move_xy_to_grid(x1, y1) #TEST
        if (x0==x1) and (y0==y1): # Zero length wire?  Not allawed!
            x1+=gridsize
        self.canvas.coords(self.line, x0, y0, x1, y1)

        self.canvas.coords(self.bubble0, x0-self.cs1*z, y0-self.cs1*z, x0+self.cs1*z, y0+self.cs1*z)
        #self.canvas.coords(self.bubble1, x1-2*z, y1-2*z, x1+2*z, y1+2*z)
        self.canvas.coords(self.bubble1, x1-self.cs1*z, y1-self.cs1*z, x1+self.cs1*z, y1-self.cs1*z, x1+self.cs1*z, y1+self.cs1*z, x1-self.cs1*z, y1+self.cs1*z, x1-self.cs1*z, y1-self.cs1*z)

        self.canvas.coords(self.circle0, x0-self.cs2*z, y0-self.cs2*z, x0+self.cs2*z, y0+self.cs2*z)
        #self.canvas.coords(self.circle1, x1-self.cs2*z, y1-self.cs2*z, x1+self.cs2*z, y1+self.cs2*z)
        self.canvas.coords(self.circle1, x1-self.cs2*z, y1-self.cs2*z, x1+self.cs2*z, y1-self.cs2*z, x1+self.cs2*z, y1+self.cs2*z, x1-self.cs2*z, y1+self.cs2*z, x1-self.cs2*z, y1-self.cs2*z)
        x0, y0, x1, y1=self.canvas.coords(self.line)
        self.canvas.coords(self.rect, self.calculate_rect(x0, y0, x1, y1,False))
        self.add_to_grid_mat()

    def sym_ascii(self):
        z=get_zoom()
        x1, y1, x2, y2 = self.canvas.coords(self.line)
        s='wire,%0.2f,%0.2f,%0.2f,%0.2f\n' % (x1/z,y1/z,x2/z,y2/z)
        for item in self.label_list:
            x1b, y1b, xb2, y2b = self.canvas.coords(item.rect)
            s+='label,%0.2f,%0.2f,%s,%d,%d\n' % (x1b/z, y1b/z, item.value, item.direction, item.visible)
        return s
        
    # Rotate the wire around its center
    def rotate_ccw(self):
        self.remove_from_grid_mat()
        x1, y1, x2, y2 = self.canvas.coords(self.line)
        cx=(x1+x2)/2
        cy=(y1+y2)/2
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
        x1, y1, x2, y2 = self.canvas.coords(self.line)
        ncx=(x1+x2)/2
        ncy=(y1+y2)/2
        self.canvas.move(self.tag, cx-ncx, cy-ncy)
        self.add_to_grid_mat()
