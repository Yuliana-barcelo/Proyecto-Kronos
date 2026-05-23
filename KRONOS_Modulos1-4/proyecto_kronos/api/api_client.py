# =============================================================================
# api/api_client.py
# Proyecto KRONOS — Subred Norte E.S.E., Bogotá D.C.
# Módulo 3: Consumo de API
# Autores: Yuliana Barcelo, Valentina Luna, Gabriela Julio
# =============================================================================

import requests
from models.entidades import RegistroPaciente

# URL base del dataset en datos.gov.co (API Socrata)
URL_BASE = "https://www.datos.gov.co/resource/2uxx-gxp3.json"


class APIClient:
    """
    Cliente HTTP para consumir el dataset de Enfermedades Crónicas
    de la Subred Norte E.S.E. desde datos.gov.co.

    Usa la API Socrata, que recibe parámetros de filtro directamente
    en la query string y soporta $limit para controlar el total de filas.
    """

    def __init__(self, url: str = URL_BASE, timeout: int = 15):
        self.url     = url
        self.timeout = timeout

    # ------------------------------------------------------------------
    # Método principal de consulta
    # ------------------------------------------------------------------

    def obtener_registros(self,
                          filtros: dict | None = None,
                          limit: int = 100) -> list[RegistroPaciente]:
        """
        Consulta la API y retorna una lista de RegistroPaciente.

        Parámetros
        ----------
        filtros : dict | None
            Pares campo=valor para filtrar en la API.
            Ejemplo: {"resultado_imc": "OBESIDAD I", "pulmonar": "Anormal"}
            IMPORTANTE: los nombres de campo deben coincidir exactamente
            con las claves JSON del dataset (ej. 'resultado_imc', no 'resultadoimc').
        limit : int
            Máximo de registros a traer (se envía como parámetro $limit
            en la URL para no descargar el dataset completo).

        Retorna
        -------
        list[RegistroPaciente]  — lista vacía si ocurre un error.
        """
        params: dict = {"$limit": limit}

        if filtros:
            params.update(filtros)

        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; KRONOS-App/1.0)",
            "Accept": "application/json",
        }

        try:
            respuesta = requests.get(self.url, params=params,
                                     headers=headers, timeout=self.timeout)
            respuesta.raise_for_status()

            datos_crudos: list[dict] = respuesta.json()

            if not isinstance(datos_crudos, list):
                print("[APIClient] Respuesta inesperada: no es una lista.")
                return []

            registros = [
                RegistroPaciente.from_json(fila, id_registro=i + 1)
                for i, fila in enumerate(datos_crudos)
            ]

            return registros

        except requests.exceptions.ConnectionError:
            print("[APIClient] Error: no hay conexión a internet.")
        except requests.exceptions.Timeout:
            print(f"[APIClient] Error: la API no respondió en {self.timeout}s.")
        except requests.exceptions.HTTPError as e:
            print(f"[APIClient] Error HTTP {e.response.status_code}: {e}")
        except requests.exceptions.RequestException as e:
            print(f"[APIClient] Error inesperado en la petición: {e}")

        return []

    # ------------------------------------------------------------------
    # Consulta con filtros predefinidos (accesos directos útiles)
    # ------------------------------------------------------------------

    def obtener_por_sede(self, sede: str, limit: int = 50) -> list[RegistroPaciente]:
        """Filtra registros por sede de atención."""
        return self.obtener_registros(filtros={"sede": sede.upper()}, limit=limit)

    def obtener_alto_riesgo(self, limit: int = 50) -> list[RegistroPaciente]:
        """
        Trae pacientes con pulmonar Anormal y escala de disnea GRAVE,
        criterios de alto riesgo según calcularPuntajeRiesgo().
        """
        return self.obtener_registros(
            filtros={"pulmonar": "Anormal", "escala_disnea": "GRAVE"},
            limit=limit
        )


# ---------------------------------------------------------------------------
# Prueba rápida (ejecutar directamente: python api/api_client.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cliente = APIClient()

    print("=== Prueba Módulo 3 — Consumo de API ===\n")

    # Consulta sin filtros
    print("1) Sin filtros (primeros 5 registros):")
    registros = cliente.obtener_registros(limit=5)
    for r in registros:
        print(f"   {r}")

    # Consulta con filtros
    print("\n2) Filtrado: resultado_imc=OBESIDAD I, pulmonar=Anormal")
    filtrados = cliente.obtener_registros(
        filtros={"resultado_imc": "OBESIDAD I", "pulmonar": "Anormal"},
        limit=5
    )
    if filtrados:
        for r in filtrados:
            print(f"   {r} | Puntaje: {r.calcularPuntajeRiesgo()}/4")
    else:
        print("   Sin resultados con esos filtros.")
