import pandas as pd
import os


base_path = f'{os.path.join(os.getcwd(), "input_net4")}'

# Tworzenie link_capacity: e : C_e
link_capacity = {
    1: 16,
    2: 8,
    3: 12,
    4: 16,
    5: 0
}

# Tworzenie demand_paths: d : [P[d,p] : {e1,e2,e3...}]
demand_paths = {
    "1": [[1], [2, 3], [2, 4, 5]],
    "2": [[2], [1, 3], [1, 4, 5]],
    "3": [[1, 4], [2, 5]],
    "4": [[3], [1, 2], [4, 5]],
    "5": [[4], [3, 5], [1, 2, 5]],
    "6": [[5], [3, 4], [1, 2, 4]]
}

# Maksymalna liczba ścieżek możliwa do wykorzystania dla danego żądania d : P
demand_maxPath = {
    "1": 3,
    "2": 3,
    "3": 2,
    "4": 3,
    "5": 3,
    "6": 3
}

# Tworzenie demand_volume: d : h_d
demand_volume = {
    "1": 23,
    "2": 24,
    "3": 15,
    "4": 2,
    "5": 23,
    "6": 17
}


# Zapis link_capacity do CSV
link_capacity_df = pd.DataFrame(list(link_capacity.items()), columns=["Link", "LinkCapacity"])
link_capacity_df.to_csv(f'{base_path}/LinkCapacity.csv', index=False)

# Zapis demand_paths do CSV
demand_path_links_data = []

for demand, paths in demand_paths.items():
    for i, path in enumerate(paths):
        demand_path_links_data.append({"Demand": demand, "Path": i + 1, "Paths": path})

demand_paths_df = pd.DataFrame(demand_path_links_data)
demand_paths_df.to_csv(f'{base_path}/DemandPath_links.csv', index=False)

# Połączenie demand_maxPath i demand_volume w jeden DataFrame
combined_data = {
    "Demand": list(demand_maxPath.keys()),
    "MaxPath": list(demand_maxPath.values()),
    "Volume": list(demand_volume.values())
}

# Tworzenie DataFrame i zapis do CSV
combined_df = pd.DataFrame(combined_data)
combined_df.to_csv(f'{base_path}/Demand_MaxPath_Volume.csv', index=False)

print("Dane zapisano do plików CSV.")
