import numpy as np
import random as rd
import csv
import json

# Ustawienia
num_chromosomes = 10  # Liczba chromosomów w populacji
num_demands = 6       # Liczba żądań (kolumn)
max_paths = 3         # Maksymalna liczba ścieżek (wierszy)

# Inicjalizacja pustej listy do przechowywania chromosomów
population = []

# Generowanie losowej populacji
for _ in range(num_chromosomes):
    # Tworzymy losową macierz o wymiarach (num_demands, max_paths)
    chromosom = np.random.randint(0, 5, size=(max_paths, num_demands))  # wartości przepływów między 0 a 4
    population.append(chromosom.tolist())  # Zamienia macierz na listę, aby zapisać w CSV

# Generowanie listy losowych prawdopodobieństw (np. z przedziału [0, 1])
random_probs = np.random.rand(num_chromosomes)

# Normalizacja prawdopodobieństw, aby ich suma wynosiła 1
normalized_probs = (random_probs / random_probs.sum()) * 100

# Przygotowanie danych do zapisania w CSV
with open('chromosomes.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    
    # Nagłówki kolumn
    writer.writerow([f'Path {i+1}' for i in range(num_demands)] + ['Probability'])
    
    # Zapisanie chromosomów i prawdopodobieństw
    for i, chromosom in enumerate(population, start=1):
        probability = normalized_probs[i-1]  # Pobranie prawdopodobieństwa dla danego chromosomu
        for row in chromosom:
            writer.writerow(row + [round(probability, 4)])

print("Dane zostały zapisane do pliku 'chromosomes.csv'")

# Przygotowanie danych do zapisania w JSON
data = {}

for i, chromosom in enumerate(population, start=1):
    chromosom_data = {
        "Matrix": chromosom,
        "Probability": round(normalized_probs[i-1], 4)
    }
    data[f"Chromosome {i}"] = chromosom_data

# Zapisanie danych do pliku JSON
with open('chromosomes.json', 'w') as json_file:
    json.dump(data, json_file, indent=4)

print("Dane zostały zapisane do pliku 'chromosomes.json'")
