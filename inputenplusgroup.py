# -*- coding: utf-8 -*-
"""
Created on Sun Oct  8 23:30:40 2023

@author: andre
"""
import os

# Percorso del tuo file di testo di input
input_file_path = r"C:\Users\andre\Desktop\Thesis_Python\enplus_models\Models_8.7_fixed\.idf.txt"

# Inizializza il contatore
count = 0
# Percorso del file EPW per "L2"
epw_l2 = r"C:\Users\andre\Desktop\Thesis_Python\weather_files\ITA_Bolzano.160200_IGDG.epw"

# Percorso del file EPW per altre condizioni
epw_other = r"C:\Users\andre\Desktop\Thesis_Python\weather_files\ITA_Palermo.164050_IWEC.epw"

# Leggi il contenuto del file di input e crea un nuovo file di output
with open(input_file_path, 'r') as input_file, open('output.txt', 'w') as output_file:
    for line in input_file:
        # Incrementa il contatore
        count += 1   
        
        # Rimuovi l'estensione ".idf" dalla riga
        path_without_filename = line.strip().replace(".idf", "")
        
        # Verifica se la linea contiene "L2" e aggiungi il percorso EPW appropriato
        if "L2" in line:
            line = line.strip() + "," + epw_l2 + "," + path_without_filename + f",      {count} \n"
        else:
            line = line.strip() + "," + epw_other + "," + path_without_filename + f",      {count} \n"
        # Scrivi la linea nel file di output
        output_file.write(line)

print("Operazione completata. Il risultato è stato scritto in 'output.txt'.")
