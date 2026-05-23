# =============================================================================
# data/storage.py
# Proyecto KRONOS — Subred Norte E.S.E., Bogotá D.C.
# Módulo 4: Persistencia y Gestión (CRUD)
# Autores: Yuliana Barcelo, Valentina Luna, Gabriela Julio
# =============================================================================

"""
Gestiona el almacenamiento local de registros en un archivo JSON.

Formato del archivo:
    Lista de dicts planos, cada uno con las mismas claves que acepta
    RegistroPaciente.from_json(), más el campo 'id_registro'.

Todas las funciones operan sobre ese archivo; la capa superior
(main.py o el CLI) trabaja siempre con objetos RegistroPaciente.
"""

import json
import os
from models.entidades import RegistroPaciente

# Ruta del archivo de persistencia local
ARCHIVO_LOCAL = os.path.join(os.path.dirname(__file__), "datos_local.json")

# Campos que se pueden editar con actualizar()
CAMPOS_EDITABLES = {
    "edad", "peso", "talla", "plan_beneficios", "sede",
    "nombre_diag", "codigo_cie10",
    "cardiovascular", "pulmonar", "neurologico", "mental", "osteomuscular",
    "imc", "resultado_imc", "escala_disnea", "bodex"
}


# ---------------------------------------------------------------------------
# Helpers internos (trabajan con dicts crudos)
# ---------------------------------------------------------------------------

def _cargar_crudos() -> list[dict]:
    """Lee el archivo JSON y retorna la lista de dicts crudos."""
    if not os.path.exists(ARCHIVO_LOCAL):
        return []
    try:
        with open(ARCHIVO_LOCAL, "r", encoding="utf-8") as f:
            datos = json.load(f)
            if isinstance(datos, list):
                return datos
            return []
    except (json.JSONDecodeError, OSError) as e:
        print(f"[Storage] Error al leer {ARCHIVO_LOCAL}: {e}")
        return []


def _guardar_crudos(datos: list[dict]) -> None:
    """Escribe la lista de dicts crudos al archivo JSON."""
    try:
        with open(ARCHIVO_LOCAL, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"[Storage] Error al guardar {ARCHIVO_LOCAL}: {e}")


def _siguiente_id(datos: list[dict]) -> int:
    """Genera el próximo id_registro disponible."""
    if not datos:
        return 1
    return max(int(d.get("id_registro", 0)) for d in datos) + 1


# ---------------------------------------------------------------------------
# CREATE — guardar lista completa desde la API
# ---------------------------------------------------------------------------

def guardar(registros: list[RegistroPaciente]) -> int:
    """
    Reemplaza el almacenamiento local con la lista recibida.
    Útil para la carga inicial desde la API.

    Retorna el número de registros guardados.
    """
    datos = [r.to_raw_dict() for r in registros]
    _guardar_crudos(datos)
    return len(datos)


# ---------------------------------------------------------------------------
# CREATE — agregar un registro individual
# ---------------------------------------------------------------------------

def agregar(datos_nuevos: dict) -> RegistroPaciente:
    """
    Agrega un nuevo registro al almacenamiento local.

    Parámetros
    ----------
    datos_nuevos : dict
        Dict con los campos del paciente (mismas claves que from_json()).
        No necesita incluir 'id_registro'; se asigna automáticamente.

    Retorna
    -------
    RegistroPaciente con el id_registro asignado.
    """
    datos = _cargar_crudos()
    nuevo_id = _siguiente_id(datos)
    datos_nuevos["id_registro"] = nuevo_id
    datos.append(datos_nuevos)
    _guardar_crudos(datos)
    return RegistroPaciente.from_json(datos_nuevos, id_registro=nuevo_id)


# ---------------------------------------------------------------------------
# READ — leer todos los registros
# ---------------------------------------------------------------------------

def leer_todos() -> list[RegistroPaciente]:
    """
    Carga todos los registros del archivo local.

    Retorna
    -------
    list[RegistroPaciente] ordenada por id_registro.
    """
    datos = _cargar_crudos()
    registros = [
        RegistroPaciente.from_json(d, id_registro=int(d.get("id_registro", i + 1)))
        for i, d in enumerate(datos)
    ]
    return sorted(registros, key=lambda r: r.id_registro)


# ---------------------------------------------------------------------------
# READ — buscar por id
# ---------------------------------------------------------------------------

def buscar_por_id(id_registro: int) -> RegistroPaciente | None:
    """
    Retorna el RegistroPaciente con ese id_registro, o None si no existe.
    """
    datos = _cargar_crudos()
    for d in datos:
        if int(d.get("id_registro", -1)) == id_registro:
            return RegistroPaciente.from_json(d, id_registro=id_registro)
    return None


# ---------------------------------------------------------------------------
# READ — filtrar por campo
# ---------------------------------------------------------------------------

def filtrar(campo: str, valor: str) -> list[RegistroPaciente]:
    """
    Retorna registros donde el campo indicado coincide con el valor
    (comparación insensible a mayúsculas/minúsculas).

    Ejemplo: filtrar("sede", "USAQUÉN")
    """
    datos = _cargar_crudos()
    campo = campo.strip().lower()
    valor = valor.strip().lower()

    coincidencias = [
        d for d in datos
        if str(d.get(campo, "")).strip().lower() == valor
    ]

    return [
        RegistroPaciente.from_json(d, id_registro=int(d.get("id_registro", i + 1)))
        for i, d in enumerate(coincidencias)
    ]


# ---------------------------------------------------------------------------
# UPDATE — actualizar un campo de un registro
# ---------------------------------------------------------------------------

def actualizar(id_registro: int, campo: str, nuevo_valor: str) -> bool:
    """
    Modifica el valor de un campo en el registro indicado.

    Parámetros
    ----------
    id_registro  : int — id del registro a editar
    campo        : str — nombre del campo (ver CAMPOS_EDITABLES)
    nuevo_valor  : str — nuevo valor a asignar

    Retorna
    -------
    True si el registro fue encontrado y actualizado, False si no existe
    o el campo no es editable.
    """
    if campo not in CAMPOS_EDITABLES:
        print(f"[Storage] Campo '{campo}' no es editable.")
        print(f"          Campos válidos: {', '.join(sorted(CAMPOS_EDITABLES))}")
        return False

    datos = _cargar_crudos()

    for d in datos:
        if int(d.get("id_registro", -1)) == id_registro:
            d[campo] = nuevo_valor
            _guardar_crudos(datos)
            return True

    print(f"[Storage] No se encontró el registro con id={id_registro}.")
    return False


# ---------------------------------------------------------------------------
# DELETE — eliminar un registro
# ---------------------------------------------------------------------------

def eliminar(id_registro: int) -> bool:
    """
    Elimina el registro con el id indicado del almacenamiento local.

    Retorna
    -------
    True si fue eliminado, False si no se encontró.
    """
    datos = _cargar_crudos()
    nuevos_datos = [d for d in datos if int(d.get("id_registro", -1)) != id_registro]

    if len(nuevos_datos) == len(datos):
        print(f"[Storage] No se encontró el registro con id={id_registro}.")
        return False

    _guardar_crudos(nuevos_datos)
    return True


# ---------------------------------------------------------------------------
# UTILIDAD — total de registros almacenados
# ---------------------------------------------------------------------------

def total() -> int:
    """Retorna la cantidad de registros en el almacenamiento local."""
    return len(_cargar_crudos())


# ---------------------------------------------------------------------------
# Prueba rápida (ejecutar directamente: python data/storage.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from models.entidades import (
        Paciente, DiagnosticoCronico, EstadoClinico,
        MedicionAntropometrica, EvaluacionPulmonar, RegistroPaciente
    )

    print("=== Prueba Módulo 4 — CRUD Local ===\n")

    # Limpiar estado previo para que la prueba sea reproducible
    if os.path.exists(ARCHIVO_LOCAL):
        os.remove(ARCHIVO_LOCAL)

    # --- CREATE: agregar dos registros de prueba ---
    r1 = agregar({
        "edad": "68", "peso": "85.0", "talla": "167.0",
        "plan_beneficios": "SUBSIDIADO", "sede": "USAQUÉN",
        "nombre_diag": "HIPERTENSION ESENCIAL (PRIMARIA)", "codigo_cie10": "I10",
        "cardiovascular": "Anormal", "pulmonar": "Normal",
        "neurologico": "Normal", "mental": "Normal", "osteomuscular": "Normal",
        "imc": "30.63", "resultado_imc": "OBESIDAD I",
        "escala_disnea": "MUY GRAVE", "bodex": None
    })
    r2 = agregar({
        "edad": "45", "peso": "70.0", "talla": "160.0",
        "plan_beneficios": "CONTRIBUTIVO", "sede": "SUBA",
        "nombre_diag": "DIABETES MELLITUS TIPO 2", "codigo_cie10": "E11",
        "cardiovascular": "Normal", "pulmonar": "Anormal",
        "neurologico": "Normal", "mental": "Anormal", "osteomuscular": "Normal",
        "imc": "27.3", "resultado_imc": "SOBREPESO",
        "escala_disnea": "LEVE", "bodex": None
    })

    print(f"[CREATE] Agregados: {r1} | {r2}")

    # --- READ: leer todos ---
    todos = leer_todos()
    print(f"\n[READ]   Total en almacenamiento: {len(todos)} registros")
    for r in todos:
        print(f"         {r}")

    # --- UPDATE: corregir sede del registro 1 ---
    ok = actualizar(1, "sede", "ENGATIVÁ")
    print(f"\n[UPDATE] Cambiar sede del registro #1 → {'OK' if ok else 'FALLÓ'}")
    print(f"         {buscar_por_id(1)}")

    # --- DELETE: eliminar registro 2 ---
    ok = eliminar(2)
    print(f"\n[DELETE] Eliminar registro #2 → {'OK' if ok else 'FALLÓ'}")
    print(f"         Total restante: {total()}")
