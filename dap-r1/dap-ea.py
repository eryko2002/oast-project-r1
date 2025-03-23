import numpy as np
import json


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