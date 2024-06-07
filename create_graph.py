from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
import numpy as np
import math
from unidecode import unidecode
import sys

EVENT = sys.argv[1] #333
isAverage = (EVENT[-2:] == "_a")

START_YEAR = 2003
END_YEAR = 2024
LIST_N = 100
ADD_FLAGS = True
PATH_TO_FLAGS = "flags/"
PATH_TO_WCA_EXPORT = "data"

LEN = END_YEAR-START_YEAR+1
W_W = 6000
W_H = 2400
W_UY = 100
W_UH = 2140
CURVE_SMOOTHNESS = 50
FLAT_MARGIN = 0.16
flags = {}

def yr_to_x(yr):
    return (yr+1)/(LEN+1)*W_W
    
def n_to_y(n):
    return W_UY+W_UH*n/LIST_N

def cary_random(stri):
    phi = 1.61803
    return ((ord(stri[0])+ord(stri[1])*phi)*phi)%1.0

def caryid_to_color(caryid):
    if "EMPTY" in caryid:
        return (128,128,128)
        
    hue = cary_random(caryid[1:3])
    hp = (hue*8)%1.0
    
    if hue < 1/8:
        result = [1,hp*0.5,0]
    elif hue < 2/8:
        result = [1,0.5+hp*0.5,0]
    elif hue < 3/8:
        result = [1-hp,1,0]
    elif hue < 4/8:
        result = [0,1,hp]
    elif hue < 5/8:
        result = [0, 1-hp*0.5, 1]
    elif hue < 6/8:
        result = [0, 0.5-hp*0.5, 1]
    elif hue < 7/8:
        result = [hp,0,1]
    else:
        result = [1,0,1-hp]
        
    mins = [80,120,0]
    brightness = cary_random(caryid[8:10])
    for ch in range(3):
        m = 255-(255-mins[ch])*(0.5+0.5*brightness)
        result[ch] = int(m+result[ch]*(255-m))
        
    return tuple(result)
    
def get_flag(ccode):
    if ccode == "00":
        return None
    if ccode not in flags:
        flags[ccode] = Image.open(f"{PATH_TO_FLAGS}/{ccode}_flag.png")
    return flags[ccode]

def simplify(stri):
    if "(" in stri:
        index = stri.index("(")
        stri = stri[:index-1]
    return unidecode(stri)

def create_wcaid_to_name():
    result = {}
    result["EMPTY"] = "Empty"
    counter = 0
    with open(f"{PATH_TO_WCA_EXPORT}/WCA_export_Persons.tsv", encoding="utf-8") as infile:
        for line in infile:
            if counter >= 1:
                parts = line.replace("\n","").split("\t")
                wcaid = parts[4]
                name = simplify(parts[1])
                result[wcaid] = name
            counter += 1
    return result

wcaid_to_name = create_wcaid_to_name()
    
def getTextWidth(stri, draw, fontsize):
    font = ImageFont.truetype("Jygquip 1.ttf", fontsize)
    return draw.textlength(stri, font=font)
    
def centerText(coor, stri, draw, fontsize, color):
    font = ImageFont.truetype("Jygquip 1.ttf", fontsize)
    x, y = coor
    hw = draw.textlength(stri, font=font)
    draw.text((x-hw/2,y-fontsize*0.45+8), stri, color, font=font)
    return hw
    
def centerTextWithFlag(coor, stri, draw, fontsize, color, flag):
    if flag is None:
        centerText(coor, stri, draw, fontsize, color)
        return
    fh = int(fontsize*0.6)
    fw = int(fh/flag.height*flag.width)
    flag_margin = fontsize*0.13
    flag_resized = flag.resize((fw,fh))

    font = ImageFont.truetype("Jygquip 1.ttf", fontsize)
    x, y = coor
    x_shift = (fw+flag_margin)*0.5
    ay = y-fontsize*0.45+8
    hw = draw.textlength(stri, font=font)
    draw.text((x-hw/2+x_shift,ay), stri, color, font=font)
    img.paste(flag_resized,(int(x-hw/2-x_shift),int(ay+fh*0.44)))
    
    

def lerp(a,b,x):
    return a+(b-a)*x

def darken(color, multiplier):
    r = color[0]*multiplier
    g = color[1]*multiplier
    b = color[2]*multiplier
    return (int(r), int(g), int(b))

def coserp(a,b,x):
    return lerp(a,b,0.5-0.5*math.cos(x*math.pi))

def curvedLine(coor, pieces, draw):
    for p in range(pieces):
        x1 = lerp(coor[0][0],coor[1][0],(p+0)/pieces)
        x2 = lerp(coor[0][0],coor[1][0],(p+1)/pieces)
        
        y1 = coserp(coor[0][1],coor[1][1],(p+0)/pieces)
        y2 = coserp(coor[0][1],coor[1][1],(p+1)/pieces)
        
        draw.line([(x1,y1),(x2,y2)], fill = (0,0,0), width = 1)
        
def curvedSector(coor, color, pieces, draw):
    for p in range(pieces):
        pcoor = [None]*4
        for c in range(4):
            prog = (p+c%2)/pieces
            c1 = (c//2)*2
            x = lerp(coor[c1][0],coor[c1+1][0],prog)
            y = coserp(coor[c1][1],coor[c1+1][1],prog)
            ca = c
            if c == 2: ca = 3
            if c == 3: ca = 2
            pcoor[ca] = (x,y)

        draw.polygon(pcoor, fill=color)
        draw.line(pcoor[0:2], fill = (0,0,0), width = 1)
        draw.line(pcoor[2:4], fill = (0,0,0), width = 1)
    
        

def whereToFindHelper(list_, value, start, end, lean):
    if end < start:
        return start
    
    mid = (start+end)//2
    compareValue = list_[mid][1]
    if value < compareValue or (value == compareValue and lean):
        return whereToFindHelper(list_, value, start, mid-1, lean)
    else:
        return whereToFindHelper(list_, value, mid+1, end, lean)
    
def whereToFind(list_, value, lean):
    return whereToFindHelper(list_, value, 0, len(list_)-1, lean)

def createArrayFor(caryid, lists):
    arr = np.zeros((LEN,2),dtype=int)
    for yr in range(LEN):
        arr[yr,0] = whereToFind(lists[yr], caryid, True)
        arr[yr,1] = whereToFind(lists[yr], caryid, False)
    return arr
    
def timify(val):
    if val < 6000:
        return f"{val/100:.2f}"
    elif val < 360000:
        seconds = val%6000
        minutes = val//6000
        secondString = f"{seconds/100:.2f}".zfill(5)
        return f"{minutes}:{secondString}"
    else:
        seconds = val%6000
        minuteString = f"{(val//6000)%60}".zfill(2)
        secondString = f"{seconds/100:.2f}".zfill(5)
        hours = val//360000
        return f"{hours}:{minuteString}:{secondString}"

def getContiguous(arr):
    prevStart = 0
    limits = []
    STRETCH = 4 # How far does a continuous blob have to "break" before we show the name again?
    for yr in range(LEN+1):
        if yr == LEN or arr[yr,1]-arr[yr,0] == 0:
            if yr > prevStart:
                limits.append([prevStart,yr])
            prevStart = yr+1
        elif yr < LEN and yr >= 1 and (arr[yr,0] >= arr[yr-1,1]+STRETCH or arr[yr,1] <= arr[yr-1,0]-STRETCH):
            if yr > prevStart:
                limits.append([prevStart,yr])
                prevStart = yr

        
    return limits
    
def findNameSpot(arr, limit):
    for leng in range(5,0,-1):
        record_validity = -1
        record_yr = 0
        record_n = 0
        for yr in range(limit[0],limit[1]-leng+1):
            n_min = np.amax(arr[yr:yr+leng,0])
            n_max = np.amin(arr[yr:yr+leng,1])
            validity = n_max-n_min
            if validity >= record_validity:
                record_validity = validity
                record_yr = yr+(leng-1)/2
                record_n = (n_min+n_max-1)/2
        if record_validity >= leng:
            return [record_yr,record_n,leng]

def get_clear_spot(yr, n1, n2, namespots):
    ncenter = (n1+n2-1)/2
    bns = None  # blocking name spot
    for namespot in namespots:
        name_yr, name_n, name_size = namespot
        if abs(name_yr-yr) < name_size/2:
            bns = namespot
    if bns == None:
        return ncenter
    
    bns_yr, bns_n, bns_size = bns
    bns_top = bns_n-(bns_size-1)/2
    bns_bot = bns_n+(bns_size-1)/2+1
    gap_top = (bns_top+n1-1)/2
    gap_bot = (bns_bot+n2-1)/2
    
    if n1 >= bns_top and n2 <= bns_bot:
        return ncenter
    if n1 >= bns_top and n2 > bns_bot:
        return gap_bot
    if n1 < bns_top and n2 <= bns_bot:
        return gap_top
        
    if n1 < bns_top and n2 > bns_bot:
        top_size = bns_top-n1
        bot_size = n2-bns_bot
        if top_size >= bot_size:
            return gap_top
        else:
            return gap_bot
    return ncenter

def exists(caryid):
    return ("EMPTY" not in caryid)

def drawShapes(cubers, draw):
    for caryid in list(cubers.keys()):
        arr = cubers[caryid]
        for yr in range(LEN):
            n1 = arr[yr,0]
            n2 = arr[yr,1]
            p0 = (yr_to_x(yr-FLAT_MARGIN),n_to_y(n1))
            p1 = (yr_to_x(yr+FLAT_MARGIN),n_to_y(n1))
            q0 = (yr_to_x(yr-FLAT_MARGIN),n_to_y(n2))
            q1 = (yr_to_x(yr+FLAT_MARGIN),n_to_y(n2))
            color = caryid_to_color(caryid)
            
            if n2 > n1:
                draw.polygon([p0,p1,q1,q0], fill=color)
                draw.line([p0,p1], fill = (0,0,0), width = 1)
                draw.line([q0,q1], fill = (0,0,0), width = 1)
            
            if yr < LEN-1:
                if n2 > n1 or arr[yr+1,1] > arr[yr+1,0]:
                    p2 = (yr_to_x(yr+1-FLAT_MARGIN),n_to_y(arr[yr+1,0]))
                    q2 = (yr_to_x(yr+1-FLAT_MARGIN),n_to_y(arr[yr+1,1]))
                    curvedSector((p1,p2,q1,q2),color,CURVE_SMOOTHNESS,draw)
            

def drawLabels(cubers, draw):
    for caryid in list(cubers.keys()):
        if not exists(caryid):
            continue
        arr = cubers[caryid]
        cgs = getContiguous(arr)
        namespots = []
        for cg in cgs:
            namespots.append(findNameSpot(arr, cg))
            
        for yr in range(LEN):    
            n1 = arr[yr,0]
            n2 = arr[yr,1]
            n_count = n2-n1
            dark_color = darken(caryid_to_color(caryid), 0.5)
            max_hw = 0
            for n in range(n1,n2):
                _time = int(lists[yr][n][0])
                hw = centerText((yr_to_x(yr),n_to_y(n)), timify(_time), draw, 22, dark_color)
                max_hw = max(hw, max_hw)
                
            if n_count >= 4:
                dire = (1 if yr < LEN-1 else -1)
                counter_text = f"({n_count})"
                MARGIN = 18
                x = yr_to_x(yr)+dire*(max_hw+getTextWidth(counter_text, draw, 22)+MARGIN)/2
                y = n_to_y(get_clear_spot(yr, n1, n2, namespots))
                centerText((x,y), counter_text, draw, 22, dark_color)
                
        for namespot in namespots:
            name_yr, name_n, name_size = namespot
            nx = yr_to_x(name_yr)
            ny = n_to_y(name_n)
            if ADD_FLAGS:
                centerTextWithFlag((nx,ny), wcaid_to_name[caryid[4:]], draw, 5+20*name_size, (0,0,0), get_flag(caryid[1:3]))
            else:
                centerText((nx,ny), wcaid_to_name[caryid[4:]], draw, 5+20*name_size, (0,0,0))

def getEventName():
    f = open(f"{PATH_TO_WCA_EXPORT}/WCA_export_Events.tsv")
    lines = f.read().split("\n")
    f.close()
    for line in lines:
        parts = line.split("\t")
        if parts[0] == EVENT.split("_")[0]:
            return parts[1]

def drawTitle(cubers, draw):
    types = "averages" if isAverage else "solves"
    centerText((W_W/2,n_to_y(-3)), f"{LIST_N} best {getEventName()} WCA {types}, per year", draw, 60, (0,0,0))
                
def drawYears(cubers, draw):
    for yr in range(LEN):
        record_low = 999999999
        record_high = 0
        for n in range(LIST_N):
            value = int(lists[yr][n][0])
            if value >= 0:
                record_low = min(record_low, value)
                record_high = max(record_high, value)
            
        x = yr_to_x(yr)
        centerText((x,n_to_y(LIST_N+1.5)), str(START_YEAR+yr), draw, 70, (0,0,0))
        if record_high == record_low:
            centerText((x,n_to_y(LIST_N+4)), f"{timify(record_low)}", draw, 32, (0,0,0))
        elif record_high >= 1:
            centerText((x,n_to_y(LIST_N+4)), f"{timify(record_low)} - {timify(record_high)}", draw, 32, (0,0,0))

def loadLists():
    f = open(f"top100_{EVENT}.csv","r+")
    lines = f.read().split("\n")
    f.close()
    lists = [None]*LEN
    yr = None
    for line in lines:
        if len(line) <= 1:
            break
        elif line[:4] == "Top ":
            yr = int(line[-4:])-START_YEAR
            lists[yr] = []
        else:
            lists[yr].append(line.split(","))
            
    for yr in range(LEN):
        shortBy = LIST_N-len(lists[yr])
        for s in range(shortBy):
            name = "000-EMPTY" if s <= shortBy/2 else "900-EMPTY"
            index = 0 if s <= shortBy/2 else len(lists[yr])
            lists[yr].insert(index, ["-1",name])
    
    return lists

def loadCubers(lists):
    cubers = {}
    for yr in range(LEN):
        for n in range(LIST_N):
            caryid = lists[yr][n][1]
            if caryid not in cubers:
                cubers[caryid] = createArrayFor(caryid, lists)
                
    return cubers


lists = loadLists()
cubers = loadCubers(lists)
img = Image.new(mode="RGB", size=(W_W, W_H), color=(255,255,255))
draw = ImageDraw.Draw(img)
drawShapes(cubers, draw)
drawLabels(cubers, draw)
drawTitle(cubers, draw)    
drawYears(cubers, draw)    
img.save(f"SAC_graph_{EVENT}.png")
