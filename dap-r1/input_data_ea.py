import numpy as np
import random
import csv
import json

# Inicjalizacja listy na chromosomy i prawdopodobieństwa
population = []
probabilities = []

# Parametry linków, pojemności i żądań
linkModuleCount = dict()
# Parametry ścieżek dla żądań (odpowiedniki DemandPath_links)
demand_paths = dict()

# Wartości żądań (objętości)
demand_volume = dict()

def read_json():
    with open('config-dap-net4.json', 'r') as file:
        config = json.load(file)
        # Konwersja kluczy ze stringów na int
        linkModuleCount = {int(k): v for k, v in config['linkModuleCount'].items()}
        demand_paths = {int(k): v for k, v in config['demand_paths'].items()}
        demand_volume = {int(k): v for k, v in config['demand_volume'].items()}
    
    return linkModuleCount, demand_paths, demand_volume


def allocate_DemandPathFlow_from_csv():
    # Odczyt danych z pliku CSV
    with open('chromosomes.csv', 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)  # Pomijamy nagłówki
        
        # Odczytanie danych
        current_chromosom = []
        for row in reader:
            # Odczytanie chromosomów (ścieżki)
            paths = list(map(int, row[:-1]))  # Wszystkie kolumny oprócz ostatniej (prawdopodobieństwo)
            
            # Odczytanie prawdopodobieństwa
            probability = float(row[-1])  # Ostatnia kolumna to prawdopodobieństwo
            
            # Dodanie chromosomu i prawdopodobieństwa
            current_chromosom.append(np.array(paths))  # Dodajemy jako numpy array
            
            # Sprawdzamy, czy chromosom jest pełny
            if len(current_chromosom) == 3:  # Zmienna max_paths
                population.append(np.array(current_chromosom))
                probabilities.append(probability)
                current_chromosom = []  # Resetujemy do następnego chromosomu

def allocate_DemandPathFlow_from_json():
    # Odczyt danych z pliku JSON
    with open('chromosomes.json', 'r') as f:
        data = json.load(f)
    
    # Przetwarzanie danych z JSON
    for chromosome, details in data.items():
        # Odczytanie macierzy (ścieżek) chromosomu
        paths = np.array(details["Matrix"])  # Przekształcenie listy w numpy array
        
        # Odczytanie prawdopodobieństwa
        probability = details["Probability"]
        
        # Dodanie chromosomu do populacji
        population.append(paths)
        probabilities.append(probability)

# Wyświetlanie odczytanych danych
def print_population():
    for i, (chromosom, probability) in enumerate(zip(population, probabilities), start=1):
        print(f"Chromosom {i}:\n{chromosom}\nPrawdopodobieństwo: {probability:.4f}\n")

#if __name__=="__main__":
 #   allocate_DemandPathFlow_from_json()
 #   print_population()
    #selected_chromosome = roulette_wheel_selection(population, probabilities)
    #print("Wylosowany chromosom: Chromosom numer {}:\n{}".format(selected_chromosome[0],selected_chromosome[1]))