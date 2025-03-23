import numpy as np
import csv
import json
import pandas as pd
import os
import random

base_path=f'{os.path.join(os.getcwd(),"input_net4")}'

demand_volume=dict()
population = list()

num_chromosomes = 10  # Liczba chromosomów w populacji
num_demands = 6       # Liczba żądań (kolumn)
max_paths = 3         # Maksymalna liczba ścieżek (wierszy)



def read_demand_volume():
    df = pd.read_csv(f'{base_path}/demand_volume.csv')
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

    return chromosome

def generate_population(num_chromosomes, demand_volume, num_demands, max_paths):
    population = []
    
    for _ in range(num_chromosomes):
        # Generowanie każdego chromosomu
        chromosome = generate_chromosome(demand_volume, num_demands, max_paths)
        population.append(chromosome)
    
    return population


# Generowanie populacji
population = generate_population(10, demand_volume, num_demands=6, max_paths=3)

# Wyświetlenie wyników
for idx, chromosom in enumerate(population):
    print(f"Chromosom {idx + 1}:")
    print(chromosom)
    print()