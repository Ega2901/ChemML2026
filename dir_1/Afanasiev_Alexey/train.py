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
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Загрузка
df = pd.read_csv("data/molecules.csv")
feature_cols = [c for c in df.columns if c != "LogS"]
X = df[feature_cols].values
y = df["LogS"].values

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
    
    # ДОБАВЛЕНО: все требуемые метрики
    results[name] = {
        "R2_test": round(r2_score(y_test, y_pred), 4),
        "MAE_test": round(mean_absolute_error(y_test, y_pred), 4),
        "RMSE_test": round(np.sqrt(mean_squared_error(y_test, y_pred)), 4)
    }

with open("results/metrics.json", "w") as f:
    json.dump(results, f, indent=2)

# ГРАФИК 1: Сравнение моделей
plt.figure(figsize=(10, 6))
plt.bar(results.keys(), [v["R2_test"] for v in results.values()])
plt.title("Model Comparison (R2)")
plt.savefig("results/model_comparison.png")

# ГРАФИК 2: Predicted vs Actual (для RandomForest)
model = models["RandomForest"]
y_pred = model.predict(X_test_scaled)
plt.figure(figsize=(6, 6))
plt.scatter(y_test, y_pred, alpha=0.5)
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')
plt.xlabel("Actual")
plt.ylabel("Predicted")
plt.title("RandomForest: Predicted vs Actual")
plt.savefig("results/pred_vs_actual.png")

# ГРАФИК 3: Важность признаков
importances = models["RandomForest"].feature_importances_
plt.figure(figsize=(10, 6))
plt.barh(feature_cols, importances)
plt.title("Feature Importance (RandomForest)")
plt.savefig("results/feature_importance.png")

print("Обучение завершено! Все метрики и 3 графика сохранены.")
