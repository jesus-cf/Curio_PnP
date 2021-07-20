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
import vectortext
import label
import sys
if sys.version_info[0] < 3:
    import Tkinter
    from Tkinter import *
    import tkSimpleDialog
    import tkMessageBox
    import tkFileDialog
else:
    import tkinter as Tkinter
    from tkinter import *
    from tkinter import simpledialog as tkSimpleDialog
    from tkinter import messagebox as tkMessageBox
    from tkinter import filedialog as tkFileDialog

class symbol:
    Count = 0

    def __init__(self, canvas, x, y):
        self.tag='Symbol' + str(symbol.Count)
        self.canvas=canvas
        self.x=x
        self.y=y
        self.zoom=get_zoom()
        self.direction=0
        self.mirrorv=0
        self.mirrorh=0
        symbol.Count+=1
        self.label_list=[]
        self.rect=0
        self.targets=[] # list of points for PnP
        self.draw()
        self.canvas.itemconfigure(self.tag, width=self.zoom)

    def roundtoint(self, x0, y0, x1, y1):
        return int(x0+0.5), int(y0+0.5), int(x1+0.5), int(y1+0.5)

    def add_to_grid_mat(self):
        pass

    def remove_from_grid_mat(self):
        pass
        
    def select(self, value):
        if value==True:
            self.canvas.itemconfig(self.rect, outline=g.select_color)
            for item in self.label_list: # For all the labels in the local list...
                if item.visible>0:
                    self.canvas.itemconfig(item.rect, outline=g.select_color)
        else:
            self.canvas.itemconfig(self.rect, outline='')
            for item in self.label_list: # For all the labels in the local list...
                self.canvas.itemconfig(item.rect, outline='')

    def clean(self):
        self.remove_from_grid_mat()
        #Delete all the labels of this symbol and remove them from the global list of labels
        for item in self.label_list: # For all the labels in the local list...
            g.label_list.remove(item)
            item.clean()
            del item        
        #Destroy all the canvas items associated with this symbol
        self.canvas.delete(self.tag)

    def addlabel(self, x, y, name, value, orientation, display):
        self.zoom=get_zoom()
        newlabel=label.label(self.canvas, self, self.x+x, self.y+y, name, value, orientation, display)
        self.label_list.append(newlabel)
        g.label_list.append(newlabel)

    def draw(self):
        self.rect=self.canvas.create_rectangle(5, 0, 15, 30, outline='', width=1, tags=(self.tag), dash=(5,5))

    def update_image(self):
        return
    
    def pointisin(self, x, y):
        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        if (x>=x1) and (x<=x2) and (y>=y1) and (y<=y2):
            return 1
        else:
            return 0

    # Move the symbol as well as its labels
    def move(self, dx, dy):
        self.canvas.move(self.tag, dx, dy)
        # Move the labels
        self.x+=dx
        self.y+=dy
        for item in self.label_list: # For all the labels in the local list...
            item.move(dx, dy)

    # Move the symbol.  Don't move the labels.
    def move_nl(self, dx, dy):
        self.canvas.move(self.tag, dx, dy)
        self.x+=dx
        self.y+=dy

    def movetogrid(self):
        self.remove_from_grid_mat()
        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        gridsize=get_zoom()
        x=int((x1+gridsize/2)/gridsize)
        y=int((y1+gridsize/2)/gridsize)
        x*=gridsize
        y*=gridsize
        self.move(x-x1, y-y1)
        self.add_to_grid_mat()
        return

    def configure_label(self, n, x, y, value, direction, visible, height=4):
        self.zoom=get_zoom()
        try:
            self.label_list[n].configure(x, y, value, direction, visible, height)
            x1, y1, x2, y2 = self.canvas.coords(self.label_list[n].rect)
            self.label_list[n].move(-x1, -y1)
            self.label_list[n].move(x*self.zoom, y*self.zoom)
        except:
            pass

    def valueset(self, root, x, y):
        self.zoom=get_zoom()        
        MyDialog(root, self.label_list, x, y)

    # Rotate the symbol around its center.  Don't rotate the labels!
    def rotate_ccw(self):
        self.remove_from_grid_mat()
        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        cx=abs(x1+x2)/2-abs(y2-y1)/2
        cy=abs(y1+y2)/2+abs(x2-x1)/2
        allitems=self.canvas.find_withtag(self.tag)
        for figitem in allitems:
            try: # Deal with the rotation of arcs
                astart=float(self.canvas.itemcget(figitem, 'start'))
                astart+=90
                self.canvas.itemconfig(figitem, start=astart)
                nothing=0
            except:
                nothing=1
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
        self.x=cx
        self.y=cy
        self.direction+=1
        if self.direction > 3:
            self.direction=0
        self.add_to_grid_mat()

    def sym_ascii(self):
        z=get_zoom()
        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        s='symbol,%s,%0.2f,%0.2f,%d,%d\n' % (self.__module__,x1/z,y1/z,self.mirrorv*2+self.mirrorh,self.direction)
        for item in self.label_list:
            x1b, y1b, xb2, y2b = self.canvas.coords(item.rect)
            s+='label,%0.2f,%0.2f,%s,%d,%d,%0.2f\n' % (x1b/z, y1b/z, item.value, item.direction, item.visible, item.height)
        return s
       
class MyDialog(tkSimpleDialog.Dialog):

    def __init__(self, parent, label_list, x, y):
        self.label_list=label_list
        self.myentries=[]
        self.result=[]
        self.on=[]
        self.tag=[]
        self.x=x
        self.y=y
        tkSimpleDialog.Dialog.__init__(self, parent, title="Symbol Settings")

    # The default position of the pop-up assigned in tkSimpleDialog.py is not good, so:
    def geometry (self, position_str):
        tkSimpleDialog.Dialog.geometry(self, "+%d+%d" % (self.parent.winfo_rootx()+self.x, self.parent.winfo_rooty()+self.y))

    def PopfileCallback(self, rowtochange):
        #print("The row is: " + str(rowtochange) + "\n")
        input_filename=tkFileDialog.askopenfilename(title='Add file...', initialdir='./Cases',  filetypes=[("All files", "*.*")] )
        if input_filename:
            self.myentries[rowtochange].delete(0, Tkinter.END)
            self.myentries[rowtochange].insert(0, input_filename[:])
    
    def body(self, master):
        Label(master, text=" Name ").grid(row=0, column=0)
        Label(master, text=" Value ").grid(row=0, column=1)
        Label(master, text=" Visible").grid(row=0, column=2)
        Label(master, text="Show tag").grid(row=0, column=3)
        
        rowcnt=1
        for item in self.label_list:
            if item.get_name().find('File')>0:
                Button(master, text =item.get_name(), command = lambda i=rowcnt-1: self.PopfileCallback(i)).grid(row=rowcnt, column=0)
            else:
                Label(master, text=item.get_name()).grid(row=rowcnt, column=0)
            rowcnt+=1
 
        rowcnt=1
        for item in self.label_list:
            new_entry=Entry(master, width=50)
            new_entry.delete(0, END)
            new_entry.insert(0, item.get_value())
            new_entry.grid(row=rowcnt, column=1)
            self.myentries.append(new_entry)
            rowcnt+=1

        rowcnt=1
        for item in self.label_list:
            self.on.append(Tkinter.IntVar())         
            self.tag.append(Tkinter.IntVar())         
            Checkbutton(master, text="", variable=self.on[rowcnt-1]).grid(row=rowcnt, column=2)
            Checkbutton(master, text="", variable=self.tag[rowcnt-1]).grid(row=rowcnt, column=3)
            if item.visible==1:
                self.on[rowcnt-1].set(1)
                self.tag[rowcnt-1].set(0)
            elif item.visible==2:
                self.on[rowcnt-1].set(1)
                self.tag[rowcnt-1].set(1)
            else:
                self.on[rowcnt-1].set(0)
                self.tag[rowcnt-1].set(0)
            rowcnt+=1

        return self.myentries[0] # initial focus

    def apply(self):
        cnt=0
        for item in self.myentries:
            if (self.on[cnt].get()==1):
                if (self.tag[cnt].get()==1):
                    self.label_list[cnt].visible=2
                else:
                    self.label_list[cnt].visible=1
            else:
                self.label_list[cnt].visible=0
            self.label_list[cnt].set_value(item.get())
            cnt+=1

