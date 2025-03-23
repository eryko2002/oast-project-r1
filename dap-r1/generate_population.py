import numpy as np
import csv
import json

# Ustawienia
num_chromosomes = 10  # Liczba chromosomów w populacji
num_demands = 6       # Liczba żądań (kolumn)
max_paths = 3         # Maksymalna liczba ścieżek (wierszy)

# Inicjalizacja pustej listy do przechowywania chromosomów
population = []

# Przykładowe wartości z demand_volume
demand_volume = {
    "1": 23,
    "2": 24,
    "3": 15,
    "4": 2,
    "5": 23,
    "6": 17
}

# Inicjalizacja pustej listy do przechowywania chromosomów
population = []

# Funkcja generująca chromosom, w którym suma wartości w każdej kolumnie odpowiada demand_volume
def generate_chromosome():
    chromosom = np.zeros((max_paths, num_demands), dtype=int)

    for col in range(num_demands):
        target_sum = demand_volume[str(col + 1)]  # docelowa suma dla tej kolumny

        # Generujemy losowe wartości dla tej kolumny, tak by ich suma wynosiła target_sum
        while True:
            # Losujemy liczby, które będą sumować się do target_sum
            random_values = np.random.randint(0, target_sum + 1, size=max_paths)
            if random_values.sum() == target_sum:
                chromosom[:, col] = random_values
                break
    
    return chromosom

# Generowanie losowej populacji
for _ in range(num_chromosomes):
    chromosom = generate_chromosome()
    population.append(chromosom.tolist())

def saveFlowTableToJSON():
    data = {}
    for i, chromosom in enumerate(population, start=1):
        # Zapisujemy tablicę chromosomów bez łączenia wierszy w ciąg tekstowy
        data[f"Chromosome {i}"] = chromosom
    
    with open('chromosomes.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)

    print("Dane zostały zapisane do pliku 'chromosomes.json'")


# Test zapisu
#saveFlowTableToCSV()
saveFlowTableToJSON()

# Wypisanie populacji
for i, chromosom in enumerate(population, 1):
    print(f"Chromosom {i}:")
    print(np.array(chromosom))  # Używamy numpy array do lepszego formatowania

#for i, arr in enumerate(population,start=1):
#    formatted_chromosome = '\n'.join(str(row) for row in arr)
#    print(f'Chromosom{i}:\n[{formatted_chromosome}]')
#