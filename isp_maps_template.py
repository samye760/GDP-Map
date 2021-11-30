"""
Updated version of the original. This uses country codes to 
map data rather than country names so it is more accurate.
"""

import csv
import math
import pygal

def read_csv_as_list_dict(filename, separator, quote):
    """
    Inputs:
      filename  - name of CSV file
      separator - character that separates fields
      quote     - character used to optionally quote fields
    Output:
      Returns a list of dictionaries where each item in the list
      corresponds to a row in the CSV file.  The dictionaries in the
      list map the field names to the field values for that row.
    """
    with open(filename, "r", newline = '') as csvfile:
        reader = csv.DictReader(csvfile, delimiter = separator, quotechar = quote)
        lines = []
        for row in reader:
            lines.append(row)
            
        return lines

def read_csv_as_nested_dict(filename, keyfield, separator, quote):
    """
    Inputs:
      filename  - Name of CSV file
      keyfield  - Field to use as key for rows
      separator - Character that separates fields
      quote     - Character used to optionally quote fields

    Output:
      Returns a dictionary of dictionaries where the outer dictionary
      maps the value in the key_field to the corresponding row in the
      CSV file.  The inner dictionaries map the field names to the
      field values for that row.
    """
    with open(filename, 'r', newline = '') as csvfile:
        reader = csv.DictReader(csvfile, delimiter = separator, quotechar = quote)
        nested_countries = {}
        for country in reader:
            nested_countries[country[keyfield]] = country
            
        return nested_countries

def build_country_code_converter(codeinfo):
    """
    Inputs:
      codeinfo      - A country code information dictionary

    Output:
      A dictionary whose keys are plot country codes and values
      are world bank country codes, where the code fields in the
      code file are specified in codeinfo.
    """
    codes = read_csv_as_list_dict(
      codeinfo["codefile"], codeinfo["separator"], codeinfo["quote"])
    
    count_codes = {}
    
    for code in codes:
        count_codes[code[codeinfo["plot_codes"]]] = code[codeinfo["data_codes"]]
        
    return count_codes


def reconcile_countries_by_code(codeinfo, plot_countries, gdp_countries):
    """
    Inputs:
      codeinfo       - A country code information dictionary
      plot_countries - Dictionary whose keys are plot library country codes
                       and values are the corresponding country name
      gdp_countries  - Dictionary whose keys are country codes used in GDP data

    Output:
      A tuple containing a dictionary and a set.  The dictionary maps
      country codes from plot_countries to country codes from
      gdp_countries.  The set contains the country codes from
      plot_countries that did not have a country with a corresponding
      code in gdp_countries.

      Note that all codes should be compared in a case-insensitive
      way.  However, the returned dictionary and set should include
      the codes with the exact same case as they have in
      plot_countries and gdp_countries.
    """
    converter = build_country_code_converter(codeinfo)
    countries = {}
    not_found = set()
    print(gdp_countries.keys())
    
    for code in plot_countries:
        up_code = code.upper()
        up_conv = dict((key.upper(), value.upper()) for key, value in converter.items())
        up_dict = dict((key.upper(), value) for key, value in gdp_countries.items())
        print(up_code, up_conv, up_dict.keys())
        
        try:
            if up_conv[up_code] in up_dict:
                for data in gdp_countries:
                    if data.upper() == up_conv[up_code]:
                        countries[code] = data
            else:
                not_found.add(code)
        except KeyError:
            not_found.add(code)
            
    return countries, not_found

def build_map_dict_by_code(gdpinfo, codeinfo, plot_countries, year):
    """
    Inputs:
      gdpinfo        - A GDP information dictionary
      codeinfo       - A country code information dictionary
      plot_countries - Dictionary mapping plot library country codes to country names
      year           - String year for which to create GDP mapping

    Output:
      A tuple containing a dictionary and two sets.  The dictionary
      maps country codes from plot_countries to the log (base 10) of
      the GDP value for that country in the specified year.  The first
      set contains the country codes from plot_countries that were not
      found in the GDP data file.  The second set contains the country
      codes from plot_countries that were found in the GDP data file, but
      have no GDP data for the specified year.
    """
    gdp_countries = read_csv_as_nested_dict(
      gdpinfo["gdpfile"], gdpinfo["country_code"], gdpinfo["separator"], gdpinfo["quote"])
    
    valid_countries = reconcile_countries_by_code(codeinfo, plot_countries, gdp_countries)
    plot_codes = valid_countries[0]
    gdp_values = {}
    no_gdp = set()
    print(plot_codes, gdp_countries.keys())
    
    for plot, data in plot_codes.items():
        print(plot, data)
        try:
            gdp_values[plot] = math.log10(float(gdp_countries[data][year]))
        except ValueError:
            no_gdp.add(plot)
    
    return gdp_values, valid_countries[1], no_gdp

def render_world_map(gdpinfo, codeinfo, plot_countries, year, map_file):
    """
    Inputs:
      gdpinfo        - A GDP information dictionary
      codeinfo       - A country code information dictionary
      plot_countries - Dictionary mapping plot library country codes to country names
      year           - String year of data
      map_file       - String that is the output map file name

    Output:
      Returns None.

    Action:
      Creates a world map plot of the GDP data in gdp_mapping and outputs
      it to a file named by svg_filename.
    """
    map_data = build_map_dict_by_code(gdpinfo, codeinfo, plot_countries, year)
    
    worldmap_chart = pygal.maps.world.World()
    worldmap_chart.add(f"Global GDP in {year}", map_data[0])
    worldmap_chart.add("Country not listed", map_data[1])
    worldmap_chart.add(f"No GDP data for {year}", map_data[2])
    
    worldmap_chart.render_in_browser()
    worldmap_chart.render_to_file(map_file)
    
def test_render_world_map():
    """
    Test the project code for several years
    """
    gdpinfo = {
        "gdpfile": "isp_gdp.csv",
        "separator": ",",
        "quote": '"',
        "min_year": 1960,
        "max_year": 2015,
        "country_name": "Country Name",
        "country_code": "Country Code"
    }

    codeinfo = {
        "codefile": "isp_country_codes.csv",
        "separator": ",",
        "quote": '"',
        "plot_codes": "ISO3166-1-Alpha-2",
        "data_codes": "ISO3166-1-Alpha-3"
    }

    # Get pygal country code map
    pygal_countries = pygal.maps.world.COUNTRIES

    # 1960
    render_world_map(gdpinfo, codeinfo, pygal_countries, "1960", "isp_gdp_world_code_1960.svg")

    # 1980
    render_world_map(gdpinfo, codeinfo, pygal_countries, "1980", "isp_gdp_world_code_1980.svg")

    # 2000
    render_world_map(gdpinfo, codeinfo, pygal_countries, "2000", "isp_gdp_world_code_2000.svg")

    # 2010
    render_world_map(gdpinfo, codeinfo, pygal_countries, "2010", "isp_gdp_world_code_2010.svg")

#test_render_world_map()