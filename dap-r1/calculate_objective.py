import numpy as np

# Funkcja do obliczania wartości celu
def calculate_objective_value(demandPath_flow, demand_maxPath, demand_volume, DemandPath_links, link_capacity):
    # Inicjalizacja zmiennych
    link_load = {e: 0 for e in link_capacity}  # Słownik do przechowywania obciążenia dla każdego linku
    
    # Obliczanie obciążenia linków na podstawie demandPath_flow
    for d in range(1, len(demand_volume) + 1):
        for p in range(1, demand_maxPath[d-1] + 1):
            for e in DemandPath_links[d-1][p-1]:
                link_load[e] += demandPath_flow[d-1][p-1]
    
    # Obliczanie przeciążenia linków (link_load - link_capacity)
    overloads = {e: max(0, link_load[e] - link_capacity[e]) for e in link_load}
    
    # Maksymalne przeciążenie
    max_link_overload = max(overloads.values())
    
    return max_link_overload


#wzorcowa tabela przepływów obliczona przez cplex
demandPath_flow = [
    [19.5, 3.5, 0],
    [24, 0, 0],
    [15, 0, 0],
    [2, 0, 0],
    [20.5, 2.5, 0],
    [17, 0, 0]
]

demand_maxPath = [3, 3, 2, 3, 3, 3]  # Maksymalna liczba ścieżek dla każdego żądania
demand_volume = {1: 23, 2: 24, 3: 15, 4: 2, 5: 23, 6: 17}  # Wolumeny żądań

# Ścieżki linków dla każdego żądania
DemandPath_links = [
    [[1], [2, 3], [2, 4, 5]],
    [[2], [1, 3], [1, 4, 5]],
    [[1, 4], [2, 5]],
    [[3], [1, 2], [4, 5]],
    [[4], [3, 5], [1, 2, 5]],
    [[5], [3, 4], [1, 2, 4]]
]

# Pojemności linków
link_capacity = {
    1: 16,
    2: 8,
    3: 12,
    4: 16,
    5: 0
}

# Obliczanie wartości funkcji celu
z_value = calculate_objective_value(demandPath_flow, demand_maxPath, demand_volume, DemandPath_links, link_capacity)
print(f"Wartość funkcji celu: {z_value}")

