# -*- coding: utf-8 -*-
"""
Created on Fri Jun 30 11:20:04 2023

@author: andrea graffagnino
"""

"#############################################################################"
"##                               Initialization                            ##"
"#############################################################################"

import os
from itertools import product
import fnmatch
from eppy.modeleditor import IDF
import pandas as pd
import re
import seaborn as sns
import dataframe_image as dfi
import matplotlib.pyplot as plt
import numpy as np
import cv2
import sys
import matplotlib.dates as mdates
import datetime


#Dictionary for all the combinations of passive solar systems
general_combinations = {
    'shape': ['B1', 'B2'],
    'use': ['R', 'O'],
    'location': ['BZ'],
    'system': ['DG', 'MW', 'SS', 'ST', 'TW'],
    'orient': ['S', 'E', 'W'],
    'WWR': ['0.2', '0.6'],
    'uglass': ['0.8', '2.3'],
    'thermal_storage': ['TS2', 'TS3']
    }

#Dictionary for the combination of the base cases
basic_combinations = {
    'shape': ['B1', 'B2'],
    'use': ['R', 'O'],
    'location': ['BZ'],
    'base_system': ['Base'],
    'base_orient': ['S'],
    'Base_WWR': ['0.12'],
    'base_uglass': ['5.9'],    
    'base_thermal_storage': ['TS1'],
    }

# Define the base case identifiers for the function verify idf
base_cases = {
    'R_L1':'B2_R_L1_Base_S_0.12_5.9_TS1',
    'R_L2':'B2_R_L2_Base_S_0.12_5.9_TS1',
    'O_L1':'B2_O_L1_Base_S_0.12_5.9_TS1',
    'O_L2':'B2_O_L2_Base_S_0.12_5.9_TS1',
    }
 
dict_orient = {
    "_S_": 180,
    "_E_": 90,
    "_W_": 270}

dict_glass = {
    "_0.8_": "3xGLASS_U0.8_AIR",
    "_1.0_": "3xGLASS_U1.0_AIR",
    "_2.3_": "2xGLASS_U2.3_KRYPTON",
    "_5.9_": "Exterior Window",   
    }
dict_glass_pure = {
    "_0.8_": "3xGLASS_U0.8_AIR",
    "_1.0_": "3xGLASS_U1.0_AIR",
    "_2.3_": "2xGLASS_U2.3_KRYPTON" 
    }

dict_storage = {
    "_TS1": "Wall",  
    "_TS2": ["TS2","TS_2"],
    "_TS3": ["TS3","TS_3"]
    }

dict_use = {
    "_O_": "OFFICE",  
    "_R_": "RES"
    }
 
parameters = {'Use': [],
        'Orient': [],
        'Glass': [],
        'Storage': []}

enplus_vers = {
    "version_thesis": "(v8.5)",
    "version87": "(v8.7)",
    "version_new": "(v22.2)"
}

# Folders
folder_main = os.getcwd()
folder_models = folder_main + "\enplus_models"
folder_weather = folder_main + "\weather_files"
folder_csv = folder_main + "\csv_outputs"
folder_images = folder_main + "\images"

folder_models85_thesis = os.path.join(folder_models, "Models_8.5_Originals")
folder_models85_fixed = os.path.join(folder_models, "Models_8.5_fixed")
folder_models87 = os.path.join(folder_models, "Models_8.7_fixed")
folder_models222 = os.path.join(folder_models, "Models_22.2")


folder_ep222 = r"C:\EnergyPlusV22-2-0"



"#############################################################################"
"##                                 Functions                               ##"
"#############################################################################"

###############################################################################
###                              file managment                             ###
###############################################################################

def delete_files_with_string(root_folder, search_string):
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if search_string in file:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Deleted file: {file_path}")

# Specify the root folder to start the search from
# root_folder = r'C:\Users\andre\Desktop\Thesis_Python\enplus_models\Models_8.7_fixed\RES'
# search_string = 'eplus'

def delete_non_idf_files(folder):
    for current_folder, subfolders, files in os.walk(folder):
        for file_name in files:
            if not file_name.endswith(".idf"):
                full_path = os.path.join(current_folder, file_name)
                os.remove(full_path)


def rename_folders(root, inp, out):

    # Iterate over each subfolder and rename the folders
    for root, dirs, files in os.walk(root):
        
        for folder in dirs:
            
            # Split folder name using underscores as the delimiter
            folder_parts = folder.split('_')
            
            for i, part in enumerate(folder_parts):
                # Check if "BZ" is one of the parts in the folder name
                if part == f"{inp}":
                    # Change the part name with "PA"
                    folder_parts[i] = f"{out}"
            
            # Create the new folder name by joining the parts back with underscores
            new_folder_name = "_".join(folder_parts)
            
            # Rename the folder
            old_path = os.path.join(root, folder)
            new_path = os.path.join(root, new_folder_name)
            os.rename(old_path, new_path)
            print(f"Renamed '{folder}' to '{new_folder_name}'")
            
def rename_idf_files(current_dir):

    # Iterate over each subfolder and rename .idf files
    for root, dirs, files in os.walk(current_dir):
        for file in files:
            if file.endswith(".idf"):
                # Get the parent folder name
                parent_folder = os.path.basename(root)

                # Construct the new file name
                new_name = os.path.join(root, parent_folder + ".idf")

                # Check if the new name already exists
                if not os.path.exists(new_name):
                    # Rename the file
                    os.rename(os.path.join(root, file), new_name)

def search_extensions(current_dir, extension_file, create_list=None):
    """
  Return a list of retrieved file paths based on the specified extension like .html or .csv.
  If create_list is True, it creates a .txt file of the list.

  Returns
  -------
  list
      A list of retrieved file paths.
  """
    #Initialize a list of valid extensions
    valid_extensions = ['.html', '.csv', '.idf', '.eso', '.htm']

   
    #this is a while loop to ensure it matches one of the valid extensions
    while extension_file not in valid_extensions:
        print("Invalid extension file")
        extension_file = input("Please enter a valid file extension: ")

    files_found = [] # list to store the retrieved files

    # use .walk funtion in the os library (remember it returns three values) for scan the folders
    for root, dirs, files in os.walk(current_dir):
        
        #use fnmatch to filter the lists of files in each directory
        for filename in fnmatch.filter(files, f'*{extension_file}'):
            
            #construct the full path using .join
            file_path = os.path.join(root, filename)
            
            #Append object to the end of the list
            files_found.append(file_path)
    
    # #print all the file found each in a new line with a for loop
    # for file_path in files_found:
    #     print(file_path)
        
    #print the total number of files found   
    count_files = len(files_found) 
    print(f"-->Total files{extension_file} found: {count_files}")
    
    if create_list:
        file_path = os.path.join(current_dir, f"{extension_file}.txt")
        with open(file_path, 'w') as file:
            for item in files_found:
                file.write(item + "\n")
        print(f"output .txt file saved in {current_dir}")


    return files_found

def ID_folder_generator (base_dir, general_combinations, basic_combinations):
    """
    Generate directories based on combinations of values from general_combinations and basic_combinations.

    Parameters
    ----------
    base_dir : str
        Base directory where new directories will be created.

    Returns
    -------
    None.
    """
    # Check if the base directory is empty
    if not base_dir:
        print("Please provide a valid base directory.")
        return
    
    ### first part: all the combinations
    
    # Define the base directory where I want to create new directories
    #base_dir = "./testIDcode"

    count = 0
    
    #generate all the combinations
    combinations = product(*general_combinations.values())

    for combo in combinations:
        dir_name = '_'.join(combo)
        dir_path = os.path.join(base_dir, dir_name)
        os.makedirs(dir_path, exist_ok=True)
        count += 1
        print(f"Created directory: {dir_path}")
        
    print(f"Total directories created: {count}")
    
    ### second part for the base directories
    
    combinations_base = product(*basic_combinations.values())
    
    for combo2 in combinations_base:
        dir_name = '_'.join(combo2)
        dir_path = os.path.join(base_dir, dir_name)
        os.makedirs(dir_path, exist_ok=True)
        count += 1
        print(f"Created directory: {dir_path}")
        
    print(count)


###############################################################################
###                              idf manipulation                           ###
###############################################################################

def replace_construction_part(file_path):
    # Get the name of the file
    file_name = os.path.basename(file_path)
    # Read the file and store its lines in a list
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Define the part to search for and its replacement
    target_part = "U-0.8_G0.7" 
    replacement_part = "3xGLASS_U0.8_AIR"
    found_at_least_once = False

    # Iterate through the lines and replace the target part if found
    for index, line in enumerate(lines):
        if target_part in line:
            # Check if 3 lines above contain "FenestrationSurface:Detailed,"
            if index >= 3 and "FenestrationSurface:Detailed," in lines[index - 3]:
                # Replace the target part with the replacement part
                lines[index] = line.replace(target_part, replacement_part)
                found_at_least_once = True

    # Write the modified lines back to the file if any replacements were made
    if found_at_least_once:
        with open(file_path, 'w') as file:
            file.writelines(lines)
        print(f"Substitution successful in {file_name}.")
    else:
        print(f"Target part not found in the file {file_name}.")  
   
        
def replace_piece_of_text(file_path, replacement_lines, start_line, end_line):
    # Read the contents of the file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    start_index = None
    end_index = None

    # Find the indices of the start and end lines
    for i, line in enumerate(lines):
        if start_line in line:
            start_index = i + 1
        elif end_line in line:
            end_index = i

    # Check if start and end lines were found
    if start_index is None or end_index is None:
        print("Start or end line not found in the file.")
        return

    # Replace lines in the specified range with the replacement_lines
    lines[start_index:end_index] = replacement_lines

    # Write the updated content back to the file
    with open(file_path, 'w') as file:
        file.writelines(lines)


# # Example usage:
# testo = r"R:\Week1\Thesis_Python-main\#enplus_models\Models_8.5_fixed\replacement.txt"
# with open(testo, 'r') as file:
#     replacement_lines = file.readlines()
    
# start_line = '!-   ===========  ALL OBJECTS IN CLASS: MATERIAL ===========\n'
# end_line = '!-   ===========  ALL OBJECTS IN CLASS: GLOBALGEOMETRYRULES ===========\n'

# base_folder = r"R:\Week1\Thesis_Python-main\#enplus_models\Models_8.5_fixed"
# list_IDFs_found = search_extensions(base_folder, extension_file = '.idf')
# for file_path in list_IDFs_found:
#     replace_piece_of_text(file_path, replacement_lines, start_line, end_line)   

def check_line(file_path, line_name):
    '''
    Check if exixsts a line under anoter specified line
    '''
    # Get the name of the file
    file_name = os.path.basename(file_path)
    # Read the file and store its lines in a list
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
    found_at_least_once = False

    # Iterate through the lines
    for index, line in enumerate(lines):
        if line_name in line:
            # Check if 3 lines above contain "FenestrationSurface:Detailed,"
            if index >= 1 and "Version," in lines[index - 1]:
                print(f"found construction at line {index}")
                found_at_least_once = True

    if found_at_least_once:
        print(f"Found in {file_name}.")
        return 1
    else:
        print(f"Not found in the file {file_name}.") 
        return 0
 
    
def split_idf_objects(file_path):
    
    idf_dict = {}
    splitter_string = "!-   ===========  ALL OBJECTS IN CLASS:"
    
    with open(file_path, 'r') as idf:
        data = idf.read()
        sections = data.split(splitter_string)
        
        for i, section in enumerate(sections[1:], start=1):
            lines = section.strip().split('\n')
            obj_name = lines[0].strip('= ')
            obj_contents = lines[1:]  # Store contents as a list
            idf_dict[obj_name] = obj_contents
            
    return idf_dict


def verifyIDF(file_path, version):
    '''
    Check if the parameters in the file and in the file's name correspond.
    Return 1 if the selected parameter is found else 0. Use this function to 
    create a list of unmatched files.
    '''
    version = version.replace("(","").replace("v","").replace(")","")
    # Get the name of the file
    file_name = os.path.basename(file_path)
    # Markers
    version_marker = "Version"
    orient_marker = "!- North Axis {deg}" 
    glass_marker = "!- Construction Name"
    storage_marker = "!- Construction Name"
    use_marker = "Schedule Name"
    # Initialize the values of the keys
    orient = None
    glass = None
    storage = None
    use= None
    
    print(f"    Reading {file_name}")
    
    ' Verify names'
    
    # Verify use
    for key in dict_use:
        if key in file_name:
            use = dict_use[key]
            print(f"Use of the file name: {use} -> {key}")
            break  # Exit the loop if a match is found
    else:
        print("Use not found in the file name")
    
    # Verify orientation
    for key in dict_orient:
        if key in file_name:
            orient = dict_orient[key]
            print(f"Orientation of the file name: {orient} -> {key}")
            break  # Exit the loop if a match is found
    else:
        print(f"Orientation not found in the {file_path}")
        
    # Verify glass
    for key in dict_glass:
        if key in file_name:
            glass = dict_glass[key]
            # Get the values of the other keys
            anti_glass = {key: value for key, value in dict_glass_pure.items() if dict_glass_pure[key] != glass}
            print(f"Glass of the file name: {glass} -> {key}")
            break  # Exit the loop if a match is found
    else:
        print(f"Glass not found in the {file_path}") 
   
    # Verify thermal storage
    for key in dict_storage:
        if key in file_name:
            storage = dict_storage[key] #return a list
            print(f"Thermal storage of the file name: {storage} -> {key}")
            break  # Exit the loop if a match is found
    else:
        print(f"TS not found in the {file_path}") 
        
        
    ' Verify files' 
    
    idf_dict = split_idf_objects(file_path)
    
    # # Read the file and store its lines in a list
    # with open(file_path, 'r') as file:
    #     lines = file.readlines()
   
    match = [0,0,0,0,0]
    
    # Verify the usage. to do this you must  verify multiple objects in the idf
    keys_to_access = ["PEOPLE", "LIGHTS", "ELECTRICEQUIPMENT", "HVACTEMPLATE:THERMOSTAT"]
    # Initialize an empty list to store the values
    use_lists = []
    # Access the values from the dictionary
    for key in keys_to_access:
        if key in idf_dict:
            use_lists.append(idf_dict[key])
        else:
            # Handle the case when a key is not found in the dictionary
            use_lists.append(None)            
    # Initialize a list to track matches
    match_use = []        
    for obj in use_lists:
        for line in obj:
            if use_marker in line and str(use) in line:
                match_use.append(True)
                break
            elif use_marker in line and not str(use) in line:
                match_use.append(False)
    # Check if all elements in match_use are True
    if all(match_use):
        match[0] = 1
        
    # Get the lines for the "VERSION" object
    version_lines = idf_dict["VERSION"]
    # Iterate through the lines in the "VERSION" object
    for line in version_lines:
        if version_marker in line and version in line:
            match[1] = 1
            
    building_lines = idf_dict["BUILDING"]
    for line in building_lines:
        if orient_marker in line and str(orient) in line:
            match[2] = 1
            
    glass_found = None
    anti_glass_found = None 
    glass_lines = idf_dict["FENESTRATIONSURFACE:DETAILED"]
    for line in glass_lines:
        if glass_marker in line and glass in line:
            glass_found = True
        # Check if one by one if there's a value of the anti_glass dict in the line
        if glass_marker in line and any(value in line for value in anti_glass.values()):
            anti_glass_found = True
        if glass_found and not anti_glass_found:
            match[3] = 1
            
    thermal_lines = idf_dict["BUILDINGSURFACE:DETAILED"]
    # Add an exception for the thermal cap 2 and 3
    for line in thermal_lines:
        if storage == ["TS3","TS_3"] or storage == ["TS2","TS_2"]:
            for element in storage:        
                if storage_marker in line and element in line:
                    match[4] = 1
        else:
            if storage_marker in line and str(storage) in line:
                match[4] = 1
       
    return match


def add_output(path_idf, reference_string, output_line):
    
    #open the file specified by path_idf in read and write mode "r+" 
    with open(path_idf, "r+") as esofile:
        #reads all the lines from the file and stores them in the 'lines' list
        lines = esofile.readlines()
        
        count = 0
        
        #use enumerate to get both the line index (i) and the line content (line)
        for i, line in enumerate(lines):
            
            #check if the reference_string is present in the current line
            if re.search(reference_string, line, re.IGNORECASE):
                

                # Check if the output line already exists
                if output_line not in lines[i +2]:
                    #then add the output line
                    lines.insert(i + 1, '\n')
                    lines.insert(i + 2, output_line)
                    count += 1
                else:
                    print(f"The output in {esofile} already exists!")
                                       
        #moves the file pointer to the beginning
        esofile.seek(0)
        #write the modified lines back to the file using the writelines
        esofile.writelines(lines)
            
    return path_idf, count


def run_idf(idf_file, iddfile, epwfile):
    try:
        IDF.setiddname(iddfile)

        # Get the directory path of the IDF file
        idf_dir = os.path.dirname(idf_file)

        # Change the current working directory to the IDF file's directory
        os.chdir(idf_dir)

        # Run the IDF file and save results in the current folder
        idf = IDF(idf_file, epwfile)
        idf.run()

    except Exception as e:
        # Handle any exceptions that might occur during the execution
        print("An error occurred while running the IDF:")
        print(e)
        

def retrieve_kpi(eso_path, key_string):
    
    # Read the eso file as a df. Engine c should be faster. Skip lines too long
    df = pd.read_csv(eso_path,header=None, engine='c', on_bad_lines='skip')
    # Find the numbers of my key_string
    all_keys = df.loc[df[3] == (key_string)][0]
    
    # Find the boundaries of values
    end_of_dictionary = df.loc[df[0] == ('End of Data Dictionary')].index[0]+1
    end_of_data = df.loc[df[0] == ('End of Data')].index[0]
    
    # trim the data: take all values between the two rows
    df_new = df.iloc[end_of_dictionary:end_of_data]
    # Take only the rows with the key numbers
    df_trimmed = df_new.loc[df[0].astype(str).isin(all_keys.astype(str))][1].astype(float)
    #print(df_trimmed)
    # Make the sum and return a float number   
    sum_df = df_trimmed.sum() / 1000
    print(sum_df)
    
    return sum_df #is a float64


def df_kpi_in_esofile(eso_path, key_number, iskW=None):
    
    # Read the eso file as a df. Engine c should be faster. Skip lines too long
    df = pd.read_csv(eso_path,header=None, engine='c', on_bad_lines='skip')
    # Convert the number to a pd series
    key_number = pd.Series(key_number)
    
    # Find the boundaries of values
    end_of_dictionary = df.loc[df[0] == ('End of Data Dictionary')].index[0]+1
    end_of_data = df.loc[df[0] == ('End of Data')].index[0]
    
    # trim the data: take all values between the two rows
    df_new = df.iloc[end_of_dictionary:end_of_data]
    # Take only the rows with the key numbers
    df_trimmed = df_new.loc[df[0].astype(str).isin(key_number.astype(str))][1].astype(float)
    # Convert the series to a df
    df_trimmed = df_trimmed.to_frame()
    # Reset the index
    df_trimmed = df_trimmed.reset_index(drop=True)
    # Rename the first column to "ciao"
    df_trimmed.rename(columns={df_trimmed.columns[0]: 'Value'}, inplace=True)
    #print(df_trimmed)
    if iskW:
        # Divide by 1000 to obtain kW   
        df_trimmed = df_trimmed / 1000
        
    # Define the start date and time
    start_date = pd.to_datetime('2009-01-01 00:00:00')
    df_trimmed['Date'] = pd.date_range(start=start_date, periods=len(df_trimmed), freq='H')
    return df_trimmed #is a df

###############################################################################
###                            graphics and outputs                         ###
###############################################################################

  
def retrieve_districtCH_html(path_html):
    '''
    Get the float value for district cooling and heating in the html table
    '''
    
    html = pd.read_html(path_html)
    # Get the folder containing the specified file
    folder_name = os.path.dirname(path_html)
    # Get the name of the last directory
    name = os.path.basename(folder_name) 
    
    # COLLECT KPI
    # Open the table with district heating and coolig
    district_table = html[3]
    # Set the first row as column names
    district_table.columns = district_table.iloc[0]
    # Set the first column as the index
    district_table = district_table.set_index(district_table.columns[0])
    # Drop the first row, which is now redundant
    district_table = district_table.iloc[1:]
    
    value_AC = district_table.at["Cooling", "District Cooling [kWh]"]
    value_AH = district_table.at["Heating", "District Heating [kWh]"]
    
    return float(value_AC), float(value_AH), name
    
def diff_from_basecase(df, col_name):
    'Create a column in the df with the diff % of a column'
    
    # Create a copy of the DataFrame to avoid modifying the original DataFrame
    result_df = df.copy()
    # Insert a new column to store the diff
    result_df.insert(result_df.columns.get_loc(col_name)+1, 'diff%_' + col_name, value=0)
    # For each row in the df
    for index, row in df.iterrows():
        # Check if the string part 'use and locality' is in one of the 4 base cases
        if index[3:7] in base_cases.keys():
            # Select the matching base case and get the corresponding value
            base_case = base_cases[index[3:7]]
            base_value = df.at[base_case, col_name]
            # Get the current value of the row
            current_value = row[col_name]
            # Compare the two values
            percentage_diff = (current_value - base_value) / base_value * 100 # Is a float
            # Store the percentage difference in the 'Percentage_difference' column on the right of col_name
            result_df.at[index,'diff%_' + col_name] = percentage_diff.round(2)

        else:
            # If the current row's index is not found in the base_cases list, store None
            result_df.at[index, 'diff%_'+ f'{col_name}'] = None

    return result_df 


def rank_values (df, column_to_rank, n, *columns ):
    '''
    extract from a df n columns, sort the df based on the column_to_rank and
    take the top n values of the new df. Return the new df
    '''
    # Take from the df only the selected columns in *columns
    trim_df = df[list(columns)]
    # Sort the values based on the column to rank
    trim_df = trim_df.sort_values(by= f"{column_to_rank}", ascending=True)
    # Take the n top values
    ranked_df = trim_df.head(n)
    
    return ranked_df


def compare_df (df1, df2, df3, version1, version2, version3):
    """
    Compare two DataFrames by joining them and rounding the values.
    """
    df1 = df1.reset_index().rename(columns={'ID_code': f'ID_code({version1})'})
    df2 = df2.reset_index().rename(columns={'ID_code': f'ID_code({version2})'})
    df3 = df3.reset_index().rename(columns={'ID_code': f'ID_code({version3})'})
    df_join = df1.join(df2)
    df_join = df_join.join(df3)
    # Arrotonda i valori nel DataFrame risultante a due decimali
    df_join = df_join.round(2)
    return df_join


def calculate_delta_percentage(df_new, df_reference, col_new, col_ref, energy):
    """
    Create a new df and calculate the delta percentage between two DataFrames for a specific column.
    """
    df = pd.DataFrame()
    df[f"Delta{energy}%_({col_ref}-{col_new})"] = round(((df_new[col_new] - df_reference[col_ref]) / df_reference[col_ref]) * 100, 2)
    return df


def rank_with_range(df, column_name, range_value):
    # Find the minimum value in the specified column
    min_value = df[column_name].min()
    
    # Select values in the specified column that are within the specified range
    selected_values = df[(df[column_name] >= min_value) & (df[column_name] <= min_value + range_value)][column_name]
    
    print(f"All values in '{column_name}' that are less than or equal to {range_value} units from the min:")
    print(selected_values)
    
    return selected_values


def vconcat_resize(img_list, interpolation = cv2.INTER_CUBIC):
    '''
    Concatenate images of different widths vertically: It is used to 
    combine images of different widths. here shape[0] represents height 
    and shape[1] represents width

    '''
    # take minimum width
    w_min = min(img.shape[1] 
                for img in img_list)
      
    # resizing images
    im_list_resize = [cv2.resize(img,
                      (w_min, int(img.shape[0] * w_min / img.shape[1])),
                                 interpolation = interpolation)
                      for img in img_list]
    # return final image
    return cv2.vconcat(im_list_resize)

def hconcat_resize(img_list, interpolation=cv2.INTER_CUBIC):
    '''
    Concatenate images of different heights horizontally: It is used to 
    combine images of different heights. Here shape[0] represents height 
    and shape[1] represents width.
    '''
    # Take minimum height
    h_min = min(img.shape[0] for img in img_list)

    # Resizing images
    im_list_resize = [cv2.resize(img,
                      (int(img.shape[1] * h_min / img.shape[0]), h_min),
                                 interpolation=interpolation)
                      for img in img_list]
    
    # Return final image
    return cv2.hconcat(im_list_resize)


def create_heamap1(df, width, height, annot_rot, title, savepath, palette):
    # Default values

    # Set the size of the heatmap using figsize
    fig, ax = plt.subplots(figsize=(width, height))  # Adjust the width and height as needed   
    # Create a diverging color palette 
    color_palette = sns.color_palette(f"{palette}", as_cmap=True)
    # Set upper and lower values
    lower_bound = -1
    upper_bound = 1
    # Set the labels
    labels = df.applymap(lambda v: v if v != 1 else '')
    # Plot a heatmap with annotation
    g = sns.heatmap(df,  
                cmap=color_palette,
                center = 0,
                vmin=lower_bound, 
                vmax=upper_bound,
                annot=labels,
                fmt='',
                ax=ax,
                linewidths=1.5,
                annot_kws={'rotation': annot_rot})
    # Set labels and title
    ax.set_title(title, weight='bold')
    # Rotate x names
    g.set_xticklabels(g.get_xticklabels(), rotation=55, horizontalalignment='right')
    # Save the heatmap as an image in the specified folder
    output_filename = os.path.join(savepath, f'{title}.png')
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    
    return output_filename


def plot_overlapping_line_charts(df_list, x_col, y_col, labels=None, x_label=None, y_label=None, title=None, save_path=None, zoom_day=None, fontsize=None):
    """
    Plot overlapping line charts for a list of dataframes.
    Returns:
        None
    """
    if zoom_day:
        fig, ax = plt.subplots(figsize=(70, 10))
    else:
        fig, ax = plt.subplots(figsize=(70, 10))
    
    # Set font size for various elements
    ax.tick_params(axis='both', labelsize=fontsize)
    ax.xaxis.label.set_fontsize(fontsize)
    ax.yaxis.label.set_fontsize(fontsize)
    ax.title.set_fontsize(fontsize)

    for i, df in enumerate(df_list):
        x = df[x_col]
        y = df[y_col]

        label = labels[i] if labels is not None else f'DataFrame {i+1}'
        ax.plot(x, y, label=label, linewidth=2, linestyle = '--')

    if x_label:
        ax.set_xlabel(x_label, fontsize=fontsize)
    if y_label:
        ax.set_ylabel(y_label, fontsize=fontsize)
    if title:
        ax.set_title(title, fontsize=fontsize)

    ax.legend(fontsize=fontsize)


    # Format x-axis to display all days or zoom to the specified day
    if zoom_day:
        ax.set_xlim(pd.Timestamp(zoom_day), pd.Timestamp(zoom_day) + pd.DateOffset(days=1))
        # Dynamically adjust y-axis scale to match the data range in the zoomed day
        data_in_zoomed_day = df_list[0][(df_list[0][x_col] >= pd.Timestamp(zoom_day)) & (df_list[0][x_col] < pd.Timestamp(zoom_day) + pd.DateOffset(days=1))]
        ax.set_ylim(data_in_zoomed_day[y_col].min(), data_in_zoomed_day[y_col].max())
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))

    else:
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        ax.set_xlim([datetime.datetime(2009,1,1,0,0,0), datetime.datetime(2010,1,1,0,0,0)])
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        
    # Set font size for x-axis and y-axis tick labels
    ax.xaxis.get_major_ticks()[0].label.set_fontsize(fontsize)
    ax.yaxis.get_major_ticks()[0].label.set_fontsize(fontsize)

    # Add a grid
    ax.grid(True)

    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.show()

# # Example usage
# eso_path1 = r"C:\Users\andre\Desktop\Thesis_Python\enplus_models\Models_8.5_Originals\RES\MW\B2_R_L2_MW_E_0.6_1.0_TS2\B2_ OFFICE MW_wwr0.6.idf.eso"
# key_number = 319
# df1 = df_kpi_in_esofile(eso_path1, key_number)

# eso_path2 = r"C:\Users\andre\Desktop\Thesis_Python\enplus_models\Models_8.7_fixed\RES\MW\B2_R_L2_MW_E_0.6_1.0_TS2\B2_R_L2_MW_E_0.6_1.0_TS2.eso"
# key_number = 319
# df2 = df_kpi_in_esofile(eso_path2, key_number)

# df_list = [df1,df2]
# # Set the save path
# save_path = folder_images
# plot_overlapping_line_charts(df_list,
#                               x_col="Date",
#                               y_col="Value",
#                               labels=["Solar Radiation Heat Gain Rate g-Value= (v8.5)","Solar Radiation Heat Gain Rate (v8.7)"],
#                               x_label="Date",
#                               y_label="Inside Face Solar Radiation Heat Gain Rate [W]",
#                               title="Surface Inside Face Solar Radiation Heat Gain Rate [W]",
#                               save_path= "comp_B2_R_L2_MW_E_0.6_1.0_TS2_heat_gain.png",
#                               zoom_month= None,
#                               fontsize = 22)




def plot_overlapping_step_charts(df_list, x_col, y_col, labels=None, x_label=None, y_label=None, title=None, save_path=None, zoom_day=None, fontsize=None):
    """
    Plot overlapping step charts for a list of dataframes.
    Returns:
        None
    """
    if zoom_day:
        fig, ax = plt.subplots(figsize=(70, 10))
    else:
        fig, ax = plt.subplots(figsize=(70, 10))

    # Set font size for various elements
    ax.tick_params(axis='both', labelsize=fontsize)
    ax.xaxis.label.set_fontsize(fontsize)
    ax.yaxis.label.set_fontsize(fontsize)
    ax.title.set_fontsize(fontsize)

    for i, df in enumerate(df_list):
        x = df[x_col]
        y = df[y_col]

        label = labels[i] if labels is not None else f'DataFrame {i+1}'
        ax.step(x, y, label=label, where='post', linewidth=2, linestyle='--')

    if x_label:
        ax.set_xlabel(x_label, fontsize=fontsize)
    if y_label:
        ax.set_ylabel(y_label, fontsize=fontsize)
    if title:
        ax.set_title(title, fontsize=fontsize)

    ax.legend(fontsize=fontsize)

    # Format x-axis to display all days or zoom to the specified day
    if zoom_day:
        ax.set_xlim(pd.Timestamp(zoom_day), pd.Timestamp(zoom_day) + pd.DateOffset(days=1))
        # Dynamically adjust y-axis scale to match the data range in the zoomed day
        data_in_zoomed_day = df_list[0][(df_list[0][x_col] >= pd.Timestamp(zoom_day)) & (df_list[0][x_col] < pd.Timestamp(zoom_day) + pd.DateOffset(days=1))]
        ax.set_ylim(data_in_zoomed_day[y_col].min(), data_in_zoomed_day[y_col].max())
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))

    else:
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        ax.set_xlim([datetime.datetime(2009, 1, 1, 0, 0, 0), datetime.datetime(2010, 1, 1, 0, 0, 0)])
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))

    # Set font size for x-axis and y-axis tick labels
    ax.xaxis.get_major_ticks()[0].label.set_fontsize(fontsize)
    ax.yaxis.get_major_ticks()[0].label.set_fontsize(fontsize)

    # Add a grid
    ax.grid(True)

    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.show()



"#############################################################################"
"##                                    Main                                 ##"
"#############################################################################"
def main(run_files=False, collect_kpi=False, verify = False):
      
    df_topAH_comp = None 
    df_topAT_comp = None
    results_dfs = None
    rank_range = None
    df_verifyIDF = None
    
    

    # ==========================
    ' Section 1: Thesis fix '
    # ==========================
    
    # Set the current secion variables
    enplus_version = enplus_vers["version_thesis"]
    folder_models = folder_models85_thesis
    title = f'Spotted_errors_thesis_files_{enplus_version}'
    
    if verify == True:
        
        # Create a list of all the files in the folders
        list_path_idf = search_extensions (folder_models, extension_file = '.idf')
        # Create an empty df to store the results
        df_idf_verified = pd.DataFrame(parameters)
        
        # Verify the idfs and store the results
        for file in list_path_idf:
            results = verifyIDF(file, enplus_version)
            file_name = os.path.basename(file).strip('.idf')
            # Store temporally the results of the verification in this dataframe
            df_to_concat = pd.DataFrame({'Use':[results[0]], 'Version':[results[1]], 'Orient': [results[2]], 'Glass': [results[3]], 'Storage': [results[4]]}, index=[file_name])
            # append the results
            df_idf_verified = pd.concat([df_idf_verified, df_to_concat])
            df_idf_verified.index.name = "ID_code"
            
        print(f"Creating an heatmap {enplus_version}")
        annot_rot = 0
        create_heamap1(df_idf_verified, 3,100, annot_rot, title, folder_images, "viridis_r")
       
        # Save the results of the df
        df_idf_verified.to_csv(folder_csv + f'\{title}.csv', index=True)

    # Read the results
    df_id_verified_85 = pd.read_csv(folder_csv + f'\{title}.csv', index_col="ID_code")

    
    if collect_kpi == True:
        
        print(f"collect kpi of {enplus_version}loading..")
        # Create a list of all the files in the folders
        list_path_html = search_extensions (folder_models, extension_file = '.html')
        # Create an empty df to store the results
        df_annual_results = pd.DataFrame()
        # Collect all the output results in the html
        for html in list_path_html:
            AC_value, AH_value, folder_name = retrieve_districtCH_html(html)
            series = pd.DataFrame({f'AC{enplus_version}':[AC_value], f'AH{enplus_version}': [AH_value]}, index=[folder_name])
            df_annual_results = pd.concat([df_annual_results, series])
            df_annual_results.index.name = "ID_code"
            df_annual_results[f"AT{enplus_version}"] = df_annual_results[f'AC{enplus_version}'] + df_annual_results[f'AH{enplus_version}']
            # Fancy console
            # Stampa un punto "." sulla stessa linea
            print('.', end='', flush=True)
        print()
        # Save the results of the df
        df_annual_results.to_csv(folder_csv + f'\\annualCHT{enplus_version}.csv', index=True)
    
    # Read the results
    df_annual_results_85 = pd.read_csv(folder_csv + f'\\annualCHT{enplus_version}.csv', index_col='ID_code')
    

    # ==========================
    ' Section 2: Version 8.7 '
    # ==========================

    # Set the current section variables
    enplus_version = enplus_vers["version87"]
    folder_models = folder_models87
    iddfile = "\#enplus_models\Models_8.7_fixed\Energy+.idd"
    title = f'Spotted_errors_thesis_files_{enplus_version}'
    
    
    if verify:
        print(f"Verifying files {enplus_version}")
        # Create a list of all the files in the folders
        list_path_idf = search_extensions (folder_models, extension_file = '.idf')
        # Create an empty df to store the results
        df_idf_verified = pd.DataFrame(parameters)
        
        # Verify the idfs and store the results
        for file in list_path_idf:
            results = verifyIDF(file, enplus_version)
            file_name = os.path.basename(file).strip('.idf')
            # Store temporally the results of the verification in this dataframe
            df_to_concat = pd.DataFrame({'Use':[results[0]], 'Version':[results[1]], 'Orient': [results[2]], 'Glass': [results[3]], 'Storage': [results[4]]}, index=[file_name])
            # append the results
            df_idf_verified = pd.concat([df_idf_verified, df_to_concat])
            df_idf_verified.index.name = "ID_code"
            
        print(f"Creating an heatmap {enplus_version}")
        annot_rot = 0
        create_heamap1(df_idf_verified, 3,100, annot_rot, title, folder_images, "viridis_r")
       
        # Save the results of the df
        df_idf_verified.to_csv(folder_csv + f'\{title}.csv', index=True)

    # Read the results
    df_id_verified_87 = pd.read_csv(folder_csv + f'\{title}.csv', index_col="ID_code")
        
    if run_files:
        
        print(f"Running files {enplus_version}")
        #set the iddfile path 
        iddfile = os.path.join(folder_models, 'Energy+.idd')
        # Find all the idf in a folder
        list_path_idf = search_extensions (folder_models, extension_file = '.idf')
        
        os.chdir(folder_models)
        
        #choose to run with palermo or bolzano weater file
        for idf_file in list_path_idf:
            
            #if the string BOLZANO in the line
            if 'L2' in idf_file:
                #Run all the idf files with the run function with the right epw
                epwfile = os.path.join(folder_weather,"ITA_Bolzano.160200_IGDG.epw")
                run_idf(idf_file, iddfile, epwfile)
            
            #else if there's PALERMO
            else:
                #Run all the idf files with the run funtion with the right epw
                epwfile = os.path.join(folder_weather,"ITA_Palermo.164050_IWEC.epw")
                run_idf(idf_file, iddfile, epwfile)
            
            os.chdir(folder_main)
            
    if collect_kpi:
        
        print(f"collect kpi of {enplus_version}loading..")
        # Create a list of all the files in the folders
        list_path_html = search_extensions (folder_models, extension_file = '.html')
        # Create an empty df to store the results
        df_annual_results = pd.DataFrame()
        # Collect all the output results in the html
        for html in list_path_html:
            AC_value, AH_value, folder_name = retrieve_districtCH_html(html)
            series = pd.DataFrame({f'AC{enplus_version}':[AC_value], f'AH{enplus_version}': [AH_value]}, index=[folder_name])
            df_annual_results = pd.concat([df_annual_results, series])
            df_annual_results.index.name = "ID_code"
            df_annual_results[f"AT{enplus_version}"] = df_annual_results[f'AC{enplus_version}'] + df_annual_results[f'AH{enplus_version}']
            # Fancy console
            # Stampa un punto "." sulla stessa linea
            print('.', end='', flush=True)
        print()
        # Save the results of the df
        df_annual_results.to_csv(folder_csv + f'\\annualCHT{enplus_version}.csv', index=True)
    
    # Read the results
    df_annual_results_87 = pd.read_csv(folder_csv + f'\\annualCHT{enplus_version}.csv', index_col='ID_code')
    
    
    
    # ==========================
    ' Section 3: Version 22.2 '
    # ==========================
    
    # Set the current section variables
    enplus_version = enplus_vers["version_new"]
    folder_models = folder_models222
    iddfile = "\#enplus_models\Models_22.2\Energy+.idd"
    title = f'Spotted_errors_thesis_files_{enplus_version}'
    

    if verify:
        print(f"Verifying files {enplus_version}")
        # Create a list of all the files in the folders
        list_path_idf = search_extensions (folder_models, extension_file = '.idf')
        # Create an empty df to store the results
        df_idf_verified = pd.DataFrame(parameters)
        
        # Verify the idfs and store the results
        for file in list_path_idf:
            results = verifyIDF(file, enplus_version)
            file_name = os.path.basename(file).strip('.idf')
            # Store temporally the results of the verification in this dataframe
            df_to_concat = pd.DataFrame({'Use':[results[0]], 'Version':[results[1]], 'Orient': [results[2]], 'Glass': [results[3]], 'Storage': [results[4]]}, index=[file_name])
            # append the results
            df_idf_verified = pd.concat([df_idf_verified, df_to_concat])
            df_idf_verified.index.name = "ID_code"
            
        print(f"Creating an heatmap {enplus_version}")
        annot_rot = 0
        create_heamap1(df_idf_verified, 3,100, annot_rot, title, folder_images, "viridis_r")
       
        # Save the results of the df
        df_idf_verified.to_csv(folder_csv + f'\{title}.csv', index=True)

      
    if run_files:
        
        print(f"Running files {enplus_version}")
        #set the iddfile path 
        iddfile = os.path.join(r"C:\EnergyPlusV22-2-0", 'Energy+.idd')
        # Find all the idf in a folder
        list_path_idf = search_extensions (folder_models, extension_file = '.idf')
        
        os.chdir(folder_models)
        
        #choose to run with palermo or bolzano weater file
        for idf_file in list_path_idf:
            
            #if the string BOLZANO in the line
            if 'L2' in idf_file:
                #Run all the idf files with the run function with the right epw
                epwfile = os.path.join(folder_weather,"ITA_Bolzano.160200_IGDG.epw")
                run_idf(idf_file, iddfile, epwfile)
            
            #else if there's PALERMO
            else:
                #Run all the idf files with the run funtion with the right epw
                epwfile = os.path.join(folder_weather,"ITA_Palermo.164050_IWEC.epw")
                run_idf(idf_file, iddfile, epwfile)
            
            os.chdir(folder_main)
            
    if collect_kpi:
        
        print(f"collect kpi of {enplus_version}loading..")
        # Create a list of all the files in the folders
        list_path_html = search_extensions (folder_models, extension_file = '.htm')
        # Create an empty df to store the results
        df_annual_results = pd.DataFrame()
        # Collect all the output results in the html
        for html in list_path_html:
            AC_value, AH_value, folder_name = retrieve_districtCH_html(html)
            series = pd.DataFrame({f'AC{enplus_version}':[AC_value], f'AH{enplus_version}': [AH_value]}, index=[folder_name])
            df_annual_results = pd.concat([df_annual_results, series])
            df_annual_results[f"AT{enplus_version}"] = df_annual_results[f'AC{enplus_version}'] + df_annual_results[f'AH{enplus_version}']
            df_annual_results.index.name = "ID_code"
            # Fancy console
            # Stampa un punto "." sulla stessa linea
            print('.', end='', flush=True)
        print()
        # Save the results of the df
        df_annual_results.to_csv(folder_csv + f'\\annualCHT{enplus_version}.csv', index=True)
    
    # Read the results
    df_annual_results_222 = pd.read_csv(folder_csv + f'\\annualCHT{enplus_version}.csv', index_col='ID_code')
    
    # ==========================
    ' Section 4: Comparison '
    # ==========================
    
    annual_energies = ["AC", "AH", "AT"]
    df_all_versions = {
    "df_annual_results_85": df_annual_results_85,
    "df_annual_results_87": df_annual_results_87,
    "df_annual_results_222": df_annual_results_222
    }
    
    # Calcola la diff dal caso base per ogni colonna di tutti i df
    for df_name, df, version in zip(df_all_versions.keys(), df_all_versions.values(), enplus_vers.values()):
            for energy in annual_energies:
                column_name = f"{energy}{version}"
                df = diff_from_basecase(df, column_name)
            # Store the new dfs in the library
            df_all_versions[df_name] = df
    
    # Create a df with all
    df_final = pd.concat(df_all_versions.values(), axis=1)    
    df_final_split = {
            'O_L1': df_final.filter(like="O_L1", axis=0),
            'O_L2': df_final.filter(like="O_L2", axis=0),
            'R_L1': df_final.filter(like="R_L1", axis=0),
            'R_L2': df_final.filter(like="R_L2", axis=0),
            }
    
    # Now calculates the delta % between values of different en plus
    
    #Differenza percentuale = [(Valore finale - Valore iniziale) / Valore iniziale] * 100 (la ref è il valore INIZIALE)
    # Nel io caso voglio vedere come è variato il mio valore 8.5 alla 8.7 con nuove g-value
    
    # version 8.5 and 8.7
    df_comp85_87 = pd.DataFrame()
    df_comp85_87['DeltaAC%(v8.7-8.5)'] = round((df_final['AC(v8.7)'] - df_final['AC(v8.5)'])/ df_final['AC(v8.5)'] *100, 2)    # Calculate the %diff   
    # Annual Heating
    df_comp85_87['DeltaAH%(v8.7-8.5)'] = round((df_final['AH(v8.7)'] - df_final['AH(v8.5)'])/ df_final['AH(v8.5)'] *100, 2)    # Calculate the %diff
    # Annual Total
    df_comp85_87['DeltaAT%(v8.7-8.5)'] = round((df_final['AT(v8.7)'] - df_final['AT(v8.5)'])/ df_final['AT(v8.5)'] *100, 2)    # Calculate the %diff
    df_comp85_87 = pd.concat([df_comp85_87,df_id_verified_85], axis=1) 
    # Save results
    df_comp85_87.to_csv(folder_csv+'\\Spotted errors from IDFs 8.5 to 8.7.csv',index=True)
    
    # version 8.7 and 22.2
    df_comp87_222 = pd.DataFrame()
    df_comp87_222['DeltaAC%(v8.7-22.2)'] = round((df_final['AC(v22.2)'] - df_final['AC(v8.7)'])/ df_final['AC(v8.7)'] *100, 2)    # Calculate the %diff   
    # Annual Heating
    df_comp87_222['DeltaAH%(v8.7-22.2)'] = round((df_final['AH(v22.2)'] - df_final['AH(v8.7)'])/ df_final['AH(v8.7)'] *100, 2)    # Calculate the %diff
    # Annual Total
    df_comp87_222['DeltaAT%(v8.7-22.2)'] = round((df_final['AT(v22.2)'] - df_final['AT(v8.7)'])/ df_final['AT(v8.7)'] *100, 2)    # Calculate the %diff
   
    
    # Create heatmaps of the comparison
    
    # Read the CSV data
    data = df_comp85_87
    # Set the figure size for the first heatmap (Reds)
    plt.figure(figsize=(20, 90))  # Adjust the width and height as needed
    data1 = data.copy()
    data1.iloc[:, [3, 4, 5, 6, 7]] = float('nan')
    ax1 = sns.heatmap(data1, annot=True, cmap="coolwarm", center =0, linewidths=1, fmt='.1f')
    # Set the figure size for the second heatmap (Greens)
    # plt.figure(figsize=(8, 50))  # Adjust the width and height as needed || se non metti questa opzione ti plotta insieme
    data2 = data.copy()
    data2.iloc[:, [0, 1, 2]] = float('nan')
    ax2 = sns.heatmap(data2, annot=True, cmap="Greens", center=0.9, linewidths=1)
    # Save the heatmap
    output_filename = "images\Delta% from IDFs 8.5 to 8.7.png"
    plt.savefig(output_filename)
  
    #second heatmap
    create_heamap1(df_comp87_222, 5, 100, annot_rot=0, title="Delta% from IDFs 8.7 to 22.2", savepath=folder_images, palette="coolwarm")
    
    # Save the df_final with the added columns Delta
    df_final = pd.concat([df_final, df_comp87_222], axis=1)
    df_final.to_csv(folder_csv + '\\df_final.csv', index=True)
    
    # Create four DataFrames from df_final and store them in a dictionary
    df_comp87_222_split = {
            'O_L1(8.7-22.2)': df_comp87_222.filter(like="O_L1", axis=0),
            'O_L2(8.7-22.2)': df_comp87_222.filter(like="O_L2", axis=0),
            'R_L1(8.7-22.2)': df_comp87_222.filter(like="R_L1", axis=0),
            'R_L2(8.7-22.2)': df_comp87_222.filter(like="R_L2", axis=0),
            }
    
    # For each of the 4 main dfs create an heatmap of AH, AC AT
    for df_name, df in df_comp87_222_split.items():
        title = df_name
        annot_rot = 90
        create_heamap1(df.T, 50, 2, annot_rot, title, folder_images, "coolwarm") 
    
    
    
    # ==========================
    ' Section 5: Rankings '
    # ==========================    
    
    def highlight_differences(val):
        columns_to_check = ['ID_code(22.2)']  # Specifica le colonne da confrontare
        for col in columns_to_check:
            if val != df['ID_code(8.7)']:  # Confronta con Colonna1
                return 'background-color: red'
            else:
                return 'background-color: green'        

    
    df_tables_rank = {}

    # Rank best solutions for AH and AT. You will have 8 dataframes
    for df_name, df in df_final_split.items():
        # Define the prefixes for AH and AT
        prefixes = ['AH', 'AT']
        
        # For each of the four dfs analyse AH and AT
        for prefix in prefixes:
            thesis_df = rank_values(df, f'diff%_{prefix}(v8.5)', 5, f'{prefix}(v8.5)', f'diff%_{prefix}(v8.5)')
            old_df = rank_values(df, f'diff%_{prefix}(v8.7)', 5, f'{prefix}(v8.7)', f'diff%_{prefix}(v8.7)')
            new_df = rank_values(df, f'diff%_{prefix}(v22.2)', 5, f'{prefix}(v22.2)', f'diff%_{prefix}(v22.2)')
            
            df_comp = compare_df(thesis_df, old_df, new_df, 8.5, 8.7, 22.2)
            
            delta_col = f'Delta{prefix}%_(v22.2-8.7)'
            df_comp[delta_col] = round((df_comp[f'{prefix}(v22.2)'] - df_comp[f'{prefix}(v8.7)']) / df_comp[f'{prefix}(v8.7)'] * 100, 2)
            
            # Store the results in the dictionary using df_name and prefix as keys
            df_tables_rank[f'top{prefix}_{df_name}'] = df_comp
       
        # You can access the results later like this:
        # df_tables_rank['AH_O_L1'] will give you the AH results for O_L1
        # If you want to access a specific column within the DataFrame stored in 'topAH_O_L1', you can use normal DataFrame indexing
        # delta_value = results['AH_O_L1']['Delta_AT%_(v22.2-8.7)']
            
            # Set the index starting from 1
            df_comp.index = range(1, len(df_comp) + 1)
            #styled_df = df_comp.style.apply(highlight_differences, axis=1) da un errore

            # Save the df as image
            dfi.export(df_comp, os.path.join(folder_images, f'top{prefix}_{df_name}.png'), dpi=300)
            
    
    
    # Merge all the tables in one and delete the originals 
    os.chdir(folder_images)
    img_list=[]
    # Concatenate ".png" to each key and create a list
    table_names = [key + ".png" for key in df_tables_rank.keys()]
    for img in table_names:
        imread = cv2.imread(img)
        # Append in the list of images
        img_list.append(imread)
    
    # function calling      
    img_v_resize = vconcat_resize(img_list)
    
    # Save only the concatenated image
    cv2.imwrite('vconcat_tables.png', img_v_resize)

    # Delete the original files
    for img in table_names:
        os.remove(img)
    os.chdir(folder_main)           
    ' Rank range'
    rank_range = {}
    # All values in '{column_name}' that are less than or equal to {range_value} units from the min 
    for df_name, df in df_final_split.items():
        range_df = rank_with_range(df, column_name='diff%_AT(v22.2)', range_value=2)
        rank_range[f'range_{df_name}'] = range_df
    
    
    
    
    return df_id_verified_85, df_id_verified_87, df_all_versions, df_topAH_comp, df_topAT_comp, results_dfs, rank_range, df_verifyIDF, df_comp85_87, df_comp87_222, df_final
    


if __name__  == "__main__" :
   df_id_verified_85, df_id_verified_87, df_all_versions, df_topAH_comp, df_topAT_comp, results_dfs, rank_range, df_verifyIDF, df_comp85_87, df_comp87_222, df_final = main()    