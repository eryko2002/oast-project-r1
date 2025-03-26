import numpy as np
import csv
import json
import pandas as pd
import os
import random

base_path=f'{os.path.join(os.getcwd(),"input_net4")}'
demand_max_path_csv = os.path.join(base_path, "Demand_MaxPath_Volume.csv")

demand_volume=dict()
population = list()

num_chromosomes = 10  # Liczba chromosomów w populacji
num_demands = 6       # Liczba żądań d 
max_paths = 3         # Maksymalna liczba ścieżek Pp


def read_demand_volume():
    df = pd.read_csv(f'{demand_max_path_csv}')
    # Konwersja danych na słownik
    demand_volume = pd.Series(df.Volume.values, index=df.Demand).to_dict() 
    return demand_volume 

demand_volume=read_demand_volume()

def generate_chromosome(demand_volume, num_demands, max_paths):
    # Inicjalizacja pustej macierzy chromosomu
    chromosome = np.zeros((max_paths, num_demands), dtype=int)

    # Generowanie wartości dla każdej kolumny (dla każdego żądania)
    for demand_idx, demand in demand_volume.items():
        # Generowanie losowych wartości, które sumują się do demand_volume[demand_idx]
        remaining_value = demand
        for path_idx in range(max_paths - 1):
            chromosome[path_idx, demand_idx - 1] = random.randint(0, remaining_value)
            remaining_value -= chromosome[path_idx, demand_idx - 1]
        
        # Pozostała wartość trafia do ostatniej komórki w kolumnie
        chromosome[max_paths - 1, demand_idx - 1] = remaining_value

    return np.array(chromosome).T

def generate_population(num_chromosomes, demand_volume, num_demands, max_paths):
    population = []
    
    for _ in range(num_chromosomes):
        # Generowanie każdego chromosomu
        chromosome = generate_chromosome(demand_volume, num_demands, max_paths)
        population.append(chromosome)
    
    return population

def save_population_to_json(population, filename="chromosomes.json"):
    # Create a dictionary with keys as "Chromosome <nr>"
    population_dict = {
        f"Chromosome {i+1}": chromosome.tolist() 
        for i, chromosome in enumerate(population)
    }
    
    with open(f'{base_path}/{filename}', 'w') as json_file:
        json.dump(population_dict, json_file, indent=4)


# Generowanie populacji
population = generate_population(num_chromosomes=num_chromosomes, demand_volume=demand_volume, num_demands=num_demands, max_paths=max_paths)

# Zapis tablicy przepływów każdego chromosomu do pliku JSON
save_population_to_json(population)
