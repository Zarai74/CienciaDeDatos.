# =============================================================
#  Modelo.py — Regresión Lineal Múltiple para Precios Airbnb
# =============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings("ignore")

# ── Constantes ────────────────────────────────────────────────
DATA_PATH   = "../Datos/train.csv"
OUTPUT_DIR  = "../Visualizaciones/"
RANDOM_SEED = 42
TEST_SIZE   = 0.20


def cargar_datos(path: str) -> pd.DataFrame:
    """Carga el dataset y devuelve un DataFrame limpio con log_price."""
    df = pd.read_csv(path, low_memory=False)
    if "log_price" not in df.columns:
        df["price"] = df["price"].replace(r"[\$,]", "", regex=True).astype(float)
        df["log_price"] = np.log(df["price"].replace(0, np.nan))
    df["price"] = np.exp(df["log_price"])
    return df


def preparar_features(df: pd.DataFrame):
    """Selecciona y codifica las variables del modelo."""
    num_cols = [c for c in ["accommodates", "bedrooms", "bathrooms",
                             "review_scores_rating", "number_of_reviews",
                             "availability_365"] if c in df.columns]
    for col in num_cols:
        df[col].fillna(df[col].median(), inplace=True)

    dummies = pd.get_dummies(df["room_type"], prefix="room", drop_first=True) \
              if "room_type" in df.columns else pd.DataFrame()

    feature_cols = num_cols + list(dummies.columns)
    df_model = pd.concat([df[num_cols + ["log_price"]], dummies], axis=1).dropna()
    return df_model, feature_cols


def entrenar_modelo(df_model: pd.DataFrame, feature_cols: list):
    """Entrena el modelo y devuelve el modelo, scaler y conjuntos de datos."""
    X = df_model[feature_cols].astype(float)
    y = df_model["log_price"].astype(float)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_SEED
    )
    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc  = scaler.transform(X_test)

    model = LinearRegression()
    model.fit(X_train_sc, y_train)

    return model, scaler, X_train_sc, X_test_sc, y_train, y_test, feature_cols


def evaluar_modelo(model, X_train_sc, X_test_sc, y_train, y_test):
    """Imprime métricas de evaluación."""
    y_pred_train = model.predict(X_train_sc)
    y_pred_test  = model.predict(X_test_sc)

    r2_train  = r2_score(y_train, y_pred_train)
    r2_test   = r2_score(y_test,  y_pred_test)
    mse_test  = mean_squared_error(y_test, y_pred_test)
    rmse_test = np.sqrt(mse_test)

    print("=" * 50)
    print("   MÉTRICAS DEL MODELO")
    print("=" * 50)
    print(f"  R²  Entrenamiento : {r2_train:.4f}")
    print(f"  R²  Prueba        : {r2_test:.4f}")
    print(f"  MSE Prueba        : {mse_test:.6f}")
    print(f"  RMSE Prueba (log) : {rmse_test:.6f}")
    print(f"  RMSE Prueba (USD) : ${np.sqrt(mean_squared_error(np.exp(y_test), np.exp(y_pred_test))):,.2f}")
    print("=" * 50)

    return y_pred_test


if __name__ == "__main__":
    df = cargar_datos(DATA_PATH)
    df_model, feature_cols = preparar_features(df)
    model, scaler, X_train_sc, X_test_sc, y_train, y_test, feature_cols = \
        entrenar_modelo(df_model, feature_cols)
    y_pred_test = evaluar_modelo(model, X_train_sc, X_test_sc, y_train, y_test)
    print("\nModelo entrenado y evaluado correctamente.")
