import pandas as pd
import os
# Tworzenie linkModuleCount
linkModuleCount = {
    "1": 8,
    "2": 4,
    "3": 6,
    "4": 8,
    "5": 0
}

# Tworzenie demand_paths
demand_paths = {
    "1": [[1], [2, 3], [2, 4, 5]],
    "2": [[2], [1, 3], [1, 4, 5]],
    "3": [[1, 4], [2, 5]],
    "4": [[3], [1, 2], [4, 5]],
    "5": [[4], [3, 5], [1, 2, 5]],
    "6": [[5], [3, 4], [1, 2, 4]]
}

# Tworzenie demand_volume
demand_volume = {
    "1": 23,
    "2": 24,
    "3": 15,
    "4": 2,
    "5": 23,
    "6": 17
}

base_path=f'{os.path.join(os.getcwd(),"input_net4")}'

# Zapis linkModuleCount do CSV
link_module_df = pd.DataFrame(list(linkModuleCount.items()), columns=["Link", "Module Count"])
link_module_df.to_csv(f'{base_path}/link_module_count.csv', index=False)

# Zapis demand_paths do CSV
demand_paths_data = []


for demand, paths in demand_paths.items():
    for i, path in enumerate(paths):
        demand_paths_data.append({"Demand": demand, "Path Level": i+1, "Paths": path})

demand_paths_df = pd.DataFrame(demand_paths_data)
demand_paths_df.to_csv(f'{base_path}/demand_paths.csv', index=False)

# Zapis demand_volume do CSV
demand_volume_df = pd.DataFrame(list(demand_volume.items()), columns=["Demand", "Volume"])
demand_volume_df.to_csv(f'{base_path}/demand_volume.csv', index=False)

print("Dane zapisano do plików CSV.")
