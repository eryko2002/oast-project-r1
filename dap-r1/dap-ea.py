import numpy as np
import json
from read_config_net4 import *
from generate_population import num_chromosomes

# Funkcja do obliczania wartości celu
def calculate_objective_value(demandPath_flow, demand_max_path, demand_volume, demand_path_links, link_capacity):
    # Inicjalizacja zmiennych
    link_load = {e: 0 for e in link_capacity}  # Słownik do przechowywania obciążenia dla każdego linku
    
    # Obliczanie obciążenia linków na podstawie demandPath_flow
    for d in demand_max_path:  # Teraz iterujemy po kluczach w słowniku demand_maxPath (to są ID żądań)
        for p in range(demand_max_path[d]):  # d to klucz, czyli numer żądania
            for e in demand_path_links[d][p]:  # Zbieramy ścieżki dla danego żądania
                # Tutaj zamiast listy zindeksowanej (d-1) używamy numpy ndarray
                link_load[e] += demandPath_flow[d-1, p]  # Indeksowanie ndarray, czyli używamy demandPath_flow[d-1, p]
    
    # Obliczanie przeciążenia linków (link_load - link_capacity)
    overloads = {e: max(0, link_load[e] - link_capacity[e]) for e in link_load}
    
    # Maksymalne przeciążenie
    max_link_overload = max(overloads.values())
    
    return max_link_overload, demandPath_flow


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

def main_model():
    #obliczamy wartość funkcji celu dla wzorca:
    demandPath_flow=load_flow_data()
    z_value,demandPath_flow = calculate_objective_value(demandPath_flow, demand_max_path, demand_volume, demand_path_links, link_capacity)
    print(f'Optimal solution from CPLEX: z= {z_value}')
    print(f'Flow table from CPLEX: \n{demandPath_flow.T}')

def main_candidate(candidate_number):
    demandPath_flow=chromosomes_data[f'Chromosome {candidate_number}']
    z_value,demandPath_flow = calculate_objective_value(demandPath_flow, demand_max_path, demand_volume, demand_path_links, link_capacity)
    print(f'Objective function for Chromosom {candidate_number}: z= {z_value}')
    print(f'Flow table for Chromosom {candidate_number}:\n{demandPath_flow.T}')

if __name__=="__main__":
    for candidate_number in range(num_chromosomes):
        print('========================================================')
        main_candidate(candidate_number=candidate_number+1)

