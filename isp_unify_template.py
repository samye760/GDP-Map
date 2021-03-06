"""
Script that creates a visual map in browser based off of world 
GDP data based on year given by user.
"""

import csv
import math
import pygal

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

def reconcile_countries_by_name(plot_countries, gdp_countries):
    """
    Inputs:
      plot_countries - Dictionary whose keys are plot library country codes
                       and values are the corresponding country name
      gdp_countries  - Dictionary whose keys are country names used in GDP data

    Output:
      A tuple containing a dictionary and a set.  The dictionary maps
      country codes from plot_countries to country names from
      gdp_countries The set contains the country codes from
      plot_countries that were not found in gdp_countries.
    """
    in_countries = {}
    out_countries = set()
    
    for code in plot_countries:
        if plot_countries[code] in gdp_countries:
            in_countries[code] = plot_countries[code]
        else:
            out_countries.add(code)
            
    return in_countries, out_countries

def build_map_dict_by_name(gdpinfo, plot_countries, year):
    """
    Inputs:
      gdpinfo        - A GDP information dictionary
      plot_countries - Dictionary whose keys are plot library country codes
                       and values are the corresponding country name
      year           - String year to create GDP mapping for

    Output:
      A tuple containing a dictionary and two sets.  The dictionary
      maps country codes from plot_countries to the log (base 10) of
      the GDP value for that country in the specified year.  The first
      set contains the country codes from plot_countries that were not
      found in the GDP data file.  The second set contains the country
      codes from plot_countries that were found in the GDP data file, but
      have no GDP data for the specified year.
    """
    countries = read_csv_as_nested_dict(
      gdpinfo["gdpfile"], gdpinfo["country_name"], gdpinfo["separator"], gdpinfo["quote"])
            
    existing_countries = reconcile_countries_by_name(plot_countries, countries)
    print(existing_countries)
    no_data = set()
    gdp = {}
    
    for code in existing_countries[0]:
        try:
            gdp[code] = math.log10(float(countries[existing_countries[0][code]][year]))
        except ValueError:
            no_data.add(code)
        
    return gdp, existing_countries[1], no_data

def render_world_map(gdpinfo, plot_countries, year, map_file):
    """
    Inputs:
      gdpinfo        - A GDP information dictionary
      plot_countries - Dictionary whose keys are plot library country codes
                       and values are the corresponding country name
      year           - String year to create GDP mapping for
      map_file       - Name of output file to create

    Output:
      Returns None.

    Action:
      Creates a world map plot of the GDP data for the given year and
      writes it to a file named by map_file.
    """
    country_data = build_map_dict_by_name(gdpinfo, plot_countries, year)
    
    worldmap_chart = pygal.maps.world.World()
    worldmap_chart.title = f"Global GDP by country for year {year}"
    worldmap_chart.add("GDP countries", country_data[0])
    worldmap_chart.add("Not listed in GDP data", country_data[1])
    worldmap_chart.add(f"No GDP in {year}", country_data[2])
    
    worldmap_chart.render_in_browser()
    worldmap_chart.render_to_file(map_file)


def test_render_world_map():
    """
    Test the project code for several years.
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

    # Get pygal country code map
    pygal_countries = pygal.maps.world.COUNTRIES

    # 1960
    render_world_map(gdpinfo, pygal_countries, "1960", "isp_gdp_world_name_1960.svg")

    # 1980
    render_world_map(gdpinfo, pygal_countries, "1980", "isp_gdp_world_name_1980.svg")

    # 2000
    render_world_map(gdpinfo, pygal_countries, "2000", "isp_gdp_world_name_2000.svg")

    # 2010
    render_world_map(gdpinfo, pygal_countries, "2010", "isp_gdp_world_name_2010.svg")

test_render_world_map()