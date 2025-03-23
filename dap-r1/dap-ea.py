import numpy as np
import json
from read_config_net4 import *

N = 10
K=1

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

def select_parents(population, fitness_values):
    # Odwracamy wartości funkcji celu, aby mniejsze wartości miały większe prawdopodobieństwo
    inverted_fitness = 1 / np.array(fitness_values)
    selection_probabilities = inverted_fitness / np.sum(inverted_fitness)
    sum_of_probabilities=np.sum(selection_probabilities)
    

    #print("Fitness_values:{}\n".format(fitness_values))
    #print("Inverted_fitness:{}\n".format(inverted_fitness))
    #print("Selection_probabilities:{}\n".format(selection_probabilities))
    #print("Sum of probabilities:{}\n".format(sum_of_probabilities))

    # Wybór dwóch rodziców na podstawie rozkładu prawdopodobieństwa
    parents_indices = np.random.choice(len(population), size=2, p=selection_probabilities)
    
    parent1 = population[parents_indices[0]].T
    parent2 = population[parents_indices[1]].T
    
    return parent1, parent2


# Funkcja główna (algorytm genetyczny)
def roulette_wheel_selection_algorithm():
    population = list(chromosomes_data.values())  # Wczytanie populacji z chromosomes_data
    parent1,parent2=None,None
    for generation in range(K):
        fitness_values = []
        
        # Obliczanie wartości fitness dla każdej macierzy (chromosomu)
        for chromosome in population:
            z_value, _ = calculate_objective_value(chromosome, demand_max_path, demand_volume, demand_path_links, link_capacity)
            fitness_values.append(z_value)
        
        parent1, parent2 = select_parents(population, fitness_values)
        print(f"Generation {generation + 1}: Selected parents")
        print(f"Parent 1:\n{parent1}")
        print(f"Parent 2:\n{parent2}")
        print("--------------------------------------------------------------------------------")

    
    return parent1,parent2


def crossover(parent1,parent2):
    crossover_point=np.random.randint(1,parent1.shape[1])
    offspring1=np.copy(parent1)
    offspring2=np.copy(parent2)
    offspring1[:,crossover_point:]=parent1[:,crossover_point:]
    offspring2[:,crossover_point:]=parent2[:,crossover_point:]

    # Zaznaczenie wartościami ujemnymi komórek rodziców, które są wykorzystywane w operacji krzyżowania
    marked_parent1 = np.copy(parent1)
    marked_parent2 = np.copy(parent2)
    
    # Oznaczenie zmienionych komórek dla rodzica 1 (które zmieniają się na podstawie rodzica 2)
    marked_parent1[:, crossover_point:] = -1  # Zmienione komórki w rodzicu 1
    # Oznaczenie zmienionych komórek dla rodzica 2 (które zmieniają się na podstawie rodzica 1)
    marked_parent2[:, crossover_point:] = -1  # Zmienione komórki w rodzicu 2
    
    return (offspring1, offspring2), (parent1,parent2),(marked_parent1, marked_parent2)

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
    #main_model()
    #print()
    #for candidate_number in range(N):
    #    print('========================================================')
    #    main_candidate(candidate_number=candidate_number+1)
    print("===========================SELECTION=====================================")
    parent1,parent2=roulette_wheel_selection_algorithm()
    print("===========================CROSSOVER=====================================")
    offspring,parents,marked_parents=crossover(parent1=parent1,parent2=parent2)

    # Wyświetlanie oryginalnych rodziców i zaznaczenie zmienionych komórek
    print("Parent 1 with marked changes (red):")
    print(marked_parents[0])
    print("Parent 2 with marked changes (red):")
    print(marked_parents[1])

    # Wyświetlanie potomków
    print("Offspring 1:")
    print(offspring[0])
    print("Offspring 2:")
    print(offspring[1])

