"""Catálogo de referencia: jurisdicciones, fuentes, datasets e indicadores.

Es la fuente única de verdad de *qué* mide el atlas y *de dónde* sale cada cifra.
Todo lo que el sitio muestre como "Fuente" sale de acá (vía la base de datos).
Las definiciones de los indicadores ENFR son las de los títulos de los cuadros
oficiales del INDEC (cuadros_definitivos_enfr_2018.xls), no las de documentos
secundarios del repositorio.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class JurisdictionDef:
    iso: str  # ISO 3166-2:AR (o "AR" para el total del país)
    slug: str
    name: str  # nombre completo (coincide con shapeName del GeoJSON)
    short: str  # nombre tal como aparece en los cuadros ENFR / CSV
    kind: str  # "country" | "province"
    region: str | None  # agrupación regional de la propia ENFR


def _p(iso: str, slug: str, name: str, region: str, short: str | None = None) -> JurisdictionDef:
    return JurisdictionDef(iso, slug, name, short or name, "province", region)


PAMPEANA = "Pampeana y GBA"
NOROESTE = "Noroeste"
NORESTE = "Noreste"
PATAGONIA = "Patagonia"
CUYO = "Cuyo"

JURISDICTIONS: tuple[JurisdictionDef, ...] = (
    JurisdictionDef("AR", "argentina", "Argentina", "Total", "country", None),
    _p("AR-C", "caba", "Ciudad Autónoma de Buenos Aires", PAMPEANA, short="CABA"),
    _p("AR-B", "buenos-aires", "Buenos Aires", PAMPEANA),
    _p("AR-X", "cordoba", "Córdoba", PAMPEANA),
    _p("AR-E", "entre-rios", "Entre Ríos", PAMPEANA),
    _p("AR-L", "la-pampa", "La Pampa", PAMPEANA),
    _p("AR-S", "santa-fe", "Santa Fe", PAMPEANA),
    _p("AR-K", "catamarca", "Catamarca", NOROESTE),
    _p("AR-Y", "jujuy", "Jujuy", NOROESTE),
    _p("AR-F", "la-rioja", "La Rioja", NOROESTE),
    _p("AR-A", "salta", "Salta", NOROESTE),
    _p("AR-G", "santiago-del-estero", "Santiago del Estero", NOROESTE),
    _p("AR-T", "tucuman", "Tucumán", NOROESTE),
    _p("AR-W", "corrientes", "Corrientes", NORESTE),
    _p("AR-H", "chaco", "Chaco", NORESTE),
    _p("AR-P", "formosa", "Formosa", NORESTE),
    _p("AR-N", "misiones", "Misiones", NORESTE),
    _p("AR-U", "chubut", "Chubut", PATAGONIA),
    _p("AR-Q", "neuquen", "Neuquén", PATAGONIA),
    _p("AR-R", "rio-negro", "Río Negro", PATAGONIA),
    _p("AR-Z", "santa-cruz", "Santa Cruz", PATAGONIA),
    _p("AR-V", "tierra-del-fuego", "Tierra del Fuego", PATAGONIA),
    _p("AR-M", "mendoza", "Mendoza", CUYO),
    _p("AR-J", "san-juan", "San Juan", CUYO),
    _p("AR-D", "san-luis", "San Luis", CUYO),
)

PROVINCES = tuple(j for j in JURISDICTIONS if j.kind == "province")
BY_SHORT = {j.short: j for j in JURISDICTIONS}
BY_NAME = {j.name: j for j in JURISDICTIONS}


@dataclass(frozen=True)
class SourceDef:
    slug: str
    name: str
    publisher: str
    url: str | None = None


SOURCES: tuple[SourceDef, ...] = (
    SourceDef(
        "enfr-2018",
        "4ª Encuesta Nacional de Factores de Riesgo (ENFR) 2018",
        "INDEC y Ministerio de Salud de la Nación",
        "https://www.indec.gob.ar/",
    ),
    SourceDef(
        "indec-censo-2010",
        "Censo Nacional de Población, Hogares y Viviendas 2010 (serie histórica NBI)",
        "INDEC",
        "https://www.indec.gob.ar/",
    ),
    SourceDef(
        "indec-eph",
        "Encuesta Permanente de Hogares (EPH) — informe de pobreza",
        "INDEC",
        "https://www.indec.gob.ar/",
    ),
    SourceDef(
        "indec-censo-2022",
        "Censo Nacional de Población, Hogares y Viviendas 2022",
        "INDEC",
        "https://www.indec.gob.ar/",
    ),
)


@dataclass(frozen=True)
class DatasetDef:
    slug: str
    source_slug: str
    name: str
    reference_period: str
    universe: str | None = None
    notes: str | None = None


ENFR_NOTES = (
    "Marcas de confiabilidad de INDEC en los cuadros: (1) las estimaciones deben ser "
    "consideradas con precaución, por tener un CV mayor a 16,6% y menor o igual a 33,3%; "
    "(2) la estimación no es confiable ya que el coeficiente de variación es superior a "
    "33,3%, la cantidad de casos involucrados es insuficiente o la proporción es menor al 5%."
)

DATASETS: tuple[DatasetDef, ...] = (
    DatasetDef(
        "enfr-2018",
        "enfr-2018",
        "ENFR 2018 — cuadros definitivos por provincia",
        "2018",
        "Población de 18 años y más en localidades de 5.000 y más habitantes",
        ENFR_NOTES,
    ),
    DatasetDef(
        "indec-nbi-2010",
        "indec-censo-2010",
        "Hogares con NBI por provincia (Censo 2010)",
        "2010",
        "Hogares",
        "El NBI se releva en años censales; 2010 es el último punto disponible de esta serie.",
    ),
    DatasetDef(
        "indec-pobreza-2018s2",
        "indec-eph",
        "Personas bajo la línea de pobreza, 2º semestre 2018",
        "2018-S2",
        "Personas en aglomerados urbanos EPH",
    ),
    DatasetDef(
        "indec-cobertura-2022",
        "indec-censo-2022",
        "Cobertura de salud por provincia (Censo 2022)",
        "2022",
        "Población total",
    ),
    DatasetDef(
        "indec-densidad-2022",
        "indec-censo-2022",
        "Densidad de población por provincia (Censo 2022)",
        "2022",
        "Población total",
    ),
)


@dataclass(frozen=True)
class IndicatorDef:
    slug: str
    label: str
    description: str
    unit: str
    decimals: int
    higher_is: str  # "better" | "worse" | "neutral"
    category: str  # "outcome" | "care" | "risk_factor" | "context"


INDICATORS: tuple[IndicatorDef, ...] = (
    IndicatorDef(
        "diabetes_prevalence",
        "Glucemia elevada o diabetes",
        "Población de 18 años y más que declara tener glucemia elevada o diabetes (autorreporte).",
        "%", 1, "worse", "outcome",
    ),
    IndicatorDef(
        "glucose_screening",
        "Control de glucemia alguna vez",
        "Población de 18 años y más que se midió la glucemia (azúcar en sangre) alguna vez "
        "en la vida, por autorreporte.",
        "%", 1, "better", "care",
    ),
    IndicatorDef(
        "diabetes_treatment",
        "Tratamiento en las últimas 2 semanas",
        "Entre quienes declaran glucemia elevada o diabetes, porcentaje que realizó algún tipo "
        "de tratamiento en las últimas dos semanas. No distingue el tipo de tratamiento.",
        "%", 1, "better", "care",
    ),
    IndicatorDef(
        "obesity",
        "Obesidad",
        "Población de 18 años y más con obesidad, por autorreporte (peso y talla declarados).",
        "%", 1, "worse", "risk_factor",
    ),
    IndicatorDef(
        "low_physical_activity",
        "Actividad física baja",
        "Población de 18 años y más con nivel de actividad física baja.",
        "%", 1, "worse", "risk_factor",
    ),
    IndicatorDef(
        "smoking",
        "Consumo de cigarrillos",
        "Población de 18 años y más que consume cigarrillos.",
        "%", 1, "worse", "risk_factor",
    ),
    IndicatorDef(
        "high_blood_pressure",
        "Presión arterial elevada",
        "Población de 18 años y más con presión arterial elevada, por autorreporte.",
        "%", 1, "worse", "risk_factor",
    ),
    IndicatorDef(
        "high_cholesterol",
        "Colesterol elevado",
        "Población de 18 años y más con colesterol elevado, por autorreporte.",
        "%", 1, "worse", "risk_factor",
    ),
    IndicatorDef(
        "fruit_veg_5plus",
        "Frutas y verduras: 5 o más porciones diarias",
        "Población de 18 años y más que consume 5 o más porciones diarias de frutas y/o verduras.",
        "%", 1, "better", "risk_factor",
    ),
    IndicatorDef(
        "nbi_households",
        "Hogares con NBI",
        "Hogares con al menos una necesidad básica insatisfecha.",
        "%", 1, "worse", "context",
    ),
    IndicatorDef(
        "poverty_persons",
        "Personas bajo la línea de pobreza",
        "Personas cuyos ingresos no alcanzan la canasta básica total (EPH).",
        "%", 1, "worse", "context",
    ),
    IndicatorDef(
        "no_health_coverage",
        "Sin obra social, prepaga ni mutual",
        "Población sin cobertura de salud de obra social, prepaga o mutual (Censo 2022).",
        "%", 1, "worse", "context",
    ),
    IndicatorDef(
        "population_density",
        "Densidad de población",
        "Habitantes por kilómetro cuadrado.",
        "hab/km²", 1, "neutral", "context",
    ),
)


@dataclass(frozen=True)
class DatasetIndicatorDef:
    dataset_slug: str
    indicator_slug: str
    source_ref: str  # ENFR: nombre de la hoja del .xls (p. ej. "Cuadro 7.3")
    note: str | None = None


def _enfr(indicator: str, cuadro: str) -> DatasetIndicatorDef:
    return DatasetIndicatorDef("enfr-2018", indicator, cuadro)


DATASET_INDICATORS: tuple[DatasetIndicatorDef, ...] = (
    _enfr("diabetes_prevalence", "Cuadro 7.3"),
    _enfr("glucose_screening", "Cuadro 7.1"),
    _enfr("diabetes_treatment", "Cuadro 7.5"),
    _enfr("obesity", "Cuadro 6.3"),
    _enfr("low_physical_activity", "Cuadro 3.1"),
    _enfr("smoking", "Cuadro 2.1"),
    _enfr("high_blood_pressure", "Cuadro 8.3"),
    _enfr("high_cholesterol", "Cuadro 9.3"),
    _enfr("fruit_veg_5plus", "Cuadro 5.7"),
    DatasetIndicatorDef(
        "indec-nbi-2010", "nbi_households",
        "serie_nbi_2022.xlsx, hoja NBI_Hogares_%_80_22, columna 2010",
    ),
    DatasetIndicatorDef(
        "indec-pobreza-2018s2", "poverty_persons",
        "cuadros_informe_pobreza_03_26.xls, Cuadro 4.3, columna «2 semestre 2018»",
        "La EPH se releva por aglomerado urbano, no por provincia completa: el valor provincial "
        "es el promedio simple de los aglomerados de cada provincia (sin ponderar por población).",
    ),
    DatasetIndicatorDef(
        "indec-cobertura-2022", "no_health_coverage",
        "c2022_tp_salud_c1.xlsx, hoja «Cobertura de salud N°1»",
        "Se excluyeron los subtotales de partidos del conurbano para no duplicar el total "
        "provincial de Buenos Aires.",
    ),
    DatasetIndicatorDef(
        "indec-densidad-2022", "population_density",
        "Censo 2022, resultados definitivos (valores cargados en src/05_build_argentina.py)",
        "Tierra del Fuego está ajustada a 8,6 hab/km² (superficie efectiva sin el sector "
        "antártico) en lugar del valor oficial de 0,20, que incluye esa superficie.",
    ),
)

# Columna del CSV integrado -> (dataset, indicador) para las fuentes que no son ENFR.
CONTEXT_COLUMNS: dict[str, tuple[str, str]] = {
    "nbi_2010_pct": ("indec-nbi-2010", "nbi_households"),
    "pobreza_personas_pct": ("indec-pobreza-2018s2", "poverty_persons"),
    "sin_cobertura_salud_pct": ("indec-cobertura-2022", "no_health_coverage"),
    "densidad_hab_km2": ("indec-densidad-2022", "population_density"),
}

# Columna del CSV integrado -> indicador ENFR (sólo para verificación cruzada).
ENFR_CSV_COLUMNS: dict[str, str] = {
    "tasa_diabetes_pct": "diabetes_prevalence",
    "obesidad_pct": "obesity",
    "inactividad_fisica_pct": "low_physical_activity",
    "tabaquismo_pct": "smoking",
    "presion_elevada_pct": "high_blood_pressure",
    "colesterol_elevado_pct": "high_cholesterol",
    "consumo_frutas_verduras_pct": "fruit_veg_5plus",
    "tratamiento_diabetes_pct": "diabetes_treatment",
    "medicion_glucemia_pct": "glucose_screening",
}

DATASET_BY_SLUG = {d.slug: d for d in DATASETS}
INDICATOR_BY_SLUG = {i.slug: i for i in INDICATORS}
