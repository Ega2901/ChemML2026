import numpy as np
import pandas as pd
import os

np.random.seed(42)
n_molecules = 500

data = {
    "MolWeight": np.random.uniform(100, 600, n_molecules),
    "LogP": np.random.normal(2.5, 1.5, n_molecules),
    "HBD": np.random.randint(0, 6, n_molecules),
    "HBA": np.random.randint(0, 10, n_molecules),
    "TPSA": np.random.uniform(20, 150, n_molecules),
    "RotBonds": np.random.randint(0, 12, n_molecules),
    "AromaticRings": np.random.randint(0, 5, n_molecules),
    "HeavyAtoms": np.random.randint(7, 45, n_molecules),
    "FormalCharge": np.random.choice([-1, 0, 0, 0, 1], n_molecules),
}

df = pd.DataFrame(data)
df["LogS"] = (-0.01 * df["MolWeight"] - 0.5 * df["LogP"] + 0.3 * df["HBD"] + 
              0.2 * df["HBA"] - 0.005 * df["TPSA"] - 0.1 * df["RotBonds"] + 
              0.4 * df["FormalCharge"] + np.random.normal(0, 0.5, n_molecules))

os.makedirs("data", exist_ok=True)
df.to_csv("data/molecules.csv", index=False)
print("Датасет создан!")