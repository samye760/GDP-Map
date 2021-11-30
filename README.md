# GDP-Map

This script creates a worldmap of GDP data based off of year selected by user. The worldmap is rendered both in browser and .svg file. The map will be colored based on GDP amount, as well as status, including no data (0 GDP) or not listed in World Map data. The script accomplishes this via parsing .csv files and formatting the data into points that the pygal module can read and map.

## Use

First, the pygal module must be installed (pip3 install pygal). I have a sample .csv file that can be used to play around with, as well as a sample function to test code. Just plug and play. The .csv files used must be in similar fomat or the code may break.

# Version 2

The version 2 code utilizes a second .csv sheet that contains country codes. Since the GDP data and pygal use different country codes, the original version matched country names, but those names often did not match up (differences in spelling, spacing, etc.). Country codes are standardized so would be better, so this sheet introduces a list of all code types, finds the types that the other sheets uses, and maps them together. The results will be much better.
