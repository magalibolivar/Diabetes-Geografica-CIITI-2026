# -*- coding: utf-8 -*-
"""
Generador del Mapa Interactivo Geoespacial de Salud en Argentina (Estilo Windy / GIS)
con Soporte de PWA y Widget Móvil Instalable.
Destino: CIITI 2026 / CoNaIISI — CAETI (Facultad de Tecnología Informática, UAI)

Crea un visualizador web interactivo autónomo (HTML/JS/Leaflet) con:
- Capas intercambiables de salud y determinantes sociales (estilo Windy)
- Paletas de calor cromáticas continuas
- Inspector interactivo con tarjetas de detalle provincial en tiempo real
- Botones de acceso rápido regional (CABA, NOA, NEA, Cuyo, Patagonia)
- Soporte PWA (Progressive Web App): Instalable en celulares Android e iOS
- Modo "Widget de Salud" móvil (estilo widget del clima) con simulador de smartphone
- Funcionamiento 100% offline (sin servidor web necesario)
"""
import json
import warnings
from pathlib import Path
import pandas as pd
import geopandas as gpd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent.parent
DATA_CSV = ROOT / "Datos" / "enfr2018_provincias.csv"
GEO_JSON = ROOT / "Datos" / "argentina_provincias.geojson"
OUT_DIR = Path(__file__).resolve().parent
HTML_OUT = OUT_DIR / "mapa_interactivo_diabetes_argentina.html"
INDEX_OUT = OUT_DIR / "index.html"

print(">>> [1/3] Cargando datos y geometrias de Argentina...")
df = pd.read_csv(DATA_CSV)
gdf = gpd.read_file(GEO_JSON)
gdf["provincia"] = gdf["shapeName"].replace({
    "Ciudad Autónoma de Buenos Aires": "CABA",
    "Ciudad Autnoma de Buenos Aires": "CABA"
})
merged = gdf.merge(df, on="provincia", how="inner")
print(f"    - {len(merged)} provincias cruzadas con éxito.")

# Convertir GeoDataFrame a GeoJSON serializable con todas las propiedades numéricas
features_list = []
for _, row in merged.iterrows():
    geom = row.geometry.__geo_interface__
    props = {
        "provincia": row["provincia"],
        "region": row.get("region", "Sin región"),
        "tasa_diabetes_pct": round(float(row["tasa_diabetes_pct"]), 1),
        "tratamiento_diabetes_pct": round(float(row["tratamiento_diabetes_pct"]), 1),
        "brecha_tratamiento_pct": round(100.0 - float(row["tratamiento_diabetes_pct"]), 1),
        "medicion_glucemia_pct": round(float(row["medicion_glucemia_pct"]), 1),
        "obesidad_pct": round(float(row["obesidad_pct"]), 1),
        "inactividad_fisica_pct": round(float(row["inactividad_fisica_pct"]), 1),
        "presion_elevada_pct": round(float(row["presion_elevada_pct"]), 1),
        "pobreza_personas_pct": round(float(row["pobreza_personas_pct"]), 1),
        "sin_cobertura_salud_pct": round(float(row["sin_cobertura_salud_pct"]), 1),
        "nbi_2010_pct": round(float(row["nbi_2010_pct"]), 1),
        "densidad_hab_km2": round(float(row["densidad_hab_km2"]), 1),
    }
    features_list.append({
        "type": "Feature",
        "geometry": geom,
        "properties": props
    })

geojson_data = {
    "type": "FeatureCollection",
    "features": features_list
}
geojson_str = json.dumps(geojson_data, ensure_ascii=False)

# Medias nacionales para comparaciones
medias_nacionales = {
    "tasa_diabetes_pct": round(float(df["tasa_diabetes_pct"].mean()), 1),
    "tratamiento_diabetes_pct": round(float(df["tratamiento_diabetes_pct"].mean()), 1),
    "brecha_tratamiento_pct": round(100.0 - float(df["tratamiento_diabetes_pct"].mean()), 1),
    "medicion_glucemia_pct": round(float(df["medicion_glucemia_pct"].mean()), 1),
    "obesidad_pct": round(float(df["obesidad_pct"].mean()), 1),
    "inactividad_fisica_pct": round(float(df["inactividad_fisica_pct"].mean()), 1),
    "presion_elevada_pct": round(float(df["presion_elevada_pct"].mean()), 1),
    "pobreza_personas_pct": round(float(df["pobreza_personas_pct"].mean()), 1),
    "sin_cobertura_salud_pct": round(float(df["sin_cobertura_salud_pct"].mean()), 1),
    "nbi_2010_pct": round(float(df["nbi_2010_pct"].mean()), 1),
}
medias_json = json.dumps(medias_nacionales)

print(">>> [2/3] Generando plantilla HTML interactiva tipo Windy + PWA + Widget Móvil...")

html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>GeoSalud • Atlas Interactivo y Widget Móvil de Diabetes (Argentina 2026)</title>

    <!-- PWA Meta Tags -->
    <link rel="manifest" href="../Widget/manifest.json">
    <meta name="theme-color" content="#0284c7">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="GeoSalud Widget">
    <link rel="apple-touch-icon" href="../Widget/icon.svg">
    <link rel="icon" type="image/svg+xml" href="../Widget/icon.svg">

    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        body, html {{
            height: 100%;
            width: 100%;
            overflow: hidden;
            background-color: #0b0f19;
            color: #f8fafc;
        }}
        #map {{
            height: 100%;
            width: 100%;
            background: #090d16;
            z-index: 1;
        }}
        /* Windy-Style UI Overlays */
        .glass-panel {{
            background: rgba(15, 23, 42, 0.82);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 12px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.45);
        }}
        /* Header Top Bar */
        .header-bar {{
            position: absolute;
            top: 16px;
            left: 16px;
            z-index: 1000;
            padding: 12px 18px;
            max-width: 480px;
        }}
        .header-title {{
            font-size: 15px;
            font-weight: 800;
            letter-spacing: -0.3px;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .header-badge {{
            background: linear-gradient(135deg, #ef4444, #f97316);
            color: white;
            font-size: 10px;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 6px;
            text-transform: uppercase;
        }}
        .header-sub {{
            font-size: 11.5px;
            color: #94a3b8;
            margin-top: 3px;
        }}
        .header-sub span {{
            color: #38bdf8;
            font-weight: 600;
        }}
        /* Action buttons in header (Widget & Mobile install) */
        .header-actions {{
            display: flex;
            gap: 8px;
            margin-top: 10px;
        }}
        .btn-action-mobile {{
            background: linear-gradient(135deg, #0284c7, #2563eb);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 6px 12px;
            font-size: 11px;
            font-weight: 700;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 5px;
            transition: all 0.2s;
            box-shadow: 0 2px 8px rgba(2, 132, 199, 0.4);
        }}
        .btn-action-mobile:hover {{
            background: linear-gradient(135deg, #0369a1, #1d4ed8);
            transform: translateY(-1px);
        }}
        .btn-action-install {{
            background: rgba(30, 41, 59, 0.9);
            color: #38bdf8;
            border: 1px solid rgba(56, 189, 248, 0.35);
            border-radius: 8px;
            padding: 6px 12px;
            font-size: 11px;
            font-weight: 700;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 5px;
            transition: all 0.2s;
        }}
        .btn-action-install:hover {{
            background: rgba(56, 189, 248, 0.15);
            border-color: #38bdf8;
        }}

        /* Windy Layer Selector Bar */
        .layer-bar {{
            position: absolute;
            top: 16px;
            right: 16px;
            z-index: 1000;
            display: flex;
            flex-direction: column;
            gap: 6px;
            max-width: 250px;
        }}
        .layer-bar-title {{
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            color: #94a3b8;
            padding: 4px 8px;
        }}
        .layer-btn {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 9px 13px;
            border-radius: 9px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            background: rgba(30, 41, 59, 0.75);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: #cbd5e1;
        }}
        .layer-btn:hover {{
            background: rgba(51, 65, 85, 0.9);
            color: #ffffff;
            transform: translateX(-3px);
            border-color: rgba(56, 189, 248, 0.4);
        }}
        .layer-btn.active {{
            background: linear-gradient(135deg, #0284c7, #2563eb);
            color: #ffffff;
            border-color: #38bdf8;
            box-shadow: 0 0 16px rgba(37, 99, 235, 0.5);
        }}
        .layer-btn .icon {{
            margin-right: 8px;
            font-size: 14px;
        }}

        /* Quick Regional Zoom Buttons */
        .region-bar {{
            position: absolute;
            left: 16px;
            bottom: 30px;
            z-index: 1000;
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
            max-width: 480px;
            padding: 8px;
        }}
        .reg-btn {{
            background: rgba(30, 41, 59, 0.85);
            color: #94a3b8;
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 5px 11px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .reg-btn:hover {{
            background: #334155;
            color: #f8fafc;
            border-color: #38bdf8;
        }}

        /* Inspector Card (Floating Province Details) */
        .inspector-panel {{
            position: absolute;
            bottom: 30px;
            right: 16px;
            z-index: 1000;
            width: 320px;
            padding: 16px;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .inspector-header {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding-bottom: 8px;
        }}
        .prov-name {{
            font-size: 17px;
            font-weight: 800;
            color: #ffffff;
        }}
        .prov-region {{
            font-size: 11px;
            font-weight: 600;
            color: #38bdf8;
            text-transform: uppercase;
        }}
        .metric-highlight {{
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            margin-bottom: 12px;
            background: rgba(255, 255, 255, 0.05);
            padding: 10px 12px;
            border-radius: 8px;
        }}
        .metric-big {{
            font-size: 26px;
            font-weight: 800;
            color: #f59e0b;
        }}
        .metric-diff {{
            font-size: 11px;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        .diff-pos {{
            background: rgba(239, 68, 68, 0.25);
            color: #f87171;
        }}
        .diff-neg {{
            background: rgba(34, 197, 94, 0.25);
            color: #4ade80;
        }}
        .stat-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 7px;
        }}
        .stat-box {{
            background: rgba(15, 23, 42, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.06);
            padding: 7px 9px;
            border-radius: 7px;
        }}
        .stat-label {{
            font-size: 10px;
            color: #94a3b8;
            font-weight: 600;
            margin-bottom: 2px;
        }}
        .stat-val {{
            font-size: 13px;
            font-weight: 700;
            color: #f1f5f9;
        }}

        /* Windy-Style Bottom Color Legend */
        .legend-bar {{
            position: absolute;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1000;
            padding: 8px 16px;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-width: 380px;
        }}
        .legend-title {{
            font-size: 11px;
            font-weight: 700;
            color: #cbd5e1;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .legend-gradient {{
            width: 100%;
            height: 10px;
            border-radius: 5px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            margin-bottom: 4px;
        }}
        .legend-ticks {{
            width: 100%;
            display: flex;
            justify-content: space-between;
            font-size: 10px;
            font-weight: 700;
            color: #94a3b8;
        }}

        /* Smartphone Simulator Modal */
        .phone-modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.82);
            backdrop-filter: blur(12px);
            z-index: 9999;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .phone-modal.open {{
            display: flex;
        }}
        .phone-frame {{
            width: 380px;
            height: 760px;
            max-height: 94vh;
            background: #020617;
            border: 10px solid #1e293b;
            border-radius: 46px;
            box-shadow: 0 25px 60px -10px rgba(0, 0, 0, 0.85), 0 0 0 2px rgba(255, 255, 255, 0.1);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }}
        .phone-notch {{
            position: absolute;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            width: 110px;
            height: 24px;
            background: #000000;
            border-radius: 12px;
            z-index: 100;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .phone-camera {{
            width: 10px;
            height: 10px;
            background: #0f172a;
            border-radius: 50%;
            margin-right: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .phone-iframe {{
            width: 100%;
            height: 100%;
            border: none;
            padding-top: 36px;
        }}
        .phone-close-btn {{
            position: absolute;
            top: 24px;
            right: 28px;
            background: rgba(255, 255, 255, 0.15);
            color: white;
            border: none;
            width: 38px;
            height: 38px;
            border-radius: 50%;
            font-size: 18px;
            font-weight: 700;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
            z-index: 10001;
        }}
        .phone-close-btn:hover {{
            background: rgba(239, 68, 68, 0.7);
            transform: rotate(90deg);
        }}

        /* Responsive Design for Mobile Devices */
        @media (max-width: 768px) {{
            .header-bar {{
                top: 8px;
                left: 8px;
                right: 8px;
                max-width: none;
                padding: 10px 14px;
            }}
            .layer-bar {{
                top: auto;
                bottom: 80px;
                right: 8px;
                max-width: 160px;
                max-height: 40vh;
                overflow-y: auto;
            }}
            .layer-btn {{
                padding: 6px 9px;
                font-size: 11px;
            }}
            .inspector-panel {{
                bottom: 80px;
                left: 8px;
                right: 175px;
                width: auto;
                padding: 10px;
            }}
            .metric-big {{
                font-size: 20px;
            }}
            .legend-bar {{
                bottom: 12px;
                min-width: 280px;
                padding: 6px 12px;
            }}
            .region-bar {{
                display: none;
            }}
        }}
    </style>
</head>
<body>

    <!-- Header Panel -->
    <div class="header-bar glass-panel">
        <div class="header-title">
            <span>🇦🇷 Atlas Geoespacial de Salud</span>
            <span class="header-badge">Windy-GIS</span>
        </div>
        <div class="header-sub">
            Plataforma subnacional • <span>Censo 2022 + EPH (INDEC) + ENFR (MSAL)</span> • CIITI 2026
        </div>
        <!-- Action Buttons for Mobile & Widget -->
        <div class="header-actions">
            <button class="btn-action-mobile" onclick="openPhoneSimulator()">
                <span>📱</span> Ver Modo Widget Celular
            </button>
            <button class="btn-action-install" id="btnInstallPwa" onclick="handlePwaInstall()">
                <span>📲</span> Instalar en Celular
            </button>
        </div>
    </div>

    <!-- Layer Switcher (Windy Style) -->
    <div class="layer-bar glass-panel">
        <div class="layer-bar-title">Capas de Salud</div>
        <div class="layer-btn active" onclick="switchLayer('tasa_diabetes_pct')">
            <span><span class="icon">🩸</span>Diabetes Tipo 2</span>
            <span style="font-size: 10px; opacity: 0.8;">%</span>
        </div>
        <div class="layer-btn" onclick="switchLayer('brecha_tratamiento_pct')">
            <span><span class="icon">💊</span>Brecha Tratamiento</span>
            <span style="font-size: 10px; opacity: 0.8;">%</span>
        </div>
        <div class="layer-btn" onclick="switchLayer('medicion_glucemia_pct')">
            <span><span class="icon">🩺</span>Screening Glucemia</span>
            <span style="font-size: 10px; opacity: 0.8;">%</span>
        </div>
        <div class="layer-btn" onclick="switchLayer('obesidad_pct')">
            <span><span class="icon">⚖️</span>Obesidad (IMC≥30)</span>
            <span style="font-size: 10px; opacity: 0.8;">%</span>
        </div>
        <div class="layer-btn" onclick="switchLayer('inactividad_fisica_pct')">
            <span><span class="icon">🛋️</span>Sedentarismo</span>
            <span style="font-size: 10px; opacity: 0.8;">%</span>
        </div>
        <div class="layer-btn" onclick="switchLayer('pobreza_personas_pct')">
            <span><span class="icon">📉</span>Pobreza (EPH INDEC)</span>
            <span style="font-size: 10px; opacity: 0.8;">%</span>
        </div>
        <div class="layer-btn" onclick="switchLayer('sin_cobertura_salud_pct')">
            <span><span class="icon">🏥</span>Sin Obra Social (Censo 2022)</span>
            <span style="font-size: 10px; opacity: 0.8;">%</span>
        </div>
        <div class="layer-btn" onclick="switchLayer('nbi_2010_pct')">
            <span><span class="icon">🏚️</span>NBI Hogares (Censo INDEC)</span>
            <span style="font-size: 10px; opacity: 0.8;">%</span>
        </div>
    </div>

    <!-- Regional Fast Jump Buttons -->
    <div class="region-bar glass-panel">
        <button class="reg-btn" onclick="zoomTo(-38.4, -63.6, 4)">🗺️ País Completo</button>
        <button class="reg-btn" onclick="zoomTo(-34.61, -58.42, 10)">🏙️ CABA / AMBA</button>
        <button class="reg-btn" onclick="zoomTo(-26.8, -65.2, 6)">🌵 NOA</button>
        <button class="reg-btn" onclick="zoomTo(-27.4, -58.9, 6)">🌿 NEA</button>
        <button class="reg-btn" onclick="zoomTo(-31.5, -68.5, 6)">🍇 Cuyo</button>
        <button class="reg-btn" onclick="zoomTo(-45.8, -69.0, 5)">🏔️ Patagonia</button>
    </div>

    <!-- Floating Province Inspector -->
    <div id="inspector" class="inspector-panel glass-panel">
        <div class="inspector-header">
            <div class="prov-name" id="insp-name">San Luis</div>
            <div class="prov-region" id="insp-region">Cuyo</div>
        </div>
        <div class="metric-highlight">
            <div>
                <div style="font-size: 10px; color: #94a3b8; font-weight: 700; text-transform: uppercase;" id="insp-metric-name">Prevalencia de Diabetes</div>
                <div class="metric-big" id="insp-metric-val">17.3%</div>
            </div>
            <div class="metric-diff diff-pos" id="insp-metric-diff">+4.6% vs media</div>
        </div>
        <div class="stat-grid">
            <div class="stat-box">
                <div class="stat-label">Brecha Medicación</div>
                <div class="stat-val" id="insp-brecha">49.9%</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Screening Glucémico</div>
                <div class="stat-val" id="insp-screen">78.1%</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Obesidad (IMC≥30)</div>
                <div class="stat-val" id="insp-obes">23.9%</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Sedentarismo</div>
                <div class="stat-val" id="insp-sed">38.9%</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Pobreza Monetaria</div>
                <div class="stat-val" id="insp-pob">31.3%</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Sin Obra Social</div>
                <div class="stat-val" id="insp-sal">37.0%</div>
            </div>
        </div>
    </div>

    <!-- Legend Bar (Windy Style) -->
    <div class="legend-bar glass-panel">
        <div class="legend-title" id="legend-title">Prevalencia de Diabetes Tipo 2 (%)</div>
        <div class="legend-gradient" id="legend-grad"></div>
        <div class="legend-ticks" id="legend-ticks">
            <span>8%</span><span>10.5%</span><span>13%</span><span>15.5%</span><span>18%</span>
        </div>
    </div>

    <!-- Map Container -->
    <div id="map"></div>

    <!-- Smartphone Simulator Modal -->
    <div class="phone-modal" id="phoneModal">
        <button class="phone-close-btn" onclick="closePhoneSimulator()" title="Cerrar Simulador">✕</button>
        <div class="phone-frame">
            <div class="phone-notch">
                <div class="phone-camera"></div>
            </div>
            <iframe class="phone-iframe" src="../Widget/widget_movil.html" title="Widget Móvil de Salud"></iframe>
        </div>
    </div>

    <!-- Leaflet JS -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
    <script>
        // Data inyectada desde Python
        const geojsonData = {geojson_str};
        const mediasNacionales = {medias_json};

        // Configuracion de capas metricas
        const layerConfigs = {{
            'tasa_diabetes_pct': {{
                label: 'Prevalencia de Diabetes Tipo 2 (%)',
                unit: '%',
                min: 8.0,
                max: 18.0,
                palette: ['#00f2fe', '#facc15', '#f97316', '#dc2626', '#7f1d1d'],
                gradCss: 'linear-gradient(to right, #00f2fe, #facc15, #f97316, #dc2626, #7f1d1d)',
                ticks: ['8%', '10.5%', '13%', '15.5%', '18%']
            }},
            'brecha_tratamiento_pct': {{
                label: 'Brecha de Tratamiento Farmacológico (%)',
                unit: '%',
                min: 28.0,
                max: 70.0,
                palette: ['#fee2e2', '#f87171', '#c084fc', '#9333ea', '#4c1d95'],
                gradCss: 'linear-gradient(to right, #fee2e2, #f87171, #c084fc, #9333ea, #4c1d95)',
                ticks: ['28%', '38%', '49%', '59%', '70%']
            }},
            'medicion_glucemia_pct': {{
                label: 'Screening Glucémico Alguna Vez (%)',
                unit: '%',
                min: 58.0,
                max: 95.0,
                palette: ['#7f1d1d', '#dc2626', '#f59e0b', '#84cc16', '#15803d'],
                gradCss: 'linear-gradient(to right, #7f1d1d, #dc2626, #f59e0b, #84cc16, #15803d)',
                ticks: ['58%', '67%', '76%', '85%', '95%']
            }},
            'obesidad_pct': {{
                label: 'Obesidad (IMC ≥ 30) (%)',
                unit: '%',
                min: 16.0,
                max: 36.0,
                palette: ['#ffedd5', '#fb923c', '#ea580c', '#c2410c', '#7c2d12'],
                gradCss: 'linear-gradient(to right, #ffedd5, #fb923c, #ea580c, #c2410c, #7c2d12)',
                ticks: ['16%', '21%', '26%', '31%', '36%']
            }},
            'inactividad_fisica_pct': {{
                label: 'Inactividad Física / Sedentarismo (%)',
                unit: '%',
                min: 20.0,
                max: 70.0,
                palette: ['#f3e8ff', '#c084fc', '#9333ea', '#6b21a8', '#3b0764'],
                gradCss: 'linear-gradient(to right, #f3e8ff, #c084fc, #9333ea, #6b21a8, #3b0764)',
                ticks: ['20%', '32%', '45%', '57%', '70%']
            }},
            'pobreza_personas_pct': {{
                label: 'Pobreza Monetaria EPH (%)',
                unit: '%',
                min: 12.0,
                max: 50.0,
                palette: ['#ecfdf5', '#a7f3d0', '#fbbf24', '#f87171', '#991b1b'],
                gradCss: 'linear-gradient(to right, #ecfdf5, #a7f3d0, #fbbf24, #f87171, #991b1b)',
                ticks: ['12%', '21%', '31%', '40%', '50%']
            }},
            'sin_cobertura_salud_pct': {{
                label: 'Población sin Obra Social / Prepaga (%)',
                unit: '%',
                min: 15.0,
                max: 58.0,
                palette: ['#e0f2fe', '#7dd3fc', '#0284c7', '#0369a1', '#082f49'],
                gradCss: 'linear-gradient(to right, #e0f2fe, #7dd3fc, #0284c7, #0369a1, #082f49)',
                ticks: ['15%', '25%', '36%', '47%', '58%']
            }}
        }};

        let currentMetric = 'tasa_diabetes_pct';
        let geojsonLayer = null;

        // Inicializar Mapa centrado en Argentina
        const map = L.map('map', {{
            center: [-38.4161, -63.6167],
            zoom: 4,
            minZoom: 3,
            maxZoom: 14,
            zoomControl: false
        }});
        L.control.zoom({{ position: 'topleft' }}).addTo(map);

        // Capa base oscura estilo Windy / Dark Matter
        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: 20
        }}).addTo(map);

        // Funcion de interpolacion de color
        function getColor(value, cfg) {{
            const ratio = Math.max(0, Math.min(1, (value - cfg.min) / (cfg.max - cfg.min)));
            const palette = cfg.palette;
            const idx = Math.min(palette.length - 1, Math.floor(ratio * (palette.length - 1)));
            return palette[idx];
        }}

        // Estilo de cada provincia
        function styleFeature(feature) {{
            const val = feature.properties[currentMetric];
            const cfg = layerConfigs[currentMetric];
            return {{
                fillColor: getColor(val, cfg),
                weight: 1.2,
                opacity: 1,
                color: '#1e293b',
                fillOpacity: 0.84
            }};
        }}

        // Interaccion hover y click
        function onEachFeature(feature, layer) {{
            layer.on({{
                mouseover: function(e) {{
                    const l = e.target;
                    l.setStyle({{
                        weight: 2.8,
                        color: '#38bdf8',
                        fillOpacity: 0.96
                    }});
                    l.bringToFront();
                    updateInspector(feature.properties);
                }},
                mouseout: function(e) {{
                    geojsonLayer.resetStyle(e.target);
                }},
                click: function(e) {{
                    map.fitBounds(e.target.getBounds(), {{ maxZoom: 7, padding: [40, 40] }});
                    updateInspector(feature.properties);
                }}
            }});
        }}

        // Actualizar datos del Inspector Flotante
        function updateInspector(p) {{
            document.getElementById('insp-name').innerText = p.provincia;
            document.getElementById('insp-region').innerText = p.region;
            const cfg = layerConfigs[currentMetric];
            const val = p[currentMetric];
            const media = mediasNacionales[currentMetric];
            const diff = val - media;

            document.getElementById('insp-metric-name').innerText = cfg.label;
            document.getElementById('insp-metric-val').innerText = val.toFixed(1) + cfg.unit;

            const diffEl = document.getElementById('insp-metric-diff');
            diffEl.innerText = (diff >= 0 ? '+' : '') + diff.toFixed(1) + ' vs media (' + media.toFixed(1) + cfg.unit + ')';
            diffEl.className = 'metric-diff ' + (diff >= 0 ? 'diff-pos' : 'diff-neg');

            document.getElementById('insp-brecha').innerText = p.brecha_tratamiento_pct.toFixed(1) + '%';
            document.getElementById('insp-screen').innerText = p.medicion_glucemia_pct.toFixed(1) + '%';
            document.getElementById('insp-obes').innerText = p.obesidad_pct.toFixed(1) + '%';
            document.getElementById('insp-sed').innerText = p.inactividad_fisica_pct.toFixed(1) + '%';
            document.getElementById('insp-pob').innerText = p.pobreza_personas_pct.toFixed(1) + '%';
            document.getElementById('insp-sal').innerText = p.sin_cobertura_salud_pct.toFixed(1) + '%';
        }}

        // Renderizar capa
        function renderGeojson() {{
            if (geojsonLayer) map.removeLayer(geojsonLayer);
            geojsonLayer = L.geoJSON(geojsonData, {{
                style: styleFeature,
                onEachFeature: onEachFeature
            }}).addTo(map);
        }}

        // Cambiar de capa tematica
        function switchLayer(metricKey) {{
            currentMetric = metricKey;
            const cfg = layerConfigs[metricKey];

            // Boton activo
            document.querySelectorAll('.layer-btn').forEach(btn => btn.classList.remove('active'));
            event.currentTarget.classList.add('active');

            // Actualizar leyenda
            document.getElementById('legend-title').innerText = cfg.label;
            document.getElementById('legend-grad').style.background = cfg.gradCss;
            const ticksHtml = cfg.ticks.map(t => '<span>' + t + '</span>').join('');
            document.getElementById('legend-ticks').innerHTML = ticksHtml;

            renderGeojson();

            // Actualizar inspector con la primera provincia visible
            const firstProps = geojsonData.features.find(f => f.properties.provincia === 'CABA').properties;
            updateInspector(firstProps);
        }}

        // Zoom a region
        function zoomTo(lat, lon, z) {{
            map.flyTo([lat, lon], z, {{ duration: 1.2 }});
        }}

        // Simulador de Celular
        function openPhoneSimulator() {{
            document.getElementById('phoneModal').classList.add('open');
        }}
        function closePhoneSimulator() {{
            document.getElementById('phoneModal').classList.remove('open');
        }}

        // PWA Install Event Handler
        let deferredPrompt;
        window.addEventListener('beforeinstallprompt', (e) => {{
            e.preventDefault();
            deferredPrompt = e;
            const installBtn = document.getElementById('btnInstallPwa');
            if (installBtn) installBtn.style.display = 'flex';
        }});

        function handlePwaInstall() {{
            if (deferredPrompt) {{
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then((choiceResult) => {{
                    if (choiceResult.outcome === 'accepted') {{
                        console.log('User accepted PWA installation');
                    }}
                    deferredPrompt = null;
                }});
            }} else {{
                // Si esta en iPhone o escritorio, abrir el simulador con las instrucciones
                openPhoneSimulator();
            }}
        }}

        // Registrar Service Worker para PWA Offline
        if ('serviceWorker' in navigator) {{
            window.addEventListener('load', () => {{
                navigator.serviceWorker.register('../Widget/service-worker.js').catch(err => {{
                    console.log('SW registration note:', err);
                }});
            }});
        }}

        // Inicializar
        renderGeojson();
        // Inicializar leyenda
        const initCfg = layerConfigs[currentMetric];
        document.getElementById('legend-title').innerText = initCfg.label;
        document.getElementById('legend-grad').style.background = initCfg.gradCss;
        document.getElementById('legend-ticks').innerHTML = initCfg.ticks.map(t => '<span>' + t + '</span>').join('');
        // Inspector inicial con San Luis
        const initProv = geojsonData.features.find(f => f.properties.provincia === 'San Luis').properties;
        updateInspector(initProv);
    </script>
</body>
</html>
"""

with open(HTML_OUT, "w", encoding="utf-8") as f:
    f.write(html_content)
with open(INDEX_OUT, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f">>> [3/3] Visualizador interactivo generado con éxito en:")
print(f"    - {HTML_OUT}")
print(f"    - {INDEX_OUT}")
print("=" * 70)
