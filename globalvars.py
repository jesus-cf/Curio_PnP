# globalvars.py
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

import sys

if sys.version_info[0] < 3:
    import ConfigParser
else:
    import configparser as ConfigParser

def initglobals():
    global zoom, bg_color, symbol_color, pin_color, label_color, wire_color, grid_color, select_color
    global canvas_xsize, canvas_ysize, grid_mat
    global symbol_list, label_list, pin_list, wire_list, junc_list, text_list
    global showgrid, recent_files

    bg_color='blue'
    symbol_color='green'
    pin_color='pink'
    wire_color='yellow'
    label_color='white'
    grid_color='#0000d0'
    select_color='red'
    # The small curio mat measures 21.6 cm x 15.3 cm.  The big one measures 21.6cm x 30.6cm.
    canvas_xsize=2160
    canvas_ysize=1530
    grid_size = 10
    grid_mat = [[0 for x in range(canvas_ysize//grid_size)] for x in range(canvas_xsize//grid_size)]
    symbol_list = []
    label_list = []
    pin_list = []
    wire_list = []
    junc_list = []
    text_list = []
    recent_files = []
    showgrid = True
    for x in range(canvas_xsize//grid_size):
        for y in range(canvas_ysize//grid_size):
            grid_mat[x][y]=0

    try:
        Config = ConfigParser.ConfigParser()
        Config.read("PNP_Curio.ini")
    except:
        return
    missing=0
    try:
        bg_color = Config.get("colors", "background")
    except:
        missing+=1
    try:
        symbol_color = Config.get("colors", "symbol")
    except:
        missing+=1
    try:
        pin_color = Config.get("colors", "pin")
    except:
        missing+=1
    try:
        label_color = Config.get("colors", "label")
    except:
        missing+=1
    try:
        wire_color = Config.get("colors", "wire")
    except:
        missing+=1
    try:
        grid_color = Config.get("colors", "grid")
    except:
        missing+=1
    try:
        select_color = Config.get("colors", "select")
    except:
        missing+=1

    # Read the recent files list
    j=0
    while True:
        try:
            filetag='file%d' % (j)
            one_recent_file = Config.get("recent_files", filetag)
            recent_files.append(one_recent_file)
            j+=1
        except:
            break

def Add_Recent_Files (menutag, Recent_File_Callback):
    global recent_files
    j=menutag.index("Exit")
    menutag.delete(j+1,100)
    menutag.add_separator()
    k=0
    for filen in recent_files:
        if k==0:
            menutag.add_command(label=filen, command=lambda:Recent_File_Callback(0))
        elif k==1:
            menutag.add_command(label=filen, command=lambda:Recent_File_Callback(1))
        elif k==2:
            menutag.add_command(label=filen, command=lambda:Recent_File_Callback(2))
        elif k==3:
            menutag.add_command(label=filen, command=lambda:Recent_File_Callback(3))
        elif k==4:
            menutag.add_command(label=filen, command=lambda:Recent_File_Callback(4))
        elif k==5:
            menutag.add_command(label=filen, command=lambda:Recent_File_Callback(5))
        elif k==6:
            menutag.add_command(label=filen, command=lambda:Recent_File_Callback(6))
        elif k==7:
            menutag.add_command(label=filen, command=lambda:Recent_File_Callback(7))
        elif k==8:
            menutag.add_command(label=filen, command=lambda:Recent_File_Callback(8))
        elif k==9:
            menutag.add_command(label=filen, command=lambda:Recent_File_Callback(9))
        else:
            break
        k+=1
       
def Add_Recent_File (fname, menutag, Recent_File_Callback):
    global recent_files
    if fname in recent_files:
        recent_files.remove(fname)
    recent_files.insert(0, fname)
    Add_Recent_Files(menutag, Recent_File_Callback)

def Remove_Recent_File (fname, menutag, Recent_File_Callback):
    global recent_files
    if fname in recent_files:
        recent_files.remove(fname)
    Add_Recent_Files(menutag, Recent_File_Callback)
        
def Save_Configuration():
    cfgfile = open("PNP_Curio.ini",'w')
    Config = ConfigParser.ConfigParser()

    Config.add_section('colors')
    Config.set("colors", "background", bg_color)
    Config.set("colors", "symbol", symbol_color)
    Config.set("colors", "pin", pin_color)
    Config.set("colors", "label", label_color)
    Config.set("colors", "wire", wire_color)
    Config.set("colors", "grid", grid_color)
    Config.set("colors", "select", select_color)

    Config.add_section('recent_files')
    j=0
    for filen in recent_files:
        filetag='file%d' % (j)
        Config.set("recent_files", filetag, filen)
        j+=1
        if j==10:
            break
    
    Config.write(cfgfile)
    cfgfile.close()

def set_zoom(val):
    global zoom
    zoom=val

def get_zoom():
    return zoom

def set_symbol_color(val):
    global symbol_color
    symbol_color=val

def get_symbol_color():
    return symbol_color

def set_pin_color(val):
    global pin_color
    pin_color=val

def get_pin_color():
    return pin_color

def set_wire_color(val):
    global wire_color
    pin_color=val

def get_wire_color():
    return wire_color

def set_label_color(val):
    global label_color
    label_color=val

def get_label_color():
    return label_color

def set_select_color(val):
    global select_color
    select_color=val

def get_select_color():
    return select_color

def setcolors(mycolors):
    global bg_color, symbol_color, pin_color, label_color, wire_color, grid_color, select_color
    bg_color=mycolors[0]
    symbol_color=mycolors[1]
    grid_color=mycolors[2]
    pin_color=mycolors[3]
    wire_color=mycolors[4]
    label_color=mycolors[5]
    select_color=mycolors[6]

    cfgfile = open("PNP_Curio.ini",'w')
    Config = ConfigParser.ConfigParser()

    Config.add_section('colors')
    Config.set("colors", "background", bg_color)
    Config.set("colors", "symbol", symbol_color)
    Config.set("colors", "pin", pin_color)
    Config.set("colors", "label", label_color)
    Config.set("colors", "wire", wire_color)
    Config.set("colors", "grid", grid_color)
    Config.set("colors", "select", select_color)
    Config.write(cfgfile)
    cfgfile.close()


