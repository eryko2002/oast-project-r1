import os
import json
import ast
import pandas as pd
import numpy as np

# Ścieżka do folderu roboczego
base_path = os.path.join(os.getcwd(), "input_net4")
chromosomes_matrix_path = os.path.join(base_path, "chromosomes.json")
demand_path_links_csv = os.path.join(base_path, "DemandPath_links.csv")
link_capacity_csv = os.path.join(base_path, "LinkCapacity.csv")
demand_max_path_csv = os.path.join(base_path, "Demand_MaxPath_Volume.csv")

def load_chromosomes_from_json(file_path):
    """
    Funkcja odczytuje dane chromosomów z pliku JSON i zapisuje je w słowniku.
    Kluczem jest "Chromosome <nr>", a wartością jest macierz.

    :param file_path: Ścieżka do pliku JSON
    :return: Słownik, gdzie kluczem jest "Chromosome <nr>", a wartością macierz (tabela przepływów))
    """
    with open(file_path, 'r') as file:
        data = json.load(file)

    chromosomes = {}
    for chrom_key, chrom_matrix in data.items():
        chrom_num = chrom_key.split()[-1]  # Odcinamy numer chromosomu
        chromosomes[f"Chromosome {chrom_num}"] = np.array(chrom_matrix)

    return chromosomes

def load_demand_path_links(file_path):
    """
    Funkcja odczytuje plik CSV z danymi DemandPath_links, przekształcając 'Paths' na listy.
    
    :param file_path: Ścieżka do pliku CSV
    :return: Słownik, gdzie kluczem jest Demand, a wartością lista ścieżek
    """
    df_paths = pd.read_csv(file_path)
    df_paths['Paths'] = df_paths['Paths'].apply(ast.literal_eval)
    
    demand_path_links = {}
    for _, row in df_paths.iterrows():
        demand = row['Demand']
        path = row['Paths']
        if demand not in demand_path_links:
            demand_path_links[demand] = []
        demand_path_links[demand].append(path)
    
    return demand_path_links

def load_link_capacity(file_path):
    """
    Funkcja odczytuje plik CSV z danymi LinkCapacity i zwraca słownik z linkami i ich pojemnościami.
    
    :param file_path: Ścieżka do pliku CSV
    :return: Słownik, gdzie kluczem jest Link ID, a wartością pojemność linku
    """
    df_link_capacity = pd.read_csv(file_path)
    return dict(zip(df_link_capacity['Link'], df_link_capacity['LinkCapacity']))

def load_demand_max_path_volume(file_path):
    """
    Funkcja odczytuje plik CSV z danymi Demand_MaxPath_Volume i zwraca słowniki z odpowiednimi wartościami.
    
    :param file_path: Ścieżka do pliku CSV
    :return: Słowniki 'maxPath' i 'volume' dla każdego zapotrzebowania
    """
    df_demand = pd.read_csv(file_path)
    demand_max_path = dict(zip(df_demand['Demand'], df_demand['MaxPath']))
    demand_volume = dict(zip(df_demand['Demand'], df_demand['Volume']))
    return demand_max_path, demand_volume

def load_flow_data():
    """
    Funkcja zwraca przykładową tabelę przepływów obliczoną przez CPLEX.
    
    :return: Macierz przepływów
    """
    return np.array([
        [19.5, 3.5, 0],
        [24, 0, 0],
        [15, 0, 0],
        [2, 0, 0],
        [20.5, 2.5, 0],
        [17, 0, 0]
    ])

chromosomes_data = load_chromosomes_from_json(chromosomes_matrix_path)
demand_path_links = load_demand_path_links(demand_path_links_csv)
link_capacity = load_link_capacity(link_capacity_csv)
demand_max_path, demand_volume = load_demand_max_path_volume(demand_max_path_csv)
demandPath_flow = load_flow_data()