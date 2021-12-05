import csv
import math
import matplotlib.pyplot as plt
from pylab import *
USA_SVG_SIZE = [555, 352]

def print_table(table):
    """
    Echo a nested list to the console
    """
    for row in table:
        print(row)

def read_csv_file(f):
    """
    Read a csv file into a nested list
    Input: the name of csv file
    Output: Nested list consisting of fields in the CSV file
    """
    result = []
    with open(f, newline = '') as csv_file:
        csv_obj = csv.reader(csv_file, delimiter = ",")
        for line in csv_obj:
            if line != []:
                result.append(line)
    return result

def write_csv_file(csv_table, file_name):
    """
    Input: Nested list csv_table and a string file_name
    Action: Write fields in csv_table into a csv file with the name file_name
    """
    with open(file_name, 'w', newline = '') as csv_file:
        csv_obj = csv.writer(csv_file, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
        for line in csv_table:
            csv_obj.writerow(line)

# Part 1 - function that creates a dictionary from a table

def make_dict(table, key_col):
    """
    Given a 2D table (list of lists) and a column index key_col,
    return a dictionary whose keys are entries of specified column
    and whose values are lists consisting of the remaining row entries
    Input: Nested list table and integer of key column in the table as key_col
    Output: A dictionary 
    """
    result = {}
    for line in table:
        key = line[key_col]
        #line.remove(key)
        result[key] = line
    return result

def test_make_dict():
    """
    Some tests for make_dict()
    """
    table1 = [[1, 2], [3, 4], [5, 6]]
    print(make_dict(table1, 0))
    print(make_dict(table1, 1))
    table2 = [[1, 2, 3], [2, 4, 6], [3, 6, 9]]
    print(make_dict(table2, 1))
    print(make_dict(table2, 2))
    
test_make_dict()


# Part 2 - script for merging the CSV files

CANCER_RISK_FIPS_COL = 2
CENTER_FIPS_COL = 0

def merge_csv_files(cancer_csv_file, center_csv_file, joined_csv_file):
    """
    Read two specified CSV files as tables
    Join the these tables by shared FIPS codes
    Write the resulting joined table as the specified file
    Analyze for problematic FIPS codes
    """
    result = {}
    # Read in both CSV files
    cancer_file = read_csv_file(cancer_csv_file)
    center_file = read_csv_file(center_csv_file)
    cancer_dict = make_dict(cancer_file, CANCER_RISK_FIPS_COL)
    center_dict = make_dict(center_file, CENTER_FIPS_COL)
    
    # Compute joined table, print warning about cancer-risk FIPS codes that are not in USA map
    count_missing = 0
    for code in cancer_dict.keys():     
        if code not in center_dict.keys():
            #print("Warning: FIPS code is not in USA map", cancer_dict[code])
            count_missing += 1
        else:
            temp = cancer_dict[code]
            temp2 = center_dict[code]
            temp2.remove(code)
            temp.extend(temp2)
            result[code] = temp
    print("There are ", count_missing, "data in cancer risk data that are missing in USA map data")
    # Write joined table
    with open(joined_csv_file, 'w', newline='') as joined_csv_file:
        #fieldnames = ['state', 'county', 'FIPS', 'population', 'lifetime_cancer_risk', 'county_code', 'horizontal_center', 'vertical_center']
        writer  = csv.writer(joined_csv_file)
        for key, value in result.items():
            writer.writerow(value)
    # Print warning about FIPS codes in USA map that are missing from cancer risk data
    count = 0
    for code in center_dict.keys():
        if code not in cancer_dict.keys():
            #print("Warning: FIPS code is not in cancer risk map", center_dict[code])
            count += 1
    print("There are ", count, " data in USA map that are missing from cancer risk data")

merge_csv_files("cancer_risk_trimmed_solution.csv", "US_counties_2014.csv", "cancer_risk_joined.csv")

"""
There are 136 data in cancer risk data that miss from USA map. They are mainly state wide summary data or data from Puerto Rico or Virgin Island.
USA map data don't include data from Puerto Rico and Virgin Islands. 
There are 3 data in USA map data that miss from cancer risk data. They are from 08014, State_Lines and separator. State_Lines and Separator are two
abnormal FIPS codes. 08014 is the only reasonable data in USA map but miss from cancer risk data. 
"""

def compute_county_cirle(county_population):
    return county_population/100000

def draw_cancer_risk_map(joined_csv_file_name, map_name, num_counties):
    """
    draw a scatter plot with scattered points of fixed size and color at the center of the
    num_counties counties with highest cancer risk. Ommiting the final argument should draw
    a scatter plot of all counties
    Input:
    joined_csv_file_name -- a string of joined file name
    map_name -- a string of USA map name
    num_counties -- an integer of the number of counties to show in the scatter plot
    Output:
    a scatter plot
    """
    joined_file = read_csv_file(joined_csv_file_name)
    joined_file.sort(key= lambda row: float(row[4]), reverse = True)
    if num_counties != "":
        trimmed_joined_file = joined_file[:num_counties]
    else:
        trimmed_joined_file = joined_file
    with open(map_name, 'rb') as image:
        im = plt.imread(image)
    
    # plot the image
    imshow(im) 
    
    #Get dimensions of USA map image
    (height, width) = im.shape[0:2]
    print(width, height)

    for item in trimmed_joined_file:
    # Plot red scatter point on Houston, Tx - include code that rescale coordinates for larger PNG files
        scatter(x=float(item[5])*width/USA_SVG_SIZE[0], y=float(item[6])*height/USA_SVG_SIZE[1],
                s=compute_county_cirle(float(item[3])), c = risk_map(float(item[4])))
    show()  
    
def create_riskmap(colormap, joined_csv_file_name):
    joined_file = read_csv_file(joined_csv_file_name)
    joined_file.sort(key= lambda row: float(row[4]), reverse = True)
    
    norm = matplotlib.colors.Normalize(vmax = math.log(float(joined_file[0][4]),10),
                                       vmin = math.log(float(joined_file[len(joined_file)-1][4]),10))
    scalar = matplotlib.cm.ScalarMappable(norm = norm, cmap = colormap)
    return lambda risk: scalar.to_rgba(math.log(risk, 10))

risk_map = create_riskmap(matplotlib.cm.jet, "cancer_risk_joined.csv")

draw_cancer_risk_map("cancer_risk_joined.csv", "USA_Counties_1000x634.png", 2000)
