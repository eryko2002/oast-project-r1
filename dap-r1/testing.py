import numpy as np
import matplotlib.pyplot as plt
import time
from read_config_net4 import *
from generate_population import num_chromosomes

DEBUG = True  # Flaga debugowania

# Domyślne parametry algorytmu EA
N = num_chromosomes  # Rozmiar populacji
K = 100  # Maksymalna liczba pokoleń
MUTATION_PROBABILITY = 0.05  # Prawdopodobieństwo mutacji
MUTATION_TYPE = 'random_reset'  # Typ mutacji: ['bit_flip', 'random_reset']
TERMINATION_THRESHOLD = 0.05  # Procentowa różnica od optimum CPLEX
SELECTION_PRESSURE = 2  # Parametr dla selekcji rank

# Zmienne przechowujące wyniki
best_solutions = []
convergence_data = []
computation_times = []

def calculate_objective_value(demandPath_flow, demand_max_path, demand_volume, demand_path_links, link_capacity):
    """
    Oblicza maksymalne przeciążenie łączy na podstawie przepływów.
    
    Parametry:
    - demandPath_flow: macierz przepływów [d, p]
    - demand_max_path: słownik z maksymalną liczbą ścieżek dla każdego żądania
    - demand_volume: słownik z objętościami żądań
    - demand_path_links: słownik ze ścieżkami dla każdego żądania
    - link_capacity: słownik z pojemnościami łączy
    
    Zwraca:
    - max_link_overload: maksymalne przeciążenie
    - demandPath_flow: macierz przepływów (dla spójności)
    """
    num_demands = demandPath_flow.shape[0]
    
    # Weryfikacja sum przepływów dla każdego żądania
    for row_idx in range(num_demands):
        d = row_idx + 1
        if np.sum(demandPath_flow[row_idx, :demand_max_path[d]]) != demand_volume[d]:
            if DEBUG:
                print(f"Error: Suma przepływów dla żądania {d} nie jest równa {demand_volume[d]}")
            return float('inf'), demandPath_flow

    # Inicjalizacja obciążenia łączy
    link_load = {e: 0 for e in link_capacity}
    
    # Obliczanie obciążenia łączy
    for d in demand_max_path:
        for p in range(demand_max_path[d]):
            for e in demand_path_links[d][p]:
                link_load[e] += demandPath_flow[d-1, p]
    
    # Obliczanie przeciążeń
    overloads = {e: max(0, link_load[e] - link_capacity[e]) for e in link_load}
    if DEBUG:
        print(f"[DEBUG] Obciążenie łączy: {link_load}")
        print(f"[DEBUG] Przeciążenia: {overloads}")
    
    max_link_overload = max(overloads.values())
    return max_link_overload, demandPath_flow

def should_terminate(best_z, optimal_z, threshold):
    """Sprawdza, czy EA powinien się zakończyć."""
    if best_z <= optimal_z * (1 + threshold):
        if DEBUG:
            print(f"[DEBUG] Kończymy: osiągnięto {best_z} (optimum: {optimal_z})")
        return True
    return False

def select_parents_rank(population, fitness_values):
    """Selekcja rodziców metodą rankingu."""
    ranked_indices = np.argsort(fitness_values)
    ranks = np.arange(1, len(population)+1)
    probabilities = (SELECTION_PRESSURE - 2*(SELECTION_PRESSURE-1)*(ranks-1)/(len(population)-1))
    probabilities = probabilities / np.sum(probabilities)
    parents_indices = np.random.choice(len(population), size=2, p=probabilities)
    return population[parents_indices[0]].T, population[parents_indices[1]].T

def select_parents_roulette(population, fitness_values):
    """Selekcja rodziców metodą ruletki."""
    inverted_fitness = 1 / np.array(fitness_values)
    selection_probabilities = inverted_fitness / np.sum(inverted_fitness)
    parents_indices = np.random.choice(len(population), size=2, p=selection_probabilities)
    if DEBUG:
        print(f"[DEBUG] Roulette selection: indeksy rodziców: {parents_indices}")
    return population[parents_indices[0]].T, population[parents_indices[1]].T

def crossover(parent1, parent2):
    """Krzyżowanie: zamiana jednego losowego wiersza między rodzicami."""
    num_rows = parent1.shape[0]
    row_to_swap = np.random.randint(0, num_rows)
    offspring1 = np.copy(parent1)
    offspring2 = np.copy(parent2)
    offspring1[row_to_swap, :] = parent2[row_to_swap, :]
    offspring2[row_to_swap, :] = parent1[row_to_swap, :]
    if DEBUG:
        print(f"[DEBUG] Krzyżowanie: zamieniono wiersz {row_to_swap}")
    return offspring1, offspring2

def mutate(flow_table, demand_volume, demand_max_path, mutation_type='random_reset', mutation_prob=1):
    """Mutacja chromosomu z zachowaniem sumy przepływów dla żądania."""
    if np.random.rand() > mutation_prob:
        if DEBUG:
            print("[DEBUG] Brak mutacji")
        return flow_table
    
    num_rows = flow_table.shape[0]
    row_idx = np.random.randint(0, num_rows)
    d = row_idx + 1
    num_paths = demand_max_path[d]
    
    if num_paths == 0:
        return flow_table
    
    col_idx = np.random.randint(0, num_paths)
    if DEBUG:
        print(f"[DEBUG] Mutacja w komórce ({row_idx}, {col_idx}) - typ: {mutation_type}")
    
    if mutation_type == 'bit_flip':
        flow_table[row_idx, col_idx] = 1 if flow_table[row_idx, col_idx] == 0 else 0
    elif mutation_type == 'random_reset':
        flow_table[row_idx, col_idx] = np.random.randint(0, demand_volume[d] + 1)
    
    # Naprawa sumy dla wiersza
    flow_table = fix_row_sum(flow_table, row_idx, col_idx, demand_volume, demand_max_path)
    if DEBUG:
        print("[DEBUG] Po mutacji i naprawie:")
        print(flow_table)
    return flow_table

def fix_row_sum(flow_table, row_idx, col_idx, demand_volume, demand_max_path):
    """Dostosowuje sumę przepływów w wierszu do objętości żądania."""
    d = row_idx + 1
    num_paths = demand_max_path[d]
    valid_cols = list(range(num_paths))
    current_sum = np.sum(flow_table[row_idx, valid_cols])
    target_sum = demand_volume[d]
    delta = target_sum - current_sum
    
    if DEBUG:
        print(f"[DEBUG] Naprawa sumy dla żądania {d}: suma = {current_sum}, cel = {target_sum}, delta = {delta}")
    
    if delta == 0:
        return flow_table
    
    other_cols = [c for c in valid_cols if c != col_idx]
    while delta != 0 and other_cols:
        c = np.random.choice(other_cols)
        if delta > 0:
            flow_table[row_idx, c] += 1
            delta -= 1
        elif delta < 0 and flow_table[row_idx, c] > 0:
            flow_table[row_idx, c] -= 1
            delta += 1
        else:
            other_cols.remove(c)
    
    if delta != 0:
        if delta > 0:
            flow_table[row_idx, col_idx] += delta
        elif delta < 0:
            adjust = min(flow_table[row_idx, col_idx], -delta)
            flow_table[row_idx, col_idx] -= adjust
            delta += adjust
        if delta != 0:
            print(f"Warning: Nie udało się dostosować sumy dla żądania {d}, delta={delta}")
    
    return flow_table

def run_ea(population_size=N, max_generations=K, mutation_prob=MUTATION_PROBABILITY, 
           mutation_type=MUTATION_TYPE, selection_method='roulette'):
    """Uruchamia algorytm ewolucyjny."""
    start_time = time.time()
    
    # Inicjalizacja populacji
    population = list(chromosomes_data.values())
    if DEBUG:
        print(f"[DEBUG] Wielkość populacji: {len(population)}")
    
    # Obliczenie optimum z CPLEX
    optimal_flow = load_flow_data()
    optimal_z, _ = calculate_objective_value(optimal_flow, demand_max_path, 
                                             demand_volume, demand_path_links, 
                                             link_capacity)
    if DEBUG:
        print(f"[DEBUG] Optimum CPLEX: {optimal_z}")
    
    best_z = float('inf')
    best_solution = None
    convergence = []
    
    for generation_index in range(max_generations):
        if DEBUG:
            print(f"\n[DEBUG] Pokolenie {generation_index + 1}")
        
        fitness_values = []
        for idx, chromosome in enumerate(population):
            z_value, _ = calculate_objective_value(chromosome, demand_max_path,
                                                  demand_volume, demand_path_links,
                                                  link_capacity)
            fitness_values.append(z_value)
            if DEBUG:
                print(f"[DEBUG] Chromosom {idx}: z = {z_value}")
        
        # Najlepsze rozwiązanie w tej generacji
        current_best_idx = np.argmin(fitness_values)
        current_best_z = fitness_values[current_best_idx]
        if current_best_z < best_z:
            best_z = current_best_z
            best_solution = population[current_best_idx]
            if DEBUG:
                print(f"[DEBUG] Nowe najlepsze rozwiązanie: z = {best_z}")
        
        convergence.append(best_z)
        if should_terminate(best_z, optimal_z, TERMINATION_THRESHOLD):
            break
        
        # Selekcja rodziców
        if selection_method == 'roulette':
            parent1, parent2 = select_parents_roulette(population, fitness_values)
        elif selection_method == 'rank':
            parent1, parent2 = select_parents_rank(population, fitness_values)
        else:
            raise ValueError("Nieznana metoda selekcji")
        
        # Krzyżowanie
        offspring1, offspring2 = crossover(parent1.T, parent2.T)
        if DEBUG:
            print("[DEBUG] Utworzono potomków")
        
        # Mutacja
        offspring1 = mutate(offspring1, demand_volume, demand_max_path, mutation_type, mutation_prob)
        offspring2 = mutate(offspring2, demand_volume, demand_max_path, mutation_type, mutation_prob)
        
        # Ocena potomków
        z1, _ = calculate_objective_value(offspring1, demand_max_path, demand_volume,
                                          demand_path_links, link_capacity)
        z2, _ = calculate_objective_value(offspring2, demand_max_path, demand_volume,
                                          demand_path_links, link_capacity)
        if DEBUG:
            print(f"[DEBUG] Z potomka1 = {z1}, Z potomka2 = {z2}")
        
        # Zastąpienie najgorszych chromosomów
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
    """Główna funkcja testująca różne konfiguracje EA."""
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
    if DEBUG:
        print(f"[DEBUG] Wartość optymalna (CPLEX): {optimal_z}")
    
    for config in configs:
        print(f"\nUruchamianie konfiguracji: {config['label']}")
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
        
        print(f"Najlepsze rozwiązanie: {result['best_z']} (optimum: {optimal_z})")
        print(f"Czas obliczeń: {result['time']:.2f} sekund")
        print(f"Liczba generacji: {result['generations']}")
    
    print("\nPodsumowanie wyników:")
    header = "{:<30} {:<15} {:<15} {:<15} {:<15}"
    print(header.format("Konfiguracja", "Z (EA)", "Z (CPLEX)", "% Optimum", "Czas (s) / Generacje"))
    for sol in best_solutions:
        percent_optimal = (sol['z_value'] / optimal_z) * 100
        print(header.format(sol['config'], f"{sol['z_value']:.2f}", f"{optimal_z:.2f}", 
                            f"{percent_optimal:.2f}%", f"{sol['time']:.2f} / {sol['generations']}"))

if __name__ == "__main__":
    main()
