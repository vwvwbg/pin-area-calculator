Pin area calculator
============
A python based calculator for pin area.

Input files
------------------------
* Def file
* Width file
(width file format: celltype width)

Output format
------------------------
* Cell name
* Cell type
* Pin name & location


Cell area calculation:
------------------------
 Vertical : from : cell location - width to cell location + width
 Horizontal :from : cell location to cell location +4320

 Pin calculation:
 --------------------------------
 Only "VIA12" or "ROUTED M2" or On "M1" is pin
 If these are in cell area, they are the pin belonging that cell

 Pin area calculation:
 From left to right
 
    if y1 > y2:
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

