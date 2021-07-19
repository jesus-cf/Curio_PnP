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

def vectorchar(mychar, mycanvas, x, y, mycolor, mytag1, mytag2, direction, text_size):

    glyph0=[]
    glyph1=[]
    glyph2=[]
    glyph3=[]
    
    if mychar==' ':
        glyph0=[3, 1, 3, 1]

    elif mychar=='!':
        glyph0=[3, 1, 3, 7, 3, 1]
        glyph1=[3, 9, 3, 10, 3, 9]

    elif mychar=='"':
        glyph0=[2, 0, 2, 3, 2, 0]
        glyph1=[4, 0, 4, 3, 4, 0]

    elif mychar=='#':
        glyph0=[3, 0, 2, 9, 3, 0]
        glyph1=[5, 0, 4, 9, 5, 0]
        glyph2=[1, 3, 6, 3, 1, 3]
        glyph3=[1, 6, 6, 6, 1, 6]

    elif mychar=='$':
        glyph0=[1, 7, 1, 8, 2, 9, 5, 9, 6, 8, 6, 6, 5, 5, 2, 5, 1, 4, 1, 2, 2, 1, 5, 1, 6, 2, 6, 3, 6, 2]
        glyph1=[4, 0, 4, 10, 4, 0]

    elif mychar=='%':
        glyph0=[4, 1, 3, 0, 2, 0, 1, 1, 1, 2, 2, 3, 3, 3, 4, 2, 4, 1]
        glyph1=[3, 7, 4, 6, 5, 6, 6, 7, 6, 8, 5, 9, 4, 9, 3, 8, 3, 7]
        glyph2=[6, 1, 1, 8, 6, 1]

    elif mychar=='&':
        glyph0=[6, 9, 6, 8, 2, 3, 2, 1, 3, 0, 4, 0, 5, 1, 5, 2, 1, 6, 1, 8, 2, 9, 6, 6, 6, 5, 6, 6]

    elif mychar=='\'':
        glyph0=[3, 0, 3, 3, 3, 0]

    elif mychar=='(':
        glyph0=[5, 1, 4, 2, 3, 4, 3, 9, 4, 11, 5, 12, 4, 11]

    elif mychar==')':
        glyph0=[2, 1, 3, 2, 4, 4, 4, 9, 3, 11, 2, 12, 3, 11]

    elif mychar=='*':
        glyph0=[1, 3, 5, 9, 1, 3]
        glyph1=[1, 9, 5, 3, 1, 9]
        glyph2=[1, 6, 5, 6, 1, 6]

    elif mychar=='+':
        glyph0=[3, 2, 3, 8, 3, 5, 6, 5, 0, 5, 3, 5]

    elif mychar==',':
        glyph0=[3, 9, 4, 9, 3, 11, 3, 9]

    elif mychar=='-':
        glyph0=[2, 6, 5, 6, 2, 6]

    elif mychar=='.':
        glyph0=[3, 9, 4, 9, 4, 10, 3, 10, 3, 9]

    elif mychar=='/':
        glyph0=[5, 0, 2, 9, 5, 0]

    elif mychar=='0':
        glyph0=[1, 8, 1, 1, 2, 0, 5, 0, 6, 1, 6, 8, 5, 9, 2, 9, 1, 8, 6, 1, 1, 8]

    elif mychar=='1':
        glyph0=[2, 9, 6, 9, 4, 9, 4, 0, 2, 2, 4, 0]

    elif mychar=='2':
        glyph0=[1, 2, 1, 1, 2, 0, 5, 0, 6, 1, 6, 3, 1, 8, 1, 9, 6, 9, 1, 9]

    elif mychar=='3':
        glyph0=[1, 1, 2, 0, 5, 0, 6, 1, 6, 3, 5, 4, 3, 4, 5, 4, 6, 5, 6, 8, 5, 9, 2, 9, 1, 8, 1, 7, 1, 8]

    elif mychar=='4':
        glyph0=[5, 9, 5, 0, 1, 6, 1, 7, 6, 7, 5, 7]

    elif mychar=='5':
        glyph0=[6, 0, 1, 0, 1, 4, 5, 4, 6, 5, 6, 8, 5, 9, 2, 9, 1, 8, 2, 9]

    elif mychar=='6':
        glyph0=[6, 2, 6, 1, 5, 0, 3, 0, 1, 2, 1, 8, 2, 9, 5, 9, 6, 8, 6, 5, 5, 4, 1, 4]

    elif mychar=='7':
        glyph0=[1, 0, 6, 0, 6, 1, 2, 7, 2, 9, 2, 7]

    elif mychar=='8':
        glyph0=[2, 0, 5, 0, 6, 1, 6, 3, 5, 4, 2, 4, 1, 5, 1, 8, 2, 9, 5, 9, 6, 8, 6, 5, 5, 4, 2, 4, 1, 3, 1, 1, 2, 0]

    elif mychar=='9':
        glyph0=[1, 7, 1, 8, 2, 9, 4, 9, 6, 7, 6, 1, 5, 0, 2, 0, 1, 1, 1, 4, 2, 5, 6, 5]

    elif mychar==':':
        glyph0=[3, 3, 4, 3, 4, 4, 3, 4, 3, 3]
        glyph1=[3, 8, 4, 8, 4, 9, 3, 9, 3, 8]

    elif mychar==';':
        glyph0=[3, 4, 4, 4, 4, 5, 3, 5, 3, 4]
        glyph1=[3, 9, 4, 9, 3, 11, 3, 9]

    elif mychar=='<':
        glyph0=[6, 2, 1, 5, 6, 8, 1, 5]

    elif mychar=='=':
        glyph0=[1, 3, 6, 3, 1, 3]
        glyph1=[1, 6, 6, 6, 1, 6]

    elif mychar=='>':
        glyph0=[1, 2, 6, 5, 1, 8, 6, 5]

    elif mychar=='?':
        glyph0=[1, 2, 1, 1, 2, 0, 5, 0, 6, 1, 6, 4, 4, 6, 4, 7, 4, 6]
        glyph1=[4, 9, 4, 10, 4, 9]

    elif mychar=='@':
        glyph0=[5, 9, 3, 9, 1, 7, 1, 2, 3, 0, 5, 0, 6, 1, 6, 6, 3, 6, 3, 4, 4, 3, 6, 3, 4, 3]

    elif mychar=='A':
        glyph0=[0, 9, 3, 0, 5, 6, 6, 9, 5, 6, 1, 6]

    elif mychar=='B':
        glyph0=[1, 0, 5, 0, 6, 1, 6, 3, 5, 4, 6, 5, 6, 8, 5, 9, 1, 9, 1, 4, 5, 4, 1, 4, 1, 0]

    elif mychar=='C':
        glyph0=[6, 2, 6, 1, 5, 0, 3, 0, 1, 2, 1, 7, 3, 9, 5, 9, 6, 8, 6, 7, 6, 8]

    elif mychar=='D':
        glyph0=[1, 0, 4, 0, 6, 2, 6, 7, 4, 9, 1, 9, 1, 0]

    elif mychar=='E':
        glyph0=[6, 0, 1, 0, 1, 4, 5, 4, 1, 4, 1, 9, 6, 9, 5, 9]

    elif mychar=='F':
        glyph0=[6, 0, 1, 0, 1, 4, 5, 4, 1, 4, 1, 9, 1, 8]

    elif mychar=='G':
        glyph0=[6, 2, 6, 1, 5, 0, 3, 0, 1, 2, 1, 7, 3, 9, 5, 9, 6, 8, 6, 5, 4, 5, 5, 5]

    elif mychar=='H':
        glyph0=[1, 0, 1, 9, 1, 4, 6, 4, 6, 0, 6, 9, 6, 8]

    elif mychar=='I':
        glyph0=[1, 0, 5, 0, 3, 0, 3, 9, 1, 9, 5, 9, 3, 9]

    elif mychar=='J':
        glyph0=[6, 0, 6, 8, 5, 9, 2, 9, 1, 8, 2, 9]

    elif mychar=='K':
        glyph0=[1, 0, 1, 9, 1, 5, 3, 5, 6, 0, 3, 5, 6, 9, 3, 5]

    elif mychar=='L':
        glyph0=[1, 0, 1, 9, 6, 9, 1, 9]

    elif mychar=='M':
        glyph0=[0, 9, 0, 0, 3, 5, 6, 0, 6, 9, 6, 0]

    elif mychar=='N':
        glyph0=[1, 9, 1, 0, 6, 9, 6, 0, 6, 9]

    elif mychar=='O':
        glyph0=[1, 2, 3, 0, 4, 0, 6, 2, 6, 7, 4, 9, 3, 9, 1, 7, 1, 2]

    elif mychar=='P':
        glyph0=[1, 9, 1, 0, 5, 0, 6, 1, 6, 4, 5, 5, 1, 5]

    elif mychar=='Q':
        glyph0=[6, 9, 4, 7, 5, 8, 6, 7, 6, 2, 4, 0, 3, 0, 1, 2, 1, 7, 3, 9, 4, 9, 5, 8]

    elif mychar=='R':
        glyph0=[1, 9, 1, 0, 5, 0, 6, 1, 6, 3, 5, 4, 1, 4, 5, 4, 6, 9, 5, 4]

    elif mychar=='S':
        glyph0=[6, 1, 5, 0, 2, 0, 1, 1, 1, 3, 2, 4, 5, 5, 6, 6, 6, 8, 5, 9, 2, 9, 1, 8, 2, 9]

    elif mychar=='T':
        glyph0=[0, 0, 6, 0, 3, 0, 3, 9, 3, 8]

    elif mychar=='U':
        glyph0=[1, 0, 1, 8, 2, 9, 5, 9, 6, 8, 6, 0, 6, 1]

    elif mychar=='V':
        glyph0=[0, 0, 3, 9, 6, 0, 3, 9]

    elif mychar=='W':
        glyph0=[0, 0, 1, 9, 3, 3, 5, 9, 6, 0, 5, 9]

    elif mychar=='X':
        glyph0=[1, 0, 6, 9, 1, 0]
        glyph1=[1, 9, 6, 0, 1, 9]

    elif mychar=='Y':
        glyph0=[0, 0, 3, 5, 6, 0, 3, 5, 3, 9]

    elif mychar=='Z':
        glyph0=[1, 0, 6, 0, 6, 1, 1, 8, 1, 9, 6, 9, 1, 9]

    elif mychar=='[':
        glyph0=[5, 0, 3, 0, 3, 12, 5, 12, 3, 12]

    elif mychar=='\\':
        glyph0=[2, 0, 5, 9, 2, 0]

    elif mychar==']':
        glyph0=[2, 0, 4, 0, 4, 12, 2, 12, 4, 12]

    elif mychar=='^':
        glyph0=[1, 5, 4, 0, 7, 5, 4, 0]

    elif mychar=='_':
        glyph0=[0, 11, 7, 11, 0, 11]

    elif mychar=='`':
        glyph0=[2, 0, 4, 2, 2, 0]

    elif mychar=='a':
        glyph0=[1, 4, 2, 3, 5, 3, 6, 4, 6, 9, 6, 6, 2, 6, 1, 7, 1, 8, 2, 9, 4, 9, 6, 7, 6, 6]

    elif mychar=='b':
        glyph0=[1, 0, 1, 9, 1, 5, 3, 3, 5, 3, 6, 4, 6, 8, 5, 9, 3, 9, 1, 7]

    elif mychar=='c':
        glyph0=[6, 4, 5, 3, 2, 3, 1, 4, 1, 8, 2, 9, 5, 9, 6, 8, 5, 9]

    elif mychar=='d':
        glyph0=[6, 5, 4, 3, 2, 3, 1, 4, 1, 8, 2, 9, 4, 9, 5, 8, 6, 7, 6, 0, 6, 9, 6, 7]

    elif mychar=='e':
        glyph0=[6, 8, 5, 9, 2, 9, 1, 8, 1, 4, 2, 3, 5, 3, 6, 4, 6, 6, 1, 6, 2, 6]

    elif mychar=='f':
        glyph0=[6, 0, 4, 0, 3, 1, 3, 9, 3, 3, 1, 3, 5, 3, 3, 3]

    elif mychar=='g':
        glyph0=[6, 5, 4, 3, 2, 3, 1, 4, 1, 8, 4, 9, 6, 7, 6, 3, 6, 11, 5, 12, 2, 12, 1, 11, 2, 12]

    elif mychar=='h':
        glyph0=[1, 0, 1, 9, 1, 5, 3, 3, 5, 3, 6, 4, 6, 9, 6, 4]

    elif mychar=='i':
        glyph0=[2, 3, 4, 3, 4, 9, 4, 3]
        glyph1=[3, 0, 4, 0, 3, 0]

    elif mychar=='j':
        glyph0=[2, 3, 4, 3, 4, 11, 3, 12, 1, 12, 3, 12]
        glyph1=[3, 0, 4, 0, 3, 0]

    elif mychar=='k':
        glyph0=[1, 0, 1, 9, 1, 6, 2, 6, 5, 3, 2, 6, 3, 6, 6, 9, 3, 6]

    elif mychar=='l':
        glyph0=[2, 0, 4, 0, 4, 9, 4, 0]

    elif mychar=='m':
        glyph0=[0, 9, 0, 3, 3, 3, 3, 9, 3, 3, 5, 3, 6, 4, 6, 9, 6, 4]

    elif mychar=='n':
        glyph0=[6, 9, 6, 4, 5, 3, 3, 3, 1, 5, 1, 9, 1, 3]

    elif mychar=='o':
        glyph0=[1, 4, 2, 3, 5, 3, 6, 4, 6, 8, 5, 9, 2, 9, 1, 8, 1, 4]

    elif mychar=='p':
        glyph0=[1, 3, 1, 12, 1, 7, 3, 9, 5, 9, 6, 8, 6, 4, 5, 3, 3, 3,  1, 5]

    elif mychar=='q':
        glyph0=[6, 3, 6, 12, 6, 5, 4, 3, 2, 3, 1, 4, 1, 8, 2, 9, 4, 9, 6, 7]

    elif mychar=='r':
        glyph0=[1, 3, 2, 3, 2, 9, 2, 5, 4, 3, 5, 3, 6, 4, 5, 3]

    elif mychar=='s':
        glyph0=[1, 8, 2, 9, 5, 9, 6, 8, 6, 7, 5, 6, 2, 6, 1, 5, 1, 4, 2, 3, 5, 3, 6, 4, 5, 3]

    elif mychar=='t':
        glyph0=[3, 1, 3, 3, 1, 3, 5, 3, 3, 3, 3, 8, 4, 9, 6, 9, 4, 9]

    elif mychar=='u':
        glyph0=[1, 3, 1, 8, 2, 9, 4, 9, 6, 7, 6, 3, 6, 9, 6, 7]

    elif mychar=='v':
        glyph0=[0, 3, 3, 9, 6, 3, 3, 9]

    elif mychar=='w':
        glyph0=[0, 3, 1, 9, 3, 3, 5, 9, 6, 3, 5, 9]

    elif mychar=='x':
        glyph0=[1, 3, 5, 9, 3, 6, 5, 3, 1, 9, 3, 6]

    elif mychar=='y':
        glyph0=[1, 3, 4, 8, 6, 3, 4, 8, 4, 10, 2, 12, 1, 12, 2, 12]

    elif mychar=='z':
        glyph0=[1, 3, 6, 3, 1, 8, 1, 9, 6, 9, 1, 9]

    elif mychar=='{':
        glyph0=[4, 0, 3, 1, 3, 5, 2, 6, 3, 7, 3, 11, 4, 12, 3, 11]

    elif mychar=='|':
        glyph0=[3, 0, 3, 12, 3, 0]

    elif mychar=='}':
        glyph0=[3, 0, 4, 1, 4, 5, 5, 6, 4, 7, 4, 11, 3, 12, 4, 11]

    elif mychar=='~':
        glyph0=[1, 5, 2, 4, 3, 4, 4, 5, 5, 5, 6, 4, 5, 5]

    else: # a question mark for unknown characters...
        glyph0=[1, 2, 1, 1, 2, 0, 5, 0, 6, 1, 6, 4, 4, 6, 4, 7, 4, 6]
        glyph1=[4, 9, 4, 10, 4, 9]

    #print("\nBefore:\n", glyph0) 

    glyph0 = [i*text_size for i in glyph0]
    glyph1 = [i*text_size for i in glyph1]
    glyph2 = [i*text_size for i in glyph2]
    glyph3 = [i*text_size for i in glyph3]

    #print("\nAfter:\n", glyph0) 

    drawglyph (glyph0, mycanvas, x, y, mycolor, mytag1, mytag2, direction)
    drawglyph (glyph1, mycanvas, x, y, mycolor, mytag1, mytag2, direction)
    drawglyph (glyph2, mycanvas, x, y, mycolor, mytag1, mytag2, direction)
    drawglyph (glyph3, mycanvas, x, y, mycolor, mytag1, mytag2, direction)


def drawglyph (myglyph, mycanvas, x, y, mycolor, mytag1, mytag2, direction):
    if len(myglyph)>0:
        #direction==0 no rotation
        if direction==1:
            index=0
            while index < len(myglyph):
                xx=myglyph[index]
                yy=myglyph[index+1]
                myglyph[index]=yy
                myglyph[index+1]=-xx
                index+=2
        elif direction==2:
            index=0
            while index < len(myglyph):
                xx=myglyph[index]
                yy=myglyph[index+1]
                myglyph[index]=-xx
                myglyph[index+1]=-yy
                index+=2
        elif direction==3:
            index=0
            while index < len(myglyph):
                xx=myglyph[index]
                yy=myglyph[index+1]
                myglyph[index]=-yy
                myglyph[index+1]=xx
                index+=2
            
        myline=mycanvas.create_line(myglyph, fill=mycolor, tags=[mytag1, mytag2, "text"])
        mycanvas.move(myline, x, y)
    

def vectorstr(mystr, mycanvas, x, y, mycolor, mytag1, mytag2, direction, text_size=4):
    myx=x
    myy=y
    for c in mystr:
        vectorchar(c, mycanvas, myx, myy, mycolor, mytag1, mytag2, direction, text_size)
        if direction==0:
           myx+=(text_size-1)*10
        elif direction==1:
           myy-=(text_size-1)*10
        elif direction==2:
           myx-=(text_size-1)*10
        elif direction==3:
           myy+=(text_size-1)*10
