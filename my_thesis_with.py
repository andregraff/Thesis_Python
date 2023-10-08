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

# Define the base case identifiers
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
    "_0.8_": "U-0.8_G0.7",
    "_1.0_": "U-1.0_G-0.7",
    "_2.3_": "2xGLASS_U2.3_KRYPTON",
    "_5.9_": "Exterior Window",   
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

"#############################################################################"
"##                            Common Functions                             ##"
"#############################################################################"

def delete_files_with_string(root_folder, search_string):
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if search_string in file:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Deleted file: {file_path}")

# Specify the root folder to start the search from
# root_folder = r'C:\Users\andre\Desktop\Week1\#enplus_models_22.2_onlyIDF'
# search_string = 'V850'

def delete_non_idf_files(folder):
    for current_folder, subfolders, files in os.walk(folder):
        for file_name in files:
            if not file_name.endswith(".idf"):
                full_path = os.path.join(current_folder, file_name)
                os.remove(full_path)

###############################################################################
###                           search_extensions                             ###
###############################################################################

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
    
    #print all the file found each in a new line with a for loop
    for file_path in files_found:
        print(file_path)
        
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



###############################################################################
###                           ID_generator_folders                          ###
###############################################################################

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
###                           rename_idf_files                              ###
###############################################################################

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
          
          
###############################################################################
###                           rename_folders                              ###
###############################################################################

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
            

###############################################################################
###                        replace_construction_line                        ###
###############################################################################

def replace_construction_part(file_path):
    # Get the name of the file
    file_name = os.path.basename(file_path)
    # Read the file and store its lines in a list
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Define the part to search for and its replacement
    target_part = "3xGLASS_U1.0_AIR"
    replacement_part = "U-1.0_G-0.7"
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


###############################################################################
###                          replace_piece_of_text                         ###
###############################################################################

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


###############################################################################
###                               check_line                                ###
###############################################################################

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


###############################################################################
###                           split_idf_objects                             ###
###############################################################################

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
       
  



###############################################################################
###                               verifyIDF                                 ###
###############################################################################
def verifyIDF(file_path, version):
    '''
    Check if the parameters in the file and in the file's name correspond.
    Return 1 if the selected parameter is found else 0. Use this function to 
    create a list of unmatched files.
    '''
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
            
    glass_lines = idf_dict["FENESTRATIONSURFACE:DETAILED"]
    for line in glass_lines:
        if glass_marker in line and glass in line:
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



    
    
###############################################################################
###                               Run_idf                               ###
###############################################################################

def Run_idf(idf_file, iddfile, epwfile):
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


###############################################################################
###                               add_output                                ###
###############################################################################
  
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


            
###############################################################################
###                        calculate_percentage_diff                        ###
###############################################################################

# Function to calculate the percentage difference
def calculate_percentage_diff(df, col_name):
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



###############################################################################
###                             retrieve_kpi3                               ###
###############################################################################

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

###############################################################################
###                               rank_values                               ###
###############################################################################
    
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

###############################################################################
###                               compare_df                                ###
###############################################################################
def compare_df (df1, df2, version1, version2):
    """
    Compare two DataFrames by joining them and rounding the values.
    """
    df1 = df1.reset_index().rename(columns={'ID_code': f'ID_code({version1})'})
    df2 = df2.reset_index().rename(columns={'ID_code': f'ID_code({version2})'})
    # Join the two dfs and see the difference
    df_join = df1.join(df2).round(2)
    return df_join


###############################################################################
###                      calculate_delta_percentage                         ###
###############################################################################

def calculate_delta_percentage(new_df, old_df, version_new, version_old, value_column):
    """
    Calculate the delta percentage between two DataFrames for a specific column.
    """
    delta_column = f'Delta_%_({version_new}-{version_old})'
    new_df[delta_column] = round(((new_df[value_column] - old_df[value_column]) / old_df[value_column]) * 100, 2)
    return new_df


###############################################################################
###                      select_values_within_range                         ###
###############################################################################

def rank_with_range(df, column_name, range_value):
    # Find the minimum value in the specified column
    min_value = df[column_name].min()
    
    # Select values in the specified column that are within the specified range
    selected_values = df[(df[column_name] >= min_value) & (df[column_name] <= min_value + range_value)][column_name]
    
    print(f"All values in '{column_name}' that are less than or equal to {range_value} units from the min:")
    print(selected_values)
    
    return selected_values

#############################################################################"
##                              STYLER SECTION                             ##"
#############################################################################"



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


def create_heamap1(df, width, height, annot_rot, title):
    # Default values

    # Set the size of the heatmap using figsize
    fig, ax = plt.subplots(figsize=(width, height))  # Adjust the width and height as needed   
    # Create a diverging color palette 
    color_palette = sns.color_palette("coolwarm", as_cmap=True)
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
    output_filename = title + '.png'
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    
    return output_filename 




"###############################################################################"
"###                                 Main                                    ###"
"###############################################################################"

def main(run_files=False, add_outputs=False, collect_kpi=False, verify = False):
    
    df_AH = None
    df_AC = None
    final_df = None  
    df_topAH_comp = None 
    df_topAT_comp = None
    
    '''
    Dictionaries
    '''
    
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
    
    enplus_vers = '(v22.2)'  #set the current En+ version

    #run this file in the root folder
    base_folder = os.getcwd()
    weather_folder = base_folder + "\weather_files"
    
    enplusmodels85_thesis = r"#enplus_models\Models_8.5_Originals"
    enplusmodels85_fixed = r"#enplus_models\Models_8.5_fixed"
    enplusmodels22 = base_folder + r"\#enplus_models\Models22.2"
         
    #create a folder to store the outputs images
    dir_images = 'images_outputs'   
    if not os.path.exists(dir_images):
        os.makedirs(dir_images)
        print("Directory '% s' created" % dir_images)
    else:
        print("Directory '% s' already exists" % dir_images)
  
        
   

    
    '''
    Create first list (idf)
    '''
    
    #First of all create a list of all the file paths with an .idf extension
    list_IDFs_found = search_extensions(enplusmodels22, extension_file = '.idf')
    list_old_idf = search_extensions(enplusmodels85_thesis, extension_file = '.idf')
    list_fixed_idf = search_extensions(enplusmodels85_fixed, extension_file = '.idf')

    
    '''
    Verify all idf files
    ''' 
    # Initialize an empty DataFrame to store the results
    data = {'Use': [],
            'Orient': [],
            'Glass': [],
            'Storage': []}
    
    old_df_verifyIDF = pd.DataFrame(data)
    df_verifyIDF = pd.DataFrame(data)

    
    if verify== True:
  
        " Original models 8.5"
        
        title= r"images_outputs\Original_Models"
        annot_rot=90
        # Verify results of 8.5 thesis
        for old_idf in list_old_idf:
            
            old_result = verifyIDF(old_idf, "8.5")
            old_file_name = os.path.basename(old_idf).strip('.idf')
            old_df_to_concat = pd.DataFrame({'Use':[old_result[0]], 'Version':[old_result[1]], 'Orient': [old_result[2]], 'Glass': [old_result[3]], 'Storage': [old_result[4]]}, index=[old_file_name])
            old_df_verifyIDF = pd.concat([old_df_verifyIDF, old_df_to_concat])
            old_df_verifyIDF.index.name = "ID_code"
            
        create_heamap1(old_df_verifyIDF.T, 150, 3, annot_rot, title)
        old_df_verifyIDF.to_csv("csv_outputs\csv_8.5_thesis\v8.5_df_verifyIDF.csv",index=True)

        " Fixed models 8.7"
        
        fixed_df_verifyIDF = pd.DataFrame(data)
        title= r"images_outputs\Fixed_Models"
        annot_rot=90
        # Verify results of 8.5 thesis
        for fix_idf in list_fixed_idf:
            
            fixed_result = verifyIDF(fix_idf, "8.5")
            file_name = os.path.basename(fix_idf).strip('.idf')
            fix_df_to_concat = pd.DataFrame({'Use':[fixed_result[0]], 'Version':[fixed_result[1]], 'Orient': [fixed_result[2]], 'Glass': [fixed_result[3]], 'Storage': [fixed_result[4]]}, index=[file_name])
            fixed_df_verifyIDF = pd.concat([fixed_df_verifyIDF, fix_df_to_concat])
            
        create_heamap1(fixed_df_verifyIDF.T, 150, 3, annot_rot, title)
        
        " New version 22.2"
        
        # Iterate through the list of files and call verifyIDF for each file
        for file_path in list_IDFs_found:
            # Call the verifyIDF function and get the result (0 or 1)
            result = verifyIDF(file_path, "22.2")   
            # Extract the file name
            file_name = os.path.basename(file_path).strip('.idf')
            # Create a DataFrame for the current file and result
            df_to_concat = pd.DataFrame({'Use':[result[0]], 'Version':[result[1]], 'Orient': [result[2]], 'Glass': [result[3]], 'Storage': [result[4]]}, index=[file_name])
            # Append the result to the DataFrame
            df_verifyIDF = pd.concat([df_verifyIDF, df_to_concat])


    '''
    add an output total cooling rate'
    '''
    
    if add_outputs == True:
        
        #define the reference_string where you want to add a new output_line
        reference_string = "Zone Ideal Loads Zone Sensible Heating Rate"
        output_line = '  Output:Variable,*,Zone Ideal Loads Zone Total Cooling Rate,Hourly;\n'
        
        #for each idf file add an output
        for path_idf in list_IDFs_found:
            
            add_output(path_idf, reference_string, output_line)
            
            
    '''
    run all idf files
    ''' 
    if run_files == True:
        
        #set the iddfile path 
        iddfile = os.path.join(base_folder, 'Energy+.idd')
        
        os.chdir(enplusmodels22)
        
        #choose to run with palermo or bolzano weater file
        for idf_file in list_IDFs_found:
            
            #if the string BOLZANO in the line
            if 'L2' in idf_file:
                #Run all the idf files with the run function with the right epw
                epwfile = os.path.join(weather_folder,"ITA_Bolzano.160200_IGDG.epw")
                Run_idf(idf_file, iddfile, epwfile)
            
            #else if there's PALERMO
            else:
                #Run all the idf files with the run funtion with the right epw
                epwfile = os.path.join(weather_folder,"ITA_Palermo.164050_IWEC.epw")
                Run_idf(idf_file, iddfile, epwfile)
            
            os.chdir(base_folder)
        

    '''
    Create second list (eso)
    ''' 
    #Create a list of all .eso files generated with the Run_idf function    
    list_ESOs_found = search_extensions(enplusmodels22, extension_file = '.eso') 
    
    
    '''
    KPI section
    ''' 
    if collect_kpi == True:
        
        " Model 8.7 fixed"
     
        files_fixed = r"#enplus_models\Models_8.5_fixed"    
        fixed_list_html_found =  search_extensions(files_fixed, extension_file = '.htm')
        thesis_fixed_df = pd.DataFrame()
        
        for file in  fixed_list_html_found:
            
            html = pd.read_html(file)
            # Get the folder containing the specified file
            folder_name = os.path.dirname(file)
            # Get the name of the last directory
            name = os.path.basename(folder_name)
            
            # COLLECT KPI
            # Open the table with district heating and coolig
            district_table = html[3]
            AC_value = district_table.at[2,4]
            AH_value = district_table.at[1,5]
            series = pd.DataFrame({'AC(v8.7)':[AC_value], 'AH(v8.7)': [AH_value]}, index=[name])
            thesis_fixed_df = pd.concat([thesis_fixed_df, series])
            thesis_fixed_df.index.name= "ID_code"
            
        thesis_fixed_df.to_csv(r"csv_outputs\csv_8.7_fixed\annual8.7_fixed_thesis.csv", index=True)
        
        '''
        Section: Thesis
        ''' 
        folder_files = r"#enplus_models\Models_8.5_Originals"    
        thesis_list_html_found =  search_extensions(folder_files, extension_file = '.html')
        thesis_df = pd.DataFrame()
        
        for file in  thesis_list_html_found:
            
            html = pd.read_html(file)
            # Get the folder containing the specified file
            folder_name = os.path.dirname(file)
            # Get the name of the last directory
            name = os.path.basename(folder_name)
            
            # COLLECT KPI
            # Open the table with district heating and coolig
            district_table = html[3]
            AC_value = district_table.at[2,4]
            AH_value = district_table.at[1,5]
            series = pd.DataFrame({'AC_thesis':[AC_value], 'AH_thesis': [AH_value]}, index=[name])
            thesis_df = pd.concat([thesis_df, series])
            thesis_df.index.name= "ID_code"
            
        thesis_df.to_csv(r"csv_outputs\csv_8.5_thesis\annual8.5_old_python.csv", index=True)
        
        
        " Model 22.2"
        
        # folder_files = r"#enplus_models\Models22.2"    
        # latest_list_html_found =  search_extensions(folder_files, extension_file = '.htm')
        # version_22_df = pd.DataFrame()
        
        # for file in  latest_list_html_found:
            
        #     html = pd.read_html(file)
        #     # Get the folder containing the specified file
        #     folder_name = os.path.dirname(file)
        #     # Get the name of the last directory
        #     name = os.path.basename(folder_name)
            
        #     # COLLECT KPI
        #     # Open the table with district heating and coolig
        #     district_table = html[3]
        #     AC_value = district_table.at[2,11]
        #     AH_value = district_table.at[1,12]
        #     series = pd.DataFrame({'AC(v22.2)':[AC_value], 'AH(v22.2)': [AH_value]}, index=[name])
        #     version_22_df = pd.concat([version_22_df, series])
        #     version_22_df.index.name= "ID_code"
            
        # version_22_df.to_csv(r"csv_outputs\annual22.2.csv", index=True)
        
        'cooling' 
        # Create an empty dictonary
        AC = {}
        string_KPI = 'Zone Ideal Loads Zone Total Cooling Rate [W] !Hourly'
        
        for esofile in list_ESOs_found:
            #extract the folder name to identify the "sum values"
            folder_name = os.path.basename(os.path.dirname(esofile))
            try:
                #find all the annual values
                output = retrieve_kpi(esofile, string_KPI) #is a float64
            except:
                print(f'Error found in: {folder_name}')
 
            # Fill the dict
            AC[folder_name] = output
            # Convert the dictionary to a DataFrame with index=folder_name
            df_AC = pd.DataFrame.from_dict(AC, orient='index', columns=[f'AC{enplus_vers}'])
            df_AC = df_AC.rename_axis('ID_code', axis='index')
        
        'heating' 
        # Create an empty dictonary
        AH = {}
        string_KPI = 'Zone Ideal Loads Zone Sensible Heating Rate [W] !Hourly'
        
        for esofile in list_ESOs_found:
            #extract the folder name to identify the "sum values"
            folder_name = os.path.basename(os.path.dirname(esofile))
            try:
                #find all the annual values
                output = retrieve_kpi(esofile, string_KPI) #is a float64
            except:
                print(f'Error found in: {folder_name}')
 
            # Fill the dict
            AH[folder_name] = output
            # Convert the dictionary to a DataFrame with index=folder_name
            df_AH = pd.DataFrame.from_dict(AH, orient='index', columns=['AH'+ enplus_vers])
            df_AH = df_AH.rename_axis('ID_code', axis='index')
        
        ' Export df in an output folder'
        
        os.chdir(base_folder)        
        #create a folder to store the outputs
        dir_csv = 'csv_outputs'      
        if not os.path.exists(dir_csv):
            os.makedirs(dir_csv)
            print("Directory '% s' created" % dir_csv)
        else:
            print("Directory '% s' already exists" % dir_csv)    
        # Change the current directory
        os.chdir(dir_csv)
        # Save the df            
        df_AC.to_csv(f'AC{enplus_vers}.csv')  
        df_AH.to_csv(f'AH{enplus_vers}.csv')
        # Create also the annual total dataframe
        df_AT = pd.concat([df_AC, df_AH], axis=1).sum(axis=1).to_frame(name=f'AT{enplus_vers}')
        df_AT.to_csv(f'AT{enplus_vers}.csv')
        #return to the current dir
        os.chdir(base_folder)
        
    
    
    '''
    Comparison step
    '''
    
    " Old results of 8.5"
    #read the old thesis results and create a  df
    old_85_file = r"C:\Users\andre\Desktop\Week1\Thesis_Python-main\csv_outputs\csv_8.5_thesis\annual8.5_old_python.csv"
    old_85 = pd.read_csv(old_85_file, index_col='ID_code')
    # Add AT
    old_85["AT(v8.5_old_py)"] = old_85["AC(v8.5_old_py)"] + old_85["AH(v8.5_old_py)"]
    # Calculate the difference from base case
    old_85 = calculate_percentage_diff(old_85, 'AC(v8.5_old_py)')
    old_85 = calculate_percentage_diff(old_85, 'AH(v8.5_old_py)')
    old_85 = calculate_percentage_diff(old_85, 'AT(v8.5_old_py)')
    
    " New results of 8.7"
    #read the new thesis results and create a df
    new_85_file = r"C:\Users\andre\Desktop\Week1\Thesis_Python-main\csv_outputs\csv_8.7_fixed\annual8.7_fixed_thesis.csv"
    new_85 = pd.read_csv(new_85_file, index_col='ID_code')
    # Add AT
    new_85["AT(v8.7)"] = new_85["AC(v8.7)"] + new_85["AH(v8.7)"]
    # Calculate the difference from base case
    new_85 = calculate_percentage_diff(new_85, 'AC(v8.7)')
    new_85 = calculate_percentage_diff(new_85, 'AH(v8.7)')
    new_85 = calculate_percentage_diff(new_85, 'AT(v8.7)')
    
    " Confronto risultati tesi con risultati corretti 8.5"
    df_comparison = pd.concat([old_85, new_85], axis=1)
    # Annual Cooling
    df_comparison['Delta_AC%_(v8.5-8.7_new)'] = round((df_comparison['AC(v8.5_old_py)'] - df_comparison['AC(v8.7)'])/ df_comparison['AC(v8.7)'] *100, 2)    # Calculate the %diff   
    # Annual Heating
    df_comparison['Delta_AH%_(v8.5-8.7_new)'] = round((df_comparison['AH(v8.5_old_py)'] - df_comparison['AH(v8.7)'])/ df_comparison['AH(v8.7)'] *100, 2)    # Calculate the %diff
    # Annual Total
    df_comparison['Delta_AT%_(v8.5-8.7_new)'] = round((df_comparison['AT(v8.5_old_py)'] - df_comparison['AT(v8.7)'])/ df_comparison['AT(v8.7)'] *100, 2)    # Calculate the %diff
    
    " Results of 22.2"

    os.chdir('csv_outputs')
    # new_C = pd.read_csv(f'AC{enplus_vers}.csv', index_col='ID_code')
    # new_H = pd.read_csv(f'AH{enplus_vers}.csv', index_col='ID_code')
    # new_T = pd.read_csv(f'AT{enplus_vers}.csv', index_col='ID_code')
    
    # # Create a df with 2 columns
    # new_CHT = pd.concat([new_C,new_H,new_T],axis=1)
    
    new_CHT = pd.read_excel('annual22.2.xlsx', index_col='ID_code')
    # Add the column diff % on the right of the selected column
    new_CHT = calculate_percentage_diff(new_CHT, col_name='AC'+ enplus_vers)
    new_CHT = calculate_percentage_diff(new_CHT, col_name='AH'+ enplus_vers)
    new_CHT = calculate_percentage_diff(new_CHT, col_name='AT'+ enplus_vers)

    " Final dataframe with all"
    final_df = pd.concat([old_85, new_85, new_CHT],axis=1)
  
    #add a new column to final_df with the delta AH from v8.7 to 22.2
    #Differenza percentuale = [(Nuovo valore - Vecchio valore) / Vecchio valore] * 100 (la ref è vecchio val)
    
    # Annual Cooling
    final_df['Delta_AC%_(v22.2-8.7_new)'] = round((final_df['AC(v22.2)'] - final_df['AC(v8.7)'])/ final_df['AC(v8.7)'] *100, 2)    # Calculate the %diff   
    # Annual Heating
    final_df['Delta_AH%_(v22.2-8.7_new)'] = round((final_df['AH(v22.2)'] - final_df['AH(v8.7)'])/ final_df['AH(v8.7)'] *100, 2)    # Calculate the %diff
    # Annual Total
    final_df['Delta_AT%_(v22.2-8.7_new)'] = round((final_df['AT(v22.2)'] - final_df['AT(v8.7)'])/ final_df['AT(v8.7)'] *100, 2)    # Calculate the %diff
    
    # # Create ranking columns
    # final_df['rank_8.7'] =   final_df['AT(v8.7)'].rank(ascending=True)
    # final_df['rank_22.2'] =   final_df['AT(v22.2)'].rank(ascending=True)
    # # Compare the rank
    # final_df['delta_rank_22.2-8.7'] = final_df['rank_22.2'] - final_df['rank_8.7']   
    final_df.to_csv('final_df.csv')
  
    
  
    ' Initialise 4 main dfs from the final_df'
    # Create four DataFrames from final_df and store them in a dictionary
    four_df = {
            'O_L1': final_df.filter(like="O_L1", axis=0),
            'O_L2': final_df.filter(like="O_L2", axis=0),
            'R_L1': final_df.filter(like="R_L1", axis=0),
            'R_L2': final_df.filter(like="R_L2", axis=0),
            }
   
   
    ' Ranking best solutions'
    
    #save the dfs as images in the right folder
    os.chdir(base_folder)
    os.chdir(dir_images)
    
    # Create an empty dictionary to store the results
    results_dfs = {}
    
    # Rank best solutions for AH and AT. You will have 8 dataframes
    for df_name, df in four_df.items():
        # Define the prefixes for AH and AT
        prefixes = ['AH', 'AT']
        
        # For each of the four dfs analyse AH and AT
        for prefix in prefixes:
            old_df = rank_values(df, f'diff%_{prefix}(v8.7)', 5, f'{prefix}(v8.7)', f'diff%_{prefix}(v8.7)')
            new_df = rank_values(df, f'diff%_{prefix}(v22.2)', 5, f'{prefix}(v22.2)', f'diff%_{prefix}(v22.2)')
            
            df_comp = compare_df(old_df, new_df, 8.7, 22.2)
            
            delta_col = f'Delta_{prefix}%_(v22.2-8.7)'
            df_comp[delta_col] = round((df_comp[f'{prefix}(v22.2)'] - df_comp[f'{prefix}(v8.7)']) / df_comp[f'{prefix}(v8.7)'] * 100, 2)
            
            # Store the results in the dictionary using df_name and prefix as keys
            results_dfs[f'top{prefix}_{df_name}'] = df_comp
       
        # You can access the results later like this:
        # results_dfs['AH_O_L1'] will give you the AH results for O_L1
        # If you want to access a specific column within the DataFrame stored in 'topAH_O_L1', you can use normal DataFrame indexing
        # delta_value = results['AH_O_L1']['Delta_AT%_(v22.2-8.7)']
            
            # Set the index starting from 1
            df_comp.index = range(1, len(df_comp) + 1)
            # Save the df as image
            dfi.export(df_comp, f'top{prefix}_{df_name}.png', dpi=300)
    
    ' Merge all the tables in one and delete the originals '
   
    img_list=[]
    # Concatenate ".png" to each key and create a list
    table_names = [key + ".png" for key in results_dfs.keys()]
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
               
    ' Rank range'
    rank_range = {}
    # All values in '{column_name}' that are less than or equal to {range_value} units from the min 
    for df_name, df in four_df.items():
        range_df = rank_with_range(df, column_name='diff%_AT(v22.2)', range_value=3)
        rank_range[f'range_{df_name}'] = range_df
    
 
    ' Create Heatmaps'
    
    # Comparison of 8.7 thesis    
    title = "8.7_comparison"
    annot_rot = 90

    # # Trim the df with only the rows containing the distance %. Function FILTER
    # df0 = df_comparison.filter(like='Delta', axis=1)
    # df0_verified = pd.read_csv(r"C:\Users\andre\Desktop\Week1\Thesis_Python-main\csv_outputs\csv_8.7_thesis\v8.7_df_verifyIDF.csv", index_col="ID_code") 
    # df_verify_heatmap = df0_verified.join(df0)
    # df_verify_heatmap.T
    # create_heamap1(df_verify_heatmap.T, 150, 5, annot_rot, title) 
    
    # For each of the 4 main dfs create an heatmap of AH, AC AT
    for df_name, df in four_df.items():
        
        title = df_name
        annot_rot = 90
    
        # Trim the df with only the rows containing the distance %. Function FILTER
        df1 = df.filter(like='%_(v22.2-8.7_new)', axis=1)
        # Df for debugging filtered by use and location

        df1.T
        create_heamap1(df1.T, 50, 5, annot_rot, title) 
    

    return df_AH, df_AC, final_df, df_topAH_comp, df_topAT_comp, results_dfs, rank_range, df_verifyIDF

    
if __name__  == "__main__" :
    df_AH, df_AC, final_df, df_topAH_comp, df_topAT_comp, results_dfs, rank_range, df_verifyIDF = main()
    



          

   
