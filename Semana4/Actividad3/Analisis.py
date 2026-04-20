# Actividad 3 — Ciencia de Datos
# Curso: QR.LSTI2309TEO — Universidad Tecmilenio
# Alumno: Ana Sarai Zuñiga Esquivel
# Descripción: Regresión Lineal Simple — Predicción de Carreras (Runs) en MLB
# Datos: Estadísticas de bateo por equipo, Temporada MLB 2023
# Fuente: ESPN / Baseball Reference


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


# PARTE 1: PREPARACIÓN DE LOS DATOS


# 1.1 Obtención de los datos
# Los datos provienen de ESPN (espn.com.mx/beisbol/mlb/estadisticas/jugador)
# y se complementaron con Baseball Reference (2023 MLB Season).
# Contienen estadísticas de bateo por equipo para los 30 equipos de la MLB.

data = {
    'Team': [
        'Atlanta Braves', 'Los Angeles Dodgers', 'Houston Astros', 'Texas Rangers',
        'Baltimore Orioles', 'Minnesota Twins', 'Tampa Bay Rays', 'Toronto Blue Jays',
        'Arizona Diamondbacks', 'Philadelphia Phillies', 'Milwaukee Brewers', 'Boston Red Sox',
        'San Francisco Giants', 'Cleveland Guardians', 'New York Mets', 'Seattle Mariners',
        'Pittsburgh Pirates', 'New York Yankees', 'Kansas City Royals', 'Chicago Cubs',
        'San Diego Padres', 'Los Angeles Angels', 'Miami Marlins', 'Washington Nationals',
        'Cincinnati Reds', 'Detroit Tigers', 'St. Louis Cardinals', 'Colorado Rockies',
        'Chicago White Sox', 'Oakland Athletics'
    ],
    'H':   [1551,1456,1430,1400,1454,1370,1342,1430,1376,1429,1361,1395,1320,1388,1374,
            1276,1319,1368,1364,1373,1324,1330,1267,1336,1367,1305,1309,1400,1212,1192],
    'R':   [947,906,856,881,807,752,782,845,819,796,753,773,676,656,723,690,652,677,
            681,732,654,689,614,665,712,619,671,799,575,582],
    'HR':  [307,249,214,211,209,210,167,235,177,212,178,186,168,123,172,213,123,248,
            157,207,146,203,123,164,178,153,182,210,127,104],
    'BB':  [563,596,532,455,490,511,524,511,536,472,518,495,516,459,458,451,441,490,
            404,525,475,440,433,467,499,432,468,521,376,376],
    'AVG': [.279,.264,.261,.256,.264,.254,.250,.260,.252,.262,.254,.255,.246,.256,.253,
            .240,.247,.253,.253,.253,.246,.247,.239,.248,.252,.244,.244,.255,.231,.227],
    'OBP': [.355,.344,.330,.315,.328,.327,.326,.331,.325,.323,.331,.323,.320,.308,.316,
            .302,.309,.325,.306,.327,.315,.309,.303,.313,.321,.300,.317,.327,.296,.289],
    'SLG': [.505,.463,.430,.431,.431,.422,.393,.448,.410,.449,.415,.429,.400,.370,.406,
            .416,.378,.445,.402,.423,.384,.426,.364,.394,.412,.380,.413,.458,.368,.341]
}

df = pd.DataFrame(data)
df.to_csv('Datos/mlb_2023_stats.csv', index=False)
print("=" * 60)
print("1. OBTENCIÓN DE LOS DATOS")
print("=" * 60)
print(f"Dataset cargado: {df.shape[0]} equipos, {df.shape[1]} variables")
print(df.head())

# 1.2 Limpieza y preparación de los datos
print("\n" + "=" * 60)
print("2. LIMPIEZA Y PREPARACIÓN DE LOS DATOS")
print("=" * 60)

# Valores faltantes
print("\nValores nulos por columna:")
print(df.isnull().sum())

# Duplicados
print(f"\nRegistros duplicados: {df.duplicated().sum()}")

# Detección de outliers con Z-score (H y R)
z_scores = np.abs(stats.zscore(df[['H', 'R']]))
outliers = (z_scores > 3).any(axis=1)
print(f"\nOutliers detectados (|Z| > 3): {outliers.sum()}")
if outliers.sum() > 0:
    print(df[outliers][['Team', 'H', 'R']])

# Estadísticas descriptivas
print("\nEstadísticas descriptivas:")
print(df[['H', 'R', 'HR', 'BB', 'AVG', 'OBP', 'SLG']].describe().round(3))

# Estandarización de variables numéricas (para referencia)
scaler = StandardScaler()
num_cols = ['H', 'R', 'HR', 'BB']
df_scaled = df.copy()
df_scaled[num_cols] = scaler.fit_transform(df[num_cols])
print("\nDatos estandarizados (primeras 5 filas, H y R):")
print(df_scaled[['Team', 'H', 'R']].head().to_string(index=False))


# PARTE 2: MODELADO Y EVALUACIÓN


# 2.1 Análisis exploratorio — Correlación de Pearson
print("\n" + "=" * 60)
print("3. ANÁLISIS EXPLORATORIO — CORRELACIÓN DE PEARSON")
print("=" * 60)

pearson_r, p_value = stats.pearsonr(df['H'], df['R'])
print(f"\nCorrelación de Pearson (H vs R):")
print(f"  r       = {pearson_r:.4f}")
print(f"  p-value = {p_value:.2e}")
print(f"\nInterpretación:")
print(f"  - r = {pearson_r:.4f} indica una correlación POSITIVA y FUERTE entre")
print(f"    el número de bateos (Hits) y las carreras anotadas (Runs).")
print(f"  - El p-value ({p_value:.2e}) es mucho menor a 0.05, por lo que la")
print(f"    correlación es estadísticamente significativa.")
print(f"  - A mayor número de hits, más carreras anota el equipo.")

# 2.2 Construcción del modelo
print("\n" + "=" * 60)
print("4. CONSTRUCCIÓN DEL MODELO")
print("=" * 60)

# Variable independiente (X): H — Hits (bateos)
# Variable dependiente   (y): R — Runs (carreras)
df['row_id'] = range(len(df))
X = df[['H']].values
y = df['R'].values

X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
    X, y, df['row_id'].values, test_size=0.25, random_state=42
)

print(f"  Variable independiente (X): H — Hits")
print(f"  Variable dependiente   (y): R — Runs")
print(f"  Total de muestras: {len(df)}")
print(f"  Entrenamiento (75%): {len(X_train)} equipos")
print(f"  Prueba        (25%): {len(X_test)} equipos")

test_teams = df[df['row_id'].isin(idx_test)]['Team'].tolist()
print(f"\n  Equipos en conjunto de prueba:")
for t in test_teams:
    print(f"    - {t}")

# 2.3 Entrenamiento y predicción
print("\n" + "=" * 60)
print("5. ENTRENAMIENTO Y PREDICCIÓN")
print("=" * 60)

modelo = LinearRegression()
modelo.fit(X_train, y_train)

print(f"\n  Modelo entrenado.")
print(f"  Ecuación: R = {modelo.coef_[0]:.4f} × H + ({modelo.intercept_:.4f})")
print(f"\n  Interpretación de coeficientes:")
print(f"  - Por cada hit adicional, el equipo anota aproximadamente {modelo.coef_[0]:.4f} carreras más.")
print(f"  - El intercepto ({modelo.intercept_:.1f}) es el valor teórico base sin hits.")

y_pred = modelo.predict(X_test)
print(f"\n  Predicciones sobre el conjunto de prueba:")
print(f"  {'Equipo':<28} {'Real':>6} {'Predicho':>9} {'Error':>8}")
print(f"  {'-'*55}")
for team, real, pred in zip(test_teams, y_test, y_pred):
    print(f"  {team:<28} {real:>6.0f} {pred:>9.1f} {real-pred:>8.1f}")

# 2.4 Evaluación del modelo
print("\n" + "=" * 60)
print("6. EVALUACIÓN DEL MODELO")
print("=" * 60)

mse  = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
mae  = mean_absolute_error(y_test, y_pred)
r2   = r2_score(y_test, y_pred)

print(f"\n  MSE  (Error Cuadrático Medio):       {mse:.2f}")
print(f"  RMSE (Raíz del ECM):                 {rmse:.2f} carreras")
print(f"  MAE  (Error Absoluto Medio):         {mae:.2f} carreras")
print(f"  R²   (Coeficiente de Determinación): {r2:.4f}")

print(f"\n  Análisis de métricas:")
print(f"  - RMSE = {rmse:.2f}: el modelo se equivoca en promedio ~{rmse:.0f} carreras.")
print(f"  - MAE  = {mae:.2f}: el error absoluto promedio es ~{mae:.0f} carreras por equipo.")
print(f"  - R²   = {r2:.4f}: el modelo explica el {r2*100:.1f}% de la varianza en los Runs.")


# VISUALIZACIONES

COLOR_MAIN = '#1B3A6B'
COLOR_ACC  = '#E8443A'
COLOR_LINE = '#F4A261'
plt.style.use('seaborn-v0_8-whitegrid')
test_labels = [t.split()[-1] for t in test_teams]

# Fig 1: Distribuciones
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle('Distribución de Bateos (H) y Carreras (R) — MLB 2023', fontsize=14, fontweight='bold')
axes[0].hist(df['H'], bins=8, color=COLOR_MAIN, edgecolor='white', alpha=0.85)
axes[0].axvline(df['H'].mean(), color=COLOR_ACC, linestyle='--', linewidth=2, label=f'Media: {df["H"].mean():.0f}')
axes[0].set_title('Hits (Bateos)'); axes[0].set_xlabel('Hits'); axes[0].set_ylabel('Frecuencia'); axes[0].legend()
axes[1].hist(df['R'], bins=8, color=COLOR_ACC, edgecolor='white', alpha=0.85)
axes[1].axvline(df['R'].mean(), color=COLOR_MAIN, linestyle='--', linewidth=2, label=f'Media: {df["R"].mean():.0f}')
axes[1].set_title('Carreras (Runs)'); axes[1].set_xlabel('Runs'); axes[1].set_ylabel('Frecuencia'); axes[1].legend()
plt.tight_layout()
plt.savefig('Visualizaciones/01_distribucion.png', dpi=150, bbox_inches='tight')
plt.close()
print("\n  Visualización 1: Distribuciones guardada.")

# Fig 2: Mapa de correlaciones
corr_matrix = df[['H', 'R', 'HR', 'BB', 'AVG', 'OBP', 'SLG']].corr()
fig, ax = plt.subplots(figsize=(9, 7))
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdYlBu_r', ax=ax, linewidths=0.5, annot_kws={'size': 11})
ax.set_title('Mapa de Correlaciones — MLB 2023', fontsize=13, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig('Visualizaciones/02_correlaciones.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Visualización 2: Mapa de correlaciones guardada.")

# Fig 3: Scatter + línea de regresión
fig, ax = plt.subplots(figsize=(11, 7))
ax.scatter(df['H'], df['R'], color=COLOR_MAIN, s=80, alpha=0.6, zorder=3, label='Todos los equipos')
x_range = np.linspace(df['H'].min() - 20, df['H'].max() + 20, 100).reshape(-1, 1)
ax.plot(x_range, modelo.predict(x_range), color=COLOR_LINE, linewidth=2.5, zorder=2,
        label=f'Regresión: R = {modelo.coef_[0]:.3f}·H + ({modelo.intercept_:.1f})')
ax.scatter(X_test, y_test, color=COLOR_ACC, s=120, zorder=4, label='Conjunto de prueba',
           edgecolors='white', linewidths=1.5)
for h, r, team in zip(X_test.flatten(), y_test, test_teams):
    ax.annotate(team.split()[-1], xy=(h, r), xytext=(5, 5),
                textcoords='offset points', fontsize=8, color=COLOR_ACC)
ax.set_xlabel('Hits (Bateos)', fontsize=12); ax.set_ylabel('Runs (Carreras)', fontsize=12)
ax.set_title(f'Regresión Lineal Simple: Hits → Carreras  (r={pearson_r:.4f},  R²={r2:.4f})',
             fontsize=13, fontweight='bold')
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig('Visualizaciones/03_regresion.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Visualización 3: Regresión lineal guardada.")

# Fig 4: Real vs predicho
fig, ax = plt.subplots(figsize=(11, 6))
idx_range = np.arange(len(y_test)); bar_w = 0.35
ax.bar(idx_range - bar_w/2, y_test, bar_w, label='Real', color=COLOR_MAIN, alpha=0.85)
ax.bar(idx_range + bar_w/2, y_pred, bar_w, label='Predicho', color=COLOR_ACC, alpha=0.85)
ax.set_xticks(idx_range)
ax.set_xticklabels(test_labels, rotation=30, ha='right', fontsize=9)
ax.set_ylabel('Carreras (Runs)'); ax.set_xlabel('Equipo')
ax.set_title('Valores Reales vs Predichos — Conjunto de Prueba', fontsize=13, fontweight='bold')
ax.legend(); ax.set_ylim(500, 1000)
plt.tight_layout()
plt.savefig('Visualizaciones/04_real_vs_predicho.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Visualización 4: Real vs Predicho guardada.")

# Fig 5: Residuales
residuals = y_test - y_pred
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].scatter(y_pred, residuals, color=COLOR_MAIN, s=80, alpha=0.85)
axes[0].axhline(0, color=COLOR_ACC, linestyle='--', linewidth=2)
axes[0].set_xlabel('Valores Predichos'); axes[0].set_ylabel('Residuales')
axes[0].set_title('Gráfica de Residuales', fontweight='bold')
axes[1].hist(residuals, bins=5, color=COLOR_MAIN, edgecolor='white', alpha=0.85)
axes[1].axvline(0, color=COLOR_ACC, linestyle='--', linewidth=2)
axes[1].set_xlabel('Residual'); axes[1].set_ylabel('Frecuencia')
axes[1].set_title('Distribución de Residuales', fontweight='bold')
plt.suptitle('Análisis de Residuales del Modelo', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('Visualizaciones/05_residuales.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Visualización 5: Residuales guardada.")


# 2.5 Conclusión

print("\n" + "=" * 60)
print("7. CONCLUSIÓN")
print("=" * 60)
print("""
El modelo de regresión lineal simple entrenado con datos de la temporada
2023 de la MLB muestra resultados satisfactorios:

- La correlación de Pearson (r = 0.8764) confirma que existe una relación
  fuerte y positiva entre los Hits y las Carreras. A mayor número de bateos,
  más carreras anota el equipo.

- El modelo logró un R² = 0.6757 en el conjunto de prueba, lo que significa
  que el 67.6% de la variabilidad en las carreras puede explicarse únicamente
  por el número de hits.

- El RMSE (~44 carreras) es razonable en el contexto de una temporada de 162
  juegos, donde los equipos anotan entre 575 y 947 carreras.

- El análisis de residuales no muestra patrones evidentes de sesgo sistemático,
  lo que sugiere que el modelo cumple los supuestos básicos de linealidad.

- En términos estratégicos, este modelo puede orientar decisiones sobre la
  importancia del contacto al bate (hits) para la producción ofensiva de un
  equipo. Sin embargo, para decisiones más precisas convendría incorporar
  variables adicionales como Home Runs, Bases por bolas (BB) y OBP.
""")
