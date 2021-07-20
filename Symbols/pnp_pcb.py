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
        self.tag='PCB' + str(sym.Count)
        self.tag2='PCB' + str(sym.Count) +'B'
        self.tag3='PCB' + str(sym.Count) +'Target'
        self.tag_fill='PCB' + str(sym.Count) +'_fill'
        self.tag_outline='PCB' + str(sym.Count) +'_outline'
        self.tag_foamcut='PCB' + str(sym.Count) + '_foamcut'
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
        self.pcbframe=0;
        self.last_Width=0
        self.last_Length=0
        self.Last_Image_File_Loaded=''
        self.Last_Centroid_File_Loaded=''
        self.prev_zoom=0
        self.draw()
        self.add_to_grid_mat()
        self.targets=[] # list of point coordinates for PnP
        self.target_name=[] # Cut tape name to use for each target
        self.target_angle=[] # Cut tape orientation to use for each target

    def rotate_ccw(self):
        return

    def draw(self):
        self.zoom=get_zoom()
        self.addlabel(0, 0, 'Ref', 'PCB', 0, 1)
        self.addlabel(0, 40, 'Width(mm)', '20.0', 0, 0)
        self.addlabel(0, 80, 'Length(mm)', '20.0', 0, 0)
        self.addlabel(0, 120, 'Image File', 'Image_Name.jpg', 0, 0)
        self.addlabel(0, 160, 'Centroid File', 'Centroids.txt', 0, 0)
        self.rect=self.canvas.create_rectangle(0, 0, 210, 680, outline='', width=1, tags=(self.tag, self.tag2, self.tag_outline), dash=(5,5))
        self.pcbframe=self.canvas.create_line(0, 0, 210, 0, 210, 680, 0, 680, 0, 0, fill = get_symbol_color(),
                                              tags=(self.tag, self.tag2, self.tag_fill, "imagebox", self.tag_foamcut))
        self.canvas.move(self.tag2, self.x, self.y)
        self.canvas.scale(self.tag2, 0, 0, self.zoom, self.zoom)
        self.canvas.itemconfigure(self.tag2, width=self.zoom)

    def update_image(self):
        x1a, y1a, x2a, y2a = self.canvas.coords(self.rect)
        self.zoom=get_zoom()       
        new_Width=int(abs(x1a-x2a))
        new_Length=int(abs(y1a-y2a))
        new_size=0

        try:
            if any(c.isalpha() for c in self.label_list[1].get_value()):
                raise ValueError('Letters not allower.')
            else:
                Width=eval(self.label_list[1].get_value())*10.0
        except:
            Width=20.0*10
            if Width!=self.last_Width:
                print ( "Warning: incorrect expresion \'%s\' of input \'%s\' in PCB \'%s\'." %
                        (self.label_list[1].get_value(), self.label_list[1].get_name(), self.label_list[0].get_value()) )
        
        try:
            if any(c.isalpha() for c in self.label_list[2].get_value()):
                raise ValueError('Letters not allower.')
            else:
                Length=eval(self.label_list[2].get_value())*10.0
        except:
            Length=20*10
            if Length!=self.last_Length:
                print ( "Warning: incorrect expresion \'%s\' of input \'%s\' in PCB \'%s\'." %
                        (self.label_list[2].get_value(), self.label_list[2].get_name(), self.label_list[0].get_value()) )

        if Width!=self.last_Width:
            #print ("Size change detected: " + str(int(float(self.label_list[1].get_value())*10)) + ", " + str(int(new_Width/self.zoom)))
            new_size=1

        if Length!=self.last_Length:
            #print ("Size change detected: " + str(int(float(self.label_list[2].get_value())*10)) + ", " + str(int(new_Length/self.zoom)))
            new_size=1

        if self.Last_Image_File_Loaded != self.label_list[3].get_value():
            new_size=1

        if self.Last_Centroid_File_Loaded != self.label_list[4].get_value():
            new_size=1

        if self.prev_zoom!=self.zoom:
            new_size=1

        if new_size==1:
            self.last_Width=Width
            self.last_Length=Length
            
            self.canvas.coords(self.rect, 0, 0, Width, Length)
            self.canvas.coords(self.pcbframe, 0, 0, Width, 0, Width, Length, 0, Length, 0, 0)

            # Update all but the image
            self.canvas.move(self.tag2, self.x, self.y)
            self.canvas.scale(self.tag2, 0, 0, self.zoom, self.zoom)
            self.canvas.itemconfigure(self.tag2, width=self.zoom)

            self.prev_zoom=0
            x1a, y1a, x2a, y2a = self.canvas.coords(self.rect)
            self.zoom=get_zoom()       
            new_Width=int(abs(x1a-x2a)) # ?????
            new_Length=int(abs(y1a-y2a)) # ?????

        if self.Last_Centroid_File_Loaded != self.label_list[4].get_value():
            if os.path.isfile(self.label_list[4].get_value()):
                self.Last_Centroid_File_Loaded=self.label_list[4].get_value()
                with open(self.label_list[4].get_value()) as f:
                    content = f.read().splitlines()
                    f.close()

                self.canvas.delete(self.tag3)
                self.targets.clear()
                self.target_name.clear()
                self.target_angle.clear()

                scale=1
                rotation=0
                topx=0
                topy=0

                for line in content:
                    #print(line)
                    word = line.split()
                    if len(word) > 1:
                        if word[0]=="SCALE_FACTOR":
                            scale=float(word[1])
                            #print("Scale factor: " + str(scale))
                        elif word[0]=="ROTATION":
                            rotation=float(word[1])
                            #print("Rotation: " + str(rotation))
                        elif word[0]=="TOP_LEFT":
                            if len(word) > 2:
                                topx=float(word[1])
                                topy=float(word[2])
                                #print("Top left: " + str((topx, topy)))
                        else:
                            if len(word) > 4:
                                # Expects something like this (Ultiboard format, units are mils):
                                # "C1 100nF 2608.00000 997.95543 90 TOP SMD R0805" 
                                x=round((float(word[2])-topx)*scale, 2)*10
                                y=round((float(word[3])-topy)*scale*-1, 2)*10
                                #print("Target: " + str((x, y)))
                                
                                #draw cross hairs in the middle of the part
                                points=[x-5, y, x+5, y]
                                self.canvas.create_line(points, fill=get_symbol_color(), tags=(self.tag, self.tag3, self.tag_fill))
                                #draw cross hairs in the middle of the part
                                points=[x, y-5, x, y+5]
                                self.canvas.create_line(points, fill=get_symbol_color(), tags=(self.tag, self.tag3, self.tag_fill))
                                #create a target object
                                points=[x, y, x+1, y]
                                newtarget=self.canvas.create_line(points, fill=get_symbol_color(), tags=(self.tag, self.tag3, self.tag_fill))
                                self.targets.append(newtarget) # Target coordinates can be obtained from the line points (one pixel!)
                                self.target_name.append(word[1]) # Cut tape name
                                self.target_angle.append(word[4]) # Part orientation

                # Update all but the image. WARNING: self.x and self.y are not updated after moving
                self.canvas.move(self.tag3, self.x, self.y)
                self.canvas.scale(self.tag3, 0, 0, self.zoom, self.zoom)
                self.canvas.itemconfigure(self.tag3, width=self.zoom)

        if self.Last_Image_File_Loaded != self.label_list[3].get_value():
            if os.path.isfile(self.label_list[3].get_value()):
                self.img=(Image.open(self.label_list[3].get_value()))
                self.Last_Image_File_Loaded=self.label_list[3].get_value()
                resized_image= self.img.resize((int(Width), int(Length)), Image.ANTIALIAS)
                self.pcb_image=ImageTk.PhotoImage(resized_image)
                self.canvas_image=self.canvas.create_image(x1a, y1a, anchor=NW, image=self.pcb_image, tags=(self.tag))
                self.canvas.tag_lower(self.canvas_image)
                self.last_Width=Width
                self.last_Length=Length
            else:
                self.Last_Image_File_Loaded=self.label_list[3].get_value()
                try:
                    self.canvas.delete(self.canvas_image)
                except:
                    pass
        else:
            if self.prev_zoom!=self.zoom:
                try:
                    self.prev_zoom=self.zoom
                    resized_image= self.img.resize((int(abs(x1a-x2a)), int(abs(y1a-y2a))), Image.ANTIALIAS)
                    self.pcb_image=ImageTk.PhotoImage(resized_image)
                    self.canvas.itemconfig(self.canvas_image, image=self.pcb_image)
                except:
                    pass




