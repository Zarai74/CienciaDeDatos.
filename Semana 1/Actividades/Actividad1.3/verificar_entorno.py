"""
Actividad 1.3 - Verificación del Entorno de Trabajo
Ciencia de Datos - Semana 1
"""

import sys

print("=" * 55)
print("  VERIFICACIÓN DEL ENTORNO DE CIENCIA DE DATOS")
print("=" * 55)

# Python
print(f"\n🐍 Python: {sys.version.split()[0]}")

# Librerías
librerias = {
    "NumPy":        "numpy",
    "Pandas":       "pandas",
    "Matplotlib":   "matplotlib",
    "Seaborn":      "seaborn",
    "Scikit-learn": "sklearn",
    "Jupyter":      "jupyter_core",
}

print("\n📦 Librerías instaladas:")
todas_ok = True
for nombre, modulo in librerias.items():
    try:
        mod = __import__(modulo)
        version = getattr(mod, "__version__", "OK")
        print(f"   ✅ {nombre:<15} {version}")
    except ImportError:
        print(f"   ❌ {nombre:<15} NO INSTALADA")
        todas_ok = False

# Demo rápida con NumPy y Pandas
print("\n🔬 Demo rápida:")

import numpy as np
import pandas as pd

arr = np.array([10, 20, 30, 40, 50])
print(f"   NumPy  → arreglo: {arr}  |  media: {arr.mean()}")

df = pd.DataFrame({
    "nombre": ["Ana", "Luis", "María"],
    "edad":   [22, 25, 21],
    "nota":   [9.5, 8.0, 9.0],
})
print(f"   Pandas → DataFrame de {df.shape[0]} filas x {df.shape[1]} columnas")
print(f"   Promedio de notas: {df['nota'].mean():.2f}")

print("\n" + "=" * 55)
if todas_ok:
    print("  ✅ Entorno listo para trabajar con Ciencia de Datos")
else:
    print("  ⚠️  Algunas librerías requieren instalación")
print("=" * 55)
