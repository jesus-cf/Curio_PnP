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
import os
import math

import sys
if sys.version_info[0] < 3:
    import Tkinter
    from Tkinter import *
    import tkSimpleDialog
else:
    import tkinter as Tkinter
    from tkinter import *
    from tkinter import simpledialog as tkSimpleDialog

from PIL import Image,ImageTk

class sym(symbol.symbol):
    Count = 0

    def __init__(self, canvas, x, y):
        self.tag='CUT_TAPE' + str(sym.Count)
        self.tag_fill='CUT_TAPE' + str(sym.Count) + '_fill'
        self.tag_outline='CUT_TAPE' + str(sym.Count) + '_outline'
        self.tag_foamcut='CUT_TAPE' + str(sym.Count) + '_foamcut'
        self.tag_foamcut_in='CUT_TAPE' + str(sym.Count) + '_foamcut_in'
        self.canvas=canvas
        self.zoom=get_zoom()
        self.x=x
        self.y=y
        self.direction=0
        self.mirrorv=0
        self.mirrorh=0
        sym.Count+=1
        self.label_list=[]
        self.pin_list=[]
        self.rect=0
        self.pcbframe=0;
        self.last_Width=0
        self.last_Length=0
        self.last_Rotation=0
        self.last_insidecut=-1
        self.pcenter=0
        self.pwidth=0
        self.plength=0
        self.targets=[] # list of coordinates for PnP targets
        self.insidecut=0

        self.draw()
        self.add_to_grid_mat()

    def rotate_ccw(self):
        try:
            if any(c.isalpha() for c in self.label_list[3].get_value()):
                raise ValueError('Letters not allower.')
            else:   
                Rotation=eval(self.label_list[3].get_value())
        except:
            Rotation=0
        Rotation+=90.0
        self.label_list[3].set_value(str(Rotation%360.0))
        return

    def getbound(self):
        points=self.canvas.coords(self.tapeframe)
        return points       

    def pointisin(self, x, y):
        inside = False

        # get the rotation angle
        try:
            if any(c.isalpha() for c in self.label_list[3].get_value()):
                raise ValueError('Letters not allower.')
            else:   
                Rotation=eval(self.label_list[3].get_value())
        except:
            Rotation=0

        # get the center of rotation
        origin=self.canvas.coords(self.rect)
        center=[origin[0], origin[1]]
        
        # get the points of the rotated rectangle
        points=self.canvas.coords(self.tapeframe)

        # undo the previously applied rotation
        angle=-1.0*Rotation      
        points=self.rotate(points, angle, center)
        tocheck=[x, y]
        tocheck=self.rotate(tocheck, angle, center)
        x=tocheck[0]
        y=tocheck[1]

        x1, y1, x2, y2 = points[0], points[1], points[4], points[5]
        #print("Points: " + str(points))
        #print("Point: %f, %f" % (x, y))
        #print("Rectangle: %f, %f, %f, %f" % (x1, y1, x2, y2))
        if (x>=x1) and (x<=x2) and (y>=y1) and (y<=y2):
            return 1
        else:
            return 0        


    # https://stackoverflow.com/questions/36620766/rotating-a-square-on-tkinter-canvas
    def rotate(self, points, angle, center):
        angle = math.radians(angle)*-1.0
        cos_val = math.cos(angle)
        sin_val = math.sin(angle)
        cx, cy = center
        new_points = []
        for i in range(0,  len(points), 2):
            x_old=points[i]
            y_old=points[i+1]
            x_old -= cx
            y_old -= cy
            x_new = x_old * cos_val - y_old * sin_val
            y_new = x_old * sin_val + y_old * cos_val
            new_points.append(x_new + cx)
            new_points.append(y_new + cy)
        return new_points

    def draw(self):
        self.zoom=get_zoom()
        self.addlabel(0, 0,   'Ref', 'Cut Tape', 0, 1)
        self.addlabel(0, 40,  'Width(mm)', '8.0', 0, 0)
        self.addlabel(0, 80,  'Length(mm)', '24.0', 0, 0)
        self.addlabel(0, 120, 'Rotation(deg)', '0.0', 0, 0)
        self.addlabel(0, 160, 'Part Width(mm)', '2.6', 0, 0)
        self.addlabel(0, 200, 'Part Length(mm)', '1.6', 0, 0)
        self.addlabel(0, 240, 'Part center to edge(mm)', '2.6', 0, 0)
        self.addlabel(0, 280, 'Cut inline(1=yes)', '0', 0, 0)
        self.update_image()
 
    def update_image(self):
        self.zoom=get_zoom()
        redraw=0

         
        if self.label_list[1].get_value() != self.last_Width:
            redraw=1

        if self.label_list[2].get_value() != self.last_Length:
            redraw=1

        if self.label_list[3].get_value() != self.last_Rotation:
            redraw=1

        if self.label_list[4].get_value() != self.pwidth:
            redraw=1

        if self.label_list[5].get_value() != self.plength:
            redraw=1
            
        if self.label_list[6].get_value() != self.pcenter:
            redraw=1

        if self.label_list[7].get_value() != self.last_insidecut:
            redraw=1

        if redraw==1:
            self.last_Width=self.label_list[1].get_value()
            self.last_Length=self.label_list[2].get_value()
            self.last_Rotation=self.label_list[3].get_value()
            self.pwidth=self.label_list[4].get_value()
            self.plength=self.label_list[5].get_value()
            self.pcenter=self.label_list[6].get_value()
            self.last_insidecut=self.label_list[7].get_value()

            defaults=[8, 24, 0, 2.6, 1.6, 2.6]
            newvalues=[]
            for i in range (0, len(defaults)):
                try:
                    if any(c.isalpha() for c in self.label_list[i+1].get_value()):
                        raise ValueError('Letters not allower.')
                    else:
                        newvalues.append(eval(self.label_list[i+1].get_value()))
                except:
                    print ("Warning: incorrect expresion \'%s\' of input \'%s\' in cut tape \'%s\'." %
                           (self.label_list[i+1].get_value(), self.label_list[i+1].get_name(), self.label_list[0].get_value()) )
                    newvalues.append(defaults[i])

            new_Width, new_Length, new_Rotation, new_pwidth, new_plength, new_pcenter=newvalues

            try:
                new_insidecut=self.label_list[7].get_value()
            except:
                new_insidecut=0

            try:
                # self.x and self.y are not being updated when moving the tape, so for now
                points=self.canvas.coords(self.rect)
                self.x=points[0]/self.zoom
                self.y=points[1]/self.zoom
            except:
                pass

            #center = ( int((new_Width*10)/2), int((new_Length*10)/2) )
            center = ( 0, 0 )
            
            self.canvas.delete(self.tag)
            self.targets.clear()

            self.rect=self.canvas.create_rectangle(0, 0, 1, 1, outline='', width=1, tags=(self.tag, self.tag_outline),
                                                   dash=(5,5))

            points=[0, 0, new_Width*10, 0, new_Width*10, new_Length*10, 0, new_Length*10, 0, 0]
            new_points=self.rotate(points, new_Rotation, center)
            self.tapeframe=self.canvas.create_line(new_points, fill = get_symbol_color(),
                                                   tags=(self.tag, self.tag_fill, self.tag_foamcut, "imagebox"))

            points=[new_Width*10-17.5, 0]
            new_points=self.rotate(points, new_Rotation, center)
            self.canvas.create_arc( new_points[0]-8,  new_points[1]-8, new_points[0]+8, new_points[1]+8,
                                    style='arc', start=new_Rotation, extent=-180, outline = get_symbol_color(),
                                    tags=(self.tag, self.tag_outline))           

            points=[new_Width*10-17.5, new_Length*10]
            new_points=self.rotate(points, new_Rotation, center)
            self.canvas.create_arc( new_points[0]-8,  new_points[1]-8, new_points[0]+8, new_points[1]+8,
                                    style='arc', start=new_Rotation, extent=+180, outline = get_symbol_color(),
                                    tags=(self.tag, self.tag_outline))

            # draw sprocket holes
            for i in range(40,  int(new_Length*10), 40):
                points=[new_Width*10-17.5, i] # the hole is 1.75mm from the edge
                new_points=self.rotate(points, new_Rotation, center)
                self.canvas.create_arc( new_points[0]-8,  new_points[1]-8, new_points[0]+8, new_points[1]+8,
                                        style='arc', start=0, extent=359, outline = get_symbol_color(), tags=(self.tag, self.tag_outline))
            # draw the part hole
            pcenter=new_pcenter*10
            pwidth=new_pwidth*10
            plength=new_plength*10
            for i in range((int(plength/40)+1)*20,  int(new_Length*10), (int(plength/40)+1) * 40):
                points=[pcenter-(pwidth/2), -(plength/2)+i, pcenter+(pwidth/2), -(plength/2)+i,
                        pcenter+(pwidth/2),  (plength/2)+i, pcenter-(pwidth/2),  (plength/2)+i,
                        pcenter-(pwidth/2), -(plength/2)+i]
                new_points=self.rotate(points, new_Rotation, center)
                self.canvas.create_line(new_points, fill=get_symbol_color(), tags=(self.tag, self.tag_fill))
                #draw cross hairs in the middle of the part
                points=[pcenter-5, i, pcenter+5, i]
                new_points=self.rotate(points, new_Rotation, center)
                self.canvas.create_line(new_points, fill=get_symbol_color(), tags=(self.tag, self.tag_fill))
                #draw cross hairs in the middle of the part
                points=[pcenter, i-5, pcenter, i+5]
                new_points=self.rotate(points, new_Rotation, center)
                self.canvas.create_line(new_points, fill=get_symbol_color(), tags=(self.tag, self.tag_fill))
                #create a target object
                points=[pcenter, i, pcenter+1, i]
                new_points=self.rotate(points, new_Rotation, center)
                newtarget=self.canvas.create_line(new_points, fill=get_symbol_color(), tags=(self.tag, self.tag_fill))
                self.targets.append(newtarget)

            x1=pcenter-(pwidth/2)
            x2=pcenter+(pwidth/2)
            y1=int((plength/40)+1)*20-(plength/2)
            y2=int(new_Length*10)-int((plength/40)+1)*20+(plength/2)
            points=[x1, y1, x2, y1, x2, y2, x1, y2, x1, y1]
            new_points=self.rotate(points, new_Rotation, center)

            if new_insidecut=='1' or new_insidecut.lower()=='yes' or new_insidecut.lower()=='y' or new_insidecut.lower()=='on':
                self.insidecut=self.canvas.create_line(new_points, fill=get_symbol_color(),
                                        tags=(self.tag, self.tag_fill, self.tag_foamcut_in),
                                        dash=(1,1))
                
            self.canvas.move(self.tag, self.x, self.y)
            self.canvas.scale(self.tag, 0, 0, self.zoom, self.zoom)
            self.canvas.itemconfigure(self.tag, width=self.zoom)






