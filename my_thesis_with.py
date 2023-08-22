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

enplus_vers = '(v22.2)'  #change the number

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


"#############################################################################"
"##                              STYLER SECTION                             ##"
"#############################################################################"


def color_negative_red(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """
    color = 'red' if val < 0 else 'black'
    return 'color: %s' % color

#df.style.apply(color_negative_red)








"###############################################################################"
"###                                 Main                                    ###"
"###############################################################################"

def main(run_files=False, add_output=None, collect_kpi=False):
    
    df_AH = None
    df_AC = None
    final_df = None    
    
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
    if run_files:
        
        #set the iddfile path 
        iddfile = iddfile = os.path.join(base_folder, 'Energy+.idd')
        
        os.chdir(r'#enplus_models')
        
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
            
            os.chdir(base_folder)
        

    '''
    Create second list (eso)
    ''' 
    #Create a list of all .eso files generated with the Run_idf function    
    list_ESOs_found = search_extensions(base_folder, extension_file = '.eso') 
    
    
    '''
    KPI section
    ''' 
    if collect_kpi:
        
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
        
        # Export df in an output folder  
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
    
    #read the old thesis results and create a  df
    old = pd.read_excel('OLD_total.xlsx', index_col='ID_code')
    # redo the diff %
    old = old.drop('diff%_AH(v8.9)', axis=1)
    old = old.drop('diff%_AT(v8.9)', axis=1)
    old2 = calculate_percentage_diff(old, 'AH(v8.9)')
    old2 = calculate_percentage_diff(old2, 'AT(v8.9)')
    
    
    
    #clean the new df with all results and leave only total consumptions
    os.chdir('csv_outputs')
    new_H = pd.read_csv(f'AH{enplus_vers}.csv', index_col='ID_code')
    new_T = pd.read_csv(f'AT{enplus_vers}.csv', index_col='ID_code')
    # Create a df with 2 columns
    new_HT = new_H.join(new_T)
    # Add the column diff % on the right of the selected column
    new_HT_diff = calculate_percentage_diff(new_HT, col_name='AH'+ enplus_vers)
    new_HT_diff = calculate_percentage_diff(new_HT_diff, col_name='AT'+ enplus_vers)

    # Now create a big df with all
    final_df = old2.join(new_HT_diff)

     
    #add a new column to final_df with the delta from v8.9 to 22.2
    #Differenza percentuale = [(Nuovo valore - Vecchio valore) / Vecchio valore] * 100 (la ref è vecchio val)
    final_df['Delta(v22.2-8.9)'] = final_df['AT(v22.2)'] - final_df['AT(v8.9)']
    final_df['Delta_%_(v22.2-8.9)'] = round((final_df['Delta(v22.2-8.9)'])/ final_df['AT(v8.9)'] *100, 2)    # Calculate the %diff
    # Create ranking columns
    final_df['rank_8.9'] =   final_df['AT(v8.9)'].rank(ascending=True)
    final_df['rank_22.2'] =   final_df['AT(v22.2)'].rank(ascending=True)
    final_df['delta_rank_22.2-8.9'] = final_df['rank_22.2'] - final_df['rank_8.9']
  
    
  
    
    ' Ranking solutions'    
    
    'Old rankings'
    df_topAH_old  = final_df[['AH(v8.9)','diff%_AH(v8.9)']]
    df_topAH_old = df_topAH_old.sort_values(by = 'diff%_AH(v8.9)', ascending = True)
    # Take the top 'n' values
    n = 5
    df_topAH_old = df_topAH_old.head(n)
 
    df_topAT_old  = final_df[['AT(v8.9)','diff%_AT(v8.9)']]
    df_topAT_old = df_topAT_old.sort_values(by = 'diff%_AT(v8.9)', ascending = True)
    # Take the top 'n' values
    n = 5
    df_topAT_old = df_topAT_old.head(n)    
    
    
    'New rankings'
    df_topAH  = final_df[['AH(v22.2)','diff%_AH(v22.2)']]
    df_topAH = df_topAH.sort_values(by = 'diff%_AH(v22.2)', ascending = True)
    # Take the top 'n' values
    n = 5
    df_topAH = df_topAH.head(n)
 
    df_topAT  = final_df[['AT(v22.2)','diff%_AT(v22.2)']]
    df_topAT = df_topAT.sort_values(by = 'diff%_AT(v22.2)', ascending = True)
    # Take the top 'n' values
    n = 5
    df_topAT = df_topAT.head(n)   



    # Compare the rankings
    # Set the index as a column
    df_topAH_old_reset = df_topAH_old.reset_index().rename(columns={'ID_code': 'ID_code(v8.9)'})
    df_topAH_reset = df_topAH.reset_index().rename(columns={'ID_code': 'ID_code(v22.2)'})
    
    df_topAT_old_reset = df_topAT_old.reset_index().rename(columns={'ID_code': 'ID_code(v8.9)'})
    df_topAT_reset = df_topAT.reset_index().rename(columns={'ID_code': 'ID_code(v22.2)'})

    # Join the two dfs and see the difference
    df_topAH_comp = df_topAH_old_reset.join(df_topAH_reset).round(2)
    df_topAT_comp = df_topAT_old_reset.join(df_topAT_reset).round(2)
    
    
    ' Create the .html'
 
    # Define the CSS styles for index and column names highlighting
    header_style = [
        {
            "selector": "th",
            "props": [("font-weight", "bold"), ("background-color", "#b2b2b2")]
        },
        {
            "selector": "th.index_name",
            "props": [("font-weight", "bold"), ("background-color", "#b2b2b2")]
        }
    ]
  
    styled_df = final_df.style.set_caption("En+ comparison table", )
    
    styled_df = styled_df.background_gradient(subset=['Delta_%_(v22.2-8.9)'], cmap='RdYlGn')
    # Apply precision to specific columns 
    styled_df = styled_df.format({'AH(v8.9)': '{:.1f}',
                                  'diff%_AH(v8.9)': '{:.2f}',
                                  'AT(v8.9)': '{:.1f}',
                                  'diff%_AT(v8.9)': '{:.2f}',
                                  'AH(v22.2)': '{:.1f}',
                                  'diff%_AH(v22.2)': '{:.2f}',
                                  'AT(v22.2)': '{:.1f}',
                                  'diff%_AT(v22.2)': '{:.2f}',
                                  'Delta(v22.2-8.9)': '{:.1f}',
                                  'Delta_%_(v22.2-8.9)': '{:.2f}',
                                  'rank_8.9': '{:.0f}',
                                  'rank_22.2': '{:.0f}',
                                  'delta_rank_22.2-8.9': '{:.0f}'})
   
    # Apply the header styles to the DataFrame
    styled_df = styled_df.set_table_styles(header_style)
    
    os.chdir(base_folder)      
    #create a folder to store the outputs
    dir_images = 'images_outputs'   
    if not os.path.exists(dir_images):
        os.makedirs(dir_images)
        print("Directory '% s' created" % dir_images)
    else:
        print("Directory '% s' already exists" % dir_images)
    #change the current directory
    os.chdir(dir_images)      
      
    # Convert the styled DataFrame to HTML representation
    html = styled_df.to_html()
    
    # Save the HTML representation to a file
    with open("styled_df.html", "w") as fp:
        fp.write(html)
        
        
        
    ' Save dataframes as images'
    
    dfi.export(df_topAH_comp, 'df_topAH_comp.png')
    dfi.export(df_topAT_comp, 'df_topAT_comp.png')
    
    
    'final df as an heatmap'
    
    # Transpose the df to exchange x and y
    transposed_df = final_df.T
    # Trim the df with only the rows containing the distance %. Function FILTER
    transposed_df = transposed_df.filter(like='Delta_%_(v22.2-8.9)', axis=0)
    # Set the size of the heatmap using figsize
    fig, ax = plt.subplots(figsize=(150, 2))  # Adjust the width and height as needed   
    # Create a diverging color palette 
    color_palette = sns.color_palette("coolwarm", as_cmap=True)
    # Plot a heatmap with annotation
    sns.heatmap(transposed_df,  
                cmap=color_palette,
                center = 0,
                annot=True,
                fmt='',
                ax=ax,
                linewidths=1.5,
                annot_kws={'rotation': 90})
    # Set labels and title
    ax.set_title('Distance % Heatmap En+ 22.2-8.9 ', weight='bold')
    # Save the heatmap as an image in the specified folder
    output_filename = 'Distance % Heatmap En+ 22.2-8.9.png'
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    
    # Display the heatmap
    plt.show()


    return df_AH, df_AC, final_df, df_topAH_comp, df_topAT_comp

    
if __name__  == "__main__" :
    df_AH, df_AC, final_df, df_topAH_comp, df_topAT_comp = main()
    

    
  
    
   
