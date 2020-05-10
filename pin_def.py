import time
import threading
import queue
import re

c_list = []
c_width = {}
net_list = []

class Components():
    def __init__(self,name,type,x,y):
        self.name = name
        self.type = type
        self.x = int(x)
        self.y = int(y)
        #dict with pin number
        self.pin = []
    def add_width(self,width):
        self.width = int(width)
    def add_area(self):
        #ll means left lower corner ,ru means right upper corner
        self.ll = [self.x , self.y]
        self.ru = [self.x+self.width , self.y+4320]
    def add_pin(self,pin_name,x,y):
        if self.ru[0]>=x>= self.ll[0] and self.ru[1]>=y>= self.ll[1]:
            self.pin.append([pin_name,x,y])

        
print("def file:")
def_file = input()
"""print("additional width information:")
wid_file = input()"""

with open(def_file, "r") as f:
    components_list = f.readlines()
with open("width.txt", "r") as f:
    width_list = f.readlines()



for line in width_list:
    wl = line.split()
    if wl[0] in c_width:
        print("ERROR!! Duplicate definition")
    c_width[wl[0]] = wl[1]


#read flag  
rf = 0
for line_num, line in enumerate(components_list):
    
    if "COMPONENTS" in line: 
        rf = rf ^ 1
        continue

    if rf == 1:
        #skip if it is TAPCELL OR FILLERCELL
        if line.find("FILLER")!=-1 or line.find("TAPCELL")!=-1:
            continue
        rl= line.split()
        #skip ;
        if rl[0] == ';':
            continue
        for index ,k in enumerate(rl):
            if k == '(' :
                x = rl[index+1]
                y = rl[index+2]

        width = 1
        c_list.append ( Components(rl[1],rl[2],x,y) )
        try:
            c_list[-1].add_width( c_width[ c_list[-1].type ] )
            c_list[-1].add_area()
        except KeyError:
            print("ERROR: No defined cell width")
s = 0
#get range of net in def
for line_num, line in enumerate(components_list):

    if "END NETS" in line: 
        s = 0
    try:
        rl = line.split()
        if rl[0] == "NETS" :
            s = 1
    except IndexError:
        pass
    if s == 1:
        net_list.append(line)

x=0
rm = 0
net_list_length = len(net_list)
#read mode flag 0 = skip (;), 1 = read pin(-) ,2 = read coordinate(++)
for line in net_list:
    x+=1
    print('percent: {:.2%}'.format(x/net_list_length))
    rl = line.split()
    if rl[0] == '-':
        nets_cell = []
        cood = []
        rm = 1
        #print(rl[1])
    elif rl[0] == '+':
        rm = 2
    elif rl[0] == ';':
        
        for nc in nets_cell:
            for cell in c_list:
                if cell.name == nc[0]:
                    for co in cood:
                        cell.add_pin(nc[1],int(co[0]),int(co[1]))



        rm = 0

    if(rm == 1):
        
        xy = re.finditer (r'\(.*?\)', line)
        for item in xy:
            item= item.group().split()
            nets_cell.append( [item[1],item[2]] )
    elif(rm == 2):
        #if on M1 or M2 with VIA12 VIA12_h or ROUTED M2
        if line.find('M1') !=-1 or line.find('ROUTED M2')!=-1 or line.find('VIA12')!=-1 or line.find('VIA12_h')!=-1:
            xy = re.finditer (r'\(.*?\)', line)
            for item in xy:
                item= item.group().split()
                if len(item)<=5:
                    if item[1] == '*':
                        item[1] = cood[-1][0]
                    elif item[2] == '*':
                        item[2] = cood[-1][1]
                    cood.append( [item[1],item[2]] )

                

            



with open("cell_info.txt",'w') as outfile:
    for i in c_list:
        
        write_list = [i.name,i.type,i.pin]
        #print(write_list)
        outfile.write(str(write_list))
        outfile.write("\n")

