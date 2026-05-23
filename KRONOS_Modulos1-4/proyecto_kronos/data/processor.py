# =============================================================================
# data/processor.py
# Proyecto KRONOS — Subred Norte E.S.E., Bogotá D.C.
# Módulo 6: Análisis de Datos (base para módulos posteriores)
# Autores: Yuliana Barcelo, Valentina Luna, Gabriela Julio
# =============================================================================

"""
Funciones de análisis y filtrado que operan sobre listas de RegistroPaciente.
No acceden al archivo JSON ni a la API directamente; reciben los datos ya cargados.
"""

from models.entidades import RegistroPaciente
from collections import Counter


# ---------------------------------------------------------------------------
# Filtros
# ---------------------------------------------------------------------------

def filtrar_adultos_mayores(registros: list[RegistroPaciente]) -> list[RegistroPaciente]:
    """Retorna solo los pacientes con 60 años o más."""
    return [r for r in registros if r.paciente.esAdultoMayor()]


def filtrar_por_riesgo(registros: list[RegistroPaciente],
                       puntaje_minimo: int = 3) -> list[RegistroPaciente]:
    """Retorna pacientes cuyo puntaje de riesgo >= puntaje_minimo."""
    return [r for r in registros if r.calcularPuntajeRiesgo() >= puntaje_minimo]


def filtrar_por_sede(registros: list[RegistroPaciente],
                     sede: str) -> list[RegistroPaciente]:
    """Filtra registros por sede (insensible a mayúsculas)."""
    sede = sede.strip().upper()
    return [r for r in registros if r.paciente.sede.strip().upper() == sede]


def filtrar_con_obesidad(registros: list[RegistroPaciente]) -> list[RegistroPaciente]:
    """Retorna pacientes con algún grado de obesidad según IMC OMS."""
    return [r for r in registros if r.medicion.tieneObesidad()]


# ---------------------------------------------------------------------------
# Agrupaciones / conteos
# ---------------------------------------------------------------------------

def contar_por_sede(registros: list[RegistroPaciente]) -> dict[str, int]:
    """Retorna un dict {sede: cantidad} ordenado de mayor a menor."""
    conteo = Counter(r.paciente.sede.strip().upper() for r in registros)
    return dict(conteo.most_common())


def contar_por_diagnostico(registros: list[RegistroPaciente]) -> dict[str, int]:
    """Retorna un dict {diagnostico: cantidad} ordenado de mayor a menor."""
    conteo = Counter(r.diagnostico.nombre_diagnostico.strip().upper() for r in registros)
    return dict(conteo.most_common())


def contar_por_puntaje_riesgo(registros: list[RegistroPaciente]) -> dict[int, int]:
    """Retorna un dict {puntaje (0-4): cantidad_de_pacientes}."""
    conteo: dict[int, int] = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    for r in registros:
        conteo[r.calcularPuntajeRiesgo()] += 1
    return conteo


def contar_por_imc(registros: list[RegistroPaciente]) -> dict[str, int]:
    """Retorna un dict {clasificacion_imc: cantidad} ordenado de mayor a menor."""
    conteo = Counter(r.medicion.resultado_imc.strip().upper() for r in registros)
    return dict(conteo.most_common())


# ---------------------------------------------------------------------------
# Estadísticas básicas
# ---------------------------------------------------------------------------

def promedio_edad(registros: list[RegistroPaciente]) -> float:
    """Retorna el promedio de edad de la lista. 0.0 si está vacía."""
    if not registros:
        return 0.0
    return sum(r.paciente.edad for r in registros) / len(registros)


def promedio_imc(registros: list[RegistroPaciente]) -> float:
    """Retorna el promedio de IMC de la lista. 0.0 si está vacía."""
    if not registros:
        return 0.0
    return sum(r.medicion.imc_valor for r in registros) / len(registros)


def resumen(registros: list[RegistroPaciente]) -> dict:
    """
    Genera un resumen estadístico de la lista.

    Retorna un dict con:
      - total              : int
      - adultos_mayores    : int
      - con_obesidad       : int
      - riesgo_alto (≥3)  : int
      - promedio_edad      : float
      - promedio_imc       : float
      - por_sede           : dict
      - por_puntaje_riesgo : dict
    """
    return {
        "total":              len(registros),
        "adultos_mayores":    len(filtrar_adultos_mayores(registros)),
        "con_obesidad":       len(filtrar_con_obesidad(registros)),
        "riesgo_alto":        len(filtrar_por_riesgo(registros, puntaje_minimo=3)),
        "promedio_edad":      round(promedio_edad(registros), 1),
        "promedio_imc":       round(promedio_imc(registros), 2),
        "por_sede":           contar_por_sede(registros),
        "por_puntaje_riesgo": contar_por_puntaje_riesgo(registros),
    }


# ---------------------------------------------------------------------------
# Prueba rápida (ejecutar directamente: python data/processor.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from api.api_client import APIClient

    print("=== Prueba Módulo 6 — Análisis de Datos ===\n")

    cliente = APIClient()
    registros = cliente.obtener_registros(limit=50)

    if not registros:
        print("Sin datos de la API. Verifica la conexión.")
    else:
        r = resumen(registros)
        print(f"Total cargados       : {r['total']}")
        print(f"Adultos mayores      : {r['adultos_mayores']}")
        print(f"Con obesidad         : {r['con_obesidad']}")
        print(f"Riesgo alto (≥3)     : {r['riesgo_alto']}")
        print(f"Promedio edad        : {r['promedio_edad']} años")
        print(f"Promedio IMC         : {r['promedio_imc']}")
        print(f"\nPor puntaje de riesgo:")
        for puntaje, cantidad in r["por_puntaje_riesgo"].items():
            print(f"  {puntaje}/4 → {cantidad} pacientes")
        print(f"\nPor sede (top 5):")
        for sede, cantidad in list(r["por_sede"].items())[:5]:
            print(f"  {sede}: {cantidad}")
