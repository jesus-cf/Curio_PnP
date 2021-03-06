#!/usr/bin/python

About_Text="""
Copyright (C) 2020-2021  Jesus Calvino-Fraga
jesuscf (at) gmail.com

This program is free software; you can redistribute
it and/or modify it under the terms of the GNU General
Public License as published by the Free Software
Foundation; either version 2, or (at your option) any
later version.

This program is distributed in the hope that it will
be useful, but WITHOUT ANY WARRANTY; without even the
implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License
for more details.

You should have received a copy of the GNU General
Public License along with this program; if not, write
to the Free Software Foundation, 59 Temple Place -
Suite 330, Boston, MA 02111-1307, USA.
"""

import globalvars as g
from globalvars import *
import sys
from threading import *
import math
import subprocess

sys.path.insert(0, './Symbols')

if sys.version_info[0] < 3:
    import Tkinter
    from Tkinter import *
    import tkMessageBox
    import tkFileDialog
else:
    import tkinter as Tkinter
    from tkinter import *
    from tkinter import messagebox as tkMessageBox
    from tkinter import filedialog as tkFileDialog
    from tkinter import simpledialog

import vectortext
import label
import wire
import os
import string
import colordialog
import ToolTip # Taken from IDLE source code
import Curio
from Curio import *
import time
import datetime

def initlocals():
    global selected_symbol_list, click_x, click_y
    global selected, selected_item, selected_label_list, selected_wire_list
    global scounter, resize_canvas, ctrlkey, wiremode
    global undu_list, undu_ctr
    global Curio_in_Use, abort_PnP, pause_PnP, wires_hidden
    global PnP_X_Offset, PnP_Y_Offset
    global prev_file_modified, file_modified
    
    selected_symbol_list=[]
    selected_label_list=[]
    selected_wire_list=[]
    click_x=0
    click_y=0
    selected=0
    selected_item=0
    scounter=0
    resize_canvas = 1
    ctrlkey=0
    Curio_in_Use=0
    abort_PnP=0
    pause_PnP=0
    wires_hidden=0
    PnP_X_Offset=0.0
    PnP_Y_Offset=0.0
    file_modified=False
    prev_file_modified=True # Used to know when to update the title bar

def addundo(toremove, toadd):
    global undo_list_toadd, undo_list_toremove, undo_ctr
    global filename
    global file_modified

    if toadd==toremove:
        return
    
    del undo_list_toremove[undo_ctr:]
    del undo_list_toadd[undo_ctr:]
    undo_list_toremove.append(toremove)
    undo_list_toadd.append(toadd)
    undo_ctr+=1

    file_modified=True

def do_undo(event=None):
    global undo_list_toadd,  undo_list_toremove, undo_ctr, selected_item
    global selected_symbol_list, selected_label_list, selected_wire_list
    global filename
    global file_modified

    # print ("Undo level is %d" % (undo_ctr)) # for testing

    if(undo_ctr>0):
        file_modified=True
        undo_ctr-=1
    else:
        return # nothing to undo

    # Deselect everything
    selected_item=0
    for item in selected_symbol_list:
        item.select(False)

    for item in selected_wire_list:
        item.select(False)

    selected_symbol_list=[]
    selected_label_list=[]
    selected_wire_list=[]
    
    s1=''.join(undo_list_toadd[undo_ctr])
    addlist=s1.split('\n')
    
    # Remove all the symbols that were added
    for elem in addlist:
        for item in g.symbol_list:
            s2=''.join(item.sym_ascii())
            itemstr=s2.split('\n')
            if itemstr[0]==elem:
                g.symbol_list.remove(item)
                item.clean()
                del item
                break # We found the added one. No need to keep looking

    # Remove all the wires that were added
    for elem in addlist:
        for item in g.wire_list:
            s2=''.join(item.sym_ascii())
            itemstr=s2.split('\n')
            if itemstr[0]==elem:
                g.wire_list.remove(item)
                item.clean()
                del item
                break # We found the added one. No need to keep looking

    # add everything that was removed
    loadfromstring(undo_list_toremove[undo_ctr], 0, False)
     
def do_redo(event=None):
    global undo_list_toadd,  undo_list_toremove, undo_ctr, selected_item
    global selected_symbol_list, selected_label_list, selected_wire_list
    global filename
    global file_modified

    l=len(undo_list_toadd)
    if undo_ctr==l:
        return # Nothing to redo

    selected_item=0
    for item in selected_symbol_list:
        item.select(False)

    for item in selected_wire_list:
        item.select(False)

    selected_symbol_list=[]
    selected_label_list=[]
    selected_wire_list=[]

    s1=''.join(undo_list_toremove[undo_ctr])
    addlist=s1.split('\n')

    # re-remove what was removed
    for elem in addlist:
        for item in g.symbol_list:
            s2=''.join(item.sym_ascii())
            itemstr=s2.split('\n')
            if itemstr[0]==elem:
                g.symbol_list.remove(item)
                item.clean()
                del item
                break # We found the one to remove. No need to keep looking

    for elem in addlist:
        for item in g.wire_list:
            s2=''.join(item.sym_ascii())
            itemstr=s2.split('\n')
            if itemstr[0]==elem:
                g.wire_list.remove(item)
                item.clean()
                del item
                break # We found the one to remove. No need to keep looking

    # re-add what was added
    loadfromstring(undo_list_toadd[undo_ctr], 0, False)
    undo_ctr+=1
    file_modified=True
  
def B1Motion(event):
    global click_x, click_y, selected_item, selected_symbol_list, selected_wire_list, ctrlkey

    if ctrlkey:
        return

    if wiremode==True:
        posx=canvas.canvasx(event.x)
        posy=canvas.canvasy(event.y)
        canvas.coords('ConstructionWire', (click_x, click_y, posx, posy))
        return
    
    if selected_symbol_list or selected_label_list or selected_wire_list:
        posx=canvas.canvasx(event.x)
        posy=canvas.canvasy(event.y)
        # move the selected symbols and their pins. Don't move their labels.
        for item in selected_symbol_list:
            item.move_nl(posx-click_x, posy-click_y)
        # now move the selected labels
        for item in selected_label_list:
            item.move(posx-click_x, posy-click_y)
        for item in selected_wire_list:
            item.move(posx-click_x, posy-click_y)
        click_x=posx
        click_y=posy
    elif selected_item!=0:
        posx=canvas.canvasx(event.x)
        posy=canvas.canvasy(event.y)
        selected_item.move(posx-click_x, posy-click_y)
        click_x=posx
        click_y=posy
    else: # Creating a selection box
        posx=canvas.canvasx(event.x)
        posy=canvas.canvasy(event.y)
        canvas.itemconfig('selection', outline=g.select_color)
        canvas.coords('selection', (click_x, click_y, posx, posy))

def B1Release(event):
    global click_x, click_y, selected_item, selected_symbol_list, selected_label_list, selected_wire_list, ctrlkey
    global buff_toremove

    # If we are adding wires:
    if wiremode==True:
        x0,y0,x1,y1=canvas.coords('ConstructionWire')
        if x0!=x1 or y0!=y1: # If the wire has zero length, ignore it
            # Search for a pin nearby.  If found one nearby, change the corresponding end of the wire
            for item in g.pin_list:
                z=get_zoom()
                a,b,c,d=canvas.coords(item.line)
                if abs(a-x0)<5 and abs(a-y0)<5:
                    x0=a
                    y0=a
                if abs(a-x1)<5 and abs(a-y1)<5:
                    x1=a
                    y1=a          
            newwire=wire.wire(canvas, x0/get_zoom(), y0/get_zoom(), x1/get_zoom(), y1/get_zoom(), '')
            g.wire_list.append(newwire)
            addundo('',newwire.sym_ascii())
        canvas.delete('ConstructionWire')
        return

    if ctrlkey==1:
        ctrlkey=0
    elif selected_symbol_list or selected_label_list or selected_wire_list:
        old_buff_toremove=buff_toremove[:]
        for item in selected_symbol_list:
            item.movetogrid()
        for item in selected_wire_list:
            item.movetogrid()
        rebuild_buff_toremove()
        addundo(old_buff_toremove, buff_toremove)
    elif selected_item!=0: # Dealing just with one item
        selected_item.movetogrid()
        try:
            addundo(buff_toremove, selected_item.parentsymbol.sym_ascii()) # for labels, we need to add the parent symbol
        except:
            addundo(buff_toremove, selected_item.sym_ascii()) # for everything else
    else: # Just created a selection box...
        xs1,ys1,xs2,ys2=canvas.coords('selection') # read the selection box rectangle
        # Reset the list of selected items
        selected_symbol_list=[]
        selected_label_list=[]
        selected_wire_list=[]
        for item in g.label_list: # For all the labels in the list...
            if item.visible!=0: # Important: only visible labels when its parent part is not moving!
                # Check if the label rectangle is completely inside the selection box rectangle
                x1,y1,x2,y2=canvas.coords(item.rect)
                if ( (x1>=xs1 and x1<=xs2) and (y1>=ys1 and y1<=ys2) ) and ( (x2>=xs1 and x2<=xs2) and (y2>=ys1 and y2<=ys2) ):
                    selected_label_list.append(item)            
                else:
                    item.select(False)
            else:
                item.select(False)

        for item in g.symbol_list: # For all the symbols in the list...
            # Check if the symbol rectangle is completely inside the selection box rectangle.  If so, select it
            # and its labels!
            x1,y1,x2,y2=canvas.coords(item.rect) # NEED TO CHANGE THIS BECAUSE IT DOESNT WORK WITH ROTATED SYMBOLS
            if ( (x1>=xs1 and x1<=xs2) and (y1>=ys1 and y1<=ys2) ) and ( (x2>=xs1 and x2<=xs2) and (y2>=ys1 and y2<=ys2) ):
                item.select(True)
                selected_symbol_list.append(item)
                for itemlabel in item.label_list:
                    # EXPERIMENT:
                    try:
                       canvas.itemconfigure(item.tag_fill, fill = get_select_color())
                       canvas.itemconfigure(item.tag_outline, outline = get_select_color())
                    except:
                       pass

                    if itemlabel not in selected_label_list:
                        selected_label_list.append(itemlabel)
                    if itemlabel.visible==0: # Important: Move invisible label with its parent part!
                        selected_label_list.append(itemlabel)
            else:
                item.select(False)
                # EXPERIMENT:
                try:
                   canvas.itemconfigure(item.tag_fill, fill = get_symbol_color())
                   canvas.itemconfigure(item.tag_outline, outline = get_symbol_color())
                except:
                   pass

        for item in selected_label_list:
            item.select(True)

        for item in g.wire_list: # For all the wires in the list...
            # Check if the wire is completely inside the selection box rectangle or if one of the ends is inside the
            # the selection rectangle.
            x1,y1,x2,y2=canvas.coords(item.line)
            if ( (x1>=xs1 and x1<=xs2) and (y1>=ys1 and y1<=ys2) ) and ( (x2>=xs1 and x2<=xs2) and (y2>=ys1 and y2<=ys2) ):
                item.select(True)
                for itemlabel in item.label_list:
                    if itemlabel not in selected_label_list:
                        selected_label_list.append(itemlabel)
                    if itemlabel.visible==0: # Important: Move invisible label with its parent part!
                        selected_label_list.append(itemlabel)
                selected_wire_list.append(item)
                item.setmove(True, True)
            elif ( (x1>=xs1 and x1<=xs2) and (y1>=ys1 and y1<=ys2) ):
                selected_wire_list.append(item)
                item.setmove(True, False)
                item.select(True)
            elif ( (x2>=xs1 and x2<=xs2) and (y2>=ys1 and y2<=ys2) ):
                selected_wire_list.append(item)
                item.setmove(False, True)
                item.select(True)
            else:
                item.setmove(False, False)
                item.select(False)

        rebuild_buff_toremove()
        canvas.itemconfig('selection', outline='')
        canvas.coords('selection', (0,0,0,0))
        
def B1Press(event):
    global click_x, click_y, selected_item, selected_symbol_list, selected_label_list, selected_wire_list, ctrlkey
    global buff_toremove
    
    if ctrlkey==1:
        return
    
    posx=canvas.canvasx(event.x)
    posy=canvas.canvasy(event.y)

    if wiremode==True:
        click_x=posx
        click_y=posy
        canvas.create_line(click_x, click_y, click_x+1, click_y+1, fill = get_select_color(), width=3*get_zoom(), tags="ConstructionWire")
        return

    # Check if the button has been pressed on any selected item.  If not, deselect all selected items
    # and check if the click is in any other item.
    count=0
    
    for item in selected_symbol_list:
        if item.pointisin(posx, posy)==1:
           count+=1
           break
        
    if count==0:
        for item in selected_label_list:
            if item.pointisin(posx, posy)==1:
                count+=1
                break
            
    if count==0:
        for item in selected_wire_list:
            if item.pointisin(posx, posy)==1:
                count+=1
                break
            
    if count==0: # not in a selected item
        for item in selected_symbol_list:
            item.select(False)
            try:
                canvas.itemconfigure(item.tag_fill, fill = get_symbol_color())
                canvas.itemconfigure(item.tag_outline, outline = get_symbol_color())
            except:
                pass
        selected_symbol_list=[]

        for item in selected_label_list:
            item.select(False)
        selected_label_list=[]
        canvas.itemconfigure('text', fill = get_label_color())

        for item in selected_wire_list:
            item.select(False)
        selected_wire_list=[]

        for item in g.label_list: # For all the labels in the list that are visible...
            if item.pointisin(posx, posy)==1 and item.visible!=0:
               canvas.itemconfigure("wirebuble", outline = get_wire_color())
               canvas.itemconfigure("wires", fill = '')
               if wires_hidden==0:
                   canvas.itemconfigure("wireline", fill = get_wire_color())
               else:
                   canvas.itemconfigure("wireline", fill = '')             
               selected_item=item
               click_x=posx
               click_y=posy
               # Change the color of the label
               canvas.itemconfigure(item.tagtext, fill = get_select_color()) 
               buff_toremove=item.parentsymbol.sym_ascii() # Must add the parent symbol!
               return

        # Give preference to the wire ends
        for item in g.wire_list: # For all the wires in the list...
            if item.nearP1(posx, posy)==True:
               canvas.itemconfigure("wirebuble", outline = get_wire_color())
               canvas.itemconfigure("wires", fill = '')
               if wires_hidden==0:
                   canvas.itemconfigure("wireline", fill = get_wire_color())
               else:
                   canvas.itemconfigure("wireline", fill = '')                  
               canvas.itemconfigure("wireline", fill = '')
               selected_item=item
               item.setmove(True, False)
               canvas.itemconfigure(item.tag, fill = get_select_color())
               canvas.itemconfigure("wirebox", fill = '')
               click_x=posx
               click_y=posy
               buff_toremove=item.sym_ascii()
               return

        # Give preference to the wire ends
        for item in g.wire_list: # For all the wires in the list...
            if item.nearP2(posx, posy)==True:
               canvas.itemconfigure("wirebuble", outline = get_wire_color())
               canvas.itemconfigure("wires", fill = '')
               if wires_hidden==0:
                   canvas.itemconfigure("wireline", fill = get_wire_color())
               else:
                   canvas.itemconfigure("wireline", fill = '')                  
               selected_item=item
               item.setmove(False, True)
               canvas.itemconfigure(item.tag, fill = get_select_color())
               canvas.itemconfigure("wirebox", fill = '')
               click_x=posx
               click_y=posy
               buff_toremove=item.sym_ascii()
               return

        if wires_hidden==0: # Hidden wires are not selectable.
            for item in g.wire_list: # For all the wires in the list...
                if item.pointisin(posx, posy)==1:
                   canvas.itemconfigure("wirebuble", outline = get_wire_color())
                   canvas.itemconfigure("wires", fill = '')
                   canvas.itemconfigure("wireline", fill = get_wire_color())
                   selected_item=item 
                   item.setmove(True, True)
                   canvas.itemconfigure(item.tag, fill = get_select_color())
                   canvas.itemconfigure("wirebox", fill = '')
                   click_x=posx
                   click_y=posy
                   buff_toremove=item.sym_ascii()
                   return

        for item in g.wire_list: # For all the wires in the list...
           canvas.itemconfigure("wirebuble", outline = get_wire_color())
           canvas.itemconfigure("wires", fill = '')
           if wires_hidden==0:
               canvas.itemconfigure("wireline", fill = get_wire_color())       
           else:
               canvas.itemconfigure("wireline", fill = '')             

        selected_item=0         
        for item in g.symbol_list: # For all the symbols in the list...
            if item.pointisin(posx, posy)==1:
               try:
                   canvas.itemconfigure(item.tag_fill, fill = get_select_color())
                   canvas.itemconfigure(item.tag_outline, outline = get_select_color())
               except:
                   pass
               selected_item=item
               click_x=posx
               click_y=posy
               buff_toremove=item.sym_ascii()
            else:
               try:
                   canvas.itemconfigure(item.tag_fill, fill = get_symbol_color())
                   canvas.itemconfigure(item.tag_outline, outline = get_symbol_color())
               except:
                   pass
        if selected_item!=0:
            return

    canvas.itemconfigure("wirebuble", outline = get_wire_color())
    canvas.itemconfigure("wires", fill = '')
    if wires_hidden==0:
        canvas.itemconfigure("wireline", fill = get_wire_color())
    else:
        canvas.itemconfigure("wireline", fill = '')
    selected_item=0
    click_x=posx
    click_y=posy

def rebuild_buff_toremove():
    global selected_label_list, selected_symbol_list, selected_wire_list
    global buff_toremove

    touched_symbol=[]
    buff_toremove=[]
    
    for item in selected_label_list:
        if item.parentsymbol not in touched_symbol:
            touched_symbol.append(item.parentsymbol)
            buff_toremove+=item.parentsymbol.sym_ascii()

    for item in selected_symbol_list:
        if item not in touched_symbol:
            touched_symbol.append(item)
            buff_toremove+=item.sym_ascii()

    for item in selected_wire_list:
        buff_toremove+=item.sym_ascii()

def B1CtrlPress(event):
    global click_x, click_y, selected_label_list, selected_symbol_list, selected_wire_list, ctrlkey

    posx=canvas.canvasx(event.x)
    posy=canvas.canvasy(event.y)
    ctrlkey=1

    for item in g.label_list: # For all the labels in the list...
        if item.pointisin(posx, posy)==1 and item.visible==1:
            if item in selected_label_list:
                selected_label_list.remove(item)
                canvas.itemconfigure(item.rect, outline = "")
                item.select(False)
            else:
                selected_label_list.append(item)
                canvas.itemconfigure(item.rect, outline = get_select_color())
                item.select(True)
            click_x=posx
            click_y=posy
            rebuild_buff_toremove()
            return

    for item in g.symbol_list: # For all the symbols in the list...
        if item.pointisin(posx, posy)==1:
            if item in selected_symbol_list:
               selected_symbol_list.remove(item)
               try:
                   canvas.itemconfigure(item.tag_fill, fill = get_symbol_color())
                   canvas.itemconfigure(item.tag_outline, outline = get_symbol_color())
               except:
                   pass
               for itemlabel in item.label_list:
                    if itemlabel in selected_label_list:
                        selected_label_list.remove(itemlabel)
                        if itemlabel.visible==1:
                            canvas.itemconfigure(item.rect, outline = "")
                        itemlabel.select(True)
               item.select(False)
            else:
               try:
                   canvas.itemconfigure(item.tag_fill, fill = get_select_color())
                   canvas.itemconfigure(item.tag_outline, outline = get_select_color())
               except:
                   pass
               selected_symbol_list.append(item)
               for itemlabel in item.label_list:
                    if itemlabel not in selected_label_list:
                        selected_label_list.append(itemlabel)
                        if itemlabel.visible==1:
                            canvas.itemconfigure(item.rect, outline = get_select_color())
                        itemlabel.select(True)
               item.select(True)
            click_x=posx
            click_y=posy
            rebuild_buff_toremove()
            return

    for item in g.wire_list: # For all the wires in the list...
        if item.pointisin(posx, posy)==1:
            item.setmove(True, True)
            #item.printmove() # For debug, prints the states of item.move0 and item.move1
            if item in selected_wire_list:
                canvas.itemconfigure(item.tag, fill = get_wire_color())
                selected_wire_list.remove(item)
                for itemlabel in item.label_list:
                    if itemlabel in selected_label_list:
                        selected_label_list.remove(itemlabel)
                        if itemlabel.visible==1:
                            canvas.itemconfigure(item.rect, outline = "")
                        itemlabel.select(True)
                item.select(False)
            else:
                canvas.itemconfigure(item.tag, fill = get_select_color())
                selected_wire_list.append(item)
                for itemlabel in item.label_list:
                    if itemlabel not in selected_label_list:
                        selected_label_list.append(itemlabel)
                        if itemlabel.visible==1:
                            canvas.itemconfigure(item.rect, outline = get_select_color())
                        itemlabel.select(True)
                item.select(True)
            click_x=posx
            click_y=posy
            rebuild_buff_toremove()
            return

    rebuild_buff_toremove()
    click_x=posx
    click_y=posy

def DoubleB1Press(event):
    posx=canvas.canvasx(event.x)
    posy=canvas.canvasy(event.y)

    # This one may take a very long time to run
    for item in g.wire_list: # For all the wires in the list...
        if item.pointisin(posx, posy)==1:
           buff_toremove=item.sym_ascii()
           item.valueset(root, event.x, event.y)
           buff_toadd=item.sym_ascii()
           addundo(buff_toremove, buff_toadd)
           return
    
    for item in g.label_list: # For all the labels in the list...
        if (item.pointisin(posx, posy)==1) and (item.visible>0):
           buff_toremove=item.parentsymbol.sym_ascii() # undo goes to its parent symbol instead
           item.valueset(root, event.x, event.y)
           buff_toadd=item.parentsymbol.sym_ascii() # undo goes to its parent symbol instead
           addundo(buff_toremove, buff_toadd)
           return

    for item in g.symbol_list: # For all the symbols in the list...
        if item.pointisin(posx, posy)==1:
           buff_toremove=item.sym_ascii()
           item.valueset(root, event.x, event.y)
           buff_toadd=item.sym_ascii()
           addundo(buff_toremove, buff_toadd)
           return
  
def do_cut(event=None):
    do_copy()
    do_delete()
    
def do_delete(event=None):
    global click_x, click_y, selected_symbol_list, selected_label_list, selected_wire_list
    global buff_toremove
    
    # Check selected items first
    if selected_symbol_list or selected_wire_list:
        buff_toremove=[]
        for item in selected_symbol_list:
            buff_toremove+=item.sym_ascii()
            item.clean()
            g.symbol_list.remove(item)
            del item
        for item in selected_wire_list:
            buff_toremove+=item.sym_ascii()
            item.clean()
            g.wire_list.remove(item)
            del item
        addundo(buff_toremove,'');
        selected_symbol_list=[]
        selected_label_list=[]
        selected_wire_list=[]
        return # skip the rest...
    
    for item in g.symbol_list: # For all the symbols in the list...
        if item.pointisin(click_x, click_y)==1:
            buff_toremove=item.sym_ascii()
            item.clean()
            g.symbol_list.remove(item)
            del item
            addundo(buff_toremove,'');
            return

    for item in g.wire_list: # For all the wires in the list...
        if item.pointisin(click_x, click_y)==1:
            buff_toremove=item.sym_ascii()
            item.clean()
            g.wire_list.remove(item)
            del item
            addundo(buff_toremove,'');
            return
        
def do_rotate_ccw(event=None):
    global click_x, click_y, selected_symbol_list, selected_label_list, selected_wire_list
    global buff_toremove

    if selected_symbol_list or selected_label_list or selected_wire_list:
        for item in selected_symbol_list:
            item.rotate_ccw()
        for item in selected_label_list:
            item.rotate_ccw()
        for item in selected_wire_list:
            item.rotate_ccw()
        toremove=buff_toremove[:] # Copy the string
        rebuild_buff_toremove()
        toadd=buff_toremove[:] # Copy the string
        addundo(toremove, toadd)
    else:
        for item in g.symbol_list: # For all the symbols in the list...
            if item.pointisin(click_x, click_y)==1:
                buff_toremove=item.sym_ascii()
                item.rotate_ccw()
                buff_add=item.sym_ascii()
                addundo(buff_toremove,buff_add)
                return
            
        for item in g.label_list: # For all the labels in the list...
            if item.pointisin(click_x, click_y)==1:
                buff_toremove=item.parentsymbol.sym_ascii()  # WARNING: undo the label parent symbol instead
                item.rotate_ccw()
                buff_add=item.parentsymbol.sym_ascii()
                addundo(buff_toremove,buff_add)
                return
            
        for item in g.wire_list: # For all the wires in the list...
            if item.pointisin(click_x, click_y)==1:
                buff_toremove=item.sym_ascii()
                item.rotate_ccw()
                buff_add=item.sym_ascii()
                addundo(buff_toremove,buff_add)
                return

def AddSymbol(event=None):
    global click_x, click_y

    input_filename=tkFileDialog.askopenfilename(title='Select new symbol', initialdir='./Symbols',
                                                filetypes=[("All files", "*.*"),('Symbol files', 'sim_*.py')] )
    if input_filename:
        head, tail = os.path.split(input_filename)
        fname, extension = os.path.splitext(tail)
        mod = __import__(fname)
        try:
            newsymbol=mod.sym(canvas, click_x/get_zoom(), click_y/get_zoom())
            newsymbol.movetogrid()
            buff_add=newsymbol.sym_ascii()
            addundo('',buff_add)
            g.symbol_list.append(newsymbol)
        except:
            tkMessageBox.showerror("PNP_Curio ERROR", "Not a valid symbol file.")

def do_zoomto(val):
    h0,h1=hbar.get()
    v0,v1=vbar.get()
    zold=float(get_zoom())
    z=val
    if z>10.0:
        z=10.0
    if z<0.5:
        z=0.5    
    set_zoom(z)
    canvas.config(scrollregion=(0,0,g.canvas_xsize*get_zoom(),g.canvas_ysize*get_zoom()))
    canvas.scale("all", 0, 0, z/zold, z/zold)
    hbar.set(h0,h1)
    vbar.set(v0,v1)
    try:
        canvas.itemconfigure("all", width=get_zoom())
    except:
        pass
    canvas.itemconfigure("wires", width=get_zoom()*3)
    canvas.itemconfigure("text", width=get_zoom()*3)
    canvas.itemconfigure("grid", width=1)
    canvas.itemconfigure("selection", width=1)
    
def do_zoomin(event=None):
    h0,h1=hbar.get()
    v0,v1=vbar.get()
    zold=float(get_zoom())
    z=zold+0.5
    if z>10.0:
        z=10.0
    set_zoom(z)
    canvas.config(scrollregion=(0,0,g.canvas_xsize*get_zoom(),g.canvas_ysize*get_zoom()))
    canvas.scale("all", 0, 0, z/zold, z/zold)
    hbar.set(h0,h1)
    vbar.set(v0,v1)
    try:
        canvas.itemconfigure("all", width=get_zoom())
    except:
        pass
    canvas.itemconfigure("wires", width=get_zoom()*3)
    canvas.itemconfigure("text", width=get_zoom()*3)
    canvas.itemconfigure("grid", width=1)
    canvas.itemconfigure("selection", width=1)

def do_zoomout(event=None):
    h0,h1=hbar.get()
    v0,v1=vbar.get()
    zold=float(get_zoom())
    z=zold-0.5
    if z<0.5:
        z=0.5
    set_zoom(z)
    canvas.scale("all", 0, 0, z/zold, z/zold)
    canvas.config(scrollregion=(0,0,g.canvas_xsize*get_zoom(),g.canvas_ysize*get_zoom()))
    hbar.set(h0,h1)
    vbar.set(v0,v1)
    try:
        canvas.itemconfigure("all", width=get_zoom())
    except:
        pass
    canvas.itemconfigure("text", width=get_zoom()*3)
    canvas.itemconfigure("wires", width=get_zoom()*3)
    canvas.itemconfigure("grid", width=1)
    canvas.itemconfigure("selection", width=1)

def do_valueset():
    global click_x, click_y

    # The functionality is built in wires, but not used so skip them
    for item in g.wire_list: # For all the wires in the list...
        if item.pointisin(click_x, click_y)==1:
            remove_buffer=item.sym_ascii()
            item.valueset(root, screen_x, screen_y)
            add_buffer=item.sym_ascii()
            addundo(remove_buffer, add_buffer)
            return

    for item in g.label_list: # For all the labels in the list...
        if (item.pointisin(click_x, click_y)==1) and (item.visible>0):
           remove_buffer=item.parentsymbol.sym_ascii() # Undo goes to the label parent symbol
           item.valueset(root, screen_x, screen_y)
           add_buffer=item.parentsymbol.sym_ascii()
           addundo(remove_buffer, add_buffer)
           return

    for item in g.symbol_list: # For all the symbols in the list...
        if item.pointisin(click_x, click_y)==1:
           remove_buffer=item.sym_ascii()
           item.valueset(root, screen_x, screen_y)
           add_buffer=item.sym_ascii()
           addundo(remove_buffer, add_buffer)
           return


def do_copy(event=None):
    global selected_symbol_list, selected_wire_list 
    copy_buffer=[]
    if selected_symbol_list or selected_wire_list:
        for item in selected_symbol_list:
            copy_buffer+=item.sym_ascii()
        for item in selected_wire_list:
            copy_buffer+=item.sym_ascii()
    elif selected_item!=0:
        copy_buffer=selected_item.sym_ascii()
    root.clipboard_clear()
    root.clipboard_append(''.join(copy_buffer))

def do_paste(event=None):
    result = root.selection_get(selection = "CLIPBOARD") 
    loadfromstring(result, 50, True)
    add_buffer=[]
    for item in selected_symbol_list:
        add_buffer+=item.sym_ascii()
    for item in selected_wire_list:
        add_buffer+=item.sym_ascii()
    addundo('',add_buffer)
    
def do_popup(event=None):
    global click_x, click_y, screen_x, screen_y
    global event_x_root, event_y_root
    # Read the scroll bars and convert to screen coordinates
    screen_x=event.x
    screen_y=event.y
    click_x=canvas.canvasx(event.x)
    click_y=canvas.canvasy(event.y)
    try:
       event_x_root=event.x_root
       event_y_root=event.y_root
       popup.tk_popup(event_x_root, event_y_root, 0)
    finally:      
       popup.grab_release() # make sure to release the grab (Tk 8.0a1 only)

def do_popup2(event=None):
    global event_x_root, event_y_root
    try:
       popup2.tk_popup(event_x_root, event_y_root, 0)
    finally:
       popup.grab_release()

def do_wireonoff(event=None):
    global wiremode
    if wiremode==True:
        wiremode=False
        canvas.config( cursor="top_left_arrow")
    else:
        wiremode=True
        canvas.config( cursor="pencil")

def do_editmode(event=None):
    global wiremode
    wiremode=False
    canvas.config( cursor="top_left_arrow")

def do_quit():
    global file_modified
    
    if file_modified:
        mymessage='File %s has changes.  Do you want to discard them?' % (filename)
        if not tkMessageBox.askyesno("Open File", mymessage):
            return
    Save_Configuration()
    root.destroy()
  
def do_savefile(event=None):
    global filename
    global file_modified

    if filename:
        text_file = open(filename, "w")
        for item in g.symbol_list: # For all the symbols in the list...
            text_file.write("%s"%item.sym_ascii())
        for item in g.wire_list: # For all the wires in the list...
            text_file.write("%s"%item.sym_ascii())
        text_file.close()
        file_modified=False
    else:
        savefileas()

def savefileas():
    global filename
    global prev_file_modified, file_modified

    output_filename=tkFileDialog.asksaveasfilename(title='Save file...', initialdir='./Cases',  filetypes=[("All files", "*.*"),('Symbol files', '*.txt')] )
    if output_filename:
        filename=output_filename[:]
        Add_Recent_File(filename, filemenu, Recent_File_Callback)
        text_file = open(output_filename, "w")
        for item in g.symbol_list: # For all the symbols in the list...
            text_file.write("%s"%item.sym_ascii())
        for item in g.wire_list: # For all the wires in the list...
            text_file.write("%s"%item.sym_ascii())
        text_file.close()
        file_modified=False
        prev_file_modified=True # To refresh title bar

def loadfromstring(str, offset, select):
    global selected_symbol_list, selected_label_list, selected_wire_list

    s=''.join(str)
    mylines=s.split('\n')

    if select==True:
        for item in selected_symbol_list:
            item.select(False)

        for item in selected_wire_list:
            item.select(False)

        selected_symbol_list=[]
        selected_label_list=[]
        selected_wire_list=[]

    for item in mylines:
        row=item.split(',')
        z=get_zoom()
        if row:
            if row[0]=='symbol':
                newsym = __import__(row[1])
                x=float(row[2])
                y=float(row[3])
                direction=int(row[5])
                currsym=newsym.sym(canvas, x, y)
                if direction==1:
                    currsym.rotate_ccw()
                elif direction==2:
                    currsym.rotate_ccw()
                    currsym.rotate_ccw()
                elif direction==3:
                    currsym.rotate_ccw()
                    currsym.rotate_ccw()
                    currsym.rotate_ccw()
                x1, y1, x2, y2 = canvas.coords(currsym.rect) # get the symbol bounding rectangle after rotation
                currsym.move( ((x+offset)*z)-x1, ((y+offset)*z)-y1 ) # move the symbol to its final position
                if select==True:
                    currsym.select(True)
                    selected_symbol_list.append(currsym)
                g.symbol_list.append(currsym)
                currsym.remove_from_grid_mat()
                currsym.add_to_grid_mat()
                labelcnt=0
            elif row[0]=='label':
                # some old files don't have the height of the label which is row[6], so
                try:
                    asdf=row[6]
                except:
                    row.append('4.0')
                currsym.configure_label(labelcnt, float(row[1])+offset, float(row[2])+offset, row[3], float(row[4]), float(row[5]), float(row[6]))
                if select==True:
                    currsym.select(True) # Doh! Need to remark the symbol/wire after altering its labels...
                    selected_label_list.append(currsym.label_list[labelcnt])
                labelcnt+=1
            elif row[0]=='wire':
                currsym=wire.wire(canvas, float(row[1])+offset, float(row[2])+offset, float(row[3])+offset, float(row[4])+offset, '')
                g.wire_list.append(currsym)
                labelcnt=0
                if select==True:
                    currsym.select(True)
                    selected_wire_list.append(currsym)
    rebuild_buff_toremove()

def Recent_File_Callback (idx):
    openfile(g.recent_files[idx])

def go_openfile(event):
    openfile()

def openfile(passed_name=''):
    global filename, undo_ctr, filemenu
    global prev_file_modified, file_modified
  
    if file_modified:
        mymessage='File %s has changes.  Do you want to discard them?' % (filename)
        if not tkMessageBox.askyesno("Open File", mymessage):
            return

    if len(passed_name)>0:
        input_filename=passed_name[:]
    else:
        input_filename=tkFileDialog.askopenfilename(title='Open file...', initialdir='./Cases',  filetypes=[("All files", "*.*"),('Symbol files', '*.txt')] )

    if input_filename:
        newfile(ask=False)
        filename=input_filename[:]

        try:
            myfile=open(input_filename, 'r')
        except:
            Remove_Recent_File(filename, filemenu, Recent_File_Callback)
            tkMessageBox.showerror("PNP_Curio ERROR", "Can not read file % s" % input_filename)
            return

        file_modified=False
        prev_file_modified=True # Updates the title bar
        Add_Recent_File(filename, filemenu, Recent_File_Callback)
        canvas.config(cursor="watch")
        canvas.update()
        all_the_text = myfile.read()
        myfile.close()
        loadfromstring(all_the_text, 0, False)
        canvas.config( cursor="top_left_arrow")
        do_zoomto(1.0)
    
def go_newfile(event):
    newfile()

def newfile(ask=True):
    global filename, undo_ctr, undo_list_toremove, undo_list_toadd
    global prev_file_modified, file_modified

    if file_modified and ask==True:
        mymessage='File %s has changes.  Do you want to discard them?' % (filename)
        if not tkMessageBox.askyesno("Open File", mymessage):
            return

    Save_Configuration()

    filename=''
    file_modified=False
    prev_file_modified=True # Updates the title bar
    for item in g.symbol_list: # For all the symbols in the list...
        item.clean()
        del item
    for item in g.wire_list: # For all the wires in the list...
        item.clean()
        del item
    initglobals()
    initlocals()
    undo_list_toremove=[]
    undo_list_toadd=[]
    undo_ctr=0

    # Reconfigure working area
    g.canvas_ysize=1530 # use small tray
    h0,h1=hbar.get()
    v0,v1=vbar.get()
    canvas.config( scrollregion=(0, 0, g.canvas_xsize*get_zoom(), g.canvas_ysize*get_zoom()) )
    hbar.set(h0,h1)
    vbar.set(v0,v1)

    g.grid_mat = [[0 for x in range(g.canvas_ysize//10)] for x in range(g.canvas_xsize//10)]
    for x in range(g.canvas_xsize//10):
        for y in range(g.canvas_ysize//10):
            g.grid_mat[x][y]=0
    drawgrid()    

def Help():
    manual="./Manual/PNP_Curio.pdf"
    if sys.platform.lower().startswith('win'):
        manual=manual.replace('/','\\')
    subprocess.Popen(manual, shell=True)

def About():
    #print (About_Text)
    tkMessageBox.showinfo("About PNP_Curio", About_Text)

def drawgrid():
    global showgrid
    try:
        canvas.delete('grid')
        canvas.delete('selection')
        canvas.delete('border')
    except:
        pass

    z=get_zoom()
    xcnt=0
    while xcnt<g.canvas_xsize:
        canvas.create_line(xcnt, 0, xcnt, g.canvas_ysize, fill = '', tags='grid')
        xcnt+=10

    ycnt=0
    while ycnt<g.canvas_ysize:
        canvas.create_line(0, ycnt, g.canvas_xsize, ycnt, fill = '', tags='grid')
        ycnt+=10

    canvas.create_line(0, 0, g.canvas_xsize, 0, g.canvas_xsize, g.canvas_ysize, 0, g.canvas_ysize, 0, 0, fill = '', tags='border')
    
    canvas.itemconfig('grid', fill=g.grid_color)
    canvas.itemconfig('border', fill=g.grid_color)
    canvas.scale('grid', 0, 0, z, z)
    canvas.scale('border', 0, 0, z, z)
    canvas.tag_lower('grid')
    canvas.tag_lower('border')
    
    showgrid=True
    canvas.create_rectangle(0, 0, 20, 30, outline='', width=1, tags='selection', dash=(5,5))

def do_gridonoff():
    global showgrid
    if showgrid==False:
        canvas.itemconfig('grid', fill=g.grid_color)
        showgrid=True
    else:
        canvas.itemconfig('grid', fill='')
        showgrid=False

def do_color_dialog():
    c=colordialog.colordialog(canvas)
    canvas.config(bg=g.bg_color)
    if showgrid==True:
        canvas.itemconfig('grid', fill=g.grid_color)

    # Load a string buffer with all the elements in the diagram
    temp_buffer=[]
    for item in g.symbol_list:
        temp_buffer+=item.sym_ascii()
        item.clean()
        del item
    for item in g.wire_list:
        temp_buffer+=item.sym_ascii()
        item.clean()
        del item

    Save_Configuration()
    initglobals()
    initlocals()
    loadfromstring(temp_buffer, 0, False) # Display all saved elements with the new colors

def GetCurioReady():
    global P
    try:
        P=SilhouetteCameo()
        P.setup(pen=True)
        P.move_origin(0)
        P.Set_Pressure(1) # 1 to 33
        P.Set_Speed(10) # 1 to 10
    except:
        pass

def go_draw_text(event=None):
    global Curio_in_Use, abort_PnP
    if Curio_in_Use:
        return
    Curio_in_Use=1
    abort_PnP=0
    t5=Thread(target=do_draw_text)
    t5.start()
    
def do_draw_text_old():
    global Curio_in_Use, abort_PnP
    global P
    z=get_zoom()

    try:
        P.clrcmds()
    except:
        GetCurioReady()
        try:
            P.clrcmds()
        except:
            tkMessageBox.showerror("PnP ERROR", "Curio not ready")
            return

    P.Use_Pen()
    P.Set_Pressure(15) # 1 to 33
    P.Set_Speed(5) # 1 to 10

    P.tool_down(0, 0)

    allitems=canvas.find_withtag("text")
    count=0
    for figitem in allitems:
        if abort_PnP==1:
            break
        points= canvas.coords(figitem)
        points = [i/z for i in points] # zoom adjust       
        points = [i/10 for i in points] # to convert to mm divide by 10
        P.addcmd(points)
        count=count+1
        if count==50:
            P.sendcmds()
            count=0

    if abort_PnP==1:
        print("\nText draw aborted by user")
        abort_PnP=0
    else:
        if count!=0:
            P.sendcmds()
            
    P.move_xy(0, 0)
    P.Use_Pen()
    P.Set_Pressure(1) # 1 to 33
    P.Set_Speed(10) # 1 to 10

    Curio_in_Use=0

def do_draw_text():
    global Curio_in_Use, abort_PnP
    global PnP_X_Offset, PnP_Y_Offset
    global P
    z=get_zoom()

    try:
        P.clrcmds()
    except:
        GetCurioReady()
        try:
            P.clrcmds()
        except:
            tkMessageBox.showerror("PnP ERROR", "Curio not ready")
            return

    P.Use_Pen()
    P.Set_Pressure(15) # 1 to 33
    P.Set_Speed(5) # 1 to 10

    P.tool_down(0, 0)

    todraw=[]
    if selected_item:
        todraw.append(selected_item)
    elif selected_label_list:
        todraw=selected_symbol_list
    else:
        todraw=g.label_list

    count=0
    for item in todraw:
        if 'LABEL' in item.tag:
            if item.visible==1:
                #allitems=canvas.find_withtag("text" and item.tag) # This add an extra line I don't know where is coming from...
                allitems=canvas.find_withtag(item.tagtext) 
                for itemtext in allitems:
                    if abort_PnP==1:
                        break
                    points= canvas.coords(itemtext)
                    points = [i/z for i in points] # zoom adjust       
                    points = [i/10 for i in points] # to convert to mm divide by 10
                    # Add the offset in mm
                    for j in range (0, len(points), 2):
                        points[j+0]=points[j+0]+PnP_X_Offset
                        points[j+1]=points[j+1]+PnP_Y_Offset
                    P.addcmd(points)
                    count=count+1
                    if count==50:
                        P.sendcmds()
                        count=0

    if abort_PnP==1:
        print("\nText draw aborted by user")
        abort_PnP=0
    else:
        if count!=0:
            P.sendcmds()
            
    P.move_xy(0, 0)
    P.Use_Pen()
    P.Set_Pressure(1) # 1 to 33
    P.Set_Speed(10) # 1 to 10

    Curio_in_Use=0

def do_draw_gage(event=None):
    global Curio_in_Use, abort_PnP
    global PnP_X_Offset, PnP_Y_Offset
    global P
    z=get_zoom()

    try:
        P.clrcmds()
    except:
        GetCurioReady()
        try:
            P.clrcmds()
        except:
            tkMessageBox.showerror("PnP ERROR", "Curio not ready")
            return

    P.Use_Pen()
    P.Set_Pressure(15) # 1 to 33
    P.Set_Speed(5) # 1 to 10

    P.tool_down(0, 0)

    count=0
    allitems=canvas.find_withtag('gage_line') 
    for item in allitems:
        if abort_PnP==1:
            break
        points= canvas.coords(item)
        points = [i/z for i in points] # zoom adjust       
        points = [i/10 for i in points] # to convert to mm divide by 10
        # Add the offset in mm
        for j in range (0, len(points), 2):
            points[j+0]=points[j+0]+PnP_X_Offset
            points[j+1]=points[j+1]+PnP_Y_Offset
        P.addcmd(points)
        count=count+1
        if count==50:
            P.sendcmds()
            count=0

    if abort_PnP==1:
        print("\nGage line draw aborted by user")
        abort_PnP=0
    else:
        if count!=0:
            P.sendcmds()
            
    P.move_xy(0, 0)
    P.Use_Pen()
    P.Set_Pressure(1) # 1 to 33
    P.Set_Speed(10) # 1 to 10

    Curio_in_Use=0

def go_cut_foam_gig(event=None):
    global Curio_in_Use, abort_PnP
    if Curio_in_Use:
        return
    Curio_in_Use=1
    abort_PnP=0
    t3=Thread(target=do_cut_foam_gig)
    t3.start()

def do_cut_foam_gig():
    global Curio_in_Use, abort_PnP
    global PnP_X_Offset, PnP_Y_Offset
    global P
    z=get_zoom()

    try:
        P.clrcmds()
    except:
        GetCurioReady()
        try:
            P.clrcmds()
        except:
            tkMessageBox.showerror("PnP ERROR", "Curio not ready")
            return

    P.Use_Blade()
    P.Set_Pressure(15) # 1 to 33
    P.Set_Speed(5) # 1 to 10

    #P.tool_down(0, 0)

    tocut=[]
    if selected_item:
        tocut.append(selected_item)
    elif selected_symbol_list:
        tocut=selected_symbol_list
    else:
        tocut=g.symbol_list

    angles=[] # list of all possible cut angles
    for item in tocut:
        points=[]
        if 'CUT_TAPE' in item.tag:
            # Are we cutting the internal or external perimeter?
            incut=item.label_list[7].get_value()
            if (incut=='1' or incut.lower()=='yes' or incut.lower()=='y' or incut.lower()=='on' or incut.lower()=='true'): 
                points=canvas.coords(item.insidecut)
            else:
                points=canvas.coords(item.tapeframe)
        elif 'PCB' in item.tag:
            points=canvas.coords(item.pcbframe)
        elif 'GAGE' in item.tag:
            points=canvas.coords(item.gageframe)

        if len(points) > 0:
            for j in range(0, len(points)-2, 2): # Check the angles of the poly lines. Append them to the list if needed.
                x=points[j+2]-points[j+0]
                y=points[j+3]-points[j+1]
                curr_angle=round(math.atan2(y, x)*180/math.pi,0) # store in degrees with no decimals (it should be enough)
                if curr_angle==-180.0:
                    curr_angle=180.0
                # print("Current angle: " + str(curr_angle) + " j: " + str(j))
                if curr_angle not in angles:
                    # print("New angle: " + str(curr_angle))
                    angles.append(curr_angle)

    x0=0.0
    y0=0.0
    for item in g.symbol_list: # Look for the configuration symbol to find out where to put the blade align cuts
        if 'CONFIGURATION' in item.tag:
            rpoints=canvas.coords(item.rect)
            x0=(rpoints[2]+rpoints[0])/2
            y0=(rpoints[3]+rpoints[1])/2
            # zoom adjust
            x0=x0/z
            y0=y0/z
            # to convert to mm
            x0=x0/10
            y0=y0/10
            print("\nFound blade alignment area centered at (%f, %f)\n" % (x0, y0))

    if x0==0.0 or y0==0.0:
        x0=15.0 # in mm
        y0=140.0 # in mm
        print("\mWARNING: Configuration symbol not found. Blade alignment area will be center at (%f, %f)\n" % (x0, y0)) 

    # Now, cut one angled line at a time
    count=0
    for cut_angle in angles:
        # Do a cut to align the blade wit the correct angle
        x1=3.0*math.cos(cut_angle*math.pi/180)+x0
        y1=3.0*math.sin(cut_angle*math.pi/180)+y0
        x2=8.0*math.cos(cut_angle*math.pi/180)+x0
        y2=8.0*math.sin(cut_angle*math.pi/180)+y0
        align_blade=[x1, y1, x2, y2]
        P.addcmd(align_blade)
        count=count+1
        
        for item in tocut:
            points=[]
            if abort_PnP==1:
                break

            if 'CUT_TAPE' in item.tag:
                # Are we cutting the internal or external perimeter?
                incut=item.label_list[7].get_value()
                if (incut=='1' or incut.lower()=='yes' or incut.lower()=='y' or incut.lower()=='on' or incut.lower()=='true'): 
                    points= canvas.coords(item.insidecut)
                else:
                    points= canvas.coords(item.tapeframe)
            elif 'PCB' in item.tag:
                points=canvas.coords(item.pcbframe)
            elif 'GAGE' in item.tag:
                points=canvas.coords(item.gageframe)

            if len(points) > 0:    
                for j in range(0, len(points)-2, 2):
                    x=points[j+2]-points[j+0]
                    y=points[j+3]-points[j+1]
                    curr_angle=round(math.atan2(y, x)*180/math.pi,0)
                    if curr_angle==-180.0:
                        curr_angle=180.0
                    if curr_angle==cut_angle:                  
                        new_points = [i/z for i in points] # zoom adjust       
                        new_points = [i/10 for i in new_points] # to convert to mm divide by 10
                        line_to_cut = [new_points[j+0]+PnP_X_Offset, new_points[j+1]+PnP_Y_Offset,
                                       new_points[j+2]+PnP_X_Offset, new_points[j+3]+PnP_Y_Offset]
                        P.addcmd(line_to_cut)
                        count=count+1
                        if count>=10:
                            P.sendcmds()
                            count=0

    if abort_PnP==1:
        print("\nFoam cut aborted by user")
        abort_PnP=0
    else:
        if count!=0:
            P.sendcmds()
            
    P.move_xy(0, 0)
    P.Use_Pen()
    P.Set_Pressure(1) # 1 to 33
    P.Set_Speed(10) # 1 to 10

    Curio_in_Use=0

def do_Abort_PnP(event=None):
    global abort_PnP
    abort_PnP=1

def do_Pause_PnP(event=None):
    global Curio_in_Use, pause_PnP
    if Curio_in_Use==1:
        if pause_PnP==1:
            print("Pause OFF")
            pause_PnP=0
        else:
            print("Pause ON")
            pause_PnP=1
    else:
        print("Pause OFF")
        pause_PnP=0

def go_PnP(event=None):
    global Curio_in_Use, abort_PnP
    if Curio_in_Use:
        return
    Curio_in_Use=1
    abort_PnP=0
    t1=Thread(target=do_PnP)
    t1.start()

def do_PnP():
    global abort_PnP, Curio_in_Use, pause_PnP
    global PnP_X_Offset, PnP_Y_Offset
    global P
    z=get_zoom()

    try:
        P.clrcmds()
    except:
        GetCurioReady()
        try:
            P.clrcmds()
        except:
            tkMessageBox.showerror("PnP ERROR", "Curio not ready")
            Curio_in_Use=0
            return

    
    try:
        P.Init_Serial_Port()
    except:
        Curio_in_Use=0
        return

    # Set default values
    ton=350
    toff=350
    servo_delay=250
    servo_max=245
    servo_min=55
    
    # Read configuration values if present
    for item in g.symbol_list: # For all the symbols in the list...
        if 'CONFIGURATION' in item.tag: # Read information from the configuration symbol
            try:
                ton=int(eval(item.label_list[5].get_value()))
                toff=int(eval(item.label_list[6].get_value()))
                servo_delay=int(eval(item.label_list[7].get_value()))
                servo_max=int(eval(item.label_list[8].get_value())*100)
                servo_min=int(eval(item.label_list[9].get_value())*100)
            except:
                pass
            break

    if P.Set_PnP_Time(ton, toff)==False:
        print("Cant proceed with pick and place")
        Curio_in_Use=0
        return

    if P.Config_Servo(servo_delay, servo_max, servo_min)==False:
        print("Cant proceed with pick and place")
        Curio_in_Use=0
        return  

    P.Use_Pen()
    P.Set_Pressure(5) # 1 to 33
    P.Set_Speed(10) # 1 to 10
    
    P.tool_down(0, 0)
    
    start = time.time()
    topnp=[]
    if selected_item:
        topnp.append(selected_item)
    elif selected_symbol_list:
        topnp=selected_symbol_list
    else:
        topnp=g.symbol_list

    # Update all the pick and place angles
    for item in g.wire_list: # For all the wires in the list...
        try:
            item.part_angle=eval(item.label_list[1].get_value())
        except:
            item.part_angle=0
        for item_tape in g.symbol_list: # For all the symbols in the list...
            if 'CUT_TAPE' in item_tape.tag:
                points= canvas.coords(item.line)
                # If source point of the pnp wire is inside the cut tape, get the tape angle
                if item_tape.pointisin(points[0], points[1])==1:
                    #print('Tape angle is: ' + str(item_tape.label_list[3].get_value()) )
                    try:
                        item.tape_angle=eval(item_tape.label_list[3].get_value())
                    except:
                        item.tape_angle=0

    # Pick and place of individual parts takes precedence over carrier cut tape or pcb pick and place
    # Therefore if there is a wire selected, do only wires:
    do_only_wires=False
    for item in g.wire_list: # For all the wires in the list...
        if item.move0==1 or item.move1==1: # if selected or 'half' selected
            do_only_wires=True
            break

    cnt=0
    if do_only_wires:
        for item in g.wire_list:
            if abort_PnP==1:
                break
            if item.move0==1 or item.move1==1: # if selected or 'half' selected
                points = canvas.coords(item.line)
                while pause_PnP==1:
                    time.sleep(1)
                if abort_PnP==1:
                    break
                #Calculate the rotation
                total_rotation=(item.part_angle-item.tape_angle+360.0)%360.0
                if total_rotation<=180:
                    servo_start=0
                    servo_end=total_rotation
                else:
                    servo_start=180
                    servo_end=total_rotation-180
                #Pick and place
                canvas.itemconfigure(item.tag2, fill = get_select_color())
                P.Set_Servo(servo_start)
                my_x=(points[0]/(10*z))+PnP_X_Offset
                my_y=(points[1]/(10*z))+PnP_Y_Offset
                #print("pick: (%f, %f)" % (my_x, my_y))
                P.Pick(my_x, my_y)
                P.Set_Servo(servo_end)
                my_x=(points[2]/(10*z))+PnP_X_Offset
                my_y=(points[3]/(10*z))+PnP_Y_Offset
                P.Place(my_x, my_y)
                canvas.itemconfigure(item.tag2, fill = get_wire_color())
                cnt=cnt+1
    else: # for PCBs and Cut Tape
        # Cut tape takes precedence over pcb
        do_only_cut_tape=False
        for item in topnp:
            if 'CUT_TAPE' in item.tag:
                do_only_cut_tape=True
                break
        
        for item in topnp:
            proceed_with_pnp=False
            if abort_PnP==1:
                break

            if 'CUT_TAPE' in item.tag:
                if do_only_cut_tape==True:
                     proceed_with_pnp=True
                     
            elif 'PCB' in item.tag:
                if do_only_cut_tape==False:
                    proceed_with_pnp=True

            if proceed_with_pnp:    
                if abort_PnP==1:
                    break
                for w_item in g.wire_list: # Check all the pick and place wires
                    if abort_PnP==1:
                        break
                    points= canvas.coords(w_item.line)
                    # If one point of the pnp wire is inside the area send to the Curio
                    if item.pointisin(points[0], points[1])==1 or item.pointisin(points[2], points[3])==1:
                        while pause_PnP==1:
                            time.sleep(1)
                        if abort_PnP==1:
                            break
                        # Calculate the rotation
                        total_rotation=(w_item.part_angle-w_item.tape_angle+360.0)%360.0
                        if total_rotation<=180:
                            servo_start=0
                            servo_end=total_rotation
                        else:
                            servo_start=180
                            servo_end=total_rotation-180
                        # print('Servo start = ' + str(servo_start) + ', Servo end = ' + str(servo_end))
                        canvas.itemconfigure(w_item.tag2, fill = get_select_color())
                        # Pick and place:
                        P.Set_Servo(servo_start)
                        my_x=(points[0]/(10*z))+PnP_X_Offset
                        my_y=(points[1]/(10*z))+PnP_Y_Offset
                        #print("pick: (%f, %f)" % (my_x, my_y))
                        if P.Pick(my_x, my_y)==False:
                            P.move_xy(0, 0)
                            P.Close_Serial_Port()
                            Curio_in_Use=0
                            print("\nSomething went wrong picking a part.\n");
                            return
                        P.Set_Servo(servo_end)
                        if P.Place((points[2]/(10*z))+PnP_X_Offset, (points[3]/(10*z))+PnP_Y_Offset)==False:
                            P.move_xy(0, 0)
                            P.Close_Serial_Port()
                            Curio_in_Use=0
                            print("\nSomething went wrong placing a part.\n");
                            return                           
                        canvas.itemconfigure(w_item.tag2, fill = get_wire_color())
                        cnt=cnt+1

    end = time.time()
    if abort_PnP==1:
        print("\nPick and Place aborted by user")
        abort_PnP=0
    P.move_xy(0, 0)
    P.Close_Serial_Port()
    print( "\n" + str(cnt) + " parts placed");
    print("Elapsed time: " + str(datetime.timedelta(seconds=int(end-start))))
    print(str( round(cnt/((end-start)/60), 2) ) + " Parts/minute\n")
    Curio_in_Use=0

def Motion(event):
    global canvas_xpos, canvas_ypos

    canvas_xpos=canvas.canvasx(event.x)
    canvas_ypos=canvas.canvasy(event.y)

def Check_Point(event):
    global P
    global canvas_xpos, canvas_ypos
    z=get_zoom()

    try:
        P.clrcmds()
    except:
        GetCurioReady()
        try:
            P.clrcmds()
        except:
            tkMessageBox.showerror("PnP ERROR", "Curio not ready")
            return

    start = time.time()
    my_x=(canvas_xpos/(10*z))+PnP_X_Offset
    my_y=(canvas_ypos/(10*z))+PnP_Y_Offset
    #print("off: (%f, %f)" % (PnP_X_Offset, PnP_Y_Offset))
    #print("check: (%f, %f)" % (my_x, my_y))
    P.move_xy( my_x, my_y)
    end = time.time()
    print("Time: " + str(round((end-start),2)) +"s")

def go_autoset_pnp(event=None):
    global canvas_xpos, canvas_ypos
    z=get_zoom()

    new_wires='' # The new wires are saved here and passed to the undo list

    autoset_pnp=[]
    if selected_item:
        autoset_pnp.append(selected_item)
    elif selected_symbol_list:
        autoset_pnp=selected_symbol_list
    else:
        autoset_pnp=g.symbol_list 
    
    for item in autoset_pnp:                    
        if 'PCB' in item.tag:
            for j in range(0, len(item.targets)):
                pcb_target_points=canvas.coords(item.targets[j])
                pcb_tx=round(pcb_target_points[0],2)
                pcb_ty=round(pcb_target_points[1],2)

                # See if there is a wire attached already
                attached_wire=False
                for itemw in g.wire_list: # For all the wires in the list...
                    x0, y0, x1, y1 = canvas.coords(itemw.line)
                    dx=pcb_tx-x1
                    dy=pcb_ty-y1
                    distance = math.sqrt( (dx**2)+(dy**2) )
                    if (distance/z)<10:  # A wire was found close to the pcb target, no need to add another one
                        attached_wire=True
                        success=True
                        break;

                if attached_wire==False:
                    # Look for a cut tape with the right name
                    success=False
                    for ct_item in g.symbol_list: # For all the symbols in the list...
                        if success:
                            break

                        if 'CUT_TAPE' in ct_item.tag:
                            # Check for cut tape match of target name and rotation
                            if ct_item.label_list[0].get_value()==item.target_name[j]:
                                target_angle=round(float(item.target_angle[j]),1)
                                # Now look for a target available in the cut tape
                                for k in range(0,len(ct_item.targets)):
                                   ct_target_points=canvas.coords(ct_item.targets[k])
                                   ct_tx=round(ct_target_points[0],2)
                                   ct_ty=round(ct_target_points[1],2)
                                   # Check if the target is available
                                   attached_wire=False
                                   for itemw in g.wire_list: # For all the wires in the list...
                                       x0, y0, x1, y1 = canvas.coords(itemw.line)
                                       dx=ct_tx-x0
                                       dy=ct_ty-y0
                                       distance = math.sqrt( (dx**2)+(dy**2) )
                                       if (distance/z)<10:  # A wire found close to the cut tape target
                                           attached_wire=True
                                           break;
                                        
                                   if attached_wire==False:
                                       success=True                                         
                                       #create a new wire
                                       newwire=wire.wire(canvas, ct_tx/z, ct_ty/z, pcb_tx/z, pcb_ty/z, '')
                                       newwire.label_list[1].set_value(target_angle) # the required part rotation
                                       g.wire_list.append(newwire)
                                       new_wires+=newwire.sym_ascii()
                                       break

                if not success:
                    print("Warning: Component \'%s\' in pcb \'%s\' is not available." %
                          (item.target_name[j], item.label_list[0].get_value()))
    if len(new_wires)>0:
        addundo('',new_wires)
    

# This one is very useful when configuring pick and place points manually
def Center_Wires_in_Part(event=None):
    global canvas_xpos, canvas_ypos
    z=get_zoom()

    old_wires='' # The old wires are saved here and passed to the undo list
    new_wires='' # The new wires are saved here and passed to the undo list
    
    center_pnp=[]
    if selected_item:
        center_pnp.append(selected_item)
    elif selected_symbol_list:
        center_pnp=selected_symbol_list
    else:
        center_pnp=g.symbol_list 

    for item in center_pnp: # For all the symbols in the list...
        if ('PCB' in item.tag) or ('CUT_TAPE' in item.tag): # Of course this only works for PCBs and Cut Tape
            cnt=1
            for target in item.targets:
                tpoints=canvas.coords(target)
                tx=round(tpoints[0],2)
                ty=round(tpoints[1],2)
                #print ("Target " + str(cnt) + " " + str((tx, ty)))
                cnt=cnt+1
                for itemw in g.wire_list: # For all the wires in the list...
                    old_wire_ascii=itemw.sym_ascii()
                    moved=False
                    x0, y0, x1, y1 = canvas.coords(itemw.line)
                    #print("points: " + str((x0, y0, x1, y1)))
                    dx=tx-x0
                    dy=ty-y0
                    distance = math.sqrt( (dx**2)+(dy**2) )
                    if (distance/z)<10:
                        #print( str(x0) + " --> " + str(tx) + ", " + str(y0) + " --> " + str(ty) )
                        x0=tx
                        y0=ty
                        itemw.canvas.coords(itemw.line, x0, y0, x1, y1)
                        itemw.canvas.move(itemw.bubble0, dx, dy)
                        itemw.canvas.move(itemw.circle0, dx, dy)
                        itemw.canvas.coords(itemw.rect, itemw.calculate_rect(x0, y0, x1, y1, False))
                        moved=True
            
                    dx=tx-x1
                    dy=ty-y1
                    distance = math.sqrt( (dx**2)+(dy**2) )
                    if (distance/z)<10:
                        #print( str(x1) + " --> " + str(tx) + ", " + str(y1) + " --> " + str(ty) )
                        x1=tx
                        y1=ty
                        itemw.canvas.coords(itemw.line, x0, y0, x1, y1)
                        itemw.canvas.move(itemw.bubble1, dx, dy)
                        itemw.canvas.move(itemw.circle1, dx, dy)
                        itemw.canvas.coords(itemw.rect, itemw.calculate_rect(x0, y0, x1, y1, False))
                        moved=True

                    if moved:
                        old_wires+=old_wire_ascii
                        new_wires+=itemw.sym_ascii()

    if len(new_wires)>0:
        addundo(old_wires, new_wires)
            
def ZeroZero_Point(event):
    global P
    try:
        P.clrcmds()
    except:
        GetCurioReady()
        try:
            P.clrcmds()
        except:
            tkMessageBox.showerror("PnP ERROR", "Curio not ready")
            return

    start = time.time()
    P.move_xy(0, 0)  
    end = time.time()
    print("Time: " + str(round((end-start),2)) +"s")

def on_mousewheel(event):
    count=0
    # respond to Linux or Windows wheel event
    if event.num == 5 or event.delta == -120:
        count -= 1
    if event.num == 4 or event.delta == 120:
        count += 1
    canvas.yview_scroll(int(-1*count), "units")       

def on_shift_mousewheel(event):
    count=0
    # respond to Linux or Windows wheel event
    if event.num == 5 or event.delta == -120:
        count -= 1
    if event.num == 4 or event.delta == 120:
        count += 1
    canvas.xview_scroll(int(-1*count), "units")

def on_control_mousewheel(event):
    if event.delta>0:
        do_zoomin(event)
    else:
        do_zoomout(event)       

def add_button(mygif, mytooltip, mycommand):
    img=PhotoImage(file=mygif)
    b = Button(toolbar, image=img, command=mycommand)
    b.img = img  # Store a reference to the image as an attribute of the widget
    b.pack(side=LEFT, padx=0, pady=0)
    ToolTip.ToolTip(b, mytooltip)

def add_separator():
    img=PhotoImage(file="Resource/sep.gif")
    b = Label(toolbar, image=img)
    b.img = img  # Store a reference to the image as an attribute of the widget
    b.pack(side=LEFT, padx=0, pady=0)

def Update_Symbol_Images():
    global wires_hidden
    global PnP_X_Offset, PnP_Y_Offset
    global prev_file_modified, file_modified
    global root

    # Refresh the title bar if needed
    if prev_file_modified!=file_modified:
        prev_file_modified=file_modified
        if file_modified:
            root.wm_title("*Curio P&P by Jesus Calvino-Fraga %s*"%(filename))
        else:
            root.wm_title("Curio P&P by Jesus Calvino-Fraga %s"%(filename))
    
    for item in g.symbol_list: # For all the symbols in the list...
        item.update_image()
        if 'CONFIGURATION' in item.tag: # Read information from the configuration symbol
            reconfigure=False
            bigmat=item.label_list[1].get_value().lower()
            if (bigmat=='1' or  bigmat=='on' or bigmat=='y' or bigmat=='yes' or bigmat=='true'):
                if g.canvas_ysize==1530: # Small tray?
                   g.canvas_ysize=1530*2 # use large tray
                   reconfigure=True
            else:
                if g.canvas_ysize!=1530: # Large tray?
                   g.canvas_ysize=1530 # use small tray
                   reconfigure=True

            if reconfigure:
                h0,h1=hbar.get()
                v0,v1=vbar.get()
                canvas.config( scrollregion=(0, 0, g.canvas_xsize*get_zoom(), g.canvas_ysize*get_zoom()) )
                hbar.set(h0,h1)
                vbar.set(v0,v1)

                g.grid_mat = [[0 for x in range(g.canvas_ysize//10)] for x in range(g.canvas_xsize//10)]
                for x in range(g.canvas_xsize//10):
                    for y in range(g.canvas_ysize//10):
                        g.grid_mat[x][y]=0
                drawgrid()

                # Need to send the PCBs back to the bottom of the canvas so the grid is displayed on top of them
                for item2 in g.symbol_list:
                    if 'PCB' in item2.tag:
                        try:
                            canvas.tag_lower(item2.canvas_image)
                        except:
                            pass

            hidwires=item.label_list[2].get_value().lower()
            if (hidwires=='1' or hidwires=='y' or hidwires=='yes' or hidwires=='on' or hidwires=='true'):
                if wires_hidden==0:
                    wires_hidden=1
                    canvas.itemconfigure('wireline', fill = '')
            else:
                if wires_hidden==1:
                    wires_hidden=0
                    canvas.itemconfigure('wireline', fill = g.get_wire_color())

            try:
                if any(c.isalpha() for c in item.label_list[3].get_value()):
                    PnP_X_Offset=0
                else:
                    PnP_X_Offset=eval(item.label_list[3].get_value())
            except:
                PnP_X_Offset=0
                
            try:
                if any(c.isalpha() for c in item.label_list[4].get_value()):
                    PnP_Y_Offset=0
                else:
                    PnP_Y_Offset=eval(item.label_list[4].get_value())
            except:
                PnP_Y_Offset=0
                       
    root.after(100, Update_Symbol_Images) # check again in 100ms
    return

def Align_Left (event=None):
    global selected_symbol_list

    if len(selected_symbol_list)<2:
        return

    old_position='' # The old positions are saved here and passed to the undo list
    new_position='' # The new positions are saved here and passed to the undo list
    
    # Find the leftmost point of the selected symbols
    left_x=1e6
    for item in selected_symbol_list:
        points=item.getbound()
        for i in range(0, len(points), 2):
            if points[i]<left_x:
                left_x=points[i]

    # Move the symbols left
    if left_x<1e6:
        for item in selected_symbol_list:
            pos_x=1e6
            points=item.getbound()
            for i in range(0, len(points), 2):
                if points[i]<pos_x:
                    pos_x=points[i]

            if len(points) > 0:
                old_position+=item.sym_ascii()
                item.move(left_x-pos_x, 0)
                new_position+=item.sym_ascii()

    if len(new_position)>0:
        addundo(old_position, new_position)        

def Align_Right (event=None):
    global selected_symbol_list

    if len(selected_symbol_list)<2:
        return

    old_position='' # The old positions are saved here and passed to the undo list
    new_position='' # The new positions are saved here and passed to the undo list
    
    # Find the rightmost point of the selected symbols
    right_x=0
    for item in selected_symbol_list:
        points=item.getbound()           
        for i in range(0, len(points), 2):
            if points[i]>right_x:
                right_x=points[i]

    # Move the symbols right
    if right_x>0:
        for item in selected_symbol_list:
            points=item.getbound()
            pos_x=0
            for i in range(0, len(points), 2):
                if points[i]>pos_x:
                    pos_x=points[i]

            if len(points) > 0:
                old_position+=item.sym_ascii()
                item.move(right_x-pos_x, 0)
                new_position+=item.sym_ascii()

    if len(new_position)>0:
        addundo(old_position, new_position)        

def Align_Bottom (event=None):
    global selected_symbol_list

    if len(selected_symbol_list)<2:
        return

    old_position='' # The old positions are saved here and passed to the undo list
    new_position='' # The new positions are saved here and passed to the undo list
    
    # Find the rightmost point of the selected symbols
    top_y=0
    for item in selected_symbol_list:
        points=item.getbound()           
        for i in range(0, len(points), 2):
            if points[i+1]>top_y:
                top_y=points[i+1]

    # Move the symbols right
    if top_y>0:
        for item in selected_symbol_list:
            points=item.getbound()
            pos_y=0
            for i in range(0, len(points), 2):
                if points[i+1]>pos_y:
                    pos_y=points[i+1]

            if len(points) > 0:
                old_position+=item.sym_ascii()
                item.move(0, top_y-pos_y)
                new_position+=item.sym_ascii()

    if len(new_position)>0:
        addundo(old_position, new_position)        

def Align_Top (event=None):
    global selected_symbol_list

    if len(selected_symbol_list)<2:
        return

    old_position='' # The old positions are saved here and passed to the undo list
    new_position='' # The new positions are saved here and passed to the undo list
    
    # Find the rightmost point of the selected symbols
    bottom_y=1e6
    for item in selected_symbol_list:
        points=item.getbound()           
        for i in range(0, len(points), 2):
            if points[i+1]<bottom_y:
                bottom_y=points[i+1]

    # Move the symbols right
    if bottom_y<1e6:
        for item in selected_symbol_list:
            points=item.getbound()
            pos_y=1e6
            for i in range(0, len(points), 2):
                if points[i+1]<pos_y:
                    pos_y=points[i+1]

            if len(points) > 0:
                old_position+=item.sym_ascii()
                item.move(0, bottom_y-pos_y)
                new_position+=item.sym_ascii()

    if len(new_position)>0:
        addundo(old_position, new_position)        

def test_circle(event=None):
    global Curio_in_Use, abort_PnP
    global PnP_X_Offset, PnP_Y_Offset
    global P
    z=get_zoom()

    try:
        P.clrcmds()
    except:
        GetCurioReady()
        try:
            P.clrcmds()
        except:
            tkMessageBox.showerror("PnP ERROR", "Curio not ready")
            return
        
    if Curio_in_Use:
        return

    Curio_in_Use=1
    
    #P.Use_Pen()
    #P.Set_Pressure(1) # 1 to 33
    #P.Set_Speed(10) # 1 to 10

    P.Use_Blade()
    P.Set_Pressure(15) # 1 to 33
    P.Set_Speed(5) # 1 to 10

    P.tool_down(100, 50)

    P.Circle(100.0, 50.0, 11.0, 0.0, 380.0) # angles in degrees

    P.move_xy(0, 0)
    P.Use_Pen()
    P.Set_Pressure(1) # 1 to 33
    P.Set_Speed(10) # 1 to 10

    Curio_in_Use=0

def rot_circle(event=None):
    global Curio_in_Use, abort_PnP
    global PnP_X_Offset, PnP_Y_Offset
    global P
    z=get_zoom()

    try:
        P.clrcmds()
    except:
        GetCurioReady()
        try:
            P.clrcmds()
        except:
            tkMessageBox.showerror("PnP ERROR", "Curio not ready")
            return
        
    if Curio_in_Use:
        return

    Curio_in_Use=1

    x = simpledialog.askstring("Rotate Circle", "Degrees")

    P.Use_Pen()
    P.Set_Pressure(33) # 1 to 33
    P.Set_Speed(1) # 1 to 10

    P.Circle(100.0, 50.0, 10.0, 0.0, float(x)) # angles in degrees

    P.move_xy(0, 0)
    P.Use_Pen()
    P.Set_Pressure(1) # 1 to 33
    P.Set_Speed(10) # 1 to 10

    Curio_in_Use=0

initglobals()
set_zoom(1.0)
initlocals()
root = Tk()
filename=''
undo_list_toremove=[]
undo_list_toadd=[]
undo_ctr=0
wiremode=False
buff_toremove=[]
        
# create a popup menu
popup = Menu(root, tearoff=0)
popup.add_command(label="--------")
popup.add_command(label="Rotate", command=do_rotate_ccw)
popup.add_command(label="Delete", command=do_delete)
popup.add_command(label="Add Symbol", command=AddSymbol)
popup.add_command(label="zoom In", command=do_zoomin)
popup.add_command(label="zoom Out", command=do_zoomout)
popup.add_command(label="Configure Item", command=do_valueset)
popup.add_command(label="Copy", command=do_copy)
popup.add_command(label="Paste", command=do_paste)
popup.add_command(label="Align >", command=do_popup2)

# create a Align popup menu
popup2 = Menu(root, tearoff=0)
popup2.add_command(label="--------")
popup2.add_command(label="Align Left", command=Align_Left)
popup2.add_command(label="Align Right", command=Align_Right)
popup2.add_command(label="Align Top", command=Align_Top)
popup2.add_command(label="Align Bottom", command=Align_Bottom)
    
# create the menubar
menubar = Menu(root)

root.protocol("WM_DELETE_WINDOW", do_quit) # Handler for the 'X' button
# create a pulldown menu and add it to the menu bar
filemenu = Menu(menubar, tearoff=1)
filemenu.add_command(label="Open", command=openfile)
filemenu.add_command(label="Save", command=do_savefile)
filemenu.add_command(label="Save as", command=savefileas)
filemenu.add_command(label="New", command=newfile)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=do_quit)
filemenu.add_separator()
filemenu.add_command(label="xyz", command=newfile)
Add_Recent_Files(filemenu, Recent_File_Callback)
menubar.add_cascade(label="File", menu=filemenu)

# create more pulldown menus
editmenu = Menu(menubar, tearoff=0)
editmenu.add_command(label="Cut <Ctrl+X>", command=do_cut)
editmenu.add_command(label="Copy <Ctrl+C>", command=do_copy)
editmenu.add_command(label="Paste <Ctrl+V>", command=do_paste)
editmenu.add_command(label="Delete <Del>", command=do_delete)
editmenu.add_separator()
editmenu.add_command(label="Undo <Ctrl+Z>", command=do_undo)
editmenu.add_command(label="Redo <Ctrl+Y>", command=do_redo)
editmenu.add_separator()
editmenu.add_command(label="Add Symbol <p>", command=AddSymbol)
editmenu.add_command(label="Add Wire <w>", command=do_wireonoff)
editmenu.add_command(label="Edit Mode <Escape>", command=do_editmode)
editmenu.add_separator()
editmenu.add_command(label="Auto Set <x>", command=go_autoset_pnp)
editmenu.add_command(label="Center Wires  <*>", command=Center_Wires_in_Part)
menubar.add_cascade(label="Edit", menu=editmenu)

# Curio jobs menu
Curiomenu = Menu(menubar, tearoff=0)
Curiomenu.add_command(label="Cut Foam (i)", command=go_draw_text)
Curiomenu.add_command(label="Draw Text (t)", command=go_draw_text)
Curiomenu.add_command(label="Pick and Place (y)", command=go_PnP)
Curiomenu.add_separator()
Curiomenu.add_command(label="Abort/Stop (q)", command=do_Abort_PnP)
Curiomenu.add_command(label="Pause Curio <space>", command=do_Pause_PnP)
menubar.add_cascade(label="Curio", menu=Curiomenu)

# Options menu
optionsmenu = Menu(menubar, tearoff=0)
optionsmenu.add_command(label="Colors", command=do_color_dialog)
menubar.add_cascade(label="Options", menu=optionsmenu)

# Help menu
helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="Help", command=Help)
helpmenu.add_command(label="About", command=About)
menubar.add_cascade(label="Help", menu=helpmenu)

# Display the menu
root.config(menu=menubar)

# Create the toolbar
toolbar = Frame(root)
# Add the buttons to the toolbar
add_button("Resource/new.gif", 'New File', newfile)
add_button("Resource/open.gif", 'Open File', openfile)
add_button("Resource/save.gif", 'Save File', do_savefile)
add_separator()
add_button("Resource/cut.gif", 'Cut', do_cut)
add_button("Resource/copy.gif", 'Copy', do_copy)
add_button("Resource/paste.gif", 'Paste', do_paste)
add_button("Resource/undo.gif", 'Undo last edit', do_undo)
add_button("Resource/redo.gif", 'Redo last edit', do_redo)
add_separator()
add_button("Resource/zoomin.gif", 'Zoom in (+)', do_zoomin)
add_button("Resource/zoomout.gif", 'Zoom out (-)', do_zoomout)
add_button("Resource/grid.gif", 'Grid on/off', do_gridonoff)
add_separator()
add_button("Resource/escape.gif", 'Edit Mode <Escape>', do_editmode)
add_button("Resource/symbol.gif", 'Add Symbol (p)', AddSymbol)
add_button("Resource/wire.gif", 'Add Wire (w)', do_wireonoff)
add_separator()
add_button("Resource/auto.gif", 'Auto set wires(x)', go_autoset_pnp)
add_button("Resource/center.gif", 'Center Wires (*)', Center_Wires_in_Part)
add_separator()
add_button("Resource/pick_and_place.gif", 'Pick and Place (y)', go_PnP)
add_button("Resource/foam_cut.gif", 'Cut Foam (i)', go_cut_foam_gig)
add_button("Resource/text_draw.gif", 'Draw Text (t)', go_draw_text)
add_separator()
add_button("Resource/stop.gif", 'Abort/Stop (q)', do_Abort_PnP)
add_button("Resource/pause.gif", 'Pause Curio <space>', do_Pause_PnP)
add_separator()
toolbar.pack(side=TOP, fill=X)

# Create the drawing canvas with its scroll bars
frame=Frame(root,width=500,height=500)
frame.pack(fill=BOTH, expand=YES)

# Check for available cursors at http://www.tcl.tk/man/tcl8.4/TkCmd/cursors.htm.
canvas = Tkinter.Canvas(frame, bg=g.bg_color, cursor="top_left_arrow", width=800 ,height=500, scrollregion=(0,0,g.canvas_xsize,g.canvas_ysize))
hbar=Scrollbar(frame,orient=HORIZONTAL)
hbar.pack(side=BOTTOM, fill=X, expand=NO)
hbar.config(command=canvas.xview)

vbar=Scrollbar(frame,orient=VERTICAL)
vbar.pack(side=RIGHT, fill=Y, expand=NO)
vbar.config(command=canvas.yview)

canvas.config(width=800,height=500)
canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
canvas.pack(fill=BOTH, expand=YES)

root.bind("w", do_wireonoff)
root.bind("p", AddSymbol)
canvas.bind("<Button-1>", B1Press)
canvas.bind("<Control-1>", B1CtrlPress)
canvas.bind("<Double-Button-1>", DoubleB1Press)
canvas.bind("<B1-Motion>", B1Motion)
canvas.bind("<Motion>", Motion)
canvas.bind("<ButtonRelease-1>", B1Release)
canvas.bind("<Button-3>", do_popup)
canvas.bind("<MouseWheel>", on_mousewheel) # Scroll vertically
canvas.bind('<Shift-MouseWheel>', on_shift_mousewheel) # Scroll horizontally
canvas.bind('<Control-MouseWheel>', on_control_mousewheel) # Zoom in/out
canvas.bind("<Button-4>", on_mousewheel) # For Linux?
canvas.bind("<Button-5>", on_mousewheel) # For Linux?
canvas.bind('<Shift-Button-4>', on_shift_mousewheel) # For Linux?
canvas.bind('<Shift-Button-5>', on_shift_mousewheel) # For Linux?
root.bind("<Control-c>", do_copy)
root.bind("<Control-v>", do_paste)
root.bind("<Control-x>", do_cut)
root.bind("<Delete>", do_delete)
root.bind("<Escape>", do_editmode)
root.bind("<Control-n>", go_newfile)
root.bind("<Control-o>", go_openfile)
root.bind("<Control-s>", do_savefile)
root.bind("<Control-z>", do_undo)
root.bind("<Control-y>", do_redo)
# These keyboard commands have menu entries and buttons
root.bind("+", do_zoomin)
root.bind("=", do_zoomin)
root.bind("-", do_zoomout)
root.bind("r", do_rotate_ccw)
root.bind("t", go_draw_text)
root.bind("i", go_cut_foam_gig)
root.bind("y", go_PnP)
root.bind("q", do_Abort_PnP)
root.bind("<space>", do_Pause_PnP)
root.bind("x", go_autoset_pnp)
root.bind("*", Center_Wires_in_Part)
root.bind("[", Align_Left)
root.bind("]", Align_Right)
root.bind("^", Align_Top)
root.bind("_", Align_Bottom)
# These ones are only available as keyboard commands
root.bind(".", Check_Point)
root.bind("<Home>", ZeroZero_Point)
root.bind("/", ZeroZero_Point)
root.bind("g", do_draw_gage)
root.bind("c", test_circle)
root.bind("d", rot_circle)
drawgrid()

Update_Symbol_Images()

root.mainloop()
    
