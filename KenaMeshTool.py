# kena mesh tool: created by kboykboy
# converts normal ue4 skeletal meshes so they can be modded into kena: bride of spirits

# import modules
import tkinter as tk
from tkinter import filedialog
import struct
import os

# add tkinter window
root = tk.Tk()
root.withdraw()

# ask open uasset
print("Select the Uasset")
Uasset = filedialog.askopenfilename(title="Select Uasset", filetypes=[("Uasset", ".uasset")])
Uexp = os.path.splitext(Uasset)[0]+'.uexp'


# it appears kena adds 64 bytes of padding just before some data which i don't even know what it is
# i am far to lazy to properly reverse engineer the .uexp to read to that location perfectly
# so i am gonna do whats called a pro gamer move and just kinda guess where it is


# open uexp for reading
with open(Uexp, 'r+b') as f:
    marker = b"\x01\x00\x02\x02\x00\x00\x00" # appears just after the area we need to update. so i am gonna use it as a marker
    ff = f.read()
    current_loc = 0
    paddingLocs = []
    while True:
        loc = ff.find(marker, current_loc) # find the stream of bytes
        if loc == -1:
            break
        else:
            paddingLocs.append(loc)        # append to list
        current_loc = loc+1

    # loop the areas we need to update
    arrayStarts = []
    data = []
    num = 0
    f.seek(0)
    for start in paddingLocs:
        start -= 4        # set the start of the padding
        loc = f.tell()    # save location
        data.append(f.read(start-loc)) # read to next padding area
        f.seek(start)
        num += 1
    endData = f.read()
    f.close()

# write new uexp
UexpNew = os.path.splitext(Uexp)[0] + 'NEW.uexp'
size = 0
with open(UexpNew, 'w+b') as f:
    for chunk in data:
        f.write(chunk)
        f.write(b"\x3C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00") # write the 64 bytes
    f.write(endData)
    f.seek(0)
    size = len(f.read())

# write new uasset
UassetNew = os.path.splitext(Uasset)[0] + 'NEW.uasset'
with open(Uasset, 'r+b') as f:
    uassetData = f.read()
with open(UassetNew, 'w+b') as f:
    f.write(uassetData)
    f.seek(73)
    f.seek(struct.unpack('<I', f.read(4))[0]-76)
    f.write(struct.pack('<I', size - 4))

