import numpy as np
import matplotlib.pyplot as plt
import time
from read_config_net4 import *
from generate_population import num_chromosomes

# Domyślne parametry algorytmu EA

N = num_chromosomes  # Rozmiar populacji
K = 100  # Maksymalna liczba pokoleń
MUTATION_PROBABILITY = 0.05 # prawdopodobieństwo mutacji
MUTATION_TYPE = 'bit_flip'  # typ mutacji, do wyboru : ['bit_flip', 'random_reset']
TERMINATION_THRESHOLD = 0.05  # procentowa różnica między przewidywanym rozwiązaniem a optymalnym rozwiązaniem cplex
SELECTION_PRESSURE = 2  # wartość parametru dla metody selekcji rodziców : rank

# Deklaracja zmiennych przechowujących wyniki EA
best_solutions = []
convergence_data = []
computation_times = []


def calculate_objective_value(demandPath_flow, demand_max_path, demand_volume, demand_path_links, link_capacity):
    '''
    demandPath_flow = flow table <=> demandPath_flow[d,p] = x[d,p]
    demand_max_path = P[p]
    demand_volume = h[d]
    demand_path_links = P[d,p]
    link_capacity = C[e]
    '''

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

def should_terminate(best_z, optimal_z, threshold):
    """Zwraca True jeśli algorytm EA powinien zakończyć działanie w momencie osiągnięcia obiecującego przewidywanego rozwiązania."""
    if best_z <= optimal_z * (1 + threshold):
        print(f"Terminating: Reached {best_z} (optimal: {optimal_z})")
        return True
    return False

def select_parents_rank(population, fitness_values):
    ranked_indices = np.argsort(fitness_values)
    ranks = np.arange(1, len(population)+1)
    probabilities = (SELECTION_PRESSURE - 2*(SELECTION_PRESSURE-1)*(ranks-1)/(len(population)-1))
    probabilities = probabilities / np.sum(probabilities)
    
    parents_indices = np.random.choice(len(population), size=2, p=probabilities)
    return population[parents_indices[0]].T, population[parents_indices[1]].T

def select_parents_roulette(population, fitness_values):
    inverted_fitness = 1 / np.array(fitness_values)
    selection_probabilities = inverted_fitness / np.sum(inverted_fitness)
    parents_indices = np.random.choice(len(population), size=2, p=selection_probabilities)
    return population[parents_indices[0]].T, population[parents_indices[1]].T

def crossover(parent1, parent2):
    num_columns = parent1.shape[1]
    
    # Wybieramy losowe kolumny do zamiany (np. 2 kolumny)
    #num_cols_to_swap = np.random.randint(1, num_columns)  # Można ustawić stałą liczbę kolumn

    #w operacji krzyżowania wykorzystywana jest 1 kolumna z każdego z 2 wybranych rodziców, a następnie jest ona wymieniana między potomkami metodą 'na krzyż'
    num_cols_to_swap = 1
    cols_to_swap = np.random.choice(num_columns, num_cols_to_swap, replace=False)
    
    offspring1 = np.copy(parent1)
    offspring2 = np.copy(parent2)

    # Zamiana wybranych kolumn
    for col in cols_to_swap:
        offspring1[:, col] = parent2[:, col]
        offspring2[:, col] = parent1[:, col]

    # Zaznaczenie ujemnymi wartościami zmienionych kolumn w rodzicach w celu pokazania które kolumny wykorzystano w procesie krzyżowania
    marked_parent1 = np.copy(parent1)
    marked_parent2 = np.copy(parent2)
    marked_parent1[:, cols_to_swap] = -1
    marked_parent2[:, cols_to_swap] = -1
    
    return offspring1,offspring2,parent1,parent2,marked_parent1,marked_parent2

def mutate(flow_table, demand_volume, mutation_type='bit_flip', mutation_prob=0.4):
    if np.random.rand() > mutation_prob:
        return flow_table  # bez mutacji

    num_columns = flow_table.shape[1]
    num_rows = flow_table.shape[0]

    col_idx = np.random.randint(0, num_columns)
    row_idx = np.random.randint(0, num_rows)

    if mutation_type == 'bit_flip':
        # Zmieniamy wartość na przeciwną, zakładając binarne geny (0/1),
        # ale że mamy liczby całkowite, możemy przyjąć uproszczony model np. zera i jedynki:
        flow_table[row_idx, col_idx] = 1 if flow_table[row_idx, col_idx] == 0 else 0

    elif mutation_type == 'random_reset':
        flow_table[row_idx, col_idx] = np.random.randint(0, demand_volume[col_idx + 1])

    # Utrzymujemy zgodność sumy kolumny z zapotrzebowaniem
    flow_table = fix_column_sum(flow_table, row_idx, col_idx, demand_volume)

    return flow_table

def fix_column_sum(flow_table, row_idx, col_idx, demand_volume):
    num_rows = flow_table.shape[0]
    demand_volume_h_d = demand_volume[col_idx + 1]
    mutated_sum_h_d = np.sum(flow_table[:, col_idx])
    delta = int(mutated_sum_h_d - demand_volume_h_d)
    #print(f"Starting Delta: {delta}")
    iteration=0
    #print("Mutated, before fix function:\n{}".format(flow_table))
    while delta!=0:
        # Indeksy komórek w danej kolumnie poza indeksem komórki która była mutowana
        indices = np.delete(np.arange(num_rows), row_idx)
        np.random.shuffle(indices)

        for idx in indices:
            iteration+=1
            if delta > 0 and flow_table[idx, col_idx]>0:
                # Zmniejszamy wartość w komórce, jeśli delta jest dodatnia
                allocate_delta = np.random.randint(1, delta + 1)
                if flow_table[idx, col_idx]-allocate_delta>=0: 
                    flow_table[idx, col_idx] -= allocate_delta 
                    delta -= allocate_delta
                    #print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
                    #print(f'Iteration number: {iteration}')
                    #print(f"Current Delta: {delta}")
                    #print("Current Flow_table \n{}".format(flow_table))
                    #print()
            elif delta < 0 and flow_table[idx, col_idx]>0:
                # Zwiększamy wartość w komórce, jeśli delta jest ujemna
                allocate_delta = np.random.randint(1, abs(delta) + 1)
                if flow_table[idx, col_idx]-allocate_delta>=0:
                    flow_table[idx, col_idx] += allocate_delta
                    delta += allocate_delta
                    #print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
                    #print(f'Iteration number: {iteration}')
                    #print(f"Current Delta: {delta}")
                    #print("Current Flow_table \n{}".format(flow_table))
                    #print()

    return flow_table


def plot_convergence(convergence_data, optimal_z, title):
    plt.figure(figsize=(10, 6))
    for i, (conv, label) in enumerate(convergence_data):
        plt.plot(conv, label=label)
    plt.axhline(y=optimal_z, color='r', linestyle='--', label='Optimal Solution')
    plt.xlabel('Generation')
    plt.ylabel('Best Z Value')
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.show()


def run_ea(population_size=N, max_generations=K, mutation_prob=MUTATION_PROBABILITY, 
           mutation_type=MUTATION_TYPE, selection_method='roulette'):

    start_time = time.time()
    
    # Incjalizacja populacji
    population = list(chromosomes_data.values())
    
    # Oblicz optymalną wartość funkcji celu dla sieci 4-węzłowej na bazie tablicy przepływu dostarczonej przez CPLEX
    optimal_flow = load_flow_data()
    optimal_z, _ = calculate_objective_value(optimal_flow, demand_max_path, 
                                           demand_volume, demand_path_links, 
                                           link_capacity)
    
    best_z = float('inf')
    best_solution = None
    convergence = []
    
    for generation_index in range(max_generations):
        # Obliczanie wartości funkcji celu dla wszystkich chromosomów z populacji 
        fitness_values = []
        for chromosome in population:
            z_value, _ = calculate_objective_value(chromosome, demand_max_path,
                                                   demand_volume, demand_path_links,
                                                   link_capacity)
            fitness_values.append(z_value)
        
        # Track best solution
        current_best_idx = np.argmin(fitness_values)
        current_best_z = fitness_values[current_best_idx]
        if current_best_z < best_z:
            best_z = current_best_z
            best_solution = population[current_best_idx]
        
        convergence.append(best_z)

        # funkcja sprawdzająca czy przewidywane rozwiązanie jest wystarczająco blisko optymalnego rozwiązania dostarczonego przez CPLEX
        if should_terminate(best_z, optimal_z, TERMINATION_THRESHOLD):
            break
        
        # Wywołąnie funkcji selekcji rodziców w zależności od podanego typu ['roulette','rank']
        if selection_method == 'roulette':
            parent1, parent2 = select_parents_roulette(population, fitness_values)
        elif selection_method == 'rank':
            parent1, parent2 = select_parents_rank(population, fitness_values)
        else:
            raise ValueError("Unknown selection method")
        
        # Wywołanie funkcji krzyżowania rodziców 
        offspring1, offspring2 = crossover(parent1.T, parent2.T)[:2]
        
        # Wywołanie funkcji mutacji 
        offspring1 = mutate(offspring1, demand_volume, mutation_type, mutation_prob)
        offspring2 = mutate(offspring2, demand_volume, mutation_type, mutation_prob)
        
        # Wyznaczenie wartości funkcji celu dla utworzonych potomków
        z1, _ = calculate_objective_value(offspring1, demand_max_path, demand_volume,
                                         demand_path_links, link_capacity)
        z2, _ = calculate_objective_value(offspring2, demand_max_path, demand_volume,
                                         demand_path_links, link_capacity)
        
        worst_indices = np.argsort(fitness_values)[-2:]
        population[worst_indices[0]] = offspring1
        population[worst_indices[1]] = offspring2
    
    end_time = time.time()
    
    return {
        'best_solution': best_solution,
        'best_z': best_z,
        'optimal_z': optimal_z,
        'convergence': convergence,
        'time': end_time - start_time,
        'generations': generation_index + 1
    }

def main():
    # Test different configurations
    configs = [
        {'mutation_type': 'bit_flip', 'selection_method': 'roulette', 'label': 'Bit Flip + Roulette'},
        {'mutation_type': 'random_reset', 'selection_method': 'roulette', 'label': 'Random Reset + Roulette'},
        {'mutation_type': 'bit_flip', 'selection_method': 'rank', 'label': 'Bit Flip + Rank'},
        {'mutation_type': 'random_reset', 'selection_method': 'rank', 'label': 'Random Reset + Rank'},
    ]
    
    optimal_flow = load_flow_data()
    optimal_z, _ = calculate_objective_value(optimal_flow, demand_max_path, 
                                           demand_volume, demand_path_links, 
                                           link_capacity)
    
    for config in configs:
        print(f"\nRunning configuration: {config['label']}")
        result = run_ea(mutation_type=config['mutation_type'], 
                       selection_method=config['selection_method'])
        
        convergence_data.append((result['convergence'], config['label']))
        best_solutions.append({
            'config': config['label'],
            'solution': result['best_solution'],
            'z_value': result['best_z'],
            'time': result['time'],
            'generations': result['generations']
        })
        
        print(f"Best solution found: {result['best_z']} (optimal: {optimal_z})")
        print(f"Computation time: {result['time']:.2f} seconds")
        print(f"Generations needed: {result['generations']}")
    
    #plot_convergence(convergence_data, optimal_z, "Convergence of Different EA Configurations")
    
    print("\nSummary of Results:")
    print("{:<30} {:<15} {:<15} {:<15} {:<15}".format(
        "Configuration", "Z (EA)", "Z (CPLEX)", "% of Optimal", "Time (s)", "Generations"))
    for sol in best_solutions:
        percent_optimal = (sol['z_value'] / optimal_z) * 100
        print("{:<30} {:<15.2f} {:<15.2f}% {:<15.2f} {:<15}".format(sol['config'], sol['z_value'], optimal_z, percent_optimal, sol['time'], sol['generations']))

if __name__ == "__main__":
    main()
