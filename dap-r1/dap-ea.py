import numpy as np
import json
from input_data_ea import *


def roulette_wheel_selection(population, probabilities):
    # Normalizowanie prawdopodobieństw (suma wszystkich prawdopodobieństw powinna wynosić 1)
    total_probability = sum(probabilities)
    normalized_probabilities = [prob / total_probability for prob in probabilities]
    
    # Akumulowanie prawdopodobieństw
    cumulative_probabilities = np.cumsum(normalized_probabilities)
    
     # Losowanie wartości z przedziału [0, 1]
    random_value = np.random.random()  # Losujemy liczbę zmiennoprzecinkową z przedziału [0, 1]
    
    # Znajdujemy chromosom, który pasuje do wylosowanej wartości
    for i, cumulative_probability in enumerate(cumulative_probabilities):
        if random_value <= cumulative_probability:
            return i, population[i]  # Zwracamy indeks (numer) i chromosom


# Funkcja celu
def calculate_z(chromosome):
    link_load = {link: 0 for link in linkModuleCount}  # Inicjalizowanie obciążenia linków
    z = 0  # Zmienna celu, maksymalne przeciążenie

    # Przechodzimy przez każdy wiersz w chromosomie (każde żądanie)
    for d in range(chromosome.shape[0]):
        # Przechodzimy przez każdą ścieżkę dla danego żądania
        for p in range(chromosome.shape[1]):
            path_id = chromosome[d, p]  # ID ścieżki dla danego żądania
            if path_id > 0 and path_id <= len(demand_paths[d + 1]):
                # Sumujemy obciążenie linków
                for link in demand_paths[d + 1][path_id - 1]:
                    link_load[link] += demand_volume[d + 1]

    # Sprawdzamy przeciążenie linków
    for link, load in link_load.items():
        if load > linkModuleCount[link]:
            z = max(z, load - linkModuleCount[link])  # Ustalamy maksymalne przeciążenie
    
    return z

#Wczytujemy dane wejściowe dla sieci 4 węzłowej
linkModuleCount,demand_paths,demand_volume=read_json()[0],read_json()[1],read_json()[2]

#alokujemy przepływy dla konkretnego żądania oraz zadanej ścieżki:
allocate_DemandPathFlow_from_json()

#Wybieramy chromosom zgodnie z metodą ruletki na podstawie prawdopodobieństw chromosomów z populacji
selected_chromosome = roulette_wheel_selection(population, probabilities)
print("Wylosowany chromosom: Chromosom numer {}:\n{}".format(selected_chromosome[0],selected_chromosome[1]))

chromosome_genes= selected_chromosome[1]

# Obliczamy wartość funkcji celu dla danego chromosomu
z_value = calculate_z(chromosome_genes)
print("Wartość funkcji celu (z):", z_value)