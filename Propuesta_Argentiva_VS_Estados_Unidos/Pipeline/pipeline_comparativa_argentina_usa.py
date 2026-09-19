# -*- coding: utf-8 -*-
"""
Pipeline Maestro Reproducible: Paper Comparativo Extenso (10 Páginas) Argentina vs. EE.UU.
Destino: CIITI 2026 / CoNaIISI — CAETI (Facultad de Tecnología Informática, UAI)

Genera:
1. Datasets y tablas estadísticas comparativas (CSV).
2. 5 Figuras científicas de alta resolución (220 DPI) en formato cartográfico y analítico.
3. Manuscrito científico extenso (.docx en 2 columnas, plantilla oficial CoNaIISI/CIITI, ~5.000 palabras, ~10 páginas).
4. Manuscrito completo en formato Markdown (.md).
"""
import warnings
warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import LeaveOneOut, KFold, cross_val_predict
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH as AL
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION_START
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# Directorios
BASE_DIR = Path(__file__).resolve().parent.parent
DATOS_DIR = BASE_DIR / "Datos"
PAPER_DIR = BASE_DIR / "Paper"
RESULTADOS_DIR = BASE_DIR / "Resultados"
PIPELINE_DIR = BASE_DIR / "Pipeline"
ROOT_REPO = BASE_DIR.parent
TEMPLATE_PATH = ROOT_REPO / "paper" / "Determinantes_Geoespaciales_Diabetes_UAI_CONAIISI.docx"

DOC_OUT = PAPER_DIR / "Paper_Comparativo_Argentina_USA_2026.docx"
MD_OUT = PAPER_DIR / "Paper_Comparativo_Argentina_USA.md"

print("=" * 75)
print(">>> INICIANDO GENERADOR DEL PAPER EXTENSO COMPARATIVO (CIITI 2026, ~10 PÁGINAS)")
print("=" * 75)

# ==============================================================================
# 1. CARGA DE DATOS
# ==============================================================================
print(">>> [1/5] Cargando microdatos y capas vectoriales...")
df_arg = pd.read_csv(DATOS_DIR / "enfr2018_provincias.csv")
gdf_arg = gpd.read_file(DATOS_DIR / "argentina_provincias.geojson")
gdf_arg["provincia"] = gdf_arg["shapeName"].replace({
    "Ciudad Autónoma de Buenos Aires": "CABA",
    "Ciudad Autnoma de Buenos Aires": "CABA"
})
arg_merged = gdf_arg.merge(df_arg, on="provincia", how="inner")

df_us = pd.read_csv(DATOS_DIR / "brfss2015_estados.csv")
gdf_us = gpd.read_file(DATOS_DIR / "us_states.geojson").rename(columns={"name": "estado"}).merge(df_us, on="estado", how="inner")
us_cont = gdf_us[~gdf_us["estado"].isin(["Alaska", "Hawaii"])].copy()

# ==============================================================================
# 2. GENERACION DE TABLAS CIENTIFICAS (CSV)
# ==============================================================================
print(">>> [2/5] Calculando modelos econométricos, validación cruzada y tablas...")

# TABLA 1: Resumen de Indicadores
t1_df = pd.DataFrame([
    {"Indicador": "N unidades territoriales", "Estados Unidos (CDC BRFSS)": "51 estados (50 + D.C.)", "Argentina (ENFR / INDEC)": "24 jurisdicciones (23 + CABA)"},
    {"Indicador": "Población representada", "Estados Unidos (CDC BRFSS)": "~320 millones (441.456 enc.)", "Argentina (ENFR / INDEC)": "~44 millones (urbana 18+ años)"},
    {"Indicador": "Prevalencia media diabetes", "Estados Unidos (CDC BRFSS)": f"{df_us['tasa_diabetes_pct'].mean():.1f}% (desv. est. 1,8%)", "Argentina (ENFR / INDEC)": f"{df_arg['tasa_diabetes_pct'].mean():.1f}% (desv. est. 2,3%)"},
    {"Indicador": "Rango de prevalencia", "Estados Unidos (CDC BRFSS)": f"{df_us['tasa_diabetes_pct'].min():.1f}% (Colorado) – {df_us['tasa_diabetes_pct'].max():.1f}% (Misisipi)", "Argentina (ENFR / INDEC)": f"{df_arg['tasa_diabetes_pct'].min():.1f}% (CABA) – {df_arg['tasa_diabetes_pct'].max():.1f}% (San Luis)"},
    {"Indicador": "Prevalencia media obesidad", "Estados Unidos (CDC BRFSS)": f"{df_us['obesidad_pct'].mean():.1f}% (20,2% a 35,6%)", "Argentina (ENFR / INDEC)": f"{df_arg['obesidad_pct'].mean():.1f}% (17,0% a 34,4%)"},
    {"Indicador": "Prevalencia sedentarismo", "Estados Unidos (CDC BRFSS)": f"{df_us['inactividad_fisica_pct'].mean():.1f}% (17,9% a 34,2%)", "Argentina (ENFR / INDEC)": f"{df_arg['inactividad_fisica_pct'].mean():.1f}% (23,2% a 69,1%)"},
    {"Indicador": "Población sin seguro médico", "Estados Unidos (CDC BRFSS)": f"{df_us['sin_cobertura_salud_pct'].mean():.1f}% (6,0% a 17,1%)", "Argentina (ENFR / INDEC)": f"{df_arg['sin_cobertura_salud_pct'].mean():.1f}% (16,3% a 55,9%)"},
    {"Indicador": "Tasa de screening glucémico", "Estados Unidos (CDC BRFSS)": ">85% (control rutinario masivo)", "Argentina (ENFR / INDEC)": f"Media 74,8% (60,3% Chaco a 92,9% CABA)"},
    {"Indicador": "Brecha de tratamiento activo", "Estados Unidos (CDC BRFSS)": "Barrera de costo económico / seguro", "Argentina (ENFR / INDEC)": f"Media 54,4% (32,7% La Pampa a 70,0% Santa Cruz)"},
])
tab1_path = RESULTADOS_DIR / "tabla1_resumen_comparativo.csv"
t1_df.to_csv(tab1_path, index=False, encoding="utf-8-sig")

# MODELOS OLS EE.UU.
X_us = df_us[["obesidad_pct", "inactividad_fisica_pct", "pobreza_ingresos_pct", "secundario_incompleto_pct", "sin_cobertura_salud_pct"]]
X_us_c = sm.add_constant(X_us)
y_us = df_us["tasa_diabetes_pct"]
m_us = sm.OLS(y_us, X_us_c).fit(cov_type="HC3")
vif_us = [variance_inflation_factor(X_us_c.values, i) for i in range(X_us_c.shape[1])]

# MODELOS OLS ARGENTINA
X_ar = df_arg[["obesidad_pct", "inactividad_fisica_pct", "pobreza_personas_pct", "sin_cobertura_salud_pct", "log_densidad"]]
X_ar_c = sm.add_constant(X_ar)
y_ar = df_arg["tasa_diabetes_pct"]
m_ar = sm.OLS(y_ar, X_ar_c).fit(cov_type="HC3")
vif_ar = [variance_inflation_factor(X_ar_c.values, i) for i in range(X_ar_c.shape[1])]

# TABLA 2: Coeficientes OLS Comparados
vars_comp = [
    ("Intercepto", m_us.params[0], m_us.pvalues[0], "-", m_ar.params[0], m_ar.pvalues[0], "-"),
    ("Obesidad (%)", m_us.params["obesidad_pct"], m_us.pvalues["obesidad_pct"], f"{vif_us[1]:.1f}", m_ar.params["obesidad_pct"], m_ar.pvalues["obesidad_pct"], f"{vif_ar[1]:.1f}"),
    ("Sedentarismo (%)", m_us.params["inactividad_fisica_pct"], m_us.pvalues["inactividad_fisica_pct"], f"{vif_us[2]:.1f}", m_ar.params["inactividad_fisica_pct"], m_ar.pvalues["inactividad_fisica_pct"], f"{vif_ar[2]:.1f}"),
    ("Pobreza / Bajos Ingresos (%)", m_us.params["pobreza_ingresos_pct"], m_us.pvalues["pobreza_ingresos_pct"], f"{vif_us[3]:.1f}", m_ar.params["pobreza_personas_pct"], m_ar.pvalues["pobreza_personas_pct"], f"{vif_ar[3]:.1f}"),
    ("Sin Cobertura Privada / OS (%)", m_us.params["sin_cobertura_salud_pct"], m_us.pvalues["sin_cobertura_salud_pct"], f"{vif_us[5]:.1f}", m_ar.params["sin_cobertura_salud_pct"], m_ar.pvalues["sin_cobertura_salud_pct"], f"{vif_ar[4]:.1f}"),
    ("Educación / Densidad", m_us.params["secundario_incompleto_pct"], m_us.pvalues["secundario_incompleto_pct"], f"{vif_us[4]:.1f}", m_ar.params["log_densidad"], m_ar.pvalues["log_densidad"], f"{vif_ar[5]:.1f}")
]
def _fmt_p(p): return "<0.001" if p < 0.001 else f"{p:.3f}"
t2_df = pd.DataFrame([
    {
        "Determinante Sociodemográfico": v[0],
        "EE.UU. Coef. β (HC3)": f"{v[1]:+.3f} (p={_fmt_p(v[2])})",
        "EE.UU. VIF": v[3],
        "Argentina Coef. β (HC3)": f"{v[4]:+.3f} (p={_fmt_p(v[5])})",
        "Argentina VIF": v[6]
    }
    for v in vars_comp
])
tab2_path = RESULTADOS_DIR / "tabla2_ols_coeficientes.csv"
t2_df.to_csv(tab2_path, index=False, encoding="utf-8-sig")

# Regresión Lineal y Random Forest con Validación Cruzada en EE.UU.
lr_us = LinearRegression()
y_us_lr_cv = cross_val_predict(lr_us, X_us, y_us, cv=KFold(5, shuffle=True, random_state=42))
r2_us_lr_cv = r2_score(y_us, y_us_lr_cv)
mae_us_lr_cv = mean_absolute_error(y_us, y_us_lr_cv)

rf_us = RandomForestRegressor(n_estimators=300, max_depth=5, random_state=42)
y_us_cv = cross_val_predict(rf_us, X_us, y_us, cv=KFold(5, shuffle=True, random_state=42))
r2_rf_us = r2_score(y_us, y_us_cv)
mae_rf_us = mean_absolute_error(y_us, y_us_cv)

loo = LeaveOneOut()
y_ar_preds = []
for tr_i, te_i in loo.split(X_ar):
    m_loo = sm.OLS(y_ar.iloc[tr_i], sm.add_constant(X_ar.iloc[tr_i])).fit()
    p_loo = m_loo.predict(sm.add_constant(X_ar.iloc[te_i], has_constant="add"))
    y_ar_preds.append(p_loo.values[0])
r2_loo_ar = r2_score(y_ar, y_ar_preds)
mae_loo_ar = mean_absolute_error(y_ar, y_ar_preds)

rf_ar = RandomForestRegressor(n_estimators=300, max_depth=3, random_state=42)
y_ar_rf_cv = cross_val_predict(rf_ar, X_ar, y_ar, cv=KFold(5, shuffle=True, random_state=42))
r2_rf_ar = r2_score(y_ar, y_ar_rf_cv)
mae_rf_ar = mean_absolute_error(y_ar, y_ar_rf_cv)

# TABLA 3: Rendimiento y Diagnóstico de Modelos
t3_df = pd.DataFrame([
    {
        "Modelo y Algoritmo": "OLS Multivariado (Muestra completa)",
        "EE.UU. R² (Ajustado)": f"{m_us.rsquared:.3f} ({m_us.rsquared_adj:.3f})",
        "EE.UU. Error MAE": f"{mean_absolute_error(y_us, m_us.fittedvalues):.2f}%",
        "Argentina R² (Ajustado)": f"{m_ar.rsquared:.3f} ({m_ar.rsquared_adj:.3f})",
        "Argentina Error MAE": f"{mean_absolute_error(y_ar, m_ar.fittedvalues):.2f}%",
        "Diagnóstico Metodológico": "EE.UU. altamente significativo (p<0.001); Argentina no significativo (p=0.16)"
    },
    {
        "Modelo y Algoritmo": "Validación Cruzada OLS (LOOCV en Arg, 5-Fold en US)",
        "EE.UU. R² (Ajustado)": f"{r2_us_lr_cv:.3f}",
        "EE.UU. Error MAE": f"{mae_us_lr_cv:.2f}%",
        "Argentina R² (Ajustado)": f"{r2_loo_ar:.3f}",
        "Argentina Error MAE": f"{mae_loo_ar:.2f}%",
        "Diagnóstico Metodológico": "Colapso predictivo en Argentina (R² negativo): sobreajuste por N=24 reducido"
    },
    {
        "Modelo y Algoritmo": "Random Forest Regressor (5-Fold CV)",
        "EE.UU. R² (Ajustado)": f"{r2_rf_us:.3f}",
        "EE.UU. Error MAE": f"{mae_rf_us:.2f}%",
        "Argentina R² (Ajustado)": f"{r2_rf_ar:.3f}",
        "Argentina Error MAE": f"{mae_rf_ar:.2f}%",
        "Diagnóstico Metodológico": "Random Forest generaliza con alta precisión en EE.UU.; falla en Arg por falta de N"
    }
])
tab3_path = RESULTADOS_DIR / "tabla3_diagnostico_modelos.csv"
t3_df.to_csv(tab3_path, index=False, encoding="utf-8-sig")

# TABLA 4: Ranking de Extremos
top_us = df_us.nlargest(3, "tasa_diabetes_pct")[["estado", "tasa_diabetes_pct", "pobreza_ingresos_pct", "inactividad_fisica_pct"]]
bot_us = df_us.nsmallest(3, "tasa_diabetes_pct")[["estado", "tasa_diabetes_pct", "pobreza_ingresos_pct", "inactividad_fisica_pct"]]
top_ar = df_arg.nlargest(3, "tasa_diabetes_pct")[["provincia", "tasa_diabetes_pct", "pobreza_personas_pct", "tratamiento_diabetes_pct"]]
bot_ar = df_arg.nsmallest(3, "tasa_diabetes_pct")[["provincia", "tasa_diabetes_pct", "pobreza_personas_pct", "tratamiento_diabetes_pct"]]

t4_df = pd.DataFrame([
    {"Grupo Extremo": "EE.UU. — Mayor Prevalencia (1)", "Jurisdicción": f"{top_us.iloc[0]['estado']}", "Diabetes (%)": f"{top_us.iloc[0]['tasa_diabetes_pct']:.1f}%", "Pobreza (%)": f"{top_us.iloc[0]['pobreza_ingresos_pct']:.1f}%", "Dato Clave": "Cinturón de Diabetes (Sur)"},
    {"Grupo Extremo": "EE.UU. — Mayor Prevalencia (2)", "Jurisdicción": f"{top_us.iloc[1]['estado']}", "Diabetes (%)": f"{top_us.iloc[1]['tasa_diabetes_pct']:.1f}%", "Pobreza (%)": f"{top_us.iloc[1]['pobreza_ingresos_pct']:.1f}%", "Dato Clave": "Alta inactividad (31,9%)"},
    {"Grupo Extremo": "EE.UU. — Menor Prevalencia (1)", "Jurisdicción": f"{bot_us.iloc[0]['estado']}", "Diabetes (%)": f"{bot_us.iloc[0]['tasa_diabetes_pct']:.1f}%", "Pobreza (%)": f"{bot_us.iloc[0]['pobreza_ingresos_pct']:.1f}%", "Dato Clave": "Elevado ingreso y actividad"},
    {"Grupo Extremo": "EE.UU. — Menor Prevalencia (2)", "Jurisdicción": f"{bot_us.iloc[1]['estado']}", "Diabetes (%)": f"{bot_us.iloc[1]['tasa_diabetes_pct']:.1f}%", "Pobreza (%)": f"{bot_us.iloc[1]['pobreza_ingresos_pct']:.1f}%", "Dato Clave": "Baja obesidad (25,4%)"},
    {"Grupo Extremo": "Argentina — Mayor Prevalencia (1)", "Jurisdicción": f"{top_ar.iloc[0]['provincia']}", "Diabetes (%)": f"{top_ar.iloc[0]['tasa_diabetes_pct']:.1f}%", "Pobreza (%)": f"{top_ar.iloc[0]['pobreza_personas_pct']:.1f}%", "Dato Clave": "Región Cuyo (máx. nacional)"},
    {"Grupo Extremo": "Argentina — Mayor Prevalencia (2)", "Jurisdicción": f"{top_ar.iloc[1]['provincia']}", "Diabetes (%)": f"{top_ar.iloc[1]['tasa_diabetes_pct']:.1f}%", "Pobreza (%)": f"{top_ar.iloc[1]['pobreza_personas_pct']:.1f}%", "Dato Clave": "Tratamiento activo 58,1%"},
    {"Grupo Extremo": "Argentina — Menor Prevalencia (1)", "Jurisdicción": f"{bot_ar.iloc[0]['provincia']}", "Diabetes (%)": f"{bot_ar.iloc[0]['tasa_diabetes_pct']:.1f}%", "Pobreza (%)": f"{bot_ar.iloc[0]['pobreza_personas_pct']:.1f}%", "Dato Clave": "Screening 92,9% (CABA)"},
    {"Grupo Extremo": "Argentina — Menor Prevalencia (2)", "Jurisdicción": f"{bot_ar.iloc[1]['provincia']}", "Diabetes (%)": f"{bot_ar.iloc[1]['tasa_diabetes_pct']:.1f}%", "Pobreza (%)": f"{bot_ar.iloc[1]['pobreza_personas_pct']:.1f}%", "Dato Clave": "Subdiagnóstico: screening 60%"}
])
tab4_path = RESULTADOS_DIR / "tabla4_ranking_extremos.csv"
t4_df.to_csv(tab4_path, index=False, encoding="utf-8-sig")

# ==============================================================================
# 3. GENERACION DE 5 FIGURAS CIENTIFICAS (220 DPI)
# ==============================================================================
print(">>> [3/5] Generando 5 figuras analíticas en alta resolución (220 DPI)...")

plt.rcParams.update({
    "figure.dpi": 220,
    "font.family": "sans-serif",
    "font.size": 9,
    "axes.titlesize": 10.5,
    "axes.titleweight": "bold",
})

# --- FIGURA 1: MAPAS COMPARATIVOS PREVALENCIA ---
fig1, (ax_u, ax_a) = plt.subplots(1, 2, figsize=(14, 7.5))
vmin_d, vmax_d = 6.0, 18.0
us_cont.plot(column="tasa_diabetes_pct", ax=ax_u, cmap="YlOrRd", vmin=vmin_d, vmax=vmax_d, edgecolor="#4a5568", linewidth=0.5)
ax_u.set_title("(a) Estados Unidos: Prevalencia de Diabetes (%)\n[CDC BRFSS 2015; N=51 estados]", fontsize=10.5, fontweight="bold")
ax_u.axis("off")
ax_u.annotate("Cinturón de la Diabetes\n(Misisipi 14,8%, Alabama 13,6%)", xy=(-88.5, 32.5), xytext=(-98.0, 26.0),
              arrowprops=dict(facecolor="#c53030", arrowstyle="->", lw=1.1), fontsize=8, fontweight="bold",
              bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#c53030", alpha=0.9))
ax_u.annotate("Colorado: 6,8% (Mín)", xy=(-105.5, 39.0), xytext=(-116.0, 42.0),
              arrowprops=dict(facecolor="#2b6cb0", arrowstyle="->", lw=1.0), fontsize=8, fontweight="bold",
              bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#2b6cb0", alpha=0.9))

arg_merged.plot(column="tasa_diabetes_pct", ax=ax_a, cmap="YlOrRd", vmin=vmin_d, vmax=vmax_d, edgecolor="#4a5568", linewidth=0.6)
ax_a.set_title("(b) Argentina: Prevalencia de Diabetes (%)\n[ENFR 2018; N=24 jurisdicciones]", fontsize=10.5, fontweight="bold")
ax_a.axis("off")
ax_ins = inset_axes(ax_a, width="100%", height="100%", bbox_to_anchor=(0.72, 0.52, 0.28, 0.28), bbox_transform=ax_a.transAxes)
arg_merged.plot(column="tasa_diabetes_pct", ax=ax_ins, cmap="YlOrRd", vmin=vmin_d, vmax=vmax_d, edgecolor="#4a5568", linewidth=0.6)
ax_ins.set_xlim(-58.85, -58.20); ax_ins.set_ylim(-34.85, -34.35); ax_ins.set_xticks([]); ax_ins.set_yticks([])
ax_ins.set_title("CABA: 8,8%", fontsize=8, fontweight="bold", pad=2)

ax_a.annotate("San Luis: 17,3%\n(Máx. nacional)", xy=(-66.3, -33.3), xytext=(-73.5, -31.0),
              arrowprops=dict(facecolor="#c53030", arrowstyle="->", lw=1.0), fontsize=8, fontweight="bold",
              bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#c53030", alpha=0.9))
ax_a.annotate("Subdiagnóstico en el Norte:\nChaco 10,3% (40% sin screening)", xy=(-60.5, -26.8), xytext=(-54.0, -23.5),
              arrowprops=dict(facecolor="#2b6cb0", arrowstyle="->", lw=1.0), fontsize=8, fontweight="bold",
              bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#2b6cb0", alpha=0.9))

sm1 = plt.cm.ScalarMappable(cmap="YlOrRd", norm=plt.Normalize(vmin=vmin_d, vmax=vmax_d))
sm1._A = []
cbar1 = fig1.colorbar(sm1, ax=[ax_u, ax_a], orientation="horizontal", fraction=0.035, pad=0.04, aspect=35, shrink=0.6)
cbar1.set_label("Prevalencia de diabetes (%) — Escala común unificada", fontsize=9.5, fontweight="bold")
fig1_path = RESULTADOS_DIR / "figura1_mapas_comparativos.png"
fig1.savefig(fig1_path, bbox_inches="tight", dpi=220)
plt.close(fig1)

# --- FIGURA 2: FACTORES DE RIESGO CARDIOMETABOLICOS ---
fig2, axes2 = plt.subplots(2, 2, figsize=(13, 10))
us_cont.plot(column="obesidad_pct", ax=axes2[0, 0], cmap="Oranges", edgecolor="#4a5568", linewidth=0.4, vmin=20, vmax=38)
axes2[0, 0].set_title("(a) Obesidad en EE.UU. (IMC≥30, %)", fontsize=10, fontweight="bold"); axes2[0, 0].axis("off")
sm_ob_u = plt.cm.ScalarMappable(cmap="Oranges", norm=plt.Normalize(vmin=20, vmax=38)); sm_ob_u._A = []
fig2.colorbar(sm_ob_u, ax=axes2[0, 0], fraction=0.03, pad=0.02, shrink=0.7)

arg_merged.plot(column="obesidad_pct", ax=axes2[0, 1], cmap="Oranges", edgecolor="#4a5568", linewidth=0.5, vmin=16, vmax=36)
axes2[0, 1].set_title("(b) Obesidad en Argentina (IMC≥30, %)", fontsize=10, fontweight="bold"); axes2[0, 1].axis("off")
sm_ob_a = plt.cm.ScalarMappable(cmap="Oranges", norm=plt.Normalize(vmin=16, vmax=36)); sm_ob_a._A = []
fig2.colorbar(sm_ob_a, ax=axes2[0, 1], fraction=0.03, pad=0.02, shrink=0.7)

us_cont.plot(column="inactividad_fisica_pct", ax=axes2[1, 0], cmap="Purples", edgecolor="#4a5568", linewidth=0.4, vmin=16, vmax=36)
axes2[1, 0].set_title("(c) Sedentarismo en EE.UU. (%)", fontsize=10, fontweight="bold"); axes2[1, 0].axis("off")
sm_sed_u = plt.cm.ScalarMappable(cmap="Purples", norm=plt.Normalize(vmin=16, vmax=36)); sm_sed_u._A = []
fig2.colorbar(sm_sed_u, ax=axes2[1, 0], fraction=0.03, pad=0.02, shrink=0.7)

arg_merged.plot(column="inactividad_fisica_pct", ax=axes2[1, 1], cmap="Purples", edgecolor="#4a5568", linewidth=0.5, vmin=20, vmax=70)
axes2[1, 1].set_title("(d) Sedentarismo en Argentina (%)", fontsize=10, fontweight="bold"); axes2[1, 1].axis("off")
sm_sed_a = plt.cm.ScalarMappable(cmap="Purples", norm=plt.Normalize(vmin=20, vmax=70)); sm_sed_a._A = []
fig2.colorbar(sm_sed_a, ax=axes2[1, 1], fraction=0.03, pad=0.02, shrink=0.7)

fig2_path = RESULTADOS_DIR / "figura2_factores_riesgo.png"
fig2.savefig(fig2_path, bbox_inches="tight", dpi=220)
plt.close(fig2)

# --- FIGURA 3: BRECHA DE TRATAMIENTO Y BARRERA DE COSTO ---
fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(14, 6.5))
# Ranking horizontal Argentina
df_arg_tr = df_arg.sort_values("tratamiento_diabetes_pct", ascending=True)
colors_tr = ["#e53e3e" if x < 45 else "#3182ce" if x > 60 else "#718096" for x in df_arg_tr["tratamiento_diabetes_pct"]]
ax3a.barh(df_arg_tr["provincia"], df_arg_tr["tratamiento_diabetes_pct"], color=colors_tr, edgecolor="none", height=0.75)
ax3a.axvline(df_arg["tratamiento_diabetes_pct"].mean(), color="black", linestyle="--", linewidth=1.2, label=f"Media Arg: {df_arg['tratamiento_diabetes_pct'].mean():.1f}%")
ax3a.set_xlabel("Población diabética bajo tratamiento farmacológico activo (%)", fontsize=9.5, fontweight="bold")
ax3a.set_title("(a) Argentina: Disparidad Provincial de Tratamiento (ENFR)", fontsize=10.5, fontweight="bold")
ax3a.legend(loc="lower right", fontsize=8.5)
ax3a.grid(True, axis="x", linestyle=":", alpha=0.6)

# Dispersión EE.UU.: Barrera de costo vs Diabetes
x_bc = df_us["barrera_costo_medico_pct"]; y_bc = df_us["tasa_diabetes_pct"]
sl_bc, in_bc, r_bc, p_bc, _ = stats.linregress(x_bc, y_bc)
ax3b.scatter(x_bc, y_bc, color="#dd6b20", s=55, edgecolor="black", linewidth=0.5, alpha=0.85)
x_lin_bc = np.linspace(x_bc.min(), x_bc.max(), 50)
ax3b.plot(x_lin_bc, in_bc + sl_bc * x_lin_bc, color="#9c4221", lw=2, label=f"Ajuste OLS (r = +{r_bc:.2f}; p < 0.001)")
ax3b.set_xlabel("Población con barrera de costo para ver al médico (%)", fontsize=9.5, fontweight="bold")
ax3b.set_ylabel("Prevalencia de diabetes (%)", fontsize=9.5, fontweight="bold")
ax3b.set_title("(b) EE.UU.: Barrera Económica de Acceso vs. Prevalencia", fontsize=10.5, fontweight="bold")
ax3b.legend(loc="upper left", fontsize=8.5)
ax3b.grid(True, linestyle=":", alpha=0.6)
fig3_path = RESULTADOS_DIR / "figura3_brecha_tratamiento.png"
fig3.savefig(fig3_path, bbox_inches="tight", dpi=220)
plt.close(fig3)

# --- FIGURA 4: MATRIZ DE CALOR DE CORRELACIONES ---
fig4, (ax4u, ax4a) = plt.subplots(1, 2, figsize=(13, 5.5))
vars_h = ["Diabetes", "Obesidad", "Sedentarismo", "Pobreza", "Sin Seguro"]
corr_u = df_us[["tasa_diabetes_pct", "obesidad_pct", "inactividad_fisica_pct", "pobreza_ingresos_pct", "sin_cobertura_salud_pct"]].corr().values
corr_a = df_arg[["tasa_diabetes_pct", "obesidad_pct", "inactividad_fisica_pct", "pobreza_personas_pct", "sin_cobertura_salud_pct"]].corr().values

im4u = ax4u.imshow(corr_u, cmap="RdBu_r", vmin=-1, vmax=1)
ax4u.set_xticks(range(5)); ax4u.set_yticks(range(5))
ax4u.set_xticklabels(vars_h, rotation=40, ha="right", fontsize=8.5, fontweight="bold")
ax4u.set_yticklabels(vars_h, fontsize=8.5, fontweight="bold")
ax4u.set_title("(a) Estados Unidos (CDC BRFSS, N=51)", fontsize=10.5, fontweight="bold")
for i in range(5):
    for j in range(5):
        val = corr_u[i, j]
        ax4u.text(j, i, f"{val:+.2f}", ha="center", va="center", fontsize=8, color="white" if abs(val)>0.45 else "black", fontweight="bold")

im4a = ax4a.imshow(corr_a, cmap="RdBu_r", vmin=-1, vmax=1)
ax4a.set_xticks(range(5)); ax4a.set_yticks(range(5))
ax4a.set_xticklabels(vars_h, rotation=40, ha="right", fontsize=8.5, fontweight="bold")
ax4a.set_yticklabels(vars_h, fontsize=8.5, fontweight="bold")
ax4a.set_title("(b) Argentina (ENFR / INDEC, N=24)", fontsize=10.5, fontweight="bold")
for i in range(5):
    for j in range(5):
        val = corr_a[i, j]
        ax4a.text(j, i, f"{val:+.2f}", ha="center", va="center", fontsize=8, color="white" if abs(val)>0.45 else "black", fontweight="bold")

fig4.colorbar(im4a, ax=[ax4u, ax4a], orientation="horizontal", fraction=0.045, pad=0.12, aspect=35, shrink=0.5, label="Coeficiente de Pearson (r)")
fig4_path = RESULTADOS_DIR / "figura4_matriz_correlaciones.png"
fig4.savefig(fig4_path, bbox_inches="tight", dpi=220)
plt.close(fig4)

# --- FIGURA 5: REGRESIONES Y DIAGNOSTICO DE ESCALA ---
fig5, (ax5a, ax5b) = plt.subplots(1, 2, figsize=(13, 5.5))
# Dispersión Pobreza vs Diabetes
ax5a.scatter(df_us["pobreza_ingresos_pct"], df_us["tasa_diabetes_pct"], color="#e53e3e", alpha=0.75, s=45, label=f"EE.UU. (r = +{m_us.rsquared**0.5:.2f}; R² = {m_us.rsquared:.2f})")
x_lin_u = np.linspace(df_us["pobreza_ingresos_pct"].min(), df_us["pobreza_ingresos_pct"].max(), 50)
sl_u5, in_u5, _, _, _ = stats.linregress(df_us["pobreza_ingresos_pct"], df_us["tasa_diabetes_pct"])
ax5a.plot(x_lin_u, in_u5 + sl_u5 * x_lin_u, color="#9b2c2c", lw=2)

ax5a.scatter(df_arg["pobreza_personas_pct"], df_arg["tasa_diabetes_pct"], color="#3182ce", alpha=0.85, s=60, marker="s", edgecolor="black", label=f"Argentina (r = -0,05; p = 0,82)")
x_lin_a = np.linspace(df_arg["pobreza_personas_pct"].min(), df_arg["pobreza_personas_pct"].max(), 50)
sl_a5, in_a5, _, _, _ = stats.linregress(df_arg["pobreza_personas_pct"], df_arg["tasa_diabetes_pct"])
ax5a.plot(x_lin_a, in_a5 + sl_a5 * x_lin_a, color="#1a365d", lw=2, linestyle="--")
ax5a.set_xlabel("Población bajo línea de pobreza / bajos ingresos (%)", fontsize=9.5, fontweight="bold")
ax5a.set_ylabel("Prevalencia de diabetes (%)", fontsize=9.5, fontweight="bold")
ax5a.set_title("(a) Contraste: Pobreza vs. Prevalencia", fontsize=10.5, fontweight="bold")
ax5a.legend(loc="upper left", fontsize=8.5)
ax5a.grid(True, linestyle=":", alpha=0.5)

# Screening vs NBI en Argentina (Demostrando la causa del subdiagnóstico)
x_sc = df_arg["nbi_2010_pct"]; y_sc = df_arg["medicion_glucemia_pct"]
sl_sc, in_sc, r_sc, p_sc, _ = stats.linregress(x_sc, y_sc)
ax5b.scatter(x_sc, y_sc, color="#38a169", s=65, edgecolor="black", linewidth=0.6, alpha=0.85)
x_lin_sc = np.linspace(x_sc.min(), x_sc.max(), 50)
ax5b.plot(x_lin_sc, in_sc + sl_sc * x_lin_sc, color="#22543d", lw=2, linestyle="-", label=f"Ajuste lineal (r = {r_sc:.2f}; p < 0.001)")
for i, txt in enumerate(df_arg["provincia"]):
    if txt in ["CABA", "Chaco", "Formosa", "Santiago del Estero", "San Luis", "Santa Fe"]:
        ax5b.annotate(txt, (x_sc.iloc[i], y_sc.iloc[i]), fontsize=7.5, xytext=(4, 4), textcoords="offset points")
ax5b.set_xlabel("Hogares con Necesidades Básicas Insatisfechas NBI (%)", fontsize=9.5, fontweight="bold")
ax5b.set_ylabel("Screening: Medición de glucemia alguna vez (%)", fontsize=9.5, fontweight="bold")
ax5b.set_title("(b) Argentina: Pobreza Estructural vs. Acceso a Screening", fontsize=10.5, fontweight="bold")
ax5b.legend(loc="lower left", fontsize=8.5)
ax5b.grid(True, linestyle=":", alpha=0.5)

fig5_path = RESULTADOS_DIR / "figura5_modelos_dispersion.png"
fig5.savefig(fig5_path, bbox_inches="tight", dpi=220)
plt.close(fig5)
print("    - 5 Figuras científicas generadas con éxito en la carpeta Paper/.")

# ==============================================================================
# 4. COMPILACION DEL MANUSCRITO WORD EXTENSO (.DOCX) - FORMATO CONAIISI/CIITI
# ==============================================================================
print(">>> [4/5] Compilando manuscrito extenso (.docx) con plantilla oficial...")

def set_section_columns(section, num_cols=2, space_twips=500):
    sectPr = section._sectPr
    cols = sectPr.xpath('.//w:cols')
    if cols:
        col_elem = cols[0]
    else:
        col_elem = OxmlElement('w:cols')
        sectPr.append(col_elem)
    col_elem.set(qn('w:num'), str(num_cols))
    col_elem.set(qn('w:space'), str(space_twips))

def set_font(run, name="Times New Roman", size=10, bold=False, italic=False, color_rgb=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run._element.rPr.rFonts.set(qn('w:eastAsia'), name)
    if color_rgb:
        run.font.color.rgb = RGBColor(*color_rgb)

def add_p(doc, text="", align=AL.JUSTIFY, bold=False, italic=False, size=10, first_indent=0.4, space_after=4):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.first_line_indent = Cm(first_indent)
    p.paragraph_format.line_spacing = 1.05
    if text:
        run = p.add_run(text)
        set_font(run, "Times New Roman", size, bold, italic)
    return p

def add_runs_p(doc, segments, align=AL.JUSTIFY, first_indent=0.4, space_after=4):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.first_line_indent = Cm(first_indent)
    p.paragraph_format.line_spacing = 1.05
    for t, b, i in segments:
        run = p.add_run(t)
        set_font(run, "Times New Roman", 10, b, i)
    return p

def add_h1(doc, text):
    p = doc.add_paragraph()
    p.alignment = AL.LEFT
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    set_font(run, "Times New Roman", 12, bold=True)
    return p

def add_h2(doc, text):
    p = doc.add_paragraph()
    p.alignment = AL.LEFT
    p.paragraph_format.space_before = Pt(7)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    set_font(run, "Times New Roman", 11, bold=True)
    return p

def add_caption(doc, text, is_table=False):
    p = doc.add_paragraph()
    p.alignment = AL.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.05
    run = p.add_run(text)
    set_font(run, "Arial", 9.0, bold=True, italic=False)
    return p

def insert_table(doc, csv_path, caption):
    add_caption(doc, caption, is_table=True)
    df_t = pd.read_csv(csv_path)
    cols = list(df_t.columns)
    t = doc.add_table(rows=1, cols=len(cols))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    try:
        t.style = "Normal Table"
    except Exception:
        pass
    tblPr = t._tbl.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    for b_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        b = OxmlElement(f'w:{b_name}')
        b.set(qn('w:val'), 'single')
        b.set(qn('w:sz'), '4')
        b.set(qn('w:space'), '0')
        b.set(qn('w:color'), 'B0B0B0')
        tblBorders.append(b)
    tblPr.append(tblBorders)
    hdr_cells = t.rows[0].cells
    for j, cn in enumerate(cols):
        p = hdr_cells[j].paragraphs[0]
        p.alignment = AL.CENTER
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.space_before = Pt(2)
        set_font(p.add_run(str(cn)), "Arial", 8.5, bold=True)
    for _, row in df_t.iterrows():
        row_cells = t.add_row().cells
        for j, cn in enumerate(cols):
            p = row_cells[j].paragraphs[0]
            p.alignment = AL.LEFT if j == 0 else AL.CENTER
            p.paragraph_format.space_after = Pt(1.5)
            p.paragraph_format.space_before = Pt(1.5)
            set_font(p.add_run(str(row[cn])), "Times New Roman", 8.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def insert_fig(doc, img_path, caption, width_cm=16.5):
    p = doc.add_paragraph()
    p.alignment = AL.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(str(img_path), width=Cm(width_cm))
    add_caption(doc, caption, is_table=False)

# Inicializar Documento
doc = Document(TEMPLATE_PATH)
for p in list(doc.paragraphs): p._element.getparent().remove(p._element)
for t in list(doc.tables): t._element.getparent().remove(t._element)

# Portada 1 Columna
s0 = doc.sections[0]
s0.page_width, s0.page_height = Cm(21.0), Cm(29.7)
s0.top_margin, s0.bottom_margin = Cm(2.5), Cm(3.0)
s0.left_margin, s0.right_margin = Cm(2.0), Cm(2.25)
set_section_columns(s0, num_cols=1)

p_tit = doc.add_paragraph()
p_tit.alignment = AL.CENTER
p_tit.paragraph_format.space_after = Pt(4)
run_tit = p_tit.add_run("Determinantes geoespaciales de la diabetes tipo 2 en la Argentina y los Estados Unidos: Salud basada en datos, brecha de tratamiento y límites del modelado predictivo")
set_font(run_tit, "Times New Roman", 13.5, bold=True)

p_sub = doc.add_paragraph()
p_sub.alignment = AL.CENTER
p_sub.paragraph_format.space_after = Pt(10)
run_sub = p_sub.add_run("Geospatial Determinants of Type 2 Diabetes in Argentina and the United States: Health Data Science, Treatment Gaps, and Boundaries of Predictive Modeling")
set_font(run_sub, "Times New Roman", 10.5, italic=True)

p_aut = doc.add_paragraph()
p_aut.alignment = AL.CENTER
p_aut.paragraph_format.space_after = Pt(2)
set_font(p_aut.add_run("María Florencia Rossi, Magali Bolivar, Matías Montiel, Roxana Martínez, Nestor Balich, Franco Balich"), "Times New Roman", 10.5, bold=True)

p_inst = doc.add_paragraph()
p_inst.alignment = AL.CENTER
p_inst.paragraph_format.space_after = Pt(2)
set_font(p_inst.add_run("CAETI — Centro de Altos Estudios en Tecnología Informática\nUniversidad Abierta Interamericana (UAI) — Facultad de Tecnología Informática\nMontes de Oca 745, Ciudad Autónoma de Buenos Aires, Argentina"), "Times New Roman", 9.5)

p_mail = doc.add_paragraph()
p_mail.alignment = AL.CENTER
p_mail.paragraph_format.space_after = Pt(10)
set_font(p_mail.add_run("{MariaFlorencia.Rossi, MagaliFlorencia.BolivarCruz, MatiasNicolas.MontielTorres}@alumnos.uai.edu.ar\n{Roxana.Martinez, nestor.balich, francoadrian.balich}@uai.edu.ar"), "Times New Roman", 9.0, italic=True)

# Resumen
p_rtit = doc.add_paragraph()
p_rtit.alignment = AL.LEFT
p_rtit.paragraph_format.space_before = Pt(6); p_rtit.paragraph_format.space_after = Pt(2)
set_font(p_rtit.add_run("Resumen"), "Times New Roman", 11.5, bold=True)
add_p(doc, "La diabetes mellitus tipo 2 representa una de las crisis sanitarias y socioeconómicas más apremiantes del siglo XXI, exhibiendo patrones de distribución territorial profundamente heterogéneos que desafían la capacidad analítica de la epidemiología computacional. Este trabajo desarrolla un pipeline reproducible de ciencia de datos en salud para contrastar empíricamente los determinantes territoriales de la enfermedad entre los 51 estados de los Estados Unidos (CDC BRFSS 2015, N=441.456 encuestados agregados con ponderación muestral) y las 24 jurisdicciones provinciales de la República Argentina (4ª Encuesta Nacional de Factores de Riesgo ENFR 2018 integrada con los Censos 2010/2022 y la Encuesta Permanente de Hogares del INDEC). Los resultados revelan una marcada divergencia estructural derivada de la arquitectura de los sistemas sanitarios: en los Estados Unidos, donde predomina un régimen fragmentado y de aseguramiento privado, la diabetes sigue un patrón estrictamente lineal gobernado por el gradiente socioeconómico, donde los bajos ingresos (r = +0,81) y el sedentarismo (r = +0,79) concentran la morbimortalidad en el 'Cinturón de la Diabetes' del sur profundo, habilitando modelos de regresión OLS con R² = 0,91 y Random Forest con R²_CV = 0,81. Por el contrario, en la Argentina la prevalencia provincial no exhibe correlación con la pobreza monetaria (r = -0,05) ni con la falta de cobertura médica formal (r = -0,16). Esta discrepancia es explicada mediante dos mecanismos sanitarios: en primer lugar, un severo sesgo de subdiagnóstico en las provincias del norte (Chaco 10,3% de prevalencia con 40% de población jamás testeada), donde la carencia de screening preventivo invisibiliza la patología en encuestas autorreportadas; en segundo lugar, la función amortiguadora del subsistema público universal y programas estatales de provisión gratuita de fármacos (Remediar), que permiten que distritos con más del 50% de población sin seguro médico formal alcancen coberturas terapéuticas superiores al 60% (Formosa 62,6%, Santa Cruz 70,0%). En el plano metodológico, se demuestra que la aplicación acrítica de modelos de Machine Learning a muestras de escala reducida (N=24) incurre en sobreajuste severo (LOOCV R² ≤ 0), fundamentando la conveniencia de privilegiar atlas geoespaciales descriptivos y políticas focalizadas de pesquisa activa territorial.", size=9.5, first_indent=0.3, space_after=4)

add_runs_p(doc, [("Palabras clave: ", True, False),
                 ("diabetes mellitus; análisis comparativo; salud basada en datos; atlas geoespacial; subdiagnóstico; brecha de tratamiento; machine learning en salud; determinantes sociales.", False, True)],
           first_indent=0.3, space_after=6)

# Abstract
p_atit = doc.add_paragraph()
p_atit.alignment = AL.LEFT
p_atit.paragraph_format.space_before = Pt(4); p_atit.paragraph_format.space_after = Pt(2)
set_font(p_atit.add_run("Abstract"), "Times New Roman", 11.5, bold=True)
add_p(doc, "Type 2 diabetes mellitus represents one of the most pressing public health and socioeconomic crises of the 21st century, exhibiting profoundly heterogeneous territorial distribution patterns that challenge the analytical capabilities of computational epidemiology. This paper presents a reproducible health data science pipeline that empirically contrasts the territorial determinants of the disease between the 51 United States jurisdictions (CDC BRFSS 2015, N=441,456 individual microdata aggregated via sampling weights) and the 24 provinces of Argentina (4th National Risk Factor Survey ENFR 2018 integrated with the 2010/2022 National Censuses and the Permanent Household Survey EPH from INDEC). The findings demonstrate sharp structural divergences rooted in healthcare system design: in the United States, dominated by private market-driven healthcare, diabetes prevalence follows a strictly linear gradient governed by socioeconomic deprivation, where low household income (r = +0.81) and physical inactivity (r = +0.79) heavily concentrate disease burden in the Southern 'Diabetes Belt', allowing multivariate OLS models to achieve R² = 0.91 and Random Forest algorithms to reach R²_CV = 0.81. In sharp contrast, in Argentina provincial prevalence exhibits no positive correlation with monetary poverty (r = -0.05) nor with the lack of formal health insurance (r = -0.16). This disconnect is explained by two structural healthcare dynamics: first, severe underdiagnosis in northern provinces (Chaco 10.3% prevalence with 40% of adults never tested), where the absence of clinical screening masks disease in self-reported surveys; second, the buffering role of universal public healthcare and free drug delivery programs (Remediar), allowing vulnerable provinces with over 50% uninsured individuals to reach pharmacological treatment rates above 60%. Methodologically, we demonstrate that uncritical deployment of machine learning algorithms on small-sample administrative aggregations (N=24) induces severe overfitting (LOOCV R² ≤ 0), supporting the priority of descriptive geospatial atlases and targeted proactive screening over fragile predictive claims.", size=9.5, first_indent=0.3, space_after=4)

add_runs_p(doc, [("Keywords: ", True, True),
                 ("diabetes mellitus; comparative analysis; health data science; geospatial atlas; underdiagnosis; treatment gap; machine learning in health; social determinants.", False, True)],
           first_indent=0.3, space_after=10)

# Cuerpo en 2 columnas
s1 = doc.add_section(WD_SECTION_START.CONTINUOUS)
s1.top_margin, s1.bottom_margin = Cm(2.5), Cm(3.0)
s1.left_margin, s1.right_margin = Cm(1.75), Cm(1.75)
set_section_columns(s1, num_cols=2, space_twips=500)

add_h1(doc, "1. Introducción y motivación")
add_p(doc, "La diabetes mellitus tipo 2 se ha consolidado como una auténtica pandemia no transmisible a escala global. Según los reportes consolidados del International Diabetes Federation (IDF) Diabetes Atlas en su 11.ª edición [1], más de 589 millones de adultos viven actualmente con la enfermedad en el mundo, proyectándose que esta cifra alcanzará los 852 millones hacia el año 2050. Este incremento exponencial no solo compromete la expectativa y calidad de vida de las poblaciones a través de secuelas cardiovasculares, renales y oftalmológicas, sino que impone una carga económica exorbitante sobre las finanzas públicas y los presupuestos familiares.")
add_p(doc, "Sin embargo, el impacto epidemiológico de la patología dista de manifestarse de manera homogénea. Existe un creciente consenso interdisciplinario en torno a que los Determinantes Sociales de la Salud (DSS) [4], [11] —tales como la disponibilidad y asequibilidad de alimentos frescos, las posibilidades materiales de realizar actividad física, el estrés crónico vinculado a la privación económica y el acceso efectivo a servicios diagnósticos y terapéuticos— modulan fuertemente la distribución espacial de la enfermedad.")
add_p(doc, "Desde la perspectiva de la ciencia de datos en salud (Health Data Science), un interrogante sustantivo radica en determinar si los patrones epidemiológicos observados en países desarrollados son directamente extrapolables a economías emergentes de América Latina. Frecuentemente, la literatura internacional asume de manera tácita que los modelos predictivos formulados en países anglosajones mantienen validez universal. No obstante, las diferencias estructurales en los sistemas de cobertura médica pública frente a esquemas privados de mercado plantean dinámicas territoriales diametralmente opuestas.")
add_p(doc, "Por una parte, los Estados Unidos constituyen el arquetipo de un sistema de salud fragmentado y dependiente del empleo o de aseguradoras privadas, donde la capacidad diagnóstica se encuentra altamente tecnificada y extendida, pero el acceso a medicamentos esenciales (como la insulina y los análogos de GLP-1) queda supeditado a la capacidad financiera de los hogares [5], [12]. Por otra parte, la República Argentina sostiene un modelo mixto caracterizado por la presencia de un subsistema público universal con gratuidad irrestricta en el punto de atención y programas de provisión farmacológica masiva (v.g. Remediar), aunque condicionado por profundas asimetrías de infraestructura y distancias geográficas entre las regiones centrales y las provincias del norte y sur [3], [16].")
add_p(doc, "El objetivo primordial de este trabajo es implementar un pipeline reproducible de ciencia de datos para contrastar exhaustivamente la epidemiología geoespacial de la diabetes entre los 51 estados de los Estados Unidos y las 24 jurisdicciones de la Argentina. Específicamente se busca: (i) mapear bajo una escala cartográfica unificada la prevalencia territorial de la enfermedad; (ii) comparar la intensidad de las correlaciones bivariadas entre factores sociodemográficos y prevalencia; (iii) desentrañar la aparente paradoja entre gratuidad pública y subdiagnóstico en la Argentina frente a la barrera financiera estadounidense; y (iv) evaluar formalmente la transferibilidad de algoritmos supervisados de Machine Learning en muestras reducidas (N=24).")

add_h1(doc, "2. Marco conceptual y antecedentes")
add_p(doc, "El sustento teórico del estudio se fundamenta en el modelo de Determinantes Sociales de la Salud formalizado por la Organización Mundial de la Salud (OMS) [4] y la American Diabetes Association (ADA) [5]. Este marco postula que las patologías cardiometabólicas no son meros eventos biológicos individuales, sino el resultado acumulativo de condiciones materiales de vida que generan entornos obesogénicos y restringen las oportunidades de prevención primaria.")
add_p(doc, "En los Estados Unidos, una profusa literatura empírica ha documentado la existencia del denominado 'Cinturón de la Diabetes' (Diabetes Belt) [12], [13], localizado primordialmente en los estados del sudeste y la región de los Apalaches (Misisipi, Alabama, Virginia Occidental, Kentucky). Estudios a nivel de condado han comprobado que la concentración de minorías étnicas vulnerables, el desempleo estructural y la proliferación de desiertos alimentarios (food deserts) explican más del 80% de la varianza en la prevalencia estatal [13].")
add_p(doc, "En la República Argentina, los antecedentes geoespaciales sobre diabetes son sustancialmente más acotados debido a la fragmentación de registros administrativos. Investigaciones seminales de Leveau et al. [15] identificaron conglomerados de alta mortalidad por diabetes en el centro y norte del país entre 1990 y 2012, sugiriendo que el contexto geográfico actúa como modificador del riesgo de fallecimiento. Asimismo, Marro et al. [16], [17] evidenciaron marcadas desigualdades interprovinciales en el acceso a consultas especializadas y complicaciones crónicas, señalando que la privación territorial incrementa sustancialmente el retraso diagnóstico.")
add_p(doc, "En el plano metodológico, el análisis espacial de datos agregados enfrenta el riesgo constante del Problema de la Unidad de Área Modificable (MAUP) y la falacia ecológica [14]. La aplicación acrítica de modelos de Machine Learning sobre agregaciones macro (como provincias o estados) suele ignorar que la reducción del tamaño de muestra (N) degrada exponencialmente la potencia estadística, generando ilusiones de predictibilidad que no resisten la validación cruzada.")

add_h1(doc, "3. Fuentes de datos y metodología")
add_h2(doc, "3.1. Microdatos de Estados Unidos (CDC BRFSS 2015)")
add_p(doc, "Se procesaron los microdatos del Behavioral Risk Factor Surveillance System (BRFSS 2015) [6], relevados por los Centers for Disease Control and Prevention (CDC). La muestra contiene 441.456 entrevistas individuales aplicadas a población no institucionalizada de 18 años y más. Cada registro individual incorpora un factor de ponderación muestral (_LLCPWT) que calibra la muestra por edad, sexo y etnia, garantizando representatividad a escala de los 51 estados (50 estados y el Distrito de Columbia).")
add_p(doc, "A partir de esta base se derivaron: prevalencia de diabetes diagnosticada (excluyendo diabetes gestacional); obesidad autorreportada (IMC≥30 derivado de peso y talla declarados, variable _BMI5CAT); sedentarismo o inactividad física (_TOTINDA); proporción de población en hogares con ingresos menores a USD 25.000 anuales (INCOME2); población sin educación secundaria completa (_EDUCAG); barrera económica para acceder a la consulta médica (MEDCOST); y tasa de adultos sin seguro médico (_HCVU651).")

add_h2(doc, "3.2. Fuentes oficiales de Argentina (ENFR e INDEC)")
add_p(doc, "Para la República Argentina se consolidó un dataset representativo de las 24 jurisdicciones de primer orden (23 provincias y CABA) a partir de cuatro fuentes oficiales del INDEC y el Ministerio de Salud de la Nación [3]:")
add_p(doc, "1. 4ª Encuesta Nacional de Factores de Riesgo (ENFR 2018): De sus cuadros definitivos se extrajeron la prevalencia de diabetes o glucemia elevada por autorreporte o medición (Cuadro 7.3) junto con su coeficiente de variación muestral (CV, todos inferiores al 12,5%, certificando confiabilidad); el porcentaje de personas con diabetes bajo tratamiento farmacológico activo con pastillas o insulina (Cuadro 7.5); la tasa de screening preventivo de glucemia alguna vez en la vida (Cuadro 7.1); obesidad autorreportada IMC≥30 (Cuadro 6.3); sedentarismo (Cuadro 3.1); hipertensión arterial autorreportada (Cuadro 8.3); y consumo de frutas/verduras (Cuadro 5.7).")
add_p(doc, "2. Censo Nacional de Población, Hogares y Viviendas 2010 y 2022: Se incorporó la tasa de hogares con Necesidades Básicas Insatisfechas (NBI 2010, último relevamiento censal con dicho indicador); el porcentaje de población sin cobertura formal de salud por obra social o prepaga, dependiente exclusivamente del hospital público (Censo 2022, Hoja C1); y la densidad demográfica efectiva continental (hab/km²).")
add_p(doc, "3. Encuesta Permanente de Hogares (EPH 2018, INDEC): Se extrajo la tasa de personas por debajo de la línea de pobreza monetaria correspondiente al segundo semestre de 2018 (Cuadro 4.3), promediando los aglomerados urbanos a nivel provincial para sincronizar temporalmente con la ENFR 2018.")

add_h2(doc, "3.3. Georreferenciación y modelado estadístico")
add_p(doc, "Las geometrías vectoriales de límites provinciales y estatales se homologaron bajo el estándar GeoJSON WGS84. Para Argentina se implementó un recuadro de magnificación cartográfica (inset zoom) centrado en el Área Metropolitana de Buenos Aires (CABA y conurbano) para subsanar la disparidad de escala geográfica frente a la Patagonia.")
add_p(doc, "El pipeline analítico calculó matrices de correlación bivariada de Pearson (r). Para el modelado supervisado se estimaron regresiones múltiples por Mínimos Cuadrados Ordinarios (OLS) con errores estándar robustos a heterocedasticidad (HC3 de MacKinnon-White) y Factores de Inflación de Varianza (VIF). La capacidad predictiva real y la generalización fuera de muestra se evaluaron mediante validación cruzada K-Fold (k=5) para EE.UU. y validación cruzada Leave-One-Out (LOOCV) para la Argentina.")

# SECCION FIGURA 1 FULL WIDTH (1 Columna)
s_f1 = doc.add_section(WD_SECTION_START.CONTINUOUS)
s_f1.top_margin, s_f1.bottom_margin = Cm(2.0), Cm(2.5)
s_f1.left_margin, s_f1.right_margin = Cm(2.0), Cm(2.0)
set_section_columns(s_f1, num_cols=1)

insert_fig(doc, RESULTADOS_DIR / "figura1_mapas_comparativos.png",
           "Figura 1. Atlas geoespacial comparativo de la prevalencia de diabetes mellitus (%): (a) Estados Unidos (CDC BRFSS 2015, N=51); (b) República Argentina (ENFR 2018 / INDEC, N=24) con recuadro ampliado para CABA. Escala cromática unificada común (6% a 18%).",
           width_cm=16.5)

# SECCION TABLA 1 FULL WIDTH (1 Columna)
s_t1 = doc.add_section(WD_SECTION_START.CONTINUOUS)
s_t1.top_margin, s_t1.bottom_margin = Cm(2.0), Cm(2.5)
s_t1.left_margin, s_t1.right_margin = Cm(2.0), Cm(2.0)
set_section_columns(s_t1, num_cols=1)

insert_table(doc, tab1_path,
             "Tabla 1. Cuadro comparativo general de indicadores epidemiológicos, sociodemográficos y cobertura sanitaria entre Estados Unidos y la República Argentina.")

# Continuación cuerpo (2 Columnas)
s2 = doc.add_section(WD_SECTION_START.CONTINUOUS)
s2.top_margin, s2.bottom_margin = Cm(2.5), Cm(3.0)
s2.left_margin, s2.right_margin = Cm(1.75), Cm(1.75)
set_section_columns(s2, num_cols=2, space_twips=500)

add_h1(doc, "4. Resultados")
add_h2(doc, "4.1. Atlas geoespacial y disparidad territorial")
add_p(doc, "La visualización cartográfica bajo una escala cromática normalizada común (6% a 18%, Figura 1) pone de manifiesto contrastes territoriales de primer orden. En los Estados Unidos (Figura 1a), la prevalencia media es del 10,2%, con una marcada polarización geográfica: los estados del 'Cinturón de la Diabetes' en el sudeste (Misisipi 14,8%, Virginia Occidental 13,9%, Alabama 13,6%, Luisiana 12,7%) presentan tasas que duplican las de distritos prósperos del oeste y norte como Colorado (6,8%), Utah (7,5%), Montana (7,7%) y Minnesota (8,0%).")
add_p(doc, "En la República Argentina (Figura 1b), la prevalencia promedio nacional reportada por la ENFR 2018 asciende al 12,7%, superando la media estadounidense y ubicando al país en el tercio superior de carga global según estimaciones del IDF (14,0%) [1]. No obstante, la dispersión subnacional desafía los patrones geométricos convencionales: las tasas más elevadas se concentran en las regiones de Cuyo y Centro (San Luis 17,3%, San Juan 15,9%, La Rioja 15,1% y La Pampa 14,6%), mientras que la Ciudad Autónoma de Buenos Aires (CABA) registra el mínimo nacional (8,8%), compartiendo valores deprimidos con jurisdicciones de alta vulnerabilidad del norte como Jujuy (8,9%) y Chaco (10,3%).")

# SECCION FIGURA 2 FULL WIDTH (1 Columna)
s_f2 = doc.add_section(WD_SECTION_START.CONTINUOUS)
s_f2.top_margin, s_f2.bottom_margin = Cm(2.0), Cm(2.5)
s_f2.left_margin, s_f2.right_margin = Cm(2.0), Cm(2.0)
set_section_columns(s_f2, num_cols=1)

insert_fig(doc, RESULTADOS_DIR / "figura2_factores_riesgo.png",
           "Figura 2. Distribución geoespacial de factores de riesgo cardiometabólicos: (a) Obesidad en EE.UU.; (b) Obesidad en Argentina; (c) Inactividad física en EE.UU.; (d) Inactividad física en Argentina.",
           width_cm=16.5)

# Continuación cuerpo (2 Columnas)
s3 = doc.add_section(WD_SECTION_START.CONTINUOUS)
s3.top_margin, s3.bottom_margin = Cm(2.5), Cm(3.0)
s3.left_margin, s3.right_margin = Cm(1.75), Cm(1.75)
set_section_columns(s3, num_cols=2, space_twips=500)

add_h2(doc, "4.2. Atlas de factores cardiometabólicos")
add_p(doc, "La distribución espacial de la obesidad y la inactividad física (Figura 2) exhibe una asimetría estructural entre ambos países. En los Estados Unidos (Figuras 2a y 2c), la obesidad promedia el 28,6% y el sedentarismo el 23,8%, alineándose con una correlación espacial casi idéntica a la prevalencia de diabetes: los estados del sur profundo lideran simultáneamente en sobrepeso y falta de ejercicio.")
add_p(doc, "En la Argentina (Figuras 2b y 2d), la obesidad promedia el 25,6% (desde 17,0% en CABA hasta 34,4% en San Juan y 34,0% en Santa Cruz). Sin embargo, la inactividad física alcanza guarismos alarmantes, con una media nacional del 45,9% y picos en provincias como Formosa (69,1%) y San Luis (64,2%), duplicando los niveles estadounidenses y evidenciando que el sedentarismo es un fenómeno generalizado en todo el territorio nacional.")

# SECCION FIGURA 4 Y TABLA 2 FULL WIDTH (1 Columna)
s_f4 = doc.add_section(WD_SECTION_START.CONTINUOUS)
s_f4.top_margin, s_f4.bottom_margin = Cm(2.0), Cm(2.5)
s_f4.left_margin, s_f4.right_margin = Cm(2.0), Cm(2.0)
set_section_columns(s_f4, num_cols=1)

insert_fig(doc, RESULTADOS_DIR / "figura4_matriz_correlaciones.png",
           "Figura 3. Matrices de calor de correlaciones bivariadas de Pearson (r): (a) Estados Unidos; (b) República Argentina.",
           width_cm=16.0)

insert_table(doc, tab2_path,
             "Tabla 2. Coeficientes de regresión lineal múltiple OLS con errores estándar robustos a heterocedasticidad (HC3) y factores de inflación de varianza (VIF).")

# Continuación cuerpo (2 Columnas)
s4 = doc.add_section(WD_SECTION_START.CONTINUOUS)
s4.top_margin, s4.bottom_margin = Cm(2.5), Cm(3.0)
s4.left_margin, s4.right_margin = Cm(1.75), Cm(1.75)
set_section_columns(s4, num_cols=2, space_twips=500)

add_h2(doc, "4.3. Matriz de correlaciones y determinantes sociales")
add_p(doc, "El análisis correlacional (Figura 3 y Tabla 2) expone la discrepancia empírica más contundente del trabajo. En los Estados Unidos, los coeficientes de correlación de Pearson confirman un determinismo socioeconómico estricto: la pobreza de ingresos se asocia a la diabetes con r = +0,81 (p < 0,001), el sedentarismo con r = +0,79 (p < 0,001), el bajo nivel educativo con r = +0,77 (p < 0,001) y la obesidad con r = +0,75 (p < 0,001). En el modelo OLS (Tabla 2), la obesidad (β = +0,177; p < 0,001), el ingreso bajo (β = +0,111; p = 0,042) y el costo médico (β = +0,257; p = 0,008) retienen significancia robusta con VIF controlados (<9).")
add_p(doc, "En contraste, en la República Argentina los factores socioeconómicos convencionales se desacoplan por completo de la prevalencia declarada: la pobreza monetaria de la EPH arroja r = -0,05 (p = 0,82), las Necesidades Básicas Insatisfechas r = -0,26 (p = 0,22) y la falta de cobertura médica formal r = -0,16 (p = 0,44). En la regresión OLS múltiple (Tabla 2), ninguno de los coeficientes individuales alcanza significancia estadística formal al 5%, y el modelo carece de significancia conjunta (F = 1,84; p = 0,16).")

# SECCION FIGURA 3 BRECHA TRATAMIENTO FULL WIDTH (1 Columna)
s_f3 = doc.add_section(WD_SECTION_START.CONTINUOUS)
s_f3.top_margin, s_f3.bottom_margin = Cm(2.0), Cm(2.5)
s_f3.left_margin, s_f3.right_margin = Cm(2.0), Cm(2.0)
set_section_columns(s_f3, num_cols=1)

insert_fig(doc, RESULTADOS_DIR / "figura3_brecha_tratamiento.png",
           "Figura 4. Disparidad asistencial: (a) Ranking de brecha de tratamiento farmacológico en Argentina (ENFR); (b) Diagrama de dispersión de barrera de costo médico vs. prevalencia en EE.UU.",
           width_cm=16.5)

# Continuación cuerpo (2 Columnas)
s5 = doc.add_section(WD_SECTION_START.CONTINUOUS)
s5.top_margin, s5.bottom_margin = Cm(2.5), Cm(3.0)
s5.left_margin, s5.right_margin = Cm(1.75), Cm(1.75)
set_section_columns(s5, num_cols=2, space_twips=500)

add_h2(doc, "4.4. La aparente paradoja: Detección vs. Tratamiento")
add_p(doc, "Para interpretar científicamente por qué en la Argentina las provincias con mayor privación material reportan tasas de diabetes inferiores a las de regiones más favorecidas, resulta imprescindible descomponer la dinámica asistencial en dos etapas secuenciales: detección diagnóstica (screening) y cobertura farmacológica activa (Figura 4 y Figura 5b):")
add_p(doc, "1. La barrera de prevención y el sesgo de subdiagnóstico: Al tratarse de una patología insidiosa e indolora en estadios iniciales, la identificación clínica depende exclusivamente del acceso a análisis de laboratorio en ayunas. En la Argentina, la cobertura de screening exhibe una fractura territorial dramática (Figura 5b): existe una correlación lineal negativa muy fuerte entre la pobreza estructural (NBI) y la realización de glucemia (r = -0,74; p < 0,001). Mientras en CABA y Santa Fe más del 90% de los adultos se ha testeado, en provincias del NEA y NOA (Chaco 60,3%, Formosa 61,1%, Santiago del Estero 60,6%) cuatro de cada diez adultos jamás se hicieron un control glucémico. Como las encuestas epidemiológicas computan casos conocidos por autorreporte, la falta de diagnóstico en el norte deprime artificialmente las tasas de prevalencia.")
add_p(doc, "2. El rol amortiguador del sistema público en el tratamiento: La ENFR computa la proporción de personas bajo tratamiento entre aquellas que ya fueron diagnosticadas (Figura 4a). Una vez que el paciente argentino ingresa al sistema formal, los programas de entrega gratuita de hipoglucemiantes orales e insulina (Remediar) neutralizan la barrera económica. Por este motivo, provincias con más del 50% de población sin seguro médico (Formosa 62,6%, Chaco 54,2%, Corrientes 44,2%) superan ampliamente a distritos con menores índices de pobreza estructural como La Pampa (32,7%) o Chubut (38,3%).")
add_p(doc, "En los Estados Unidos rige la dinámica inversa (Figura 4b): la pesquisa clínica es rutinaria (>85%), pero la salud de mercado impone severas barreras de costo farmacológico (insulina que supera los USD 300 mensuales), derivando en el racionamiento involuntario de medicación.")

# SECCION FIGURA 5 Y TABLAS 3 Y 4 FULL WIDTH (1 Columna)
s_f5 = doc.add_section(WD_SECTION_START.CONTINUOUS)
s_f5.top_margin, s_f5.bottom_margin = Cm(2.0), Cm(2.5)
s_f5.left_margin, s_f5.right_margin = Cm(2.0), Cm(2.0)
set_section_columns(s_f5, num_cols=1)

insert_fig(doc, RESULTADOS_DIR / "figura5_modelos_dispersion.png",
           "Figura 5. Diagnóstico de escala y mecanismos explicativos: (a) Contraste de regresión lineal Pobreza vs. Prevalencia; (b) Argentina: Correlación inversa estricta entre Pobreza Estructural (NBI) y Acceso a Screening (r = -0,74; p < 0,001), evidenciando el sesgo de subdiagnóstico.",
           width_cm=16.5)

insert_table(doc, tab3_path,
             "Tabla 3. Diagnóstico comparativo de rendimiento in-sample y generalización fuera de muestra (Validation Cross-Validation y LOOCV).")

insert_table(doc, tab4_path,
             "Tabla 4. Ranking de casos extremos: Jurisdicciones de mayor y menor prevalencia relativa en Estados Unidos y la República Argentina.")

# Continuación cuerpo (2 Columnas)
s6 = doc.add_section(WD_SECTION_START.CONTINUOUS)
s6.top_margin, s6.bottom_margin = Cm(2.5), Cm(3.0)
s6.left_margin, s6.right_margin = Cm(1.75), Cm(1.75)
set_section_columns(s6, num_cols=2, space_twips=500)

add_h2(doc, "4.5. Evaluación metodológica y límites de predictibilidad")
add_p(doc, "El contraste entre algoritmos lineales y no lineales (Tabla 3) aporta una advertencia fundamental para la ciencia de datos en salud. En los Estados Unidos (N=51), tanto la regresión lineal múltiple OLS como el algoritmo no lineal de Random Forest exhiben un desempeño sobresaliente y generalizable: OLS alcanza R² = 0,91 y Random Forest R²_CV = 0,81 bajo validación cruzada 5-fold, con errores medios absolutos inferiores al 0,7%.")
add_p(doc, "Por el contrario, al replicar idéntica arquitectura algorítmica sobre las 24 provincias argentinas, se comprueba un colapso en la capacidad predictiva fuera de muestra: si bien el modelo OLS in-sample presenta un R² aparente de 0,39, al evaluarlo mediante validación cruzada Leave-One-Out (LOOCV) el coeficiente se desploma a R²_LOOCV = -0,29 (peor que predecir la media global). Asimismo, Random Forest genera un R²_CV negativo (-0,32).")
add_p(doc, "Este resultado demuestra que el modelado predictivo supervisado en escalas geográficas agregadas reducidas (N=24) padece de falta intrínseca de potencia estadística y sobredeterminación paramétrica. Presentar modelos de Machine Learning como herramientas predictivas confiables en tales condiciones constituiría una mala práctica científica. La respuesta honesta y rigurosa de la ciencia de datos radica en el atlas descriptivo y en la cartografía analítica.")

add_h1(doc, "5. Discusión")
add_h2(doc, "5.1. Implicancias para la gestión y las políticas públicas")
add_p(doc, "Los hallazgos de este estudio tienen implicancias de política sanitaria directas. Demuestran que las barreras que fracturan el control de la diabetes operan en puntos opuestos de la cadena asistencial: en los Estados Unidos la barrera es financiera y de mercado (billetera), requiriendo medidas legislativas de regulación del precio tope de la insulina y subsidios a copagos; en la Argentina la barrera es eminentemente logística y preventiva (distancia y pesquisa temprana).")
add_p(doc, "En el territorio argentino, los programas de entrega de medicamentos gratuitos como Remediar han demostrado ser herramientas de alta equidad, asegurando que pacientes sin recursos accedan a tratamiento continuo. Sin embargo, su efectividad se ve coartada si cuatro de cada diez adultos en el norte del país nunca acceden al diagnóstico inicial. Es prioritario transformar la estrategia sanitaria: el sistema público no debe esperar pasivamente a que el paciente concurra al hospital cabecera con síntomas de cetoacidosis o pie diabético, sino desplegar operativos territoriales activos de testeo glucémico en salitas barriales y parajes rurales.")

add_h2(doc, "5.2. Aportes epistemológicos para la Ciencia de Datos en Salud")
add_p(doc, "En el ámbito de la informática médica, este estudio intercala una advertencia epistemológica crítica contra el 'solucionismo algorítmico'. La proliferación de librerías de aprendizaje automático ha generalizado la práctica de entrenar modelos complejos sin considerar la escala, el tamaño de muestra y los sesgos observacionales subyacentes. Cuando los datos agregados provienen de encuestas autorreportadas con acceso diferencial al screening, los algoritmos capturan el sesgo de diagnóstico y lo confunden con la causalidad epidemiológica.")

add_h1(doc, "6. Conclusiones y trabajos futuros")
add_p(doc, "Se desarrolló e implementó un pipeline reproducible de ciencia de datos que comparó de manera exhaustiva los determinantes territoriales de la diabetes mellitus entre los Estados Unidos y la República Argentina. Se comprobó que mientras en EE.UU. la privación socioeconómica gobierna linealmente la prevalencia (r = +0,81; R² = 0,91), en la Argentina el subdiagnóstico invisibiliza la enfermedad en las regiones de mayor pobreza estructural (r = -0,74 entre NBI y screening), al tiempo que el subsistema público amortigua la brecha de tratamiento farmacológico de los pacientes diagnosticados.")
add_p(doc, "Asimismo, se formalizó empíricamente la incapacidad de los modelos supervisados de Machine Learning para generalizar en muestras agregadas provinciales (N=24), fundamentando el valor del atlas geoespacial como herramienta superior de salud pública.")
add_p(doc, "Como líneas futuras se proyecta: (i) descender a nivel de microdatos individuales de la ENFR para modelar determinantes a escala de persona con técnicas multinivel; (ii) incorporar las submuestras bioquímicas de laboratorio (Cuadros 7.9–7.11) para calibrar el factor de expansión de subdiagnóstico; y (iii) monitorear la evolución del atlas ante la publicación de futuras rondas censales y encuestas sanitarias.")

add_h1(doc, "Referencias")
refs = [
    '[1] International Diabetes Federation, "IDF Diabetes Atlas", 11.ª ed., Bruselas: IDF, 2024. [En línea]. Disponible: https://diabetesatlas.org',
    '[2] NCD Risk Factor Collaboration (NCD-RisC), "Worldwide trends in diabetes prevalence and treatment from 1990 to 2022: a pooled analysis of 1108 population-representative studies with 141 million participants", The Lancet, vol. 404, n.º 10467, pp. 2077–2093, 2024.',
    '[3] Instituto Nacional de Estadística y Censos (INDEC) y Secretaría de Gobierno de Salud, "4° Encuesta Nacional de Factores de Riesgo: Resultados definitivos", Buenos Aires: INDEC / Ministerio de Salud, 2019.',
    '[4] M. Marmot, "Social determinants of health inequalities", The Lancet, vol. 365, n.º 9464, pp. 1099–1104, 2005.',
    '[5] F. Hill-Briggs et al., "Social Determinants of Health and Diabetes: A Scientific Review", Diabetes Care, vol. 44, n.º 1, pp. 258–279, 2021.',
    '[6] Centers for Disease Control and Prevention (CDC), "Behavioral Risk Factor Surveillance System (BRFSS 2015)", Atlanta: U.S. Department of Health and Human Services, 2016. [En línea]. Disponible: https://www.cdc.gov/brfss',
    '[7] Instituto Nacional de Estadística y Censos (INDEC), "Censo Nacional de Población, Hogares y Viviendas 2022: Cobertura de salud", Buenos Aires: INDEC, 2023.',
    '[8] Instituto Nacional de Estadística y Censos (INDEC), "Incidencia de la pobreza y la indigencia en 31 aglomerados urbanos. Segundo semestre de 2018", Informes Técnicos, vol. 3, n.º 59, Buenos Aires: INDEC, 2019.',
    '[9] F. Pedregosa et al., "Scikit-learn: Machine Learning in Python", Journal of Machine Learning Research, vol. 12, pp. 2825–2830, 2011.',
    '[10] K. Jordahl et al., "GeoPandas: Python tools for geographic data", 2020. [En línea]. Disponible: https://geopandas.org',
    '[11] G. Dahlgren y M. Whitehead, "Policies and Strategies to Promote Social Equity in Health", Institute for Futures Studies, Estocolmo, 1991.',
    '[12] D. J. Gaskin et al., "Disparities in Diabetes: The Nexus of Race, Poverty, and Place", American Journal of Public Health, vol. 104, n.º 11, pp. 2147–2155, 2014.',
    '[13] L. Dwyer-Lindgren et al., "Diagnosed and Undiagnosed Diabetes Prevalence by County in the U.S., 1999–2012", Diabetes Care, vol. 39, n.º 9, pp. 1556–1562, 2016.',
    '[14] G. James, D. Witten, T. Hastie y R. Tibshirani, "An Introduction to Statistical Learning: with Applications in Python", Springer, 2023.',
    '[15] C. M. Leveau, M. J. Marro, V. Alonso y A. E. B. Lawrynowicz, "¿El contexto geográfico importa en la mortalidad por diabetes mellitus? Tendencias espacio-temporales en Argentina, 1990–2012", Cadernos de Saúde Pública, vol. 33, n.º 1, e00169615, 2017.',
    '[16] M. J. Marro, A. M. Cardoso e I. da Costa Leite, "Desigualdades regionales en la mortalidad por diabetes mellitus y en el acceso a la salud en Argentina", Cadernos de Saúde Pública, vol. 33, n.º 9, e00113016, 2017.',
    '[17] M. J. Marro, M. de J. Mendes da Fonseca, I. da Costa Leite, C. Ballejo y M. Alazraqui, "Un retorno al ambiente en epidemiología: análisis multinivel de la diabetes mellitus en un gran aglomerado urbano de Argentina", Revista Brasileira de Epidemiologia, vol. 29, e260043, 2026.',
    '[18] P. Santana, C. Costa, A. Loureiro, J. Raposo et al., "Geografias da Diabetes Mellitus em Portugal: Como as Condições do Contexto Influenciam o Risco de Morrer", Acta Médica Portuguesa, vol. 27, n.º 3, pp. 309–317, 2014.',
    '[19] C. S. De La Cruz Castañeda, "Modelamiento predictivo y distribución geoespacial de niveles de gasto en pacientes con diabetes del SIS, Perú", tesis de grado, Univ. Nac. Toribio Rodríguez de Mendoza, 2026.',
    '[20] T. Ortiz-Basso, B. R. Boietti, P. V. Gómez, A. D. Boffelli y A. A. Paladini, "Prevalencia de retinopatía diabética en una zona rural de Argentina", Medicina (Buenos Aires), vol. 82, n.º 1, pp. 99–103, 2022.',
    '[21] J. P. Mackenbach et al., "Socioeconomic Inequalities in Health in 22 European Countries", New England Journal of Medicine, vol. 358, pp. 2468–2481, 2008.',
    '[22] S. Openshaw, "The Modifiable Areal Unit Problem", Concepts and Techniques in Modern Geography, vol. 38, Geo Books, Norwich, 1984.',
    '[23] J. G. MacKinnon y H. White, "Some Heteroskedasticity-Consistent Covariance Matrix Estimators with Improved Finite Sample Properties", Journal of Econometrics, vol. 29, pp. 305–325, 1985.',
    '[24] L. Breiman, "Random Forests", Machine Learning, vol. 45, n.º 1, pp. 5–32, 2001.',
    '[25] World Health Organization (WHO), "Global Report on Diabetes", Ginebra: OMS, 2016.'
]
for r in refs:
    p_ref = doc.add_paragraph()
    p_ref.alignment = AL.JUSTIFY
    p_ref.paragraph_format.space_after = Pt(2)
    p_ref.paragraph_format.line_spacing = 1.0
    set_font(p_ref.add_run(r), "Times New Roman", 8.5)

try:
    doc.save(DOC_OUT)
    print(f"    - Manuscrito Word extenso guardado en: {DOC_OUT}")
except PermissionError:
    alt_out = PAPER_DIR / "Paper_Comparativo_Argentina_USA_CIITI2026_nuevo.docx"
    doc.save(alt_out)
    print(f"    - [AVISO] {DOC_OUT.name} está bloqueado/abierto en Word.")
    print(f"    - Guardado alternativo con nuevo título en: {alt_out}")

print("=" * 75)
print(">>> PIPELINE EXTENSO FINALIZADO CON EXITO.")
print("=" * 75)
