# =============================================================
#  Limpieza.py — Preprocesamiento del Dataset Airbnb
# =============================================================

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# ── Constantes ────────────────────────────────────────────────
DATA_PATH   = "../Datos/train.csv"
OUTPUT_PATH = "../Datos/train_limpio.csv"

PRICE_MIN        = 10          # precio mínimo razonable (USD)
PRICE_PERCENTILE = 0.995       # umbral superior para outliers
COLS_IMPUTAR     = [           # columnas numéricas a imputar con mediana
    "accommodates", "bedrooms", "bathrooms",
    "review_scores_rating", "number_of_reviews", "availability_365"
]


def cargar_raw(path: str) -> pd.DataFrame:
    """Carga el CSV en crudo."""
    df = pd.read_csv(path, low_memory=False)
    print(f"[✓] Dataset cargado: {df.shape[0]:,} filas × {df.shape[1]} columnas")
    return df


def convertir_precio(df: pd.DataFrame) -> pd.DataFrame:
    """Crea las columnas 'price' y 'log_price' a partir del CSV."""
    if "log_price" in df.columns:
        df["price"] = np.exp(df["log_price"])
    elif "price" in df.columns:
        if df["price"].dtype == object:
            df["price"] = df["price"].replace(r"[\$,]", "", regex=True).astype(float)
        df["log_price"] = np.log(df["price"].replace(0, np.nan))
    print(f"[✓] Precios: min=${df['price'].min():.2f} | max=${df['price'].max():.2f} | media=${df['price'].mean():.2f}")
    return df


def eliminar_nulos_target(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina filas donde el target (log_price) es nulo."""
    n_antes = len(df)
    df = df.dropna(subset=["log_price"])
    print(f"[✓] Nulos en log_price eliminados: {n_antes - len(df):,} filas")
    return df


def imputar_numericas(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """Imputa columnas numéricas con la mediana de cada columna."""
    cols_exist = [c for c in cols if c in df.columns]
    for col in cols_exist:
        n_nulos = df[col].isnull().sum()
        if n_nulos > 0:
            mediana = df[col].median()
            df[col].fillna(mediana, inplace=True)
            print(f"  · {col}: {n_nulos:,} nulos → imputados con mediana ({mediana:.2f})")
    print(f"[✓] Imputación completa en {len(cols_exist)} columnas")
    return df


def eliminar_outliers_precio(df: pd.DataFrame,
                              price_min: float = PRICE_MIN,
                              pct: float = PRICE_PERCENTILE) -> pd.DataFrame:
    """Filtra precios fuera del rango [price_min, percentil pct]."""
    price_max = df["price"].quantile(pct)
    mask = (df["price"] >= price_min) & (df["price"] <= price_max)
    n_out = (~mask).sum()
    df = df[mask].copy()
    print(f"[✓] Outliers de precio eliminados: {n_out:,} filas (rango: ${price_min}–${price_max:,.0f})")
    return df


def corregir_valores_negativos(df: pd.DataFrame,
                                cols: list = ["accommodates", "bedrooms", "bathrooms"]) -> pd.DataFrame:
    """Elimina filas con valores negativos en variables de tamaño."""
    cols_exist = [c for c in cols if c in df.columns]
    total = 0
    for col in cols_exist:
        n_neg = (df[col] < 0).sum()
        if n_neg:
            df = df[df[col] >= 0]
            total += n_neg
            print(f"  · {col}: {n_neg} valores negativos eliminados")
    if total == 0:
        print("[✓] No se encontraron valores negativos")
    return df


def recalcular_log_price(df: pd.DataFrame) -> pd.DataFrame:
    """Recalcula log_price tras el filtrado."""
    df["log_price"] = np.log(df["price"])
    return df


def resumen_final(df: pd.DataFrame) -> None:
    """Imprime un resumen del dataset limpio."""
    print("\n" + "=" * 50)
    print("   RESUMEN — DATASET LIMPIO")
    print("=" * 50)
    print(f"  Filas        : {len(df):,}")
    print(f"  Columnas     : {df.shape[1]}")
    print(f"  Nulos totales: {df.isnull().sum().sum():,}")
    print(f"  Precio mín.  : ${df['price'].min():.2f}")
    print(f"  Precio máx.  : ${df['price'].max():.2f}")
    print(f"  Precio media : ${df['price'].mean():.2f}")
    print("=" * 50)


if __name__ == "__main__":
    df = cargar_raw(DATA_PATH)
    df = convertir_precio(df)
    df = eliminar_nulos_target(df)
    df = imputar_numericas(df, COLS_IMPUTAR)
    df = eliminar_outliers_precio(df)
    df = corregir_valores_negativos(df)
    df = recalcular_log_price(df)
    resumen_final(df)

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\n[✓] Dataset limpio guardado en: {OUTPUT_PATH}")
