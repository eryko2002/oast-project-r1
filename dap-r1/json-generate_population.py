import numpy as np
import json

# Ustawienia
num_chromosomes = 10  # Liczba chromosomów w populacji
num_demands = 6       # Liczba żądań (kolumn)
max_paths = 3         # Maksymalna liczba ścieżek (wierszy)

# Generowanie losowej populacji
population = []
for _ in range(num_chromosomes):
    chromosom = np.random.randint(0, 5, size=(max_paths, num_demands)).tolist()
    population.append(chromosom)

# Generowanie listy losowych prawdopodobieństw
random_probs = np.random.rand(num_chromosomes)
normalized_probs = (random_probs / random_probs.sum()) * 100

# Przygotowanie danych w odpowiedniej strukturze
data = {
    f"Chromosome {i + 1}": {
        "Matrix": population[i],
        "Probability": round(normalized_probs[i], 4)
    }
    for i in range(num_chromosomes)
}

# Zapis do pliku JSON w poprawnym formacie
with open('chromosomes.json', 'w') as f:
    json.dump(data, f, indent=4)

print("Dane zostały zapisane do pliku 'chromosomes.json'")
