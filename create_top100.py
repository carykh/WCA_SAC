import datetime
import time
import math
import sys

EVENT = sys.argv[1] #333
isAverage = (EVENT[-2:] == "_a")
    
FIRST_YEAR = 2003
LAST_YEAR = 2024
LIST_N = 100
PRINT_EVERY = 200000

lists = {}
for y in range(FIRST_YEAR, LAST_YEAR+1):
    lists[y] = []

def getCompUnix(parts):
    year = parts[16]
    month = parts[17]
    day = parts[18]
    endMonth = parts[19]
    endDay = parts[20]
    
    if month == 12 and endMonth == 1:
        year += 1
    
    dateString = year+"-"+month+"-"+day
    unix = math.floor(time.mktime(datetime.datetime.strptime(dateString, "%Y-%m-%d").timetuple())/86400)
    return unix
    
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
    continent_abbr = {"_Europe":"0","_North America":"1", "_Asia":"2","_Multiple Continents":"3","_Africa":"4","_Oceania":"5","_South America":"6"}
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
    

def create_wcaid_to_country(country_to_ccode):
    result = {}
    counter = 0
    with open("data/WCA_export_Persons.tsv", encoding="utf-8") as infile:
        for line in infile:
            if counter >= 1:
                parts = line.replace("\n","").split("\t")
                wcaid = parts[4]
                country = parts[2]
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
            if event == EVENT.split("_")[0]:
                cid = parts[0]
                year = cid_to_year[cid]
                wcaid = parts[7]
                caryid = wcaid_to_country[wcaid]+"-"+wcaid
                
                if year in lists:
                    list_ = lists[year]
                    
                    if isAverage:
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

f = open(f"top100_{EVENT}.csv","w+")
for key in keys:
    f.write(f"Top {LIST_N} {EVENT} singles for {key}\n")
    list_ = lists[key]
    
    list_.sort(key=lambda x:x[1])
    for rank in range(len(list_)):
        f.write(f"{list_[rank][0]},{list_[rank][1]}\n")   
f.flush()
f.close()