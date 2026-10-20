"""Control de calidad de la geometría: ¿cada capital cae en su provincia? ¿se solapan?

Existe porque el GeoJSON heredado del repo está muy simplificado (y CABA/Buenos Aires
están mal dibujadas). Un mapa puede "verse bien" a escala país y aun así ser incorrecto.
"""

from shapely.geometry import MultiPolygon, Point

# (slug, capital, lat, lng)
CAPITALS: tuple[tuple[str, str, float, float], ...] = (
    ("caba", "Ciudad de Buenos Aires", -34.6037, -58.3816),
    ("buenos-aires", "La Plata", -34.9205, -57.9536),
    ("cordoba", "Córdoba", -31.4201, -64.1888),
    ("santa-fe", "Santa Fe", -31.6333, -60.7000),
    ("entre-rios", "Paraná", -31.7333, -60.5333),
    ("mendoza", "Mendoza", -32.8895, -68.8458),
    ("tucuman", "San Miguel de Tucumán", -26.8083, -65.2176),
    ("salta", "Salta", -24.7821, -65.4232),
    ("jujuy", "San Salvador de Jujuy", -24.1858, -65.2995),
    ("neuquen", "Neuquén", -38.9516, -68.0591),
    ("chubut", "Rawson", -43.3002, -65.1023),
    ("santa-cruz", "Río Gallegos", -51.6226, -69.2181),
    ("tierra-del-fuego", "Ushuaia", -54.8019, -68.3030),
    ("misiones", "Posadas", -27.3671, -55.8961),
    ("chaco", "Resistencia", -27.4511, -58.9867),
    ("corrientes", "Corrientes", -27.4692, -58.8306),
    ("formosa", "Formosa", -26.1857, -58.1756),
    ("santiago-del-estero", "Santiago del Estero", -27.7951, -64.2615),
    ("catamarca", "San Fernando del Valle de Catamarca", -28.4696, -65.7795),
    ("la-rioja", "La Rioja", -29.4131, -66.8558),
    ("san-juan", "San Juan", -31.5375, -68.5364),
    ("san-luis", "San Luis", -33.2950, -66.3356),
    ("la-pampa", "Santa Rosa", -36.6203, -64.2906),
    ("rio-negro", "Viedma", -40.8135, -62.9967),
)

# Una capital a menos de este margen (grados, ~5 km) de su provincia se considera dentro:
# tolera la simplificación de costas y ríos limítrofes.
TOLERANCE_DEG = 0.05


def capitals_outside(shapes: dict[str, MultiPolygon]) -> list[str]:
    bad = []
    for slug, city, lat, lng in CAPITALS:
        if shapes[slug].distance(Point(lng, lat)) > TOLERANCE_DEG:
            bad.append(f"{city} queda fuera de {slug}")
    return bad


def overlaps(shapes: dict[str, MultiPolygon], min_area_deg2: float = 0.01) -> list[str]:
    """Pares de provincias que se pisan más de `min_area_deg2` (≈ 100 km² a esta latitud)."""
    slugs = sorted(shapes)
    found = []
    for i, a in enumerate(slugs):
        for b in slugs[i + 1 :]:
            area = shapes[a].intersection(shapes[b]).area
            if area > min_area_deg2:
                found.append(f"{a} y {b} se solapan ({area:.3f} grados²)")
    return found
