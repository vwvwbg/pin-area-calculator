import time
import re

c_list = {}
c_width = {}
net_list = []
chip_pin_area = 0
class Components():
    def __init__(self,name,type,x,y):
        self.name = name
        self.type = type
        self.x = int(x)
        self.y = int(y)
        #dict with pin number
        self.pin = []
        self.pin_total_area = 0
    def add_width(self,width):
        self.width = int(width)
    def add_area(self):
        #ll means left lower corner ,ru means right upper corner
        self.ll = [self.x , self.y]
        self.ru = [self.x+self.width , self.y+4320]
    def add_pin(self,pin_name,x,y):
        if self.ru[0]>=x>= self.ll[0] and self.ru[1]>=y>= self.ll[1]:
            self.pin.append([pin_name,x,y])
    def pin_area_cal(self):
        x1 = 0
        x2 = 0
        y1 = 0
        y2 = 0
        if len(self.pin) <=1:
            return 0
        for i in range(len(self.pin)-1):
            x1 = self.pin[i][1]
            x2 = self.pin[i+1][1]
            y1 = self.pin[i][2]
            y2 = self.pin[i+1][2]
            if (x1 == x2) or (y1 == y2):
                pin_area = 0
            elif y1 > y2:
                x1 = x1 - 144
                y1 = y1 + 144
                x2 = x2 + 144
                y2 = y2 - 144
                pin_area = (x2-x1) * (y1-y2)
            elif y1 < y2:
                x1 = x1 - 144
                y1 = y1 - 144
                x2 = x2 + 144
                y2 = y2 + 144
                pin_area = (x2-x1) * (y2-y1)
            self.pin_total_area += pin_area
        return int(self.pin_total_area)

                


        
print("Def file :")
def_file = input()


with open(def_file, "r") as f:
    components_list = f.readlines()


print("Width information file :")
width_file = input()


with open(width_file, "r") as f:
    width_list = f.readlines()

print("Save as :")
out_file = input()

print("Reading input file...")

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

        c_list[ rl[1] ] = ( Components(rl[1],rl[2],x,y) )
        try:
            c_list[rl[1]].add_width( c_width[ c_list[rl[1]].type ] )
            c_list[rl[1]].add_area()
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

print("Checking pins locations...")
x=0
rm = 0
net_list_length = len(net_list)
#read mode flag 0 = skip (;), 1 = read pin(-) ,2 = read coordinate(++)
for line in net_list:
    x+=1
    print('\rpercent: {:.2%}'.format(x/net_list_length), end="")
    rl = line.split()
    if rl[0] == '-':
        nets_cell = []
        cood = []
        rm = 1
    elif rl[0] == '+':
        rm = 2
    elif rl[0] == ';':
        
        for nc in nets_cell:            
            for co in cood:

                try:
                    c_list[nc[0]].add_pin(nc[1],int(co[0]),int(co[1]))
                except KeyError:
                    print("ERROR!! Cell Not Found")
                    break



        rm = 0

    if(rm == 1):
        
        xy = re.finditer (r'\(.*?\)', line)
        for item in xy:
            item= item.group().split()
            if item[1] != "PIN":
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

                

for key,value in c_list.items():
    value.pin = sorted(value.pin, key=lambda x:x[1], reverse=False)
    chip_pin_area += value.pin_area_cal()





with open(out_file,'w') as outfile:
    outfile.write("******************************\n")
    outfile.write("def file = : "+def_file+"\n")
    outfile.write("width file = : "+width_file+"\n")
    for key,value in c_list.items():
        outfile.write("******************************\n")
        outfile.write(value.name+"\n")
        outfile.write(value.type+"\n")
        outfile.write(str(value.pin)+"\n")
        outfile.write("Cell pin area = :")
        outfile.write(str(value.pin_total_area)+"\n")
        outfile.write("******************************\n")
    outfile.write("Cell with one/zero pin \n")
    for key,value in c_list.items():
        if len(value.pin) <=1:
            outfile.write("******************************\n")
            outfile.write(value.name+"\n")
            outfile.write(value.type+"\n")
            outfile.write(str(value.pin)+"\n")
            outfile.write("******************************\n")
    outfile.write("Chip total pin area = :")
    outfile.write(str(chip_pin_area)+"\n")
    outfile.write("******************************\n")

    outfile.write("EOF")

