# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 11:44:29 2023

@author: andre
"""

import os

from my_thesis_with import df_kpi_in_esofile, plot_overlapping_line_charts, plot_overlapping_step_charts




"#############################################################################"
"##                         B2_R_L2_MW_E_0.6_1.0_TS2                        ##"
"#############################################################################"


# Set a zoom day of the year
zoom_day = "22-05-2009" # Friday


# Minimum difference of the comparison B2_R_L2_MW_E_0.6_1.0_TS2 8.5 and 8.7
save_path = r"C:\Users\andre\OneDrive\Lavoro\Week_1\Presentation\IDF_analizzati\B2_R_L2_MW_E_0.6_1.0_TS2"
# 8.5
eso_path1 = os.path.join(save_path, "B2_R_L2_MW_E_0.6_1.0_TS2(8.5)\B2_OFFICE MW_wwr0.6.idf.eso")
# 8.7
eso_path2 = os.path.join(save_path, r"B2_R_L2_MW_E_0.6_1.0_TS2(8.7)\B2_R_L2_MW_E_0.6_1.0_TS2.eso")





# Set the parameter name
parameter = "Surface Inside Face Solar Radiation Heat Gain Rate"

key_number = 319
df1 = df_kpi_in_esofile(eso_path1, key_number)
key_number = 320
df2 = df_kpi_in_esofile(eso_path2, key_number)

df_list = [df1,df2]

plot_overlapping_line_charts(df_list,
                              x_col="Date",
                              y_col="Value",
                              labels=["Solar Radiation Heat Gain Rate [W], g-Value=0.7 (v8.5)",
                                      "Solar Radiation Heat Gain Rate [W], g-Value=0.4 (v8.7)"],
                              x_label="Date",
                              y_label="Inside Face Solar Radiation Heat Gain Rate [W]",
                              title="Surface Inside Face Solar Radiation Heat Gain Rate [W]",
                              save_path= os.path.join(save_path, f"{parameter}.png"),
                              zoom_day= None,
                              fontsize = 22)

plot_overlapping_line_charts(df_list,
                              x_col="Date",
                              y_col="Value",
                              labels=["Solar Radiation Heat Gain Rate [W], g-Value=0.7 (v8.5)",
                                      "Solar Radiation Heat Gain Rate [W], g-Value=0.4 (v8.7)"],
                              x_label="Date",
                              y_label="Inside Face Solar Radiation Heat Gain Rate [W]",
                              title="Surface Inside Face Solar Radiation Heat Gain Rate [W]",
                              save_path= os.path.join(save_path, f"{parameter}_day.png"),
                              zoom_day= zoom_day,
                              fontsize = 22)



# Set the parameter name
parameter = "Zone Mean Air Temperature [C]"

key_number = 327
df1 = df_kpi_in_esofile(eso_path1, key_number)
key_number = 328
df2 = df_kpi_in_esofile(eso_path2, key_number)

df_list = [df1,df2]

plot_overlapping_line_charts(df_list,
                              x_col="Date",
                              y_col="Value",
                              labels=[f"{parameter}, livingroom (v8.5)",
                                      f"{parameter}, livingroom (v8.7)"],
                              x_label="Date",
                              y_label=f"{parameter}",
                              title=f"{parameter}",
                              save_path= os.path.join(save_path, f"{parameter}_year.png"),
                              zoom_day= None,
                              fontsize = 22)
# day
plot_overlapping_line_charts(df_list,
                              x_col="Date",
                              y_col="Value",
                              labels=[f"{parameter}, livingroom (v8.5)",
                                      f"{parameter}, livingroom (v8.7)"],
                              x_label="Date",
                              y_label=f"{parameter}",
                              title=f"{parameter}",
                              save_path= os.path.join(save_path, f"{parameter}_day.png"),
                              zoom_day= zoom_day,
                              fontsize = 22)

# Set the parameter name
parameter = "Zone Ideal Loads Zone Sensible Heating Rate [W]"
key_number = 605
df1 = df_kpi_in_esofile(eso_path1, key_number)
key_number = 606
df2 = df_kpi_in_esofile(eso_path2, key_number)
df_list = [df1,df2]

plot_overlapping_line_charts(df_list,
                              x_col="Date",
                              y_col="Value",
                              labels=[f"{parameter}, livingroom (v8.5)",
                                      f"{parameter}, livingroom (v8.7)"],
                              x_label="Date",
                              y_label=f"{parameter}",
                              title=f"{parameter}",
                              save_path= os.path.join(save_path, f"{parameter}_year.png"),
                              zoom_day= None,
                              fontsize = 22)
# day
plot_overlapping_line_charts(df_list,
                              x_col="Date",
                              y_col="Value",
                              labels=[f"{parameter}, livingroom (v8.5)",
                                      f"{parameter}, livingroom (v8.7)"],
                              x_label="Date",
                              y_label=f"{parameter}",
                              title=f"{parameter}",
                              save_path= os.path.join(save_path, f"{parameter}_day.png"),
                              zoom_day= zoom_day,
                              fontsize = 22)




# Set the parameter name
parameter = "RESID_COOLING_SCHEDULE [°C] !Hourly"

key_number = 709
df3 = df_kpi_in_esofile(eso_path1, key_number)

df_list = [df3]

plot_overlapping_step_charts(df_list,
                              x_col="Date",
                              y_col="Value",
                              labels=[f"{parameter} (v8.5)",
                                      f"{parameter} (v8.7)"],
                              x_label="Date",
                              y_label=f"{parameter}",
                              title=f"{parameter}",
                              save_path= os.path.join(save_path, f"{parameter}_day.png"),
                              zoom_day= zoom_day,
                              fontsize = 22)

'''
1.15.5.2.6 Site Daylighting Model Sky Clearness []
Clearness of sky. One of the factors used to determine sky type and luminous efficacy of solar radiation
(see EnergyPlus Engineering Document). Sky Clearness close to 1.0 corresponds to an overcast sky. Sky
Clearness > 6 is a clear sky

'''



"#############################################################################"
"##                         B2_R_L1_ST_W_0.2_2.3_TS2                        ##"
"#############################################################################"


# Set a zoom day of the year
zoom_day = "22-05-2009" # Friday


# Minimum difference of the comparison B2_R_L2_MW_E_0.6_1.0_TS2 8.5 and 8.7
save_path = r"C:\Users\andre\OneDrive\Lavoro\Week_1\Presentation\IDF_analizzati\B2_R_L1_ST_W_0.2_2.3_TS2"
# 8.5
eso_path1 = os.path.join(save_path, "B2_R_L1_ST_W_0.2_2.3_TS2(8.7)\B2_R_L1_ST_W_0.2_2.3_TS2.eso")
# 8.7
eso_path2 = os.path.join(save_path, r"B2_R_L1_ST_W_0.2_2.3_TS2(22.2)\eplusout.eso")


# Set the parameter name
parameter = "Surface Window Transmitted Solar Radiation Energy [J]"
key_number = 243
df1 = df_kpi_in_esofile(eso_path1, key_number)
key_number = 402
df2 = df_kpi_in_esofile(eso_path2, key_number)
df_list = [df1]

plot_overlapping_line_charts(df_list,
                              x_col="Date",
                              y_col="Value",
                              labels=[f"{parameter}, livingroom (v8.5)",
                                      f"{parameter}, livingroom (v8.7)"],
                              x_label="Date",
                              y_label=f"{parameter}",
                              title=f"{parameter}",
                              save_path= os.path.join(save_path, f"{parameter}_year.png"),
                              zoom_day= None,
                              fontsize = 22)
# day
plot_overlapping_line_charts(df_list,
                              x_col="Date",
                              y_col="Value",
                              labels=[f"{parameter}, livingroom (v8.5)",
                                      f"{parameter}, livingroom (v8.7)"],
                              x_label="Date",
                              y_label=f"{parameter}",
                              title=f"{parameter}",
                              save_path= os.path.join(save_path, f"{parameter}_day.png"),
                              zoom_day= zoom_day,
                              fontsize = 22)


















