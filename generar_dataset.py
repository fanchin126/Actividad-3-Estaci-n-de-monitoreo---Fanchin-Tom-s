"""
Simulador de Estación de Monitoreo Ambiental - Algoritmos y Estructuras de Datos
Generación de dataset sintético con modelo físico y anomalías conocidas (Ground Truth).
"""

import csv
import math
import random
from typing import List, Tuple

# ==============================================================================
# CONFIGURACIÓN Y PARÁMETROS DEL EXPERIMENTO
# ==============================================================================
SEMILLA_ALEATORIA = 42

# Dimensiones del experimento
CANT_SENSORES = 5         # M = 5 (Identificadores 1 al 5)
LECTURAS_POR_SENSOR = 24  # N = 24 (Horas 1 a 24 del ciclo diario)
ARCHIVO_SALIDA = "lecturas_sensores.csv"

# Parámetros del modelo físico térmico nominal (Sinusoide)
# T_min = 18.0 °C (madrugada/06:00 h), T_max = 33.0 °C (tarde/15:00 h)
TEMP_MEDIA = 25.5         # (33.0 + 18.0) / 2
AMPLITUD_TERMICA = 7.5    # (33.0 - 18.0) / 2
HORA_PICO = 15.0          # Máximo térmico a las 15:00 h

# Parámetros de ruido instrumental y deriva
RUIDO_NOMINAL_STD = 0.4   # Desviación estándar baja (Sensores 1, 2, 3 y 5)
RUIDO_DIVERGENTE_STD = 1.2 # Mayor dispersión térmica (Sensor 4)
DRIFT_LINEAL_PASO = 0.25  # Pérdida de calibración (+0.25 °C por lectura en Sensor 4)


def calcular_temperatura_base(hora: int) -> float:
    """
    Calcula el componente térmico nominal diurno mediante una función sinusoidal.
    
    El modelo alcanza su pico a las 15:00 h (33.0 °C) y su mínimo en la madrugada
    (18.0 °C a las 03:00 h, rondando 20.2 °C a las 06:00 h).
    """
    # Desplazamiento de fase para que el seno alcance +1 en hora = 15
    fase = 2.0 * math.pi * (hora - (HORA_PICO - 6.0)) / 24.0
    return TEMP_MEDIA + AMPLITUD_TERMICA * math.sin(fase)


def simular_lectura(sensor_id: int, nro_lectura: int) -> float:
    """
    Genera el valor de temperatura para un sensor y lectura dados, aplicando
    las reglas de comportamiento físico o inyección de anomalías conocidas.
    """
    # -------------------------------------------------------------------------
    # Inyección de anomalías conocidas (Ground Truth)
    # -------------------------------------------------------------------------
    # Racha 1: Sensor 2, lecturas 13 a 16 (longitud 4), valores entre 44.0 y 47.0 °C
    if sensor_id == 2 and 13 <= nro_lectura <= 16:
        return random.uniform(44.0, 47.0)

    # Racha 2: Sensor 5, lecturas 6 a 8 (longitud 3), saturados en torno a 51.5 °C
    if sensor_id == 5 and 6 <= nro_lectura <= 8:
        return random.gauss(51.5, 0.2)

    # -------------------------------------------------------------------------
    # Comportamiento físico estándar
    # -------------------------------------------------------------------------
    t_base = calcular_temperatura_base(nro_lectura)

    if sensor_id == 4:
        # Sensor divergente: Ruido elevado y deriva paulatina de calibración
        ruido = random.gauss(0.0, RUIDO_DIVERGENTE_STD)
        deriva = DRIFT_LINEAL_PASO * nro_lectura
        return t_base + deriva + ruido

    # Sensores 1, 2, 3 y 5 (en lecturas normales): Comportamiento nominal
    ruido = random.gauss(0.0, RUIDO_NOMINAL_STD)
    return t_base + ruido


def generar_dataset() -> List[Tuple[int, int, float]]:
    """
    Simula la matriz completa de lecturas para M sensores y N lecturas por sensor.
    Retorna una lista de tuplas (sensor, nro, valor_redondeado).
    """
    registros = []
    for s in range(1, CANT_SENSORES + 1):
        for nro in range(1, LECTURAS_POR_SENSOR + 1):
            val = simular_lectura(sensor_id=s, nro_lectura=nro)
            registros.append((s, nro, round(val, 2)))
    return registros


def exportar_csv(datos: List[Tuple[int, int, float]], ruta_archivo: str) -> None:
    """
    Escribe los registros en formato CSV con encabezado exacto: sensor,nro,valor.
    """
    encabezados = ["sensor", "nro", "valor"]
    with open(ruta_archivo, mode="w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(encabezados)
        escritor.writerows(datos)


def main() -> None:
    # 1. Fijar semilla aleatoria para reproducibilidad matemática estricta
    random.seed(SEMILLA_ALEATORIA)

    # 2. Generar datos simulados
    registros = generar_dataset()

    # 3. Exportar a CSV
    exportar_csv(registros, ARCHIVO_SALIDA)

    # 4. Confirmación por consola
    print(
        f"Archivo '{ARCHIVO_SALIDA}' generado exitosamente con {len(registros)} registros."
    )


if __name__ == "__main__":
    main()
