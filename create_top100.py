import datetime
import time
import math
import sys

def dateString_to_unix(stri):
    unix = math.floor(time.mktime(datetime.datetime.strptime(stri, "%Y-%m-%d").timetuple())/86400)
    return unix

FIRST_YEAR = 2003
LAST_YEAR = datetime.datetime.now().year
LIST_N = 100
PRINT_EVERY = 200000
RANDOM_ORDER = True # if false, the IDs will generally be sorted with older IDs on the top, and newer IDs on the bottom. If false, it will be more random, to get a more balanced graph from top-to-bottom.


EVENT_FULL = sys.argv[1]
eventParts = EVENT_FULL.split("_")
EVENT = eventParts[0] #333
IS_AVERAGE = (len(eventParts) >= 2 and eventParts[1].upper() == "A")
REGION = "" if len(eventParts) <= 2 else eventParts[2].upper()
if EVENT == "333mbf":  # multi blind doesn't have averages
    IS_AVERAGE = False

continentOrder = "1234567" if len(sys.argv) <= 2 else sys.argv[2]
# use this parameter to re-order the order the continents show up in, top-to-bottom
# "1234567" will present the continents in their standard order, "7654321" will vertically flip them, etc.

C_COUNT = 7
co2 = [None]*C_COUNT
for i in range(C_COUNT):
    val = int(continentOrder[i])-1
    co2[val] = str(i+1)
    
continent_abbr = {"_Europe":co2[0],
"_North America":co2[1],"_Asia":co2[2],
"_Multiple Continents":co2[3],
"_Africa":co2[4],"_Oceania":co2[5],
"_South America":co2[6]}

pre_cont = {"_Europe":"ECONT",
"_North America":"NACONT","_Asia":"ASCONT",
"_Multiple Continents":"MCCONT",
"_Africa":"AFCONT","_Oceania":"OCCONT",
"_South America":"SACONT"}

continent_region_name = {}
for key in list(continent_abbr.keys()):
    continent_region_name[continent_abbr[key]] = pre_cont[key]
# takes in a number, like "1", and outputs the continent region name, like "ECONT"


lists = {}
for y in range(FIRST_YEAR, LAST_YEAR+1):
    lists[y] = []
    
def getCompYear(parts):
    year = parts[16]
    month = parts[17]
    endMonth = parts[19]
    if month == 12 and endMonth == 1:
        year += 1
    return int(year)
    
def whereToAddHelper(list_, value, start, end):
    if end < start:
        return start
    
    mid = (start+end)//2
    compareValue = list_[mid][0]
    if value == compareValue:
        return mid
    elif value < compareValue:
        return whereToAddHelper(list_, value, start, mid-1)
    else:
        return whereToAddHelper(list_, value, mid+1, end)
    
def whereToAdd(list_, value):
    return whereToAddHelper(list_, value, 0, len(list_)-1)

def create_cid_to_year():
    result = {}
    counter = 0
    with open("data/WCA_export_Competitions.tsv", encoding="utf-8") as infile:
        for line in infile:
            if counter >= 1:
                parts = line.replace("\n","").split("\t")
                year = getCompYear(parts)
                cid = parts[0]
                result[cid] = year
            
            counter += 1
    return result

def create_country_to_ccode():
    result = {}
    counter = 0
    with open("data/WCA_export_Countries.tsv", encoding="utf-8") as infile:
        for line in infile:
            if counter >= 1:
                parts = line.replace("\n","").split("\t")
                country = parts[0]
                continent = parts[1]
                ccode = parts[2]
                result[country] = continent_abbr[continent]+ccode
                
            counter += 1
    return result
    
def cary_random(stri):
    phi = 1.61803
    sum_ = 0
    for i in range(len(stri)):
        sum_ += ord(stri[i])*phi
    return sum_%1.0

def create_wcaid_to_country(country_to_ccode):
    result = {}
    counter = 0
    with open("data/WCA_export_Persons.tsv", encoding="utf-8") as infile:
        for line in infile:
            if counter >= 1:
                parts = line.replace("\n","").split("\t")
                if parts[0] == "1":  # This is the most up-to-date name and country of the person!
                    wcaid = parts[4]
                    country = parts[2]
                    
                    if RANDOM_ORDER:  #add some randomness to each WCA ID
                        salt = (int)(cary_random(wcaid)*10000)
                        result[wcaid] = country_to_ccode[country]+str(salt).zfill(4)
                    else:
                        result[wcaid] = country_to_ccode[country]
                    
            counter += 1
    return result

def addValue(value, list_, caryid):
    if value >= 1:
        index = whereToAdd(list_, value)
        
        if index < LIST_N:
            list_.insert(index, [value, caryid])
            
        while len(list_) > LIST_N:
            list_.pop()

country_to_ccode = create_country_to_ccode()
cid_to_year = create_cid_to_year()
wcaid_to_country = create_wcaid_to_country(country_to_ccode)



counter = 0
with open("data/WCA_export_Results.tsv", encoding="utf-8") as infile:
    for line in infile:
        if counter >= 1:
            parts = line.split("\t")
            event = parts[1]
            if event == EVENT:
                cid = parts[0]
                year = cid_to_year[cid]
                wcaid = parts[7]
                caryid = wcaid_to_country[wcaid]+"-"+wcaid
                
                regionAllowed = True
                if len(REGION) >= 4:  # continental region
                    regionAllowed = (continent_region_name[caryid[0]] == REGION) 
                elif len(REGION) == 2:  # national region
                    regionAllowed = (caryid[1:3] == REGION)
                    
                if year in lists and regionAllowed:
                    list_ = lists[year]
                    
                    if IS_AVERAGE:
                        addValue(int(parts[5]), list_, caryid)
                    else:
                        for v in range(5):
                            value = int(parts[9+v])
                            addValue(value, list_, caryid)
        
        
        counter += 1
        if counter%PRINT_EVERY == 0:
            print(f"Done processing {counter} lines.")
            
keys = list(lists.keys())
keys.sort()

f = open(f"top100_{EVENT_FULL}.csv","w+")
for key in keys:
    f.write(f"Top {LIST_N} {EVENT_FULL} results for {key}\n")
    list_ = lists[key]
    
    list_.sort(key=lambda x:x[1])
    for rank in range(len(list_)):
        f.write(f"{list_[rank][0]},{list_[rank][1]}\n")   
f.flush()
f.close()