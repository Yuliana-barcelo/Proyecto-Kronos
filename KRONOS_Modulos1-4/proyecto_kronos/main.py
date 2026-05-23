# =============================================================================
# main.py
# Proyecto KRONOS — Subred Norte E.S.E., Bogotá D.C.
# Punto de entrada — Menú CLI (Módulos 1–4)
# Autores: Yuliana Barcelo, Valentina Luna, Gabriela Julio
# =============================================================================

"""
Ejecutar desde la raíz del proyecto:
    python main.py
"""


import sys
sys.stdout.reconfigure(encoding='utf-8')

from api.api_client import APIClient
from data import storage
from data.processor import resumen, filtrar_por_riesgo, filtrar_adultos_mayores
from models.entidades import RegistroPaciente

# Instancia global del cliente API
_cliente = APIClient()

# Campos válidos para editar (se muestra al usuario)
CAMPOS_EDITABLES = sorted(storage.CAMPOS_EDITABLES)


# ---------------------------------------------------------------------------
# Helpers de presentación
# ---------------------------------------------------------------------------

def _separador(titulo: str = "") -> None:
    linea = "=" * 55
    if titulo:
        print(f"\n{linea}")
        print(f"  {titulo}")
        print(linea)
    else:
        print(linea)


def _mostrar_registros(registros: list[RegistroPaciente], cabecera: str = "") -> None:
    if cabecera:
        print(f"\n{cabecera}")
    if not registros:
        print("  (sin resultados)")
        return
    for r in registros:
        print(f"  {r}")


def _pedir_int(mensaje: str, minimo: int = 1) -> int | None:
    """Pide un entero al usuario. Retorna None si la entrada no es válida."""
    try:
        valor = int(input(mensaje).strip())
        if valor < minimo:
            print(f"  El valor mínimo es {minimo}.")
            return None
        return valor
    except ValueError:
        print("  Entrada inválida. Escribe un número entero.")
        return None


# ---------------------------------------------------------------------------
# Acciones del menú
# ---------------------------------------------------------------------------

def accion_consultar_api() -> None:
    """Módulo 3 — consulta la API y guarda localmente."""
    _separador("CONSULTAR API")
    print("  Opciones de consulta:")
    print("  1. Sin filtros (primeros N registros)")
    print("  2. Con filtros personalizados")
    opcion = input("  Elige [1/2]: ").strip()

    filtros = {}
    if opcion == "2":
        print("\n  Campos disponibles para filtrar:")
        print("  sede, resultado_imc, pulmonar, escala_disnea,")
        print("  cardiovascular, neurologico, mental, osteomuscular,")
        print("  plan_beneficios, nombre_diag")
        while True:
            campo = input("\n  Campo (Enter para terminar): ").strip()
            if not campo:
                break
            valor = input(f"  Valor para '{campo}': ").strip()
            if campo and valor:
                filtros[campo] = valor

    limit = _pedir_int("  ¿Cuántos registros traer? (ej. 50): ", minimo=1) or 50

    print(f"\n  Consultando API... (limit={limit}, filtros={filtros or 'ninguno'})")
    registros = _cliente.obtener_registros(filtros=filtros or None, limit=limit)

    if not registros:
        print("  No se obtuvieron datos. Verifica conexión o filtros.")
        return

    guardados = storage.guardar(registros)
    print(f"  ✓ {guardados} registros guardados localmente.")
    _mostrar_registros(registros[:5], cabecera="  Vista previa (primeros 5):")


def accion_ver_todos() -> None:
    """Módulo 4 READ — muestra todos los registros locales."""
    _separador("VER REGISTROS LOCALES")
    registros = storage.leer_todos()
    print(f"  Total almacenado: {storage.total()} registros\n")
    _mostrar_registros(registros)


def accion_buscar_por_id() -> None:
    """Módulo 4 READ — busca un registro por id."""
    _separador("BUSCAR POR ID")
    id_r = _pedir_int("  ID a buscar: ")
    if id_r is None:
        return
    registro = storage.buscar_por_id(id_r)
    if registro:
        print(f"\n  {registro}")
        print(f"  ¿Adulto mayor?       {registro.paciente.esAdultoMayor()}")
        print(f"  Sistemas anormales:  {registro.estado_clinico.contarSistemasAnormales()}")
        print(f"  ¿Tiene obesidad?     {registro.medicion.tieneObesidad()}")
        print(f"  Disnea crítica:      {registro.evaluacion_pulmonar.esCritica()}")
        print(f"  Puntaje de riesgo:   {registro.calcularPuntajeRiesgo()}/4")
    else:
        print(f"  No se encontró el registro #{id_r}.")


def accion_agregar() -> None:
    """Módulo 4 CREATE — agrega un registro manual."""
    _separador("AGREGAR REGISTRO MANUAL")
    print("  Completa los campos (Enter = dejar en blanco):\n")

    datos = {
        "edad":            input("  Edad (años): ").strip(),
        "peso":            input("  Peso (kg): ").strip(),
        "talla":           input("  Talla (cm): ").strip(),
        "plan_beneficios": input("  Plan (CONTRIBUTIVO / SUBSIDIADO): ").strip().upper(),
        "sede":            input("  Sede: ").strip().upper(),
        "nombre_diag":     input("  Diagnóstico: ").strip().upper(),
        "codigo_cie10":    input("  Código CIE-10 (ej. I10): ").strip().upper(),
        "cardiovascular":  input("  Cardiovascular (Normal/Anormal): ").strip().capitalize(),
        "pulmonar":        input("  Pulmonar (Normal/Anormal): ").strip().capitalize(),
        "neurologico":     input("  Neurológico (Normal/Anormal): ").strip().capitalize(),
        "mental":          input("  Mental (Normal/Anormal): ").strip().capitalize(),
        "osteomuscular":   input("  Osteomuscular (Normal/Anormal): ").strip().capitalize(),
        "imc":             input("  IMC (valor numérico): ").strip(),
        "resultado_imc":   input("  Clasificación IMC (ej. OBESIDAD I): ").strip().upper(),
        "escala_disnea":   input("  Escala disnea (LEVE/MODERADO/GRAVE/MUY GRAVE): ").strip().upper(),
        "bodex":           input("  Estadio BODEX (A/B/C/D o Enter si no aplica): ").strip() or None,
    }

    nuevo = storage.agregar(datos)
    print(f"\n  ✓ Registro creado: {nuevo}")


def accion_actualizar() -> None:
    """Módulo 4 UPDATE — edita un campo de un registro."""
    _separador("EDITAR REGISTRO")
    id_r = _pedir_int("  ID del registro a editar: ")
    if id_r is None:
        return

    registro = storage.buscar_por_id(id_r)
    if not registro:
        print(f"  No existe el registro #{id_r}.")
        return

    print(f"\n  Registro actual: {registro}")
    print(f"\n  Campos editables:")
    for i, campo in enumerate(CAMPOS_EDITABLES, 1):
        print(f"    {i:2}. {campo}")

    campo = input("\n  Nombre del campo a editar: ").strip().lower()
    if campo not in storage.CAMPOS_EDITABLES:
        print(f"  '{campo}' no es un campo editable.")
        return

    nuevo_valor = input(f"  Nuevo valor para '{campo}': ").strip()
    ok = storage.actualizar(id_r, campo, nuevo_valor)

    if ok:
        print(f"  ✓ Registro #{id_r} actualizado.")
        print(f"  {storage.buscar_por_id(id_r)}")


def accion_eliminar() -> None:
    """Módulo 4 DELETE — elimina un registro."""
    _separador("ELIMINAR REGISTRO")
    id_r = _pedir_int("  ID del registro a eliminar: ")
    if id_r is None:
        return

    registro = storage.buscar_por_id(id_r)
    if not registro:
        print(f"  No existe el registro #{id_r}.")
        return

    print(f"\n  Vas a eliminar: {registro}")
    confirmar = input("  ¿Confirmar? (s/n): ").strip().lower()
    if confirmar == "s":
        storage.eliminar(id_r)
        print(f"  ✓ Registro #{id_r} eliminado. Total restante: {storage.total()}")
    else:
        print("  Operación cancelada.")


def accion_resumen() -> None:
    """Muestra estadísticas del almacenamiento local."""
    _separador("RESUMEN ESTADÍSTICO")
    registros = storage.leer_todos()

    if not registros:
        print("  No hay datos locales. Consulta la API primero.")
        return

    r = resumen(registros)
    print(f"  Total de registros   : {r['total']}")
    print(f"  Adultos mayores      : {r['adultos_mayores']}")
    print(f"  Con obesidad         : {r['con_obesidad']}")
    print(f"  Riesgo alto (≥3)     : {r['riesgo_alto']}")
    print(f"  Promedio de edad     : {r['promedio_edad']} años")
    print(f"  Promedio de IMC      : {r['promedio_imc']}")

    print(f"\n  Distribución por puntaje de riesgo:")
    for puntaje, cantidad in r["por_puntaje_riesgo"].items():
        barra = "█" * cantidad if cantidad <= 40 else "█" * 40 + f"  (+{cantidad - 40})"
        print(f"    {puntaje}/4 | {barra} {cantidad}")

    print(f"\n  Pacientes por sede (top 8):")
    for sede, cantidad in list(r["por_sede"].items())[:8]:
        print(f"    {sede:<25} {cantidad}")


def accion_filtrar_riesgo() -> None:
    """Filtra registros locales por puntaje de riesgo mínimo."""
    _separador("FILTRAR POR RIESGO")
    puntaje = _pedir_int("  Puntaje mínimo (1-4): ", minimo=1)
    if puntaje is None or puntaje > 4:
        print("  Puntaje inválido.")
        return
    registros = storage.leer_todos()
    filtrados = filtrar_por_riesgo(registros, puntaje_minimo=puntaje)
    _mostrar_registros(
        filtrados,
        cabecera=f"  Pacientes con riesgo ≥ {puntaje}/4 ({len(filtrados)} encontrados):"
    )


# ---------------------------------------------------------------------------
# Menú principal
# ---------------------------------------------------------------------------

MENU = """
╔══════════════════════════════════════════════╗
║          KRONOS — Subred Norte E.S.E.        ║
║         Sistema de Gestión de Pacientes      ║
╠══════════════════════════════════════════════╣
║  API                                         ║
║   1. Consultar API y guardar localmente      ║
╠══════════════════════════════════════════════╣
║  CRUD Local                                  ║
║   2. Ver todos los registros                 ║
║   3. Buscar registro por ID                  ║
║   4. Agregar registro manual                 ║
║   5. Editar un campo de un registro          ║
║   6. Eliminar un registro                    ║
╠══════════════════════════════════════════════╣
║  Análisis                                    ║
║   7. Resumen estadístico                     ║
║   8. Filtrar por puntaje de riesgo           ║
╠══════════════════════════════════════════════╣
║   0. Salir                                   ║
╚══════════════════════════════════════════════╝
"""

ACCIONES = {
    "1": accion_consultar_api,
    "2": accion_ver_todos,
    "3": accion_buscar_por_id,
    "4": accion_agregar,
    "5": accion_actualizar,
    "6": accion_eliminar,
    "7": accion_resumen,
    "8": accion_filtrar_riesgo,
}


def main() -> None:
    while True:
        print(MENU)
        opcion = input("  Elige una opción: ").strip()

        if opcion == "0":
            print("\n  Hasta luego.\n")
            break
        elif opcion in ACCIONES:
            try:
                ACCIONES[opcion]()
            except KeyboardInterrupt:
                print("\n  (operación cancelada con Ctrl+C)")
        else:
            print("  Opción no válida. Elige entre 0 y 8.")

        input("\n  Presiona Enter para continuar...")


if __name__ == "__main__":
    main()
