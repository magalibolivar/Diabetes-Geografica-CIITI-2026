# -*- coding: utf-8 -*-
"""
08 - Generador de figura y análisis comparativo Argentina vs. Estados Unidos.

Genera un gráfico comparativo de alto impacto visual (mapas de calor geográficos,
matriz de calor de correlaciones y diagrama de dispersión de pobreza vs. diabetes).

Salidas:
- figures/comparativa_argentina_usa.png
- PRopuesta_Argentiva_VS_Est_Unidos/figura_comparativa_argentina_usa.png
"""
import warnings
warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import scipy.stats as stats

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processed"
GEO = ROOT / "geo"
FIG = ROOT / "figures"
PROP_DIR = ROOT / "PRopuesta_Argentiva_VS_Est_Unidos"
FIG.mkdir(exist_ok=True)
PROP_DIR.mkdir(exist_ok=True)

# 1. CARGA DE DATOS
print(">>> Cargando datasets y capas geograficas...")
df_arg = pd.read_csv(DATA / "enfr2018_provincias.csv")
gdf_arg = gpd.read_file(GEO / "argentina_provincias.geojson")
gdf_arg["provincia"] = gdf_arg["shapeName"].replace({
    "Ciudad Autónoma de Buenos Aires": "CABA",
    "Ciudad Autnoma de Buenos Aires": "CABA"
})
arg_merged = gdf_arg.merge(df_arg, on="provincia", how="inner")

df_us = pd.read_csv(DATA / "brfss2015_estados.csv")
gdf_us = gpd.read_file(GEO / "us_states.geojson").rename(columns={"name": "estado"}).merge(df_us, on="estado", how="inner")
us_cont = gdf_us[~gdf_us["estado"].isin(["Alaska", "Hawaii"])].copy()

# 2. CONFIGURACION DE LA FIGURA MULTIPANEL
plt.rcParams.update({
    "figure.dpi": 200,
    "font.family": "sans-serif",
    "font.size": 9,
    "axes.titlesize": 10.5,
    "axes.titleweight": "bold",
})

fig = plt.figure(figsize=(15, 12))
# GridSpec: 2 filas x 2 columnas principales
gs = fig.add_gridspec(2, 2, height_ratios=[1.15, 1.0], hspace=0.28, wspace=0.22)

# Normalizacion comun para los mapas de calor de diabetes
vmin_diab, vmax_diab = 6.0, 18.0
cmap_heat = "YlOrRd"

# ------------------------------------------------------------------------------
# PANEL 1: MAPA ESTADOS UNIDOS (Arriba Izquierda)
# ------------------------------------------------------------------------------
ax_us = fig.add_subplot(gs[0, 0])
us_cont.plot(column="tasa_diabetes_pct", ax=ax_us, cmap=cmap_heat,
             vmin=vmin_diab, vmax=vmax_diab, edgecolor="#4a5568", linewidth=0.5)
ax_us.set_title("Estados Unidos: Prevalencia de Diabetes (%)\n[CDC BRFSS 2015; N=51 estados]", fontsize=11, fontweight="bold")
ax_us.set_axis_off()

# Anotaciones en EE.UU.
ax_us.annotate("Cinturón de la Diabetes\n(Misisipi 14,8%, Alabama 13,6%)",
               xy=(-88.5, 32.5), xytext=(-98.0, 26.5),
               arrowprops=dict(facecolor="#c53030", arrowstyle="->", lw=1.2),
               fontsize=8, fontweight="bold",
               bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#c53030", alpha=0.95))

ax_us.annotate("Colorado: 6,8% (Mín)",
               xy=(-105.5, 39.0), xytext=(-116.0, 42.0),
               arrowprops=dict(facecolor="#2b6cb0", arrowstyle="->", lw=1.0),
               fontsize=8, fontweight="bold",
               bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#2b6cb0", alpha=0.95))

# ------------------------------------------------------------------------------
# PANEL 2: MAPA ARGENTINA (Arriba Derecha)
# ------------------------------------------------------------------------------
ax_arg = fig.add_subplot(gs[0, 1])
arg_merged.plot(column="tasa_diabetes_pct", ax=ax_arg, cmap=cmap_heat,
                vmin=vmin_diab, vmax=vmax_diab, edgecolor="#4a5568", linewidth=0.6)
ax_arg.set_title("Argentina: Prevalencia de Diabetes (%)\n[ENFR 2018; N=24 jurisdicciones]", fontsize=11, fontweight="bold")
ax_arg.set_axis_off()

# Inset CABA
ax_ins = inset_axes(ax_arg, width="100%", height="100%",
                    bbox_to_anchor=(0.72, 0.52, 0.28, 0.28), bbox_transform=ax_arg.transAxes, borderpad=0)
arg_merged.plot(column="tasa_diabetes_pct", ax=ax_ins, cmap=cmap_heat,
                vmin=vmin_diab, vmax=vmax_diab, edgecolor="#4a5568", linewidth=0.6)
ax_ins.set_xlim(-58.85, -58.20)
ax_ins.set_ylim(-34.85, -34.35)
ax_ins.set_xticks([]); ax_ins.set_yticks([])
for sp in ax_ins.spines.values():
    sp.set_edgecolor("#2d3748"); sp.set_linewidth(1.2)
ax_ins.set_title("CABA: 8,8%", fontsize=8, fontweight="bold", pad=2)

# Anotaciones en Argentina
ax_arg.annotate("San Luis: 17,3%\n(Máx. nacional)",
                xy=(-66.3, -33.3), xytext=(-73.5, -31.0),
                arrowprops=dict(facecolor="#c53030", arrowstyle="->", lw=1.0),
                fontsize=8, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#c53030", alpha=0.95))

ax_arg.annotate("Subdiagnóstico en el Norte:\nChaco 10,3% (40% sin screening)",
                xy=(-60.5, -26.8), xytext=(-54.0, -23.5),
                arrowprops=dict(facecolor="#2b6cb0", arrowstyle="->", lw=1.0),
                fontsize=8, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#2b6cb0", alpha=0.95))

# Barra de color compartida para los mapas
sm = plt.cm.ScalarMappable(cmap=cmap_heat, norm=plt.Normalize(vmin=vmin_diab, vmax=vmax_diab))
sm._A = []
cbar = fig.colorbar(sm, ax=[ax_us, ax_arg], orientation="horizontal",
                    fraction=0.035, pad=0.04, aspect=35, shrink=0.6)
cbar.set_label("Prevalencia de diabetes (%) — Escala común", fontsize=10, fontweight="bold")

# ------------------------------------------------------------------------------
# PANEL 3: HEATMAP COMPARATIVO DE CORRELACIONES (Abajo Izquierda)
# ------------------------------------------------------------------------------
ax_corr = fig.add_subplot(gs[1, 0])

# Variables equivalentes
common_vars = ["Diabetes", "Obesidad", "Sedentarismo", "Pobreza", "Sin Cobertura"]

# EE.UU.
us_sub = df_us[["tasa_diabetes_pct", "obesidad_pct", "inactividad_fisica_pct", "pobreza_ingresos_pct", "sin_cobertura_salud_pct"]]
r_us = us_sub.corr()["tasa_diabetes_pct"].values

# Argentina
arg_sub = df_arg[["tasa_diabetes_pct", "obesidad_pct", "inactividad_fisica_pct", "pobreza_personas_pct", "sin_cobertura_salud_pct"]]
r_arg = arg_sub.corr()["tasa_diabetes_pct"].values

corr_compare = pd.DataFrame({
    "EE.UU. (BRFSS)": r_us,
    "Argentina (ENFR)": r_arg
}, index=common_vars)

im = ax_corr.imshow(corr_compare.values, cmap="RdBu_r", vmin=-1.0, vmax=1.0, aspect="auto")
ax_corr.set_xticks(range(2))
ax_corr.set_xticklabels(["EE.UU. (N=51)", "Argentina (N=24)"], fontsize=10, fontweight="bold")
ax_corr.set_yticks(range(len(common_vars)))
ax_corr.set_yticklabels(common_vars, fontsize=9.5, fontweight="bold")
ax_corr.set_title("Mapa de Calor de Correlaciones con Diabetes (r de Pearson)", fontsize=11, fontweight="bold")

for i in range(len(common_vars)):
    for j in range(2):
        val = corr_compare.values[i, j]
        color = "white" if abs(val) > 0.45 else "black"
        ax_corr.text(j, i, f"{val:+.2f}", ha="center", va="center",
                     fontsize=10, fontweight="bold", color=color)

cb_corr = fig.colorbar(im, ax=ax_corr, shrink=0.85, pad=0.04)
cb_corr.set_label("Coeficiente de Pearson (r)", fontsize=8.5)

# ------------------------------------------------------------------------------
# PANEL 4: DISPERSION POBREZA VS. DIABETES (Abajo Derecha)
# ------------------------------------------------------------------------------
ax_scat = fig.add_subplot(gs[1, 1])

# Datos EE.UU.
x_us = df_us["pobreza_ingresos_pct"]
y_us = df_us["tasa_diabetes_pct"]
slope_u, int_u, r_u, p_u, _ = stats.linregress(x_us, y_us)
ax_scat.scatter(x_us, y_us, color="#e53e3e", alpha=0.75, s=45, label=f"EE.UU. (r = +{r_u:.2f}; R² = {r_u**2:.2f})", edgecolor="none")
x_line_u = np.linspace(x_us.min(), x_us.max(), 50)
ax_scat.plot(x_line_u, int_u + slope_u * x_line_u, color="#9b2c2c", lw=2, linestyle="-")

# Datos Argentina
x_ar = df_arg["pobreza_personas_pct"]
y_ar = df_arg["tasa_diabetes_pct"]
slope_a, int_a, r_a, p_a, _ = stats.linregress(x_ar, y_ar)
ax_scat.scatter(x_ar, y_ar, color="#3182ce", alpha=0.85, s=60, marker="s", label=f"Argentina (r = {r_a:.2f}; p = {p_a:.2f})", edgecolor="black", linewidth=0.5)
x_line_a = np.linspace(x_ar.min(), x_ar.max(), 50)
ax_scat.plot(x_line_a, int_a + slope_a * x_line_a, color="#1a365d", lw=2, linestyle="--")

ax_scat.set_xlabel("Población en situación de pobreza / bajos ingresos (%)", fontsize=9.5, fontweight="bold")
ax_scat.set_ylabel("Prevalencia de diabetes (%)", fontsize=9.5, fontweight="bold")
ax_scat.set_title("Contraste: Pobreza vs. Prevalencia de Diabetes", fontsize=11, fontweight="bold")
ax_scat.legend(loc="upper left", fontsize=8.5, framealpha=0.95)
ax_scat.grid(True, linestyle=":", alpha=0.5)

# Anotacion en scatter
ax_scat.text(0.98, 0.05,
             "EE.UU.: Asociación lineal directa fuerte\nArgentina: Desacople por sesgo de screening",
             transform=ax_scat.transAxes, ha="right", va="bottom",
             fontsize=8, style="italic",
             bbox=dict(boxstyle="round,pad=0.3", fc="#edf2f7", ec="#cbd5e0"))

# Titulo principal general
fig.suptitle("Determinantes Geoespaciales de la Diabetes: Análisis Comparativo Estados Unidos vs. Argentina",
             fontsize=13.5, fontweight="bold", y=0.98)

# Guardar figura
out_fig1 = FIG / "comparativa_argentina_usa.png"
out_fig2 = PROP_DIR / "figura_comparativa_argentina_usa.png"
fig.savefig(out_fig1, bbox_inches="tight", dpi=220)
fig.savefig(out_fig2, bbox_inches="tight", dpi=220)
plt.close(fig)

print(f">>> Figura generada con éxito en:\n    - {out_fig1}\n    - {out_fig2}")
