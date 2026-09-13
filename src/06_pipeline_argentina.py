# -*- coding: utf-8 -*-
"""
06 - Pipeline de analisis descriptivo, atlas geoespacial y brecha de tratamiento (Argentina).

Fuente: ENFR 2018 + INDEC (Censo 2010/2022, EPH 2018) para las 24 jurisdicciones.
Genera mapas coropléticos de alta resolución, figuras analíticas y tablas para publicación.

Entradas: data/processed/enfr2018_provincias.csv, geo/argentina_provincias.geojson
Salidas:  figures/argentina_*.png, tables/argentina_*.csv
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
import statsmodels.api as sm
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import LeaveOneOut, KFold, cross_val_predict
from sklearn.metrics import r2_score, mean_absolute_error

# Rutas del proyecto
ROOT = Path(__file__).resolve().parent.parent
DATA_CSV = ROOT / "data" / "processed" / "enfr2018_provincias.csv"
GEO_JSON = ROOT / "geo" / "argentina_provincias.geojson"
FIG_DIR = ROOT / "figures"
TAB_DIR = ROOT / "tables"
FIG_DIR.mkdir(exist_ok=True)
TAB_DIR.mkdir(exist_ok=True)

# Configuracion estetica para publicacion cientifica
plt.rcParams.update({
    "figure.dpi": 200,
    "font.size": 9.5,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "axes.labelsize": 10,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "font.family": "sans-serif",
    "figure.autolayout": False,
})

# ==============================================================================
# 1. CARGA Y PREPARACION DE DATOS
# ==============================================================================
print(">>> [1/5] Cargando datos y geometrias...")
df = pd.read_csv(DATA_CSV)
gdf = gpd.read_file(GEO_JSON)

# Homogeneizar nombre de CABA para el cruce
gdf["provincia"] = gdf["shapeName"].replace({
    "Ciudad Autónoma de Buenos Aires": "CABA",
    "Ciudad Autnoma de Buenos Aires": "CABA"
})
merged = gdf.merge(df, on="provincia", how="inner")
if len(merged) != 24:
    raise ValueError(f"Se esperaba cruzar 24 provincias, se cruzaron {len(merged)}")
print(f"    Cruce exitoso: {len(merged)} jurisdicciones.")

# Etiquetas legibles para figuras y tablas
LABELS = {
    "tasa_diabetes_pct": "Prevalencia de diabetes (%)",
    "tratamiento_diabetes_pct": "Población con diabetes bajo tratamiento (%)",
    "medicion_glucemia_pct": "Screening de glucemia alguna vez (%)",
    "obesidad_pct": "Obesidad autorreportada IMC≥30 (%)",
    "inactividad_fisica_pct": "Inactividad física / sedentarismo (%)",
    "presion_elevada_pct": "Presión arterial elevada (%)",
    "colesterol_elevado_pct": "Colesterol elevado (%)",
    "tabaquismo_pct": "Tabaquismo actual (%)",
    "consumo_frutas_verduras_pct": "Consumo 5+ porc. frutas/verduras (%)",
    "nbi_2010_pct": "Hogares con NBI (%)",
    "pobreza_personas_pct": "Pobreza monetaria EPH (%)",
    "sin_cobertura_salud_pct": "Población sin cobertura médica privada/OS (%)",
    "densidad_hab_km2": "Densidad poblacional (hab/km²)",
    "log_densidad": "Log10 densidad poblacional",
    "cv_diabetes_pct": "Coef. de variación estimación (%)",
}

# Paleta regional consistente
REGION_COLORS = {
    "Pampeana y GBA": "#2b6cb0",   # Azul
    "Cuyo": "#d69e2e",             # Ocre / Mostaza
    "Noroeste": "#dd6b20",         # Naranja terroso
    "Noreste": "#38a169",          # Verde
    "Patagonia": "#805ad5"         # Violeta
}

# ==============================================================================
# 2. GENERACION DE TABLAS DESCRIPTIVAS
# ==============================================================================
print(">>> [2/5] Generando tablas estadísticas...")

# Tabla 1: Ranking provincial completo
cols_ranking = [
    "provincia", "region", "tasa_diabetes_pct", "cv_diabetes_pct",
    "tratamiento_diabetes_pct", "medicion_glucemia_pct", "obesidad_pct",
    "presion_elevada_pct", "inactividad_fisica_pct", "sin_cobertura_salud_pct",
    "pobreza_personas_pct", "nbi_2010_pct"
]
t1 = df[cols_ranking].sort_values("tratamiento_diabetes_pct", ascending=False).copy()
t1.rename(columns={
    "provincia": "Jurisdicción",
    "region": "Región",
    "tasa_diabetes_pct": "Diabetes (%)",
    "cv_diabetes_pct": "CV Diabetes (%)",
    "tratamiento_diabetes_pct": "Tratamiento (%)",
    "medicion_glucemia_pct": "Screening Glucemia (%)",
    "obesidad_pct": "Obesidad (%)",
    "presion_elevada_pct": "Presión Elevada (%)",
    "inactividad_fisica_pct": "Sedentarismo (%)",
    "sin_cobertura_salud_pct": "Sin Cobertura Salud (%)",
    "pobreza_personas_pct": "Pobreza EPH (%)",
    "nbi_2010_pct": "NBI (%)"
}).to_csv(TAB_DIR / "argentina_tabla1_ranking_provincias.csv", index=False, encoding="utf-8-sig")

# Tabla 2: Resumen por región
vars_resumen = [
    "tasa_diabetes_pct", "tratamiento_diabetes_pct", "medicion_glucemia_pct",
    "obesidad_pct", "presion_elevada_pct", "inactividad_fisica_pct",
    "sin_cobertura_salud_pct", "pobreza_personas_pct", "nbi_2010_pct"
]
reg_mean = df.groupby("region")[vars_resumen].mean().round(2)
reg_count = df.groupby("region")["provincia"].count()
reg_summary = reg_mean.copy()
reg_summary.insert(0, "N_jurisdicciones", reg_count)
reg_summary.rename(columns={
    "tasa_diabetes_pct": "Diabetes media (%)",
    "tratamiento_diabetes_pct": "Tratamiento medio (%)",
    "medicion_glucemia_pct": "Screening medio (%)",
    "obesidad_pct": "Obesidad media (%)",
    "presion_elevada_pct": "Presión elevada media (%)",
    "inactividad_fisica_pct": "Sedentarismo medio (%)",
    "sin_cobertura_salud_pct": "Sin cobertura media (%)",
    "pobreza_personas_pct": "Pobreza media (%)",
    "nbi_2010_pct": "NBI medio (%)"
}).to_csv(TAB_DIR / "argentina_tabla2_resumen_regional.csv", encoding="utf-8-sig")

# Tabla 3: Matriz de correlaciones de Pearson
corr_vars = [
    "tasa_diabetes_pct", "tratamiento_diabetes_pct", "medicion_glucemia_pct",
    "obesidad_pct", "presion_elevada_pct", "inactividad_fisica_pct",
    "colesterol_elevado_pct", "tabaquismo_pct", "sin_cobertura_salud_pct",
    "pobreza_personas_pct", "nbi_2010_pct", "log_densidad"
]
corr_matrix = df[corr_vars].corr().round(3)
corr_renamed = corr_matrix.rename(index=LABELS, columns=LABELS)
corr_renamed.to_csv(TAB_DIR / "argentina_tabla3_correlaciones.csv", encoding="utf-8-sig")

# Tabla 4: Resumen metodologico del diagnostico predictivo (por que no replica EE.UU.)
# Evaluamos formalmente los modelos para documentar la brecha de potencia estadistica
X_full = df[["obesidad_pct", "inactividad_fisica_pct", "tabaquismo_pct", "presion_elevada_pct", "nbi_2010_pct", "log_densidad"]]
X_red = df[["obesidad_pct", "presion_elevada_pct", "nbi_2010_pct"]]
X_dens = df[["log_densidad"]]
y = df["tasa_diabetes_pct"].values

loo = LeaveOneOut()
def eval_ols_loo(X_data, y_data):
    X_const = sm.add_constant(X_data)
    m = sm.OLS(y_data, X_const).fit()
    y_preds = []
    for train_idx, test_idx in loo.split(X_data):
        X_tr, y_tr = X_data.iloc[train_idx], y_data[train_idx]
        X_te = X_data.iloc[test_idx]
        m_loo = sm.OLS(y_tr, sm.add_constant(X_tr)).fit()
        pred = m_loo.predict(sm.add_constant(X_te, has_constant="add"))
        y_preds.append(pred.values[0])
    r2_loo = r2_score(y_data, y_preds)
    mae_loo = mean_absolute_error(y_data, y_preds)
    return m.rsquared, m.rsquared_adj, m.f_pvalue, r2_loo, mae_loo

m1_r2, m1_adj, m1_p, m1_loor2, m1_loomae = eval_ols_loo(X_full, y)
m2_r2, m2_adj, m2_p, m2_loor2, m2_loomae = eval_ols_loo(X_red, y)
m3_r2, m3_adj, m3_p, m3_loor2, m3_loomae = eval_ols_loo(X_dens, y)

# Random Forest con 5-fold CV
rf = RandomForestRegressor(n_estimators=300, max_depth=3, random_state=42)
kf = KFold(n_splits=5, shuffle=True, random_state=42)
y_rf_cv = cross_val_predict(rf, X_full, y, cv=kf)
rf_r2_cv = r2_score(y, y_rf_cv)
rf_mae_cv = mean_absolute_error(y, y_rf_cv)

diag_df = pd.DataFrame([
    {
        "Modelo": "OLS Completo (6 variables: obesidad, sedentarismo, tabaco, presión, NBI, densidad)",
        "N": 24, "R2_Muestra": round(m1_r2, 3), "R2_Ajustado": round(m1_adj, 3),
        "p_valor_F": f"{m1_p:.3f}", "R2_LOOCV": round(m1_loor2, 3), "MAE_LOOCV": round(m1_loomae, 2),
        "Diagnóstico": "Sobreajuste severo: p=0.16 (no significativo), R2_LOOCV negativo"
    },
    {
        "Modelo": "OLS Reducido (3 variables: obesidad, presión, NBI)",
        "N": 24, "R2_Muestra": round(m2_r2, 3), "R2_Ajustado": round(m2_adj, 3),
        "p_valor_F": f"{m2_p:.3f}", "R2_LOOCV": round(m2_loor2, 3), "MAE_LOOCV": round(m2_loomae, 2),
        "Diagnóstico": "Ajusta en muestra (p=0.037) pero capacidad predictiva nula fuera de muestra (R2≈0.007)"
    },
    {
        "Modelo": "OLS Univariado (1 variable: log_densidad)",
        "N": 24, "R2_Muestra": round(m3_r2, 3), "R2_Ajustado": round(m3_adj, 3),
        "p_valor_F": f"{m3_p:.3f}", "R2_LOOCV": round(m3_loor2, 3), "MAE_LOOCV": round(m3_loomae, 2),
        "Diagnóstico": "Único modelo con LOOCV positivo modesto (0.069), pero dependiente de CABA (outlier)"
    },
    {
        "Modelo": "Random Forest (5-fold CV, 6 variables)",
        "N": 24, "R2_Muestra": "—", "R2_Ajustado": "—",
        "p_valor_F": "—", "R2_LOOCV": round(rf_r2_cv, 3), "MAE_LOOCV": round(rf_mae_cv, 2),
        "Diagnóstico": "R2 CV negativo; algoritmos no lineales requieren mayor N que las 24 unidades provinciales"
    }
])
diag_df.to_csv(TAB_DIR / "argentina_tabla4_diagnostico_modelos.csv", index=False, encoding="utf-8-sig")
print("    Tablas guardadas en tables/.")

# ==============================================================================
# 3. GENERACION DE FIGURAS
# ==============================================================================
print(">>> [3/5] Generando figuras cartograficas y analiticas...")

def plot_caba_inset(ax, gdf_data, col, cmap, vmin, vmax, bbox=(0.70, 0.50, 0.28, 0.28)):
    """Inserta un recuadro zoom para CABA y el conurbano bonaerense."""
    ax_ins = inset_axes(ax, width="100%", height="100%",
                        bbox_to_anchor=bbox, bbox_transform=ax.transAxes, borderpad=0)
    gdf_data.plot(column=col, ax=ax_ins, cmap=cmap, vmin=vmin, vmax=vmax,
                  edgecolor="#4a5568", linewidth=0.6)
    # Bounding box alrededor del AMBA
    ax_ins.set_xlim(-58.85, -58.20)
    ax_ins.set_ylim(-34.85, -34.35)
    ax_ins.set_xticks([])
    ax_ins.set_yticks([])
    for spine in ax_ins.spines.values():
        spine.set_edgecolor("#2d3748")
        spine.set_linewidth(1.2)
    val_caba = gdf_data.loc[gdf_data["provincia"] == "CABA", col].values[0]
    ax_ins.set_title(f"CABA: {val_caba:.1f}%", fontsize=7.5, fontweight="bold", pad=2, color="#1a202c")
    return ax_ins

# ------------------------------------------------------------------------------
# FIGURA 1: Atlas Geoespacial — Prevalencia de Diabetes vs. Brecha de Tratamiento
# ------------------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 8))

# Panel (a): Prevalencia de Diabetes
vmin1, vmax1 = 8.0, 18.0
merged.plot(column="tasa_diabetes_pct", ax=ax1, cmap="YlOrRd", vmin=vmin1, vmax=vmax1,
            edgecolor="#4a5568", linewidth=0.7)
ax1.set_title("(a) Prevalencia de diabetes (%) por provincia\n(ENFR 2018; autorreporte + screening)", fontsize=11, fontweight="bold")
ax1.set_axis_off()
plot_caba_inset(ax1, merged, "tasa_diabetes_pct", "YlOrRd", vmin1, vmax1)

# Barra de color para mapa 1
sm1 = plt.cm.ScalarMappable(cmap="YlOrRd", norm=plt.Normalize(vmin=vmin1, vmax=vmax1))
sm1._A = []
cbar1 = fig.colorbar(sm1, ax=ax1, fraction=0.035, pad=0.02, shrink=0.75)
cbar1.set_label("Prevalencia (%)", fontsize=9)

# Anotaciones extremas en mapa 1
ax1.annotate("San Luis: 17,3%\n(Máx)", xy=(-66.3, -33.3), xytext=(-71.5, -31.5),
             arrowprops=dict(facecolor="black", arrowstyle="->", lw=0.8),
             fontsize=8, fontweight="bold", bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#e53e3e", alpha=0.9))
ax1.annotate("CABA: 8,8%\n(Mín)", xy=(-58.4, -34.6), xytext=(-53.5, -34.0),
             arrowprops=dict(facecolor="black", arrowstyle="->", lw=0.8),
             fontsize=8, fontweight="bold", bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#3182ce", alpha=0.9))

# Panel (b): Brecha de Tratamiento
vmin2, vmax2 = 30.0, 72.0
merged.plot(column="tratamiento_diabetes_pct", ax=ax2, cmap="Blues", vmin=vmin2, vmax=vmax2,
            edgecolor="#4a5568", linewidth=0.7)
ax2.set_title("(b) Población con diabetes bajo tratamiento (%)\n(ENFR 2018; tratamiento farmacológico activo)", fontsize=11, fontweight="bold")
ax2.set_axis_off()
plot_caba_inset(ax2, merged, "tratamiento_diabetes_pct", "Blues", vmin2, vmax2)

# Barra de color para mapa 2
sm2 = plt.cm.ScalarMappable(cmap="Blues", norm=plt.Normalize(vmin=vmin2, vmax=vmax2))
sm2._A = []
cbar2 = fig.colorbar(sm2, ax=ax2, fraction=0.035, pad=0.02, shrink=0.75)
cbar2.set_label("Bajo tratamiento (%)", fontsize=9)

# Anotaciones extremas en mapa 2
ax2.annotate("La Pampa: 32,7%\n(Mínimo nacional)", xy=(-64.3, -36.6), xytext=(-72.5, -37.5),
             arrowprops=dict(facecolor="black", arrowstyle="->", lw=0.8),
             fontsize=8, fontweight="bold", bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#e53e3e", alpha=0.9))
ax2.annotate("Santa Cruz / TDF: 70,0%\n(Máximo nacional)", xy=(-69.2, -49.3), xytext=(-60.5, -48.5),
             arrowprops=dict(facecolor="black", arrowstyle="->", lw=0.8),
             fontsize=8, fontweight="bold", bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#2b6cb0", alpha=0.9))

fig.suptitle("Atlas Geoespacial de la Diabetes en Argentina: Prevalencia y Brecha de Tratamiento",
             fontsize=13, fontweight="bold", y=0.96)
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(FIG_DIR / "argentina_figura1_prevalencia_tratamiento.png", bbox_inches="tight")
plt.close(fig)

# ------------------------------------------------------------------------------
# FIGURA 2: Disparidad de Tratamiento y Desconexión con Factores Socioeconómicos
# ------------------------------------------------------------------------------
fig, (ax_bar, ax_sc) = plt.subplots(1, 2, figsize=(14, 7.5), gridspec_kw={"width_ratios": [1.1, 1.0]})

# (a) Ranking horizontal por provincia
df_sorted = df.sort_values("tratamiento_diabetes_pct", ascending=True).copy()
bars = ax_bar.barh(df_sorted["provincia"], df_sorted["tratamiento_diabetes_pct"],
                   color=[REGION_COLORS[r] for r in df_sorted["region"]],
                   edgecolor="white", height=0.75)

promedio_trat = df["tratamiento_diabetes_pct"].mean()
ax_bar.axvline(promedio_trat, color="#e53e3e", linestyle="--", linewidth=1.2,
               label=f"Promedio nacional: {promedio_trat:.1f}%")
ax_bar.set_xlabel("Población con diabetes bajo tratamiento (%)", fontweight="bold")
ax_bar.set_title("(a) Ranking provincial de cobertura de tratamiento\n(Brecha: 32,7% en La Pampa a 70,0% en Santa Cruz y TDF)", fontsize=10.5, fontweight="bold")
ax_bar.set_xlim(25, 76)
ax_bar.grid(axis="x", linestyle=":", alpha=0.6)

# Etiquetas de valor en las barras
for bar in bars:
    w = bar.get_width()
    ax_bar.text(w + 0.6, bar.get_y() + bar.get_height()/2, f"{w:.1f}%",
                va="center", fontsize=7.5, color="#2d3748")

# Leyenda de regiones en ax_bar
patches = [mpatches.Patch(color=c, label=r) for r, c in REGION_COLORS.items()]
patches.append(plt.Line2D([0], [0], color="#e53e3e", linestyle="--", label=f"Promedio: {promedio_trat:.1f}%"))
ax_bar.legend(handles=patches, loc="lower right", fontsize=8, framealpha=0.95)

# (b) Scatter: Tratamiento vs Sin Cobertura de Salud y Pobreza
corr_cob = np.corrcoef(df["sin_cobertura_salud_pct"], df["tratamiento_diabetes_pct"])[0, 1]

for reg, grp in df.groupby("region"):
    ax_sc.scatter(grp["sin_cobertura_salud_pct"], grp["tratamiento_diabetes_pct"],
                  s=70, color=REGION_COLORS[reg], edgecolors="black", linewidth=0.6,
                  label=reg, alpha=0.9)

# Anotar casos notables en el scatter
for _, row in df.iterrows():
    if row["provincia"] in ["La Pampa", "Santa Cruz", "Tierra del Fuego", "Chaco", "Santiago del Estero", "CABA"]:
        ax_sc.annotate(row["provincia"], (row["sin_cobertura_salud_pct"], row["tratamiento_diabetes_pct"]),
                       xytext=(4, 3), textcoords="offset points", fontsize=7.8, fontweight="bold")

# Recta de tendencia
m_fit = np.polyfit(df["sin_cobertura_salud_pct"], df["tratamiento_diabetes_pct"], 1)
x_line = np.linspace(df["sin_cobertura_salud_pct"].min(), df["sin_cobertura_salud_pct"].max(), 50)
ax_sc.plot(x_line, np.polyval(m_fit, x_line), color="#718096", linestyle=":", linewidth=1.5,
           label=f"Tendencia lineal (r = {corr_cob:+.2f}; p = 0.58)")

ax_sc.set_xlabel("Población sin cobertura de salud privada/obra social (%) [Censo 2022]", fontweight="bold")
ax_sc.set_ylabel("Población con diabetes bajo tratamiento (%) [ENFR 2018]", fontweight="bold")
ax_sc.set_title("(b) La paradoja de tratamiento: ausencia de relación\ncon la cobertura formal de salud o nivel socioeconómico", fontsize=10.5, fontweight="bold")
ax_sc.grid(True, linestyle=":", alpha=0.6)
ax_sc.legend(loc="upper right", fontsize=8, framealpha=0.95)

fig.suptitle("Disparidad Territorial de la Brecha de Tratamiento de Diabetes en Argentina",
             fontsize=12.5, fontweight="bold", y=0.98)
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(FIG_DIR / "argentina_figura2_brecha_tratamiento.png", bbox_inches="tight")
plt.close(fig)

# ------------------------------------------------------------------------------
# FIGURA 3: Atlas de Factores de Riesgo Cardiometabolicos (Panel 2x2)
# ------------------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(12, 12))
panel_configs = [
    (axes[0, 0], "obesidad_pct", "(a) Obesidad autorreportada (IMC≥30, %)", "Reds", 15.0, 36.0, "%"),
    (axes[0, 1], "presion_elevada_pct", "(b) Presión arterial elevada (%)", "Oranges", 25.0, 54.0, "%"),
    (axes[1, 0], "inactividad_fisica_pct", "(c) Inactividad física / sedentarismo (%)", "YlOrBr", 20.0, 70.0, "%"),
    (axes[1, 1], "medicion_glucemia_pct", "(d) Screening de glucemia alguna vez (%)", "Blues", 58.0, 95.0, "%"),
]

for ax, col, title, cmap, vmin, vmax, unit in panel_configs:
    merged.plot(column=col, ax=ax, cmap=cmap, vmin=vmin, vmax=vmax,
                edgecolor="#4a5568", linewidth=0.6)
    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=8)
    ax.set_axis_off()
    plot_caba_inset(ax, merged, col, cmap, vmin, vmax, bbox=(0.72, 0.52, 0.26, 0.26))
    
    sm_p = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm_p._A = []
    cb = fig.colorbar(sm_p, ax=ax, fraction=0.035, pad=0.02, shrink=0.7)
    cb.set_label(unit, fontsize=8.5)

fig.suptitle("Atlas de Factores de Riesgo Cardiometabólicos y Screening — Provincias de Argentina (ENFR 2018)",
             fontsize=13, fontweight="bold", y=0.98)
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(FIG_DIR / "argentina_figura3_factores_riesgo.png", bbox_inches="tight")
plt.close(fig)

# ------------------------------------------------------------------------------
# FIGURA 4: Matriz de Correlación Bivariada (Heatmap)
# ------------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9.5, 8.5))
corr_vals = corr_matrix.values
im = ax.imshow(corr_vals, cmap="RdBu_r", vmin=-1, vmax=1)

ax.set_xticks(range(len(corr_vars)))
ax.set_yticks(range(len(corr_vars)))
short_labels = [
    "Diabetes", "Tratamiento", "Screening Gluc.", "Obesidad", "Presión Elev.",
    "Sedentarismo", "Colesterol", "Tabaquismo", "Sin Cob. Salud", "Pobreza EPH",
    "NBI Hogares", "Log Densidad"
]
ax.set_xticklabels(short_labels, rotation=45, ha="right", fontsize=8.5, fontweight="bold")
ax.set_yticklabels(short_labels, fontsize=8.5, fontweight="bold")

for i in range(len(corr_vars)):
    for j in range(len(corr_vars)):
        val = corr_vals[i, j]
        color = "white" if abs(val) > 0.45 else "black"
        ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=8, color=color, fontweight="bold")

cbar = fig.colorbar(im, ax=ax, shrink=0.8, pad=0.03)
cbar.set_label("Coeficiente de correlación de Pearson (r)", fontsize=9.5)
ax.set_title("Matriz de Correlación Bivariada entre Indicadores de Salud y Territorio\n(24 jurisdicciones de Argentina; ENFR 2018 + INDEC)",
             fontsize=11.5, fontweight="bold", pad=12)

fig.tight_layout()
fig.savefig(FIG_DIR / "argentina_figura4_correlaciones.png", bbox_inches="tight")
plt.close(fig)

# ------------------------------------------------------------------------------
# FIGURA 5: Diagnostico Metodologico — Efecto de la Escala y Casos Atípicos (Densidad vs CABA)
# ------------------------------------------------------------------------------
fig, (ax_d1, ax_d2) = plt.subplots(1, 2, figsize=(12, 5))

# (a) Con CABA
m_full = sm.OLS(df["tasa_diabetes_pct"], sm.add_constant(df["log_densidad"])).fit()
r2_with = m_full.rsquared
p_with = m_full.pvalues["log_densidad"]

ax_d1.scatter(df["log_densidad"], df["tasa_diabetes_pct"],
              c=[REGION_COLORS[r] for r in df["region"]], s=65, edgecolors="black", linewidth=0.6)
x_plot = np.linspace(df["log_densidad"].min(), df["log_densidad"].max(), 50)
ax_d1.plot(x_plot, m_full.params["const"] + m_full.params["log_densidad"] * x_plot,
           color="#2b6cb0", linestyle="-", lw=1.5, label=f"OLS: R² = {r2_with:.2f} (p = {p_with:.3f})")

for _, r in df.iterrows():
    if r["provincia"] in ["CABA", "San Luis", "San Juan", "Jujuy", "Formosa"]:
        ax_d1.annotate(r["provincia"], (r["log_densidad"], r["tasa_diabetes_pct"]),
                       xytext=(3, 3), textcoords="offset points", fontsize=8, fontweight="bold")

ax_d1.set_xlabel("Log10 Densidad Poblacional (hab/km²)", fontweight="bold")
ax_d1.set_ylabel("Prevalencia de diabetes (%)", fontweight="bold")
ax_d1.set_title("(a) Todas las jurisdicciones (N=24)\n(Asociación inversa aparente con la densidad)", fontsize=10, fontweight="bold")
ax_d1.grid(True, linestyle=":", alpha=0.6)
ax_d1.legend(loc="upper right", fontsize=8.5)

# (b) Sin CABA
df_nocaba = df[df["provincia"] != "CABA"]
m_nocaba = sm.OLS(df_nocaba["tasa_diabetes_pct"], sm.add_constant(df_nocaba["log_densidad"])).fit()
r2_without = m_nocaba.rsquared
p_without = m_nocaba.pvalues["log_densidad"]

ax_d2.scatter(df_nocaba["log_densidad"], df_nocaba["tasa_diabetes_pct"],
              c=[REGION_COLORS[r] for r in df_nocaba["region"]], s=65, edgecolors="black", linewidth=0.6)
x_plot2 = np.linspace(df_nocaba["log_densidad"].min(), df_nocaba["log_densidad"].max(), 50)
ax_d2.plot(x_plot2, m_nocaba.params["const"] + m_nocaba.params["log_densidad"] * x_plot2,
           color="#e53e3e", linestyle="--", lw=1.5, label=f"OLS sin CABA: R² = {r2_without:.2f} (p = {p_without:.3f})")

for _, r in df_nocaba.iterrows():
    if r["provincia"] in ["San Luis", "San Juan", "Jujuy", "Formosa", "Buenos Aires"]:
        ax_d2.annotate(r["provincia"], (r["log_densidad"], r["tasa_diabetes_pct"]),
                       xytext=(3, 3), textcoords="offset points", fontsize=8, fontweight="bold")

ax_d2.set_xlabel("Log10 Densidad Poblacional (hab/km²)", fontweight="bold")
ax_d2.set_ylabel("Prevalencia de diabetes (%)", fontweight="bold")
ax_d2.set_title("(b) Excluyendo CABA (N=23)\n(La asociación se diluye: R² cae de 0,19 a 0,03; no signif.)", fontsize=10, fontweight="bold")
ax_d2.grid(True, linestyle=":", alpha=0.6)
ax_d2.legend(loc="upper right", fontsize=8.5)

fig.suptitle("Diagnóstico de Robustez: Dependencia de Casos Extremos en Muestras Reducidas (N=24)",
             fontsize=12, fontweight="bold", y=0.98)
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(FIG_DIR / "argentina_figura5_densidad_diagnostico.png", bbox_inches="tight")
plt.close(fig)

print(">>> [4/5] Figuras generadas con éxito:")
for f in FIG_DIR.glob("argentina_*.png"):
    print(f"    - {f.name}")

print(">>> [5/5] Pipeline de Argentina completado con éxito.")
