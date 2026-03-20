import json
import os
import matplotlib
matplotlib.use("Agg") 
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

df = pd.read_csv("data/molecules.csv")
X = df.drop("LogS", axis=1)
y = df["LogS"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

models = {
    "LinearRegression": LinearRegression(),
    "RandomForest": RandomForestRegressor(n_estimators=100, random_state=42),
    "GradientBoosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
    "SVR": SVR(kernel="rbf", C=1.0)
}

results = {}
os.makedirs("results", exist_ok=True)
for name, model in models.items():
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    results[name] = {"R2_test": round(r2_score(y_test, y_pred), 4)}

with open("results/metrics.json", "w") as f:
    json.dump(results, f, indent=2)

plt.figure(figsize=(10, 6))
plt.bar(results.keys(), [v["R2_test"] for v in results.values()])
plt.title("Model Comparison")
plt.savefig("results/model_comparison.png")
print("Обучение завершено!")