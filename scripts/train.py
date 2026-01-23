import pandas as pd
import json
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.linear_model import Lasso
from sklearn.metrics import mean_squared_error, r2_score

os.makedirs("outputs/model", exist_ok=True)
os.makedirs("outputs/results", exist_ok=True)

df = pd.read_csv("dataset/winequality-red.csv", sep=";")

X = df.drop("quality", axis=1)
y = df["quality"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = Lasso(alpha=0.1)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("MSE:", mse)
print("R2:", r2)

joblib.dump(model, "outputs/model/model.pkl")

with open("outputs/results/results.json", "w") as f:
    json.dump({"mse": mse, "r2": r2}, f, indent=4)
