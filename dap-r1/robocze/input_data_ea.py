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


# Wyświetlanie odczytanych danych
def print_population():
    for i, (chromosom, probability) in enumerate(zip(population, probabilities), start=1):
        print(f"Chromosom {i}:\n{chromosom}\nPrawdopodobieństwo: {probability:.4f}\n")

#if __name__=="__main__":
 #   allocate_DemandPathFlow_from_json()
 #   print_population()
    #selected_chromosome = roulette_wheel_selection(population, probabilities)
    #print("Wylosowany chromosom: Chromosom numer {}:\n{}".format(selected_chromosome[0],selected_chromosome[1]))