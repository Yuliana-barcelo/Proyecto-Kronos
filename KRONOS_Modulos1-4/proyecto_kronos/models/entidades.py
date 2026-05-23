# =============================================================================
# models/entidades.py
# Proyecto KRONOS — Subred Norte E.S.E., Bogotá D.C.
# Módulo 2: Estructuras y Clases
# Autores: Yuliana Barcelo, Valentina Luna, Gabriela Julio
# =============================================================================

# NOTA: La API Socrata entrega todos los campos como str.
# La conversión a tipos nativos se hace aquí, en la capa del modelo.


# ---------------------------------------------------------------------------
# Entidad base
# ---------------------------------------------------------------------------

class Entidad:

    def to_dict(self) -> dict:
        """Devuelve una representación en diccionario del objeto."""
        return self.__dict__

    def __repr__(self) -> str:
        nombre_clase = self.__class__.__name__
        campos = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{nombre_clase}({campos})"


# ---------------------------------------------------------------------------
# Sub-entidades (componen a RegistroPaciente)
# ---------------------------------------------------------------------------

class Paciente(Entidad):
    """Datos demográficos y administrativos del paciente."""

    def __init__(self, edad: int, peso: float, talla: float,
                 plan_beneficios: str, sede: str):
        self.edad            = edad
        self.peso            = peso
        self.talla           = talla
        self.plan_beneficios = plan_beneficios
        self.sede            = sede

    def esAdultoMayor(self) -> bool:
        """Retorna True si el paciente tiene 60 años o más."""
        return self.edad >= 60


class DiagnosticoCronico(Entidad):
    """Diagnóstico principal registrado en CIE-10."""

    def __init__(self, nombre_diagnostico: str, codigo_cie10: str = ""):
        self.nombre_diagnostico = nombre_diagnostico
        self.codigo_cie10       = codigo_cie10


class EstadoClinico(Entidad):
    """Estado de los cinco sistemas clínicos evaluados."""

    SISTEMAS = ("cardiovascular", "pulmonar", "neurologico", "mental", "osteomuscular")

    def __init__(self, cardiovascular: str, pulmonar: str,
                 neurologico: str, mental: str, osteomuscular: str):
        self.cardiovascular = cardiovascular
        self.pulmonar       = pulmonar
        self.neurologico    = neurologico
        self.mental         = mental
        self.osteomuscular  = osteomuscular

    def contarSistemasAnormales(self) -> int:
        """Cuenta cuántos sistemas tienen estado 'Anormal'."""
        valores = [self.cardiovascular, self.pulmonar,
                   self.neurologico, self.mental, self.osteomuscular]
        return sum(1 for v in valores if isinstance(v, str) and v.strip().lower() == "anormal")


class MedicionAntropometrica(Entidad):
    """Mediciones de IMC y su clasificación OMS."""

    CATEGORIAS_OBESIDAD = {"OBESIDAD I", "OBESIDAD II", "OBESIDAD III", "OBESIDAD MORBIDA"}

    def __init__(self, imc_valor: float, resultado_imc: str):
        self.imc_valor     = imc_valor
        self.resultado_imc = resultado_imc

    def tieneObesidad(self) -> bool:
        """Retorna True si la clasificación OMS indica algún grado de obesidad."""
        return self.resultado_imc.strip().upper() in self.CATEGORIAS_OBESIDAD


class EvaluacionPulmonar(Entidad):
    """Escala de disnea MRC y estadio BODEX (EPOC)."""

    ESCALAS_CRITICAS = {"GRAVE", "MUY GRAVE", "MUY_GRAVE"}

    def __init__(self, escala_disnea: str, bodex: str | None = None):
        self.escala_disnea = escala_disnea
        self.bodex         = bodex   # puede ser None si no aplica

    def esCritica(self) -> bool:
        """Retorna True si la escala de disnea es GRAVE o MUY GRAVE."""
        return self.escala_disnea.strip().upper() in self.ESCALAS_CRITICAS


# ---------------------------------------------------------------------------
# Registro
# ---------------------------------------------------------------------------

class Registro(Entidad):
    """Clase intermedia que representa un registro genérico de datos.
    RegistroPaciente hereda de ella para cumplir con el enunciado del módulo."""

    def __init__(self, id_registro: int = 0):
        self.id_registro = id_registro


# ---------------------------------------------------------------------------
# RegistroPaciente — entidad principal
# ---------------------------------------------------------------------------

class RegistroPaciente(Registro):
    """
    Consolidado completo de un paciente crónico de la Subred Norte E.S.E.
    Usa composición (*--) porque los datos clínicos y demográficos dependen
    de la existencia del registro.
    """

    def __init__(self,
                 paciente: Paciente,
                 diagnostico: DiagnosticoCronico,
                 estado_clinico: EstadoClinico,
                 medicion: MedicionAntropometrica,
                 evaluacion_pulmonar: EvaluacionPulmonar,
                 id_registro: int = 0):

        super().__init__(id_registro)
        self.paciente            = paciente
        self.diagnostico         = diagnostico
        self.estado_clinico      = estado_clinico
        self.medicion            = medicion
        self.evaluacion_pulmonar = evaluacion_pulmonar

    # -------------------------------------------------------------------
    # Factory method: construye un RegistroPaciente desde el JSON de la API
    # -------------------------------------------------------------------

    @classmethod
    def from_json(cls, json_data: dict, id_registro: int = 0) -> "RegistroPaciente":
        """
        Convierte un dict proveniente de la API Socrata (todos los valores son str)
        en un RegistroPaciente con tipos nativos de Python.

        Soporta los nombres de campo reales de la API:
          - nombre_dx      (API) o nombre_diag   (registros manuales)
          - resultadoimc   (API) o resultado_imc  (registros manuales)
          - neurol_gico    (API) o neurologico    (registros manuales)
        """

        def a_int(valor, defecto: int = 0) -> int:
            try:
                return int(float(valor))
            except (TypeError, ValueError):
                return defecto

        def a_float(valor, defecto: float = 0.0) -> float:
            try:
                return float(valor)
            except (TypeError, ValueError):
                return defecto

        def a_str(valor, defecto: str = "") -> str:
            return str(valor).strip() if valor is not None else defecto

        # Si el dict ya trae id_registro guardado (desde storage local), lo usa
        id_final = int(json_data.get("id_registro", id_registro)) or id_registro

        paciente = Paciente(
            edad            = a_int(json_data.get("edad")),
            peso            = a_float(json_data.get("peso")),
            talla           = a_float(json_data.get("talla")),
            plan_beneficios = a_str(json_data.get("plan_beneficios")),
            sede            = a_str(json_data.get("sede"))
        )

        diagnostico = DiagnosticoCronico(
            nombre_diagnostico = a_str(json_data.get("nombre_dx") or json_data.get("nombre_diag")),
            codigo_cie10       = a_str(json_data.get("codigo_cie10"))
        )

        estado_clinico = EstadoClinico(
            cardiovascular = a_str(json_data.get("cardiovascular")),
            pulmonar       = a_str(json_data.get("pulmonar")),
            neurologico    = a_str(json_data.get("neurol_gico") or json_data.get("neurologico")),
            mental         = a_str(json_data.get("mental")),
            osteomuscular  = a_str(json_data.get("osteomuscular"))
        )

        medicion = MedicionAntropometrica(
            imc_valor     = a_float(json_data.get("imc")),
            resultado_imc = a_str(json_data.get("resultadoimc") or json_data.get("resultado_imc"))
        )

        evaluacion_pulmonar = EvaluacionPulmonar(
            escala_disnea = a_str(json_data.get("escala_disnea")),
            bodex         = json_data.get("bodex")
        )

        return cls(
            paciente            = paciente,
            diagnostico         = diagnostico,
            estado_clinico      = estado_clinico,
            medicion            = medicion,
            evaluacion_pulmonar = evaluacion_pulmonar,
            id_registro         = id_final
        )

    # -------------------------------------------------------------------
    # Serialización — necesaria para persistencia local (Módulo 4)
    # -------------------------------------------------------------------

    def to_raw_dict(self) -> dict:
        """
        Serializa el registro a un dict plano con las mismas claves que usa
        from_json(), más 'id_registro'. Permite guardar y recargar sin pérdida.
        """
        return {
            "id_registro":    self.id_registro,
            "edad":           str(self.paciente.edad),
            "peso":           str(self.paciente.peso),
            "talla":          str(self.paciente.talla),
            "plan_beneficios": self.paciente.plan_beneficios,
            "sede":           self.paciente.sede,
            "nombre_diag":    self.diagnostico.nombre_diagnostico,
            "codigo_cie10":   self.diagnostico.codigo_cie10,
            "cardiovascular": self.estado_clinico.cardiovascular,
            "pulmonar":       self.estado_clinico.pulmonar,
            "neurologico":    self.estado_clinico.neurologico,
            "mental":         self.estado_clinico.mental,
            "osteomuscular":  self.estado_clinico.osteomuscular,
            "imc":            str(self.medicion.imc_valor),
            "resultado_imc":  self.medicion.resultado_imc,
            "escala_disnea":  self.evaluacion_pulmonar.escala_disnea,
            "bodex":          self.evaluacion_pulmonar.bodex,
        }

    # -------------------------------------------------------------------
    # Lógica de riesgo
    # -------------------------------------------------------------------

    def calcularPuntajeRiesgo(self) -> int:
        """
        Calcula el nivel de riesgo del paciente (0-4).

        Criterios (1 punto cada uno):
        +1 — Adulto mayor (>= 60 años)
        +1 — 2 o más sistemas clínicos anormales
        +1 — IMC en rango de obesidad
        +1 — Escala de disnea GRAVE o MUY GRAVE
        """
        puntaje = 0

        if self.paciente.esAdultoMayor():
            puntaje += 1

        if self.estado_clinico.contarSistemasAnormales() >= 2:
            puntaje += 1

        if self.medicion.tieneObesidad():
            puntaje += 1

        if self.evaluacion_pulmonar.esCritica():
            puntaje += 1

        return puntaje

    def __str__(self) -> str:
        bodex_str = self.evaluacion_pulmonar.bodex if self.evaluacion_pulmonar.bodex else "N/A"
        return (
            f"[#{self.id_registro}] "
            f"Edad: {self.paciente.edad} | "
            f"Sede: {self.paciente.sede} | "
            f"Plan: {self.paciente.plan_beneficios} | "
            f"Diag: {self.diagnostico.nombre_diagnostico} | "
            f"Cardio: {self.estado_clinico.cardiovascular} | "
            f"Pulm: {self.estado_clinico.pulmonar} | "
            f"Neuro: {self.estado_clinico.neurologico} | "
            f"Mental: {self.estado_clinico.mental} | "
            f"Osteo: {self.estado_clinico.osteomuscular} | "
            f"IMC: {self.medicion.imc_valor} ({self.medicion.resultado_imc}) | "
            f"Disnea: {self.evaluacion_pulmonar.escala_disnea} | "
            f"BODEX: {bodex_str} | "
            f"Riesgo: {self.calcularPuntajeRiesgo()}/4"
        )


# ---------------------------------------------------------------------------
# Prueba rápida (ejecutar directamente: python models/entidades.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    muestra = {
        "edad": "68",
        "peso": "85.0",
        "talla": "167.0",
        "plan_beneficios": "SUBSIDIADO",
        "sede": "USAQUEN",
        "nombre_dx": "HIPERTENSION ESENCIAL (PRIMARIA)",
        "cardiovascular": "Anormal",
        "pulmonar": "Normal",
        "neurol_gico": "Normal",
        "mental": "Normal",
        "osteomuscular": "Normal",
        "imc": "30.63",
        "resultadoimc": "OBESIDAD I",
        "escala_disnea": "MUY GRAVE",
        "bodex": None
    }

    registro = RegistroPaciente.from_json(muestra, id_registro=1)

    print("=== Prueba Módulo 2 ===")
    print(registro)
    print(f"  Adulto mayor:        {registro.paciente.esAdultoMayor()}")
    print(f"  Sistemas anormales:  {registro.estado_clinico.contarSistemasAnormales()}")
    print(f"  Tiene obesidad:      {registro.medicion.tieneObesidad()}")
    print(f"  Evaluacion critica:  {registro.evaluacion_pulmonar.esCritica()}")
    print(f"  Puntaje de riesgo:   {registro.calcularPuntajeRiesgo()}/4")