
Markdown
# 🏥 Proyecto KRONOS

Sistema de consulta y filtrado clínico para pacientes con enfermedades crónicas de la Subred Norte E.S.E., Bogotá D.C.

**Autores:** Yuliana Barcelo, Valentina Luna, Gabriela Julio

---

## 📅 Estructura del Proyecto (Patrón MVC)
```text
El sistema está organizado bajo la siguiente estructura jerárquica para garantizar la modularidad y el orden del código en Python:
proyecto_datos_colombia/
├──main.py (Punto de entrada)
├── api/
│   └── api_client.py (Consumo de datos HTTP)
├── data/
│   ├── processor.py (Análisis y filtrado)
│   └── storage.py (CRUD y Persistencia local JSON)
├── models/
│   └── entidades.py (Clases y Modelo de datos)
├── utils/
│   └── visualizer.py (Gráficas estadísticas)
└── docs/
└── README.md (Documentación del proyecto)

```
---

## 📊 Dataset

| Campo         | Detalle |
|---------------|---------|
| **Nombre** | Enfermedades Crónicas — Subred Norte E.S.E. |
| **Registros** | 2.602 filas · 14 columnas seleccionadas de 29 |
| **URL** | [datos.gov.co/resource/2uxx-gxp3](https://www.datos.gov.co/Salud-y-Protecci-n-Social/Enfermedades-Cr-nicas/2uxx-gxp3/about_data) |
| **API** | `GET https://www.datos.gov.co/resource/2uxx-gxp3.json` |

---

## 📋 Columnas Seleccionadas

De las 29 columnas originales se conservaron 14 con valor directo para la lógica de priorización de riesgo.

| Campo JSON        | Tipo Nativo (Python) | Grupo | Descripción |
| ------------------|----------------------|-------|-------------|
| `edad`            | `int`                | Demografía | Edad en años |
| `peso`            | `float`              | Demografía | Peso en kg |
| `talla`           | `float`              | Demografía | Estatura en cm |
| `plan_beneficios` | `str`                | Administrativo | Régimen: CONTRIBUTIVO / SUBSIDIADO |
| `sede`            | `str`                | Administrativo | Sede de atención |
| `nombre_diag`     | `str`                | Diagnóstico | Diagnóstico principal CIE-10 |
| `cardiovascular`  | `str`                | Estado clínico | Normal / Anormal |
| `pulmonar`        | `str`                | Estado clínico | Normal / Anormal |
| `neurologico`     | `str`                | Estado clínico | Normal / Anormal |
| `mental`          | `str`                | Estado clínico | Normal / Anormal |
| `osteomuscular`   | `str`                | Estado clínico | Normal / Anormal |
| `imc`             | `float`              | Antropometría | Valor numérico del IMC |
| `resultado_imc`   | `str`                | Antropometría | Clasificación OMS (OBESIDAD I, PESO NORMAL…) |
| `escala_disnea`   | `str`                | Pulmonar | LEVE / MODERADO / GRAVE / MUY_GRAVE |
| `bodex`           | `str` o `None`       | Pulmonar | Estadio EPOC A–D. Puede ser nulo. |

> **Nota:** La API Socrata entrega todos los valores como texto (`String`). La conversión a tipos nativos de Python se realiza en la capa del modelo (`models/entidades.py`).

---

## 🧪 Muestra JSON

```json
{
  "edad": "68",
  "peso": "85.0",
  "talla": "167.0",
  "plan_beneficios": "SUBSIDIADO",
  "sede": "USAQUÉN",
  "nombre_diag": "HIPERTENSION ESENCIAL (PRIMARIA)",
  "cardiovascular": "Anormal",
  "pulmonar": "Normal",
  "neurologico": "Normal",
  "mental": "Normal",
  "osteomuscular": "Normal",
  "imc": "30.63",
  "resultado_imc": "OBESIDAD I",
  "escala_disnea": "MUY GRAVE",
  "bodex": null
}
```
## 📐Diagrama de clases (UML)
Este diagrama preliminar representa las entidades del negocio. Se utiliza Composición (*--) debido a que los datos clínicos y demográficos dependen enteramente de la existencia de un registro consolidado del paciente.
```
classDiagram
    class RegistroPaciente {
        +paciente: Paciente
        +diagnostico: DiagnosticoCronico
        +estadoClinico: EstadoClinico
        +medicion: MedicionAntropometrica
        +evaluacionPulmonar: EvaluacionPulmonar
        +from_json(json_data: dict) RegistroPaciente
        +calcularPuntajeRiesgo() int
    }

    class Paciente {
        -edad: int
        -peso: float
        -talla: float
        -planBeneficios: str
        -sede: str
        +esAdultoMayor() bool
    }

    class DiagnosticoCronico {
        -nombreDiagnostico: str
        -codigoCIE10: str
    }

    class EstadoClinico {
        -cardiovascular: str
        -pulmonar: str
        -neurologico: str
        -mental: str
        -osteomuscular: str
        +contarSistemasAnormales() int
    }

    class MedicionAntropometrica {
        -imcValor: float
        -resultadoIMC: str
        +tieneObesidad() bool
    }

    class EvaluacionPulmonar {
        -escalaDisnea: str
        -bodex: str
        +esCritica() bool
    }
    


    RegistroPaciente *-- Paciente
    RegistroPaciente *-- DiagnosticoCronico
    RegistroPaciente *-- EstadoClinico
    RegistroPaciente *-- MedicionAntropometrica
    RegistroPaciente *-- EvaluacionPulmonar
```
## Lógica de Riesgo

`calcularPuntajeRiesgo()` devuelve un entero de 0–4 que permite ordenar la lista de pacientes:

|           Condición                | +Puntos |
|------------------------------------|---------|
| Paciente adulto mayor (≥ 60 años)  | +1      |
| 2 o más sistemas clínicos anormales| +1      |
| IMC en rango de obesidad           | +1      |
| Escala disnea GRAVE o MUY_GRAVE    | +1      |



