"""
validar_dataset.py
------------------
Script de verificación y validación algorítmica para la materia
Algoritmos y Estructuras de Datos (AED).

Replica de forma exacta la lógica algorítmica del pseudocódigo (pseudocódigo.psc),
procesa el archivo 'lecturas_sensores.csv' y contrasta los resultados obtenidos
frente a la verdad conocida (Ground Truth).
"""

import csv
import os
import sys

# Configurar salida estándar en UTF-8 para visualización correcta de caracteres especiales en Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# =============================================================================
# CONSTANTES DEL PROBLEMA (Fieles al pseudocódigo)
# =============================================================================
N_LECTURAS = 24             # N = 24 lecturas por sensor (24 horas)
CANT_SENSORES = 5          # Sensores 1 a 5
UMBRAL_ANOMALIA = 42.0     # Umbral térmico crítico
LONG_MIN_RACHA = 3         # Longitud mínima de lecturas consecutivas

# =============================================================================
# VERDAD CONOCIDA (Ground Truth para contraste)
# =============================================================================
VERDAD_CONOCIDA = {
    1: {"espera_racha": False, "inicio": None, "longitud": 0},
    2: {"espera_racha": True,  "inicio": 13,   "longitud": 4},
    3: {"espera_racha": False, "inicio": None, "longitud": 0},
    4: {"espera_racha": False, "inicio": None, "longitud": 0},
    5: {"espera_racha": True,  "inicio": 6,    "longitud": 3},
}


# =============================================================================
# FUNCIONES ALGORÍTMICAS (Equivalentes al pseudocódigo)
# =============================================================================
def cargar_dataset(ruta_csv, cant_sensores=CANT_SENSORES, n=N_LECTURAS):
    """
    Lee 'lecturas_sensores.csv' y organiza las lecturas por sensor (1 a 5)
    y número de lectura (1 a 24).
    Utiliza arreglos indexados en base 1 para mantener paridad directa
    con el pseudocódigo ('vec_lecturas = ARREGLO [1..N] de real').
    """
    datos = {s: [0.0] * (n + 1) for s in range(1, cant_sensores + 1)}

    with open(ruta_csv, mode="r", encoding="utf-8") as f:
        lector = csv.DictReader(f)
        for fila in lector:
            sensor = int(fila["sensor"])
            nro = int(fila["nro"])
            valor = float(fila["valor"])
            if 1 <= sensor <= cant_sensores and 1 <= nro <= n:
                datos[sensor][nro] = valor

    return datos


def calcular_estadisticas(a, n=N_LECTURAS):
    """
    Equivalente estricto al procedimiento 'CalcularEstadisticas' del pseudocódigo:
    Recorre el arreglo en una única pasada (complejidad O(N)).
    Calcula:
      - Máximo (valor y posición)
      - Mínimo (valor y posición)
      - Promedio general
    Retorna: (pos_max, max_val, pos_min, min_val, prom)
    """
    max_val = a[1]
    pos_max = 1
    min_val = a[1]
    pos_min = 1
    suma = a[1]

    for i in range(2, n + 1):
        # Búsqueda de máximo
        if a[i] > max_val:
            max_val = a[i]
            pos_max = i

        # Búsqueda de mínimo
        if a[i] < min_val:
            min_val = a[i]
            pos_min = i

        suma += a[i]

    prom = suma / n
    return pos_max, max_val, pos_min, min_val, prom


def detectar_racha(a, n=N_LECTURAS, long_min=LONG_MIN_RACHA, umbral=UMBRAL_ANOMALIA):
    """
    Equivalente estricto al procedimiento 'DetectarRacha' del pseudocódigo:
    Recorre linealmente las lecturas con corte anticipado al detectar la
    primera racha de al menos 'long_min' lecturas consecutivas sobre 'umbral'.
    Si el valor supera el umbral, incrementa contador; si no, lo reinicia a 0.
    Retorna: (hay_racha, pos_inicio)
    """
    i = 1
    cont_racha = 0
    hay_racha = False
    pos_inicio = 0

    while i <= n and not hay_racha:
        if a[i] > umbral:
            cont_racha += 1
            if cont_racha >= long_min:
                hay_racha = True
                pos_inicio = i - long_min + 1
        else:
            cont_racha = 0
        i += 1

    return hay_racha, pos_inicio


# =============================================================================
# ENTORNO DE PRUEBAS Y VALIDACIÓN
# =============================================================================
def ejecutar_validacion():
    ruta_script = os.path.dirname(os.path.abspath(__file__))
    ruta_csv = os.path.join(ruta_script, "lecturas_sensores.csv")

    if not os.path.exists(ruta_csv):
        print(f"Error: No se encontró el archivo '{ruta_csv}'.")
        return

    # 1. Carga y parseo del dataset
    datos = cargar_dataset(ruta_csv, CANT_SENSORES, N_LECTURAS)

    print("=" * 70)
    print(" ENTORNO DE PRUEBAS Y VERIFICACIÓN ALGORÍTMICA - AED (ACTIVIDAD 3)")
    print("=" * 70)

    # Contadores de validación global
    vp = 0  # Verdaderos Positivos
    vn = 0  # Verdaderos Negativos
    fp = 0  # Falsos Positivos
    fn = 0  # Falsos Negativos

    sensor_mayor_prom = None
    mayor_prom_val = float("-inf")

    # 2. Procesamiento sensor por sensor
    for sensor in range(1, CANT_SENSORES + 1):
        lecturas = datos[sensor]
        verdad = VERDAD_CONOCIDA[sensor]

        # Estadísticas en una pasada
        pos_max, max_val, pos_min, min_val, prom = calcular_estadisticas(lecturas, N_LECTURAS)

        # Registro del sensor con mayor promedio térmico
        if prom > mayor_prom_val:
            mayor_prom_val = prom
            sensor_mayor_prom = sensor

        # Detección de racha algorítmica
        hay_racha, pos_inicio = detectar_racha(lecturas, N_LECTURAS, LONG_MIN_RACHA, UMBRAL_ANOMALIA)

        # Clasificación frente a la verdad conocida
        espera_racha = verdad["espera_racha"]
        if hay_racha and espera_racha:
            if pos_inicio == verdad["inicio"]:
                clasificacion = "Acierto (Verdadero Positivo)"
                vp += 1
            else:
                clasificacion = f"Falso Positivo (detectada en #{pos_inicio}, esperada en #{verdad['inicio']})"
                fp += 1
        elif not hay_racha and not espera_racha:
            clasificacion = "Verdadero Negativo"
            vn += 1
        elif hay_racha and not espera_racha:
            clasificacion = "Falso Positivo"
            fp += 1
        else:  # not hay_racha and espera_racha
            clasificacion = "Falso Negativo"
            fn += 1

        # Impresión de resultados por sensor
        print(f"\n--- SENSOR {sensor} ---")
        print(f"  * Métricas térmicas:")
        print(f"      - Máximo  : {max_val:.2f} °C (en lectura #{pos_max})")
        print(f"      - Mínimo  : {min_val:.2f} °C (en lectura #{pos_min})")
        print(f"      - Promedio: {prom:.2f} °C")
        print(f"  * Detección de racha (Umbral > {UMBRAL_ANOMALIA:.1f} °C, Long >= {LONG_MIN_RACHA}):")
        if hay_racha:
            print(f"      - Resultado : Racha DETECTADA (inicio en lectura #{pos_inicio})")
        else:
            print(f"      - Resultado : Sin racha anómala")
        print(f"  * Clasificación de validación: {clasificacion}")

    # 3. Resumen global del experimento
    total_aciertos = vp + vn
    print("\n" + "=" * 70)
    print(" RESUMEN GLOBAL DEL EXPERIMENTO")
    print("=" * 70)
    print(f"  * Total de Sensores Evaluados : {CANT_SENSORES}")
    print(f"  * Total de Aciertos           : {total_aciertos}/{CANT_SENSORES} (VP: {vp}, VN: {vn})")
    print(f"  * Falsos Positivos (FP)       : {fp}")
    print(f"  * Falsos Negativos (FN)       : {fn}")
    print(f"  * Tasa de Exactitud (Accuracy): {(total_aciertos / CANT_SENSORES) * 100:.1f}%")
    print("-" * 70)
    print(f"  * Sensor con Mayor Promedio Térmico: SENSOR {sensor_mayor_prom} ({mayor_prom_val:.2f} °C)")
    print("=" * 70)


if __name__ == "__main__":
    ejecutar_validacion()
