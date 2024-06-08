# Stacked Area Charts of Top WCA solves

Creates a Stacked Area Chart of the 100 best WCA results of an event, per year!

![a stacked area chart of the top 100 3x3 solves per year](SAC_graph_333.png)

## Steps for setup:
* 1. Download this repo.
* 2.  Download the most recent WCA .tsv export from here (https://www.worldcubeassociation.org/export/results), extract the .zip, and put the files in the /data folder.
* 3.  Extract the flags.zip folder. (Set the destination to YOUR_PROJECT_FOLDER/flags, so that the flag images are in the /flags folder!)
  4.  Run this command to install the required libraries (it's just numpy, unidecode, and Pillow, which you may already have):
     ```
     pip install -r requirements.txt
     ```

## Steps for creating images:
* 1. Open a command prompt from this directory.
* 2. Run this command (Takes 5-7 seconds on my computer)
   ```
   python create_graph.py 333
   ```
     This will create a simplified .csv data file, draw a 6000x2400px .png file from that data file, and open that .png.
  
* 4. Voila! The image should also appear in your folder as "SAC_graph_333.png".

## Customize the event!

You can change the event to whatever you want. In these examples, it's 333. But you can also choose from this list (taken from WCA_export_Events.tsv):
```
222, 333, 333bf, 333fm, 333ft, 333mbf, 333mbo, 333oh, 444, 444bf, 555, 555bf, 666, 777, clock, magic, minx, mmagic, pyram, skewb, sq1
```

If you want to make a chart for averages, not singles, simply append "_A" to the end of the event parameter, like so:
 ```
 python create_top100.py 333_A
 ```
## Customize the country!  (NEW as of June 7, 2024)

If you want to make a chart for just one country (like the United States), add that country's code to the end ("US") like so.
 ```
 python create_top100.py 333_A_US
 ```
The country code must always been the third chunk of the list. So if you want to find the best 5BLD singles in China ("CN"), do this:
```
 python create_top100.py 555bf_S_CN
```
To find all country codes, go into the file "WCA_export_Countries.tsv".

## Customize the continent!  (NEW as of June 7, 2024)

If you want to make a chart for just one continent (like Africa), add that continent's code to the end ("AFCONT") like so.
```
 python create_top100.py 333_A_AFCONT
```
There are 6 continents. Here are the codes you can use for them!

| Continent  | Continent code you use for this project |
| ------------- | ------------- |
| Africa  | AFCONT |
| Europe  | ECONT |
| North America  | NACONT |
| South America  | SACONT |
| Asia  | ASCONT |
| Oceania  | OCCONT |

Notice that these continent codes are just the names of continental records (AfR, ER, NAR), but with the "R" removed and "CONT" added. Also, these country codes or continent codes are NOT case-sensitive, so don't worry about that!

## Disclaimer

I wrote this code in a couple days, so the text might not show up correctly with the oddball events, like FMC or Multi-Blind.
