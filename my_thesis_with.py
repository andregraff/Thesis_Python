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


# Define the base case identifiers
base_cases = {
    'R_L1':'B2_R_L1_Base_S_0.12_5.9_TS1',
    'R_L2':'B2_R_L2_Base_S_0.12_5.9_TS1',
    'O_L1':'B2_O_L1_Base_S_0.12_5.9_TS1',
    'O_L2':'B2_O_L2_Base_S_0.12_5.9_TS1',
    }
    

"#############################################################################"
"##                            Common Functions                             ##"
"#############################################################################"



###############################################################################
###                           search_extensions                             ###
###############################################################################

def search_extensions(current_dir, extension_file, create_list=None):
    """
  Return a list of retrieved file paths based on the specified extension like .html or .csv.
  If create_list is True, it creates a .txt file of the list.

  Parameters
  ----------
  current_dir : str
      The directory path to search for files.
  extension_file : str
      The file extension to search for (e.g., '.html', '.csv').
  create_list : bool, optional
      If True, creates a .txt file of the list. Default is None.

  Returns
  -------
  list
      A list of retrieved file paths.
  """
    #Initialize a list of valid extensions
    valid_extensions = ['.html', '.csv', '.idf', '.eso']

   
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
    print(f"-->Total files found: {count_files}")
    
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

def replace_construction_line(file_path):
    # Read the file and store its lines in a list
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Search for the target construction line and replace it wherever it occurs
    target_line = "    2xGLASS_U2.3_KRYPTON,    !- Construction Name\n"
    replacement_line = "3xGLASS_U1.0_AIR,    \n"
    found_at_least_once = False

    for index, line in enumerate(lines):
        if target_line in line:
            # Check if 3 lines above contain "FenestrationSurface:Detailed,"
            if index >= 3 and "  FenestrationSurface:Detailed,\n" in lines[index - 3]:
                lines[index] = replacement_line
                found_at_least_once = True

    # Write the modified lines back to the file if any replacements were made
    if found_at_least_once:
        with open(file_path, 'w') as file:
            file.writelines(lines)
        print("Substitution successful.")
    else:
        print("Target construction line not found in the file.")               


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
###                             find_KPInumber                              ###
###############################################################################


def find_KPInumber(esofile, string_KPI):
    list_of_KPIs = []  # Store the lines that match the pattern
    KPI_number = []  # Store the extracted  ID number of the KPI defined by the .eso file
    
    with open(esofile) as file:
        for line in file:
            
            if re.search(string_KPI, line, re.IGNORECASE):
                
                # Extract the variable number.
                #\d is the pattern that matches any digit, and + is a quantifier that matches one or more occurrences of the preceding pattern.
                variable_number = re.findall(r'\d+', line)[0] 
                list_of_KPIs.append((variable_number, line.strip()))  # Append the line to the list
                KPI_number.append(variable_number)  # Append the variable number to the list
    
    print(KPI_number)  # Print the extracted variable numbers
    
    return list_of_KPIs, KPI_number




###############################################################################
###                            collect_KPIvalues                            ###
###############################################################################

def collect_KPIvalues(esofile, string_KPI):
    
    list_of_KPIs, KPI_number = find_KPInumber(esofile, string_KPI)
    
    lines_found = []  # Store the lines that match the variable numbers
    start_collecting = False
    
    with open(esofile) as file:
        for line in file:
            if start_collecting:
                line_elements = line.strip().split(",")
                if line_elements[0] in KPI_number:  # Check if the variable number matches
                    lines_found.append(line_elements)  # Append the line as a list of elements
            elif line.strip() == "End of Data Dictionary":
                start_collecting = True  # Start collecting lines after "End of Data Dictionary"

    column_value = 'value'
    df = pd.DataFrame(lines_found, columns=[string_KPI, column_value])  # Create a data frame with the found lines    

    # The 'pd.to_numeric' function is used to convert the column values to numeric type
    # The 'errors' argument is set to 'coerce' to replace any non-convertible values with 'NaN'
    # The converted numeric values are then assigned back to the column in the DataFrame
    df[column_value] = pd.to_numeric(df[column_value], errors='coerce')
    
    sum_value = df['value'].sum() / 1000 #[W] to [kW] #####potrei aggiungere un IF per quando nella stringa ho [W]
    new_df = pd.DataFrame({'sum_value': [sum_value]})
    
    
    return new_df



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




def retrieve_kpi (eso_path, key_string):
    
    values = []

    # First, let's read the lines from the file and filter out the relevant keys
    with open(eso_path, "r") as esofile:
        lines = esofile.readlines()
    
    all_keys = [line.split(',')[0] for line in lines if key_string in line]
    
    # Now, let's extract the values for the keys we found earlier
    with open(eso_path, "r") as esofile:
        lines = esofile.readlines()
    
    for line in lines:
        values_line = line.split(',')
        if len(values_line) < 3 and values_line[0] in all_keys:
            values.append(abs(float(values_line[1])))
    
    # Calculate the total and divide by 1000
    total_value = sum(values) / 1000
    total_value = round(total_value, 1)
    
    # Printing the result or using it for further analysis
    print("Total cooling:", total_value) 

    return total_value   #is a float

###############################################################################
###                        calculate_percentage_diff                        ###
###############################################################################

# Function to calculate the percentage difference
def calculate_percentage_diff(df, col_name):
    'Create a column in the df with the diff % of a column'
    
    # Create a copy of the DataFrame to avoid modifying the original DataFrame
    result_df = df.copy()
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
            percentage_diff = (current_value - base_value) / base_value * 100
            # Store the percentage difference in the 'Percentage_difference' column
            result_df.at[index, 'Percentage_diff'] = percentage_diff.round(2)

        else:
            # If the current row's index is not found in the base_cases list, store None
            result_df.at[index, 'Percentage_diff'] = None

    return result_df 
    
    
"###############################################################################"
"###                                 Main                                    ###"
"###############################################################################"

def main(run_files=False, add_output=None, collect_kpi=False):
    
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
    


    #run this file in the root folder
    base_folder = os.getcwd()
    
    df_sorted = None
    df2_sorted = None
    top_nvalues_H = None
    top_nvalues_C = None
    df_tot = None
    top_nvalues_tot = None
    new_perc = None

    
    '''
    Create first list (idf)
    '''
    
    #First of all create a list of all the file paths with an .idf extension
    list_IDFs_found = search_extensions(base_folder, extension_file = '.idf')
    
    
    '''
    add an output total cooling rate'
    '''
    
    if add_output:
        
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
        iddfile = iddfile = os.path.join(base_folder, 'Energy+.idd')
        
        #choose to run with palermo or bolzano weater file
        for idf_file in list_IDFs_found:
            
            #if the string BOLZANO in the line
            if 'BOLZANO' in idf_file:
                #Run all the idf files with the run function with the right epw
                epwfile = os.path.join(base_folder,"ITA_Bolzano.160200_IGDG.epw")
                Run_idf(idf_file, iddfile, epwfile)
            
            #else if there's PALERMO
            else:
                #Run all the idf files with the run funtion with the right epw
                epwfile = os.path.join(base_folder,"ITA_Palermo.164050_IWEC.epw")
                Run_idf(idf_file, iddfile, epwfile)
        

    '''
    Create second list (eso)
    ''' 
    #Create a list of all .eso files generated with the Run_idf function    
    list_ESOs_found = search_extensions(base_folder, extension_file = '.eso') 
    
    
    '''
    KPI section
    ''' 
    if collect_kpi:
        
        'heating'
        
        #for each esofile in the list, retrieve the KPI values and create a df
        df = pd.DataFrame()
        string_KPI = 'Zone Ideal Loads Zone Sensible Heating Rate'
        
        for esofile in list_ESOs_found:
            
            #create a df with the sum values of the retrieved KPI
            current_df = collect_KPIvalues(esofile, string_KPI)
            
            #extract the folder name to identify the "sum values"
            folder_name = os.path.basename(os.path.dirname(esofile))
            
            # Add a new column with the folder name
            current_df['folder_name'] = folder_name
            
            #create a df with the values of all the folders
            df = pd.concat([df, current_df], ignore_index= True)
        
        #sort the dataframe from the lowest to the highest
        df_sorted = df.sort_values(by = "sum_value", ascending = True)
        
        #take the top "n" values
        
        n = 5
        top_nvalues_H = df_sorted.head(n)
        print(top_nvalues_H)
          
        'cooling'
        
        #for each esofile in the list, retrieve the KPI values and create a df
        df2 = pd.DataFrame()
        string_KPI2 = 'Zone Ideal Loads Zone Total Cooling Rate'
        
        for esofile in list_ESOs_found:
            
            #create a df with the sum values of the retrieved KPI
            current_df2 = collect_KPIvalues(esofile, string_KPI2)
            
            #extract the folder name to identify the "sum values"
            folder_name = os.path.basename(os.path.dirname(esofile))
            
            # Add a new column with the folder name
            current_df2['folder_name'] = folder_name
            
            #create a df with the values of all the folders
            df2 = pd.concat([df2, current_df2], ignore_index= True)
        
        #sort the dataframe from the lowest to the highest
        df2_sorted = df2.sort_values(by = "sum_value", ascending = True)
        
        #take the top "n" values
        
        n = 5
        top_nvalues_C = df2_sorted.head(n)
        print(top_nvalues_C)
           
        'Total'
        
        df_tot = pd.concat([df, df2], axis=1, ignore_index=True)
        #replace the current df_tot setting inplace = true
        df_tot.rename(columns={0:'value_heat', 1:'Heating', 2:'value_cool', 3:'Cooling'}, inplace=True)
    
        #add a new column 'total' that is the sum of the heat and cool
        df_tot['Total_consumption'] = df_tot['value_heat'] + df_tot['value_cool']
        
        #sort by total consumptions from min to max and take the top 5 results
        top_nvalues_tot = df_tot.sort_values(by = 'Total_consumption')
       
        'export step'
        
        #export xlsx files in an output folder
        os.chdir(base_folder)
        
        #create a folder to store the outputs
        dir_csv = 'csv_outputs'
        
        if not os.path.exists(dir_csv):
            os.makedirs(dir_csv)
            print("Directory '% s' created" % dir_csv)
        else:
            print("Directory '% s' already exists" % dir_csv)
    
        #change the current directory
        os.chdir(dir_csv)
        
        
        df_tot.to_csv('results_summary.csv')  
        top_nvalues_H.to_csv('top_nvalues_H.csv')
        top_nvalues_tot.to_csv('top_nvalues_total.csv')
       
    #return to the current dir
    os.chdir(base_folder)
    
    'comparison step'
    

    #read the old thesis results and create a  df
    old = pd.read_excel('OLD_total.xlsx', index_col='ID_code')
    old = old.round(2)
    
    #clean the new df with all results and leave only total consumptions
    os.chdir('csv_outputs')
    new = pd.read_csv('results_summary.csv')
    new = new.drop(['Unnamed: 0','value_heat','Heating','value_cool'], axis=1)
    #change column names
    new = new.set_index('Cooling')
    new = new.rename_axis('ID_code', axis='index')
    

    
    new_perc = calculate_percentage_diff(new, col_name='Total_consumption')

    # Now join the two df old and new
    final_df = old.join(new_perc)
    final_df.rename(columns={'En. Totale': 'tot_en(v8.9)', 'Diff. En. Tot. %': 'Diff%', 'Total_consumption': 'tot_en(v22.2)', 'Percentage_diff': 'newDiff%'}, inplace=True)

    
    
    #add a new column to final_df with the distance from v8.9 to 22.2
    final_df['Delta_rel(v22.2-8.9)'] = round((final_df['tot_en(v22.2)'] - final_df['tot_en(v8.9)']) / final_df['tot_en(v8.9)'] *100, 2)
    
    final_df['rank_8.9'] =   final_df['tot_en(v8.9)'].rank(ascending=True)
    final_df['rank_22.2'] =   final_df['tot_en(v22.2)'].rank(ascending=True)
    final_df['rank_22.2-8.9'] = final_df['rank_22.2'] - final_df['rank_8.9'] # - è salito di posizione
    
    

    
    
    return df_sorted, df2_sorted, top_nvalues_H, top_nvalues_C, df_tot, top_nvalues_tot, final_df

    
if __name__  == "__main__" :
    results_heat, results_cool, top_nvalues_C, top_nvalues_H, df_tot, top_nvalues_tot, final_df = main()
    

    
  
    
   
