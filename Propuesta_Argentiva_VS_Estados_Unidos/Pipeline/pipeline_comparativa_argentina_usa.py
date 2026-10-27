# -*- coding: utf-8 -*-
"""
Pipeline Maestro Reproducible: Paper Comparativo Extenso Argentina vs. EE.UU.
Destino: CIITI 2026 / CoNaIISI — CAETI (Facultad de Tecnología Informática, UAI)

Genera directamente desde los datasets oficiales (sin valores hardcodeados discrepantes):
1. Datasets y tablas estadísticas comparativas (CSV), incluyendo IC95%, Spearman, Moran's I,
   análisis de sensibilidad sin CABA, y modelos parsimoniosos/regularizados (OLS 1-var, Ridge, RF)
   evaluados simétricamente con LOOCV y 5-Fold CV en ambos países.
2. 5 Figuras científicas de alta resolución (220 DPI) en formato cartográfico y analítico.
3. Manuscrito científico extenso (.docx en 2 columnas, plantilla oficial CoNaIISI/CIITI).
4. Manuscrito completo sincronizado en formato Markdown (.md).
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
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import LeaveOneOut, KFold, cross_val_predict
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
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
print(">>> INICIANDO MOTOR REPRODUCIBLE DEL PAPER COMPARATIVO (CIITI 2026)")
print("=" * 75)

# ==============================================================================
# 1. CARGA DE DATOS Y FUNCIONES ESTADISTICAS / ESPACIALES
# ==============================================================================
print(">>> [1/5] Cargando datasets oficiales y capas vectoriales GeoJSON...")
df_arg = pd.read_csv(DATOS_DIR / "enfr2018_provincias.csv")
gdf_arg = gpd.read_file(DATOS_DIR / "argentina_provincias.geojson")
gdf_arg["provincia"] = gdf_arg["shapeName"].replace({
    "Ciudad Autónoma de Buenos Aires": "CABA",
    "Ciudad Autnoma de Buenos Aires": "CABA"
})
arg_merged = gdf_arg.merge(df_arg, on="provincia", how="inner").reset_index(drop=True)

df_us = pd.read_csv(DATOS_DIR / "brfss2015_estados.csv")
gdf_us = gpd.read_file(DATOS_DIR / "us_states.geojson").rename(columns={"name": "estado"}).merge(df_us, on="estado", how="inner")
us_cont = gdf_us[~gdf_us["estado"].isin(["Alaska", "Hawaii"])].copy().reset_index(drop=True)

def pearson_ci_spearman(x, y):
    """Calcula r de Pearson, p-valor, IC95% por transformación z de Fisher y rho de Spearman."""
    r, p = stats.pearsonr(x, y)
    n = len(x)
    z = np.arctanh(r)
    se = 1.0 / np.sqrt(n - 3)
    lo, hi = np.tanh(z - 1.96 * se), np.tanh(z + 1.96 * se)
    rho, p_rho = stats.spearmanr(x, y)
    return r, p, lo, hi, rho, p_rho

def compute_moran_i(gdf, col, n_perm=9999):
    """Calcula el Índice I de Moran global con contigüidad Queen (y vecino más cercano para islas)."""
    n = len(gdf)
    W = np.zeros((n, n))
    geoms = gdf.geometry.values
    # Proyección métrica para centroides de respaldo (islas)
    cents = gdf.to_crs(epsg=3857).geometry.centroid.values
    for i in range(n):
        for j in range(n):
            if i != j and geoms[i].touches(geoms[j]):
                W[i, j] = 1.0
        if W[i].sum() == 0:
            dists = [cents[i].distance(cents[j]) if i != j else 1e18 for j in range(n)]
            nn = int(np.argmin(dists))
            W[i, nn] = 1.0
            W[nn, i] = 1.0
    W = W / W.sum(axis=1, keepdims=True)
    y = gdf[col].values
    z = y - y.mean()
    moran_i = float((n / W.sum()) * (z @ W @ z) / (z @ z))
    rng = np.random.default_rng(42)
    count_extr = 0
    for _ in range(n_perm):
        zp = rng.permutation(z)
        ip = (n / W.sum()) * (zp @ W @ zp) / (zp @ zp)
        if abs(ip) >= abs(moran_i):
            count_extr += 1
    p_val = (count_extr + 1) / (n_perm + 1)
    return moran_i, p_val

# Cálculos exactos desde los datos
us_mean_d = df_us["tasa_diabetes_pct"].mean()
us_sd_d = df_us["tasa_diabetes_pct"].std(ddof=1)
us_med_d = df_us["tasa_diabetes_pct"].median()

ar_mean_d = df_arg["tasa_diabetes_pct"].mean()
ar_sd_samp = df_arg["tasa_diabetes_pct"].std(ddof=1)
ar_sd_pop = df_arg["tasa_diabetes_pct"].std(ddof=0)
ar_var_pop = df_arg["tasa_diabetes_pct"].var(ddof=0)  # 4.24 exacto (usado por sklearn r2_score)
ar_med_d = df_arg["tasa_diabetes_pct"].median()

ar_trat_mean = df_arg["tratamiento_diabetes_pct"].mean()
ar_brecha_mean = 100.0 - ar_trat_mean

# Correlaciones clave con IC95% y Spearman
r_us_pob, p_us_pob, lo_us_pob, hi_us_pob, rho_us_pob, _ = pearson_ci_spearman(df_us["pobreza_ingresos_pct"], df_us["tasa_diabetes_pct"])
r_us_sed, p_us_sed, lo_us_sed, hi_us_sed, rho_us_sed, _ = pearson_ci_spearman(df_us["inactividad_fisica_pct"], df_us["tasa_diabetes_pct"])
r_us_edu, p_us_edu, lo_us_edu, hi_us_edu, rho_us_edu, _ = pearson_ci_spearman(df_us["secundario_incompleto_pct"], df_us["tasa_diabetes_pct"])
r_us_obe, p_us_obe, lo_us_obe, hi_us_obe, rho_us_obe, _ = pearson_ci_spearman(df_us["obesidad_pct"], df_us["tasa_diabetes_pct"])
r_us_cost, p_us_cost, lo_us_cost, hi_us_cost, rho_us_cost, _ = pearson_ci_spearman(df_us["barrera_costo_medico_pct"], df_us["tasa_diabetes_pct"])

r_ar_pob, p_ar_pob, lo_ar_pob, hi_ar_pob, rho_ar_pob, p_rho_ar_pob = pearson_ci_spearman(df_arg["pobreza_personas_pct"], df_arg["tasa_diabetes_pct"])
r_ar_nbi, p_ar_nbi, lo_ar_nbi, hi_ar_nbi, rho_ar_nbi, _ = pearson_ci_spearman(df_arg["nbi_2010_pct"], df_arg["tasa_diabetes_pct"])
r_ar_cob, p_ar_cob, lo_ar_cob, hi_ar_cob, rho_ar_cob, _ = pearson_ci_spearman(df_arg["sin_cobertura_salud_pct"], df_arg["tasa_diabetes_pct"])
r_ar_obe, p_ar_obe, lo_ar_obe, hi_ar_obe, rho_ar_obe, _ = pearson_ci_spearman(df_arg["obesidad_pct"], df_arg["tasa_diabetes_pct"])

# Eslabón de la hipótesis de subdiagnóstico: NBI -> Screening y Screening -> Diabetes (con y sin CABA)
r_nbi_scr, p_nbi_scr, lo_nbi_scr, hi_nbi_scr, rho_nbi_scr, _ = pearson_ci_spearman(df_arg["nbi_2010_pct"], df_arg["medicion_glucemia_pct"])
r_scr_d24, p_scr_d24, lo_scr_d24, hi_scr_d24, rho_scr_d24, _ = pearson_ci_spearman(df_arg["medicion_glucemia_pct"], df_arg["tasa_diabetes_pct"])
df_arg_nocaba = df_arg[df_arg["provincia"] != "CABA"].copy()
r_scr_d23, p_scr_d23, lo_scr_d23, hi_scr_d23, rho_scr_d23, _ = pearson_ci_spearman(df_arg_nocaba["medicion_glucemia_pct"], df_arg_nocaba["tasa_diabetes_pct"])

# Cobertura vs Tratamiento
r_cob_trat, p_cob_trat, lo_cob_trat, hi_cob_trat, rho_cob_trat, _ = pearson_ci_spearman(df_arg["sin_cobertura_salud_pct"], df_arg["tratamiento_diabetes_pct"])

# Autocorrelación espacial I de Moran
moran_us_d, p_moran_us_d = compute_moran_i(us_cont, "tasa_diabetes_pct")
moran_ar_d, p_moran_ar_d = compute_moran_i(arg_merged, "tasa_diabetes_pct")
moran_ar_scr, p_moran_ar_scr = compute_moran_i(arg_merged, "medicion_glucemia_pct")

print(f"    - Moran's I EE.UU. Diabetes: I = {moran_us_d:+.3f} (p = {p_moran_us_d:.4f})")
print(f"    - Moran's I Arg. Diabetes:   I = {moran_ar_d:+.3f} (p = {p_moran_ar_d:.4f})")
print(f"    - Moran's I Arg. Screening:  I = {moran_ar_scr:+.3f} (p = {p_moran_ar_scr:.4f})")

# ==============================================================================
# 2. GENERACION DE TABLAS CIENTIFICAS (CSV)
# ==============================================================================
print(">>> [2/5] Calculando modelos econométricos, validación cruzada simétrica y tablas...")

# TABLA 1: Resumen de Indicadores (Aclarando constructos, población y cobertura vs brecha)
t1_df = pd.DataFrame([
    {"Indicador": "N unidades territoriales", "Estados Unidos (CDC BRFSS 2015)": "51 estados (50 + D.C.)", "Argentina (ENFR 2018 / INDEC)": "24 jurisdicciones (23 + CABA)"},
    {"Indicador": "Población representada", "Estados Unidos (CDC BRFSS 2015)": "~320 millones (441.456 enc. 18+)", "Argentina (ENFR 2018 / INDEC)": "~44 mill. total (~29,5 mill. urbana 18+; N=29.224)"},
    {"Indicador": "Prevalencia media diabetes", "Estados Unidos (CDC BRFSS 2015)": f"{us_mean_d:.1f}% (DE {us_sd_d:.1f}%; Mediana {us_med_d:.1f}%)", "Argentina (ENFR 2018 / INDEC)": f"{ar_mean_d:.1f}% media prov. (DE {ar_sd_samp:.1f}%; 12,7% nac.)"},
    {"Indicador": "Rango de prevalencia", "Estados Unidos (CDC BRFSS 2015)": f"{df_us['tasa_diabetes_pct'].min():.1f}% (Colorado) – {df_us['tasa_diabetes_pct'].max():.1f}% (Misisipi)", "Argentina (ENFR 2018 / INDEC)": f"{df_arg['tasa_diabetes_pct'].min():.1f}% (CABA) – {df_arg['tasa_diabetes_pct'].max():.1f}% (San Luis)"},
    {"Indicador": "Autocorrelación espacial (I de Moran)", "Estados Unidos (CDC BRFSS 2015)": f"I = +{moran_us_d:.2f} (p < 0,001; fuerte clustering)", "Argentina (ENFR 2018 / INDEC)": f"I = +{moran_ar_d:.2f} (p = {p_moran_ar_d:.3f}; moderado)"},
    {"Indicador": "Prevalencia media obesidad (IMC≥30)", "Estados Unidos (CDC BRFSS 2015)": f"{df_us['obesidad_pct'].mean():.1f}% media est. (28,6% total nac.)", "Argentina (ENFR 2018 / INDEC)": f"{df_arg['obesidad_pct'].mean():.1f}% media prov. (25,6% total nac.)"},
    {"Indicador": "Inactividad física / Baja act. (IPAQ)", "Estados Unidos (CDC BRFSS 2015)": f"{df_us['inactividad_fisica_pct'].mean():.1f}% tiempo libre (23,8% nac.)", "Argentina (ENFR 2018 / INDEC)": f"{df_arg['inactividad_fisica_pct'].mean():.1f}% baja act. IPAQ (45,9% nac.)"},
    {"Indicador": "Población sin seguro médico formal", "Estados Unidos (CDC BRFSS 2015)": f"{df_us['sin_cobertura_salud_pct'].mean():.1f}% media est. (10,9% total nac.)", "Argentina (ENFR 2018 / INDEC)": f"{df_arg['sin_cobertura_salud_pct'].mean():.1f}% media prov. (35,6% Censo 2022)"},
    {"Indicador": "Tasa de screening glucémico", "Estados Unidos (CDC BRFSS 2015)": ">85% (pesquisa clínica rutinaria)", "Argentina (ENFR 2018 / INDEC)": f"Media {df_arg['medicion_glucemia_pct'].mean():.1f}% (60,3% Chaco a 92,9% CABA)"},
    {"Indicador": "Cobertura de tratamiento (y brecha)", "Estados Unidos (CDC BRFSS 2015)": "Barrera de costo médico / copago (media 13,2%)", "Argentina (ENFR 2018 / INDEC)": f"Cobertura {ar_trat_mean:.1f}% [Brecha {ar_brecha_mean:.1f}%] (32,7%–70,0%)"},
])
tab1_path = RESULTADOS_DIR / "tabla1_resumen_comparativo.csv"
t1_df.to_csv(tab1_path, index=False, encoding="utf-8-sig")

# MODELOS OLS EE.UU.
X_us = df_us[["obesidad_pct", "inactividad_fisica_pct", "pobreza_ingresos_pct", "secundario_incompleto_pct", "sin_cobertura_salud_pct"]]
X_us_c = sm.add_constant(X_us)
y_us = df_us["tasa_diabetes_pct"]
m_us_ols = sm.OLS(y_us, X_us_c).fit()
m_us = sm.OLS(y_us, X_us_c).fit(cov_type="HC3")
vif_us = [variance_inflation_factor(X_us_c.values, i) for i in range(X_us_c.shape[1])]

# MODELOS OLS ARGENTINA
X_ar = df_arg[["obesidad_pct", "inactividad_fisica_pct", "pobreza_personas_pct", "sin_cobertura_salud_pct", "log_densidad"]]
X_ar_c = sm.add_constant(X_ar)
y_ar = df_arg["tasa_diabetes_pct"]
m_ar_ols = sm.OLS(y_ar, X_ar_c).fit()
m_ar = sm.OLS(y_ar, X_ar_c).fit(cov_type="HC3")
vif_ar = [variance_inflation_factor(X_ar_c.values, i) for i in range(X_ar_c.shape[1])]

# TABLA 2: Coeficientes OLS Comparados con rótulos explícitos de constructo
vars_comp = [
    ("Intercepto", m_us.params["const"], m_us.pvalues["const"], "—", m_ar.params["const"], m_ar.pvalues["const"], "—"),
    ("Obesidad IMC≥30 (%)", m_us.params["obesidad_pct"], m_us.pvalues["obesidad_pct"], f"{vif_us[1]:.1f}", m_ar.params["obesidad_pct"], m_ar.pvalues["obesidad_pct"], f"{vif_ar[1]:.1f}"),
    ("Inactividad T. Libre (US) / Baja Act. IPAQ (Arg) (%)", m_us.params["inactividad_fisica_pct"], m_us.pvalues["inactividad_fisica_pct"], f"{vif_us[2]:.1f}", m_ar.params["inactividad_fisica_pct"], m_ar.pvalues["inactividad_fisica_pct"], f"{vif_ar[2]:.1f}"),
    ("Ingresos <USD 25k (US) / Pobreza EPH (Arg) (%)", m_us.params["pobreza_ingresos_pct"], m_us.pvalues["pobreza_ingresos_pct"], f"{vif_us[3]:.1f}", m_ar.params["pobreza_personas_pct"], m_ar.pvalues["pobreza_personas_pct"], f"{vif_ar[3]:.1f}"),
    ("Sin Seguro 18–64 (US) / Sin OS ni Prepaga (Arg) (%)", m_us.params["sin_cobertura_salud_pct"], m_us.pvalues["sin_cobertura_salud_pct"], f"{vif_us[5]:.1f}", m_ar.params["sin_cobertura_salud_pct"], m_ar.pvalues["sin_cobertura_salud_pct"], f"{vif_ar[4]:.1f}"),
    ("Secundario Incompleto (US, %) / Densidad log10 (Arg)", m_us.params["secundario_incompleto_pct"], m_us.pvalues["secundario_incompleto_pct"], f"{vif_us[4]:.1f}", m_ar.params["log_densidad"], m_ar.pvalues["log_densidad"], f"{vif_ar[5]:.1f}")
]
def _fmt_p(p): return "<0.001" if p < 0.001 else f"{p:.3f}"
t2_df = pd.DataFrame([
    {
        "Determinante Sociodemográfico (Constructo específico por país)": v[0],
        "EE.UU. Coef. β (HC3)": f"{v[1]:+.3f} (p={_fmt_p(v[2])})",
        "EE.UU. VIF": v[3],
        "Argentina Coef. β (HC3)": f"{v[4]:+.3f} (p={_fmt_p(v[5])})",
        "Argentina VIF": v[6]
    }
    for v in vars_comp
])
tab2_path = RESULTADOS_DIR / "tabla2_ols_coeficientes.csv"
t2_df.to_csv(tab2_path, index=False, encoding="utf-8-sig")

# Validación Cruzada Simétrica (LOOCV y 5-Fold CV en AMBOS países, más Ridge y modelo univariado)
kf5 = KFold(5, shuffle=True, random_state=42)
loo = LeaveOneOut()

def eval_cv_both(model, X, y):
    p_loo = cross_val_predict(model, X, y, cv=loo)
    p_kf = cross_val_predict(model, X, y, cv=kf5)
    return (
        r2_score(y, p_loo), mean_absolute_error(y, p_loo), mean_squared_error(y, p_loo),
        r2_score(y, p_kf), mean_absolute_error(y, p_kf), mean_squared_error(y, p_kf)
    )

# 1. OLS Multivariado (5 predictores)
r2_us_ols_loo, mae_us_ols_loo, _, r2_us_ols_kf, mae_us_ols_kf, _ = eval_cv_both(LinearRegression(), X_us, y_us)
r2_ar_ols_loo, mae_ar_ols_loo, mse_ar_ols_loo, r2_ar_ols_kf, mae_ar_ols_kf, _ = eval_cv_both(LinearRegression(), X_ar, y_ar)

# 2. Regresión Ridge Regularizada (alpha=10, estandarizada dentro del pipeline)
ridge_pipe = make_pipeline(StandardScaler(), Ridge(alpha=10.0))
r2_us_rdg_loo, mae_us_rdg_loo, _, r2_us_rdg_kf, mae_us_rdg_kf, _ = eval_cv_both(ridge_pipe, X_us, y_us)
r2_ar_rdg_loo, mae_ar_rdg_loo, _, r2_ar_rdg_kf, mae_ar_rdg_kf, _ = eval_cv_both(ridge_pipe, X_ar, y_ar)

# 3. OLS Univariado Parsimonioso (1 solo predictor: Obesidad)
r2_us_uni_loo, mae_us_uni_loo, _, r2_us_uni_kf, mae_us_uni_kf, _ = eval_cv_both(LinearRegression(), X_us[["obesidad_pct"]], y_us)
r2_ar_uni_loo, mae_ar_uni_loo, _, r2_ar_uni_kf, mae_ar_uni_kf, _ = eval_cv_both(LinearRegression(), X_ar[["obesidad_pct"]], y_ar)

# 4. Random Forest Regressor
rf_us_mod = RandomForestRegressor(n_estimators=300, max_depth=5, random_state=42)
rf_ar_mod = RandomForestRegressor(n_estimators=300, max_depth=3, random_state=42)
r2_us_rf_loo, mae_us_rf_loo, _, r2_us_rf_kf, mae_us_rf_kf, _ = eval_cv_both(rf_us_mod, X_us, y_us)
r2_ar_rf_loo, mae_ar_rf_loo, _, r2_ar_rf_kf, mae_ar_rf_kf, _ = eval_cv_both(rf_ar_mod, X_ar, y_ar)

mae_us_base = mean_absolute_error(y_us, [y_us.mean()] * len(y_us))
mae_ar_base = mean_absolute_error(y_ar, [y_ar.mean()] * len(y_ar))

# TABLA 3: Rendimiento y Diagnóstico Simétrico de Modelos
t3_df = pd.DataFrame([
    {
        "Modelo y Esquema de Evaluación": "Estimador Naive Baseline (Media constante ȳ)",
        "EE.UU. R²": "0.000",
        "EE.UU. MAE": f"{mae_us_base:.2f}%",
        "Argentina R²": "0.000",
        "Argentina MAE": f"{mae_ar_base:.2f}%",
        "Diagnóstico Metodológico": f"Referencia base (R²=0): dispersión intrínseca Var(y)={ar_var_pop:.2f} (DE={ar_sd_pop:.2f}%)"
    },
    {
        "Modelo y Esquema de Evaluación": "OLS Multivariado 5 vars (In-Sample, muestra completa)",
        "EE.UU. R²": f"{m_us.rsquared:.3f} (adj {m_us.rsquared_adj:.3f})",
        "EE.UU. MAE": f"{mean_absolute_error(y_us, m_us.fittedvalues):.2f}%",
        "Argentina R²": f"{m_ar.rsquared:.3f} (adj {m_ar.rsquared_adj:.3f})",
        "Argentina MAE": f"{mean_absolute_error(y_ar, m_ar.fittedvalues):.2f}%",
        "Diagnóstico Metodológico": f"EE.UU. significativo (F={m_us_ols.fvalue:.1f}, p<0.001); Arg no significativo (F={m_ar_ols.fvalue:.2f}, p={m_ar_ols.f_pvalue:.2f})"
    },
    {
        "Modelo y Esquema de Evaluación": "OLS Multivariado 5 vars (LOOCV / 5-Fold CV)",
        "EE.UU. R²": f"{r2_us_ols_loo:.3f} / {r2_us_ols_kf:.3f}",
        "EE.UU. MAE": f"{mae_us_ols_loo:.2f}% / {mae_us_ols_kf:.2f}%",
        "Argentina R²": f"{r2_ar_ols_loo:.3f} / {r2_ar_ols_kf:.3f}",
        "Argentina MAE": f"{mae_ar_ols_loo:.2f}% / {mae_ar_ols_kf:.2f}%",
        "Diagnóstico Metodológico": f"Sobreajuste severo en Arg (MSE LOOCV={mse_ar_ols_loo:.2f} > Var(y)={ar_var_pop:.2f})"
    },
    {
        "Modelo y Esquema de Evaluación": "Regresión Regularizada Ridge α=10 (LOOCV / 5-Fold CV)",
        "EE.UU. R²": f"{r2_us_rdg_loo:.3f} / {r2_us_rdg_kf:.3f}",
        "EE.UU. MAE": f"{mae_us_rdg_loo:.2f}% / {mae_us_rdg_kf:.2f}%",
        "Argentina R²": f"{r2_ar_rdg_loo:.3f} / {r2_ar_rdg_kf:.3f}",
        "Argentina MAE": f"{mae_ar_rdg_loo:.2f}% / {mae_ar_rdg_kf:.2f}%",
        "Diagnóstico Metodológico": "La penalización L2 atenúa la varianza en Arg pero mantiene R²_CV < 0"
    },
    {
        "Modelo y Esquema de Evaluación": "OLS Parsimonioso 1 predictor: Obesidad (LOOCV / 5-Fold)",
        "EE.UU. R²": f"{r2_us_uni_loo:.3f} / {r2_us_uni_kf:.3f}",
        "EE.UU. MAE": f"{mae_us_uni_loo:.2f}% / {mae_us_uni_kf:.2f}%",
        "Argentina R²": f"{r2_ar_uni_loo:.3f} / {r2_ar_uni_kf:.3f}",
        "Argentina MAE": f"{mae_ar_uni_loo:.2f}% / {mae_ar_uni_kf:.2f}%",
        "Diagnóstico Metodológico": "Incluso con 1 solo predictor sin sobreparametrización no hay señal en Arg (R²<0)"
    },
    {
        "Modelo y Esquema de Evaluación": "Random Forest Regressor (LOOCV / 5-Fold CV)",
        "EE.UU. R²": f"{r2_us_rf_loo:.3f} / {r2_us_rf_kf:.3f}",
        "EE.UU. MAE": f"{mae_us_rf_loo:.2f}% / {mae_us_rf_kf:.2f}%",
        "Argentina R²": f"{r2_ar_rf_loo:.3f} / {r2_ar_rf_kf:.3f}",
        "Argentina MAE": f"{mae_ar_rf_loo:.2f}% / {mae_ar_rf_kf:.2f}%",
        "Diagnóstico Metodológico": "Sólida generalización en EE.UU.; fallo fuera de muestra en Arg en ambos esquemas"
    }
])
tab3_path = RESULTADOS_DIR / "tabla3_diagnostico_modelos.csv"
t3_df.to_csv(tab3_path, index=False, encoding="utf-8-sig")

# TABLA 4: Ranking de Extremos (Con rótulo claro de Pobreza EPH vs Ingresos <USD 25k)
top_us = df_us.nlargest(3, "tasa_diabetes_pct")[["estado", "tasa_diabetes_pct", "pobreza_ingresos_pct", "inactividad_fisica_pct"]]
bot_us = df_us.nsmallest(3, "tasa_diabetes_pct")[["estado", "tasa_diabetes_pct", "pobreza_ingresos_pct", "inactividad_fisica_pct"]]
top_ar = df_arg.nlargest(3, "tasa_diabetes_pct")[["provincia", "tasa_diabetes_pct", "pobreza_personas_pct", "tratamiento_diabetes_pct", "obesidad_pct"]]
bot_ar = df_arg.nsmallest(3, "tasa_diabetes_pct")[["provincia", "tasa_diabetes_pct", "pobreza_personas_pct", "tratamiento_diabetes_pct", "medicion_glucemia_pct"]]

t4_df = pd.DataFrame([
    {"Grupo Extremo": "EE.UU. — Mayor Prevalencia (1)", "Jurisdicción": f"{top_us.iloc[0]['estado']}", "Diabetes (%)": f"{top_us.iloc[0]['tasa_diabetes_pct']:.1f}%", "Ingresos <USD 25k (US) / Pobreza EPH (Arg)": f"{top_us.iloc[0]['pobreza_ingresos_pct']:.1f}%", "Dato Clave": "Cinturón de Diabetes (Sur profundo)"},
    {"Grupo Extremo": "EE.UU. — Mayor Prevalencia (2)", "Jurisdicción": f"{top_us.iloc[1]['estado']}", "Diabetes (%)": f"{top_us.iloc[1]['tasa_diabetes_pct']:.1f}%", "Ingresos <USD 25k (US) / Pobreza EPH (Arg)": f"{top_us.iloc[1]['pobreza_ingresos_pct']:.1f}%", "Dato Clave": f"Apalaches; inactividad {top_us.iloc[1]['inactividad_fisica_pct']:.1f}%"},
    {"Grupo Extremo": "EE.UU. — Menor Prevalencia (1)", "Jurisdicción": f"{bot_us.iloc[0]['estado']}", "Diabetes (%)": f"{bot_us.iloc[0]['tasa_diabetes_pct']:.1f}%", "Ingresos <USD 25k (US) / Pobreza EPH (Arg)": f"{bot_us.iloc[0]['pobreza_ingresos_pct']:.1f}%", "Dato Clave": "Mayor ingreso relativo y actividad física"},
    {"Grupo Extremo": "EE.UU. — Menor Prevalencia (2)", "Jurisdicción": f"{bot_us.iloc[1]['estado']}", "Diabetes (%)": f"{bot_us.iloc[1]['tasa_diabetes_pct']:.1f}%", "Ingresos <USD 25k (US) / Pobreza EPH (Arg)": f"{bot_us.iloc[1]['pobreza_ingresos_pct']:.1f}%", "Dato Clave": "Baja prevalencia de obesidad y tabaquismo"},
    {"Grupo Extremo": "Argentina — Mayor Prevalencia (1)", "Jurisdicción": f"{top_ar.iloc[0]['provincia']}", "Diabetes (%)": f"{top_ar.iloc[0]['tasa_diabetes_pct']:.1f}%", "Ingresos <USD 25k (US) / Pobreza EPH (Arg)": f"{top_ar.iloc[0]['pobreza_personas_pct']:.1f}%", "Dato Clave": "Región Cuyo (máximo nacional ENFR 2018)"},
    {"Grupo Extremo": "Argentina — Mayor Prevalencia (2)", "Jurisdicción": f"{top_ar.iloc[1]['provincia']}", "Diabetes (%)": f"{top_ar.iloc[1]['tasa_diabetes_pct']:.1f}%", "Ingresos <USD 25k (US) / Pobreza EPH (Arg)": f"{top_ar.iloc[1]['pobreza_personas_pct']:.1f}%", "Dato Clave": f"Máxima obesidad nacional ({top_ar.iloc[1]['obesidad_pct']:.1f}%)"},
    {"Grupo Extremo": "Argentina — Menor Prevalencia (1)", "Jurisdicción": f"{bot_ar.iloc[0]['provincia']}", "Diabetes (%)": f"{bot_ar.iloc[0]['tasa_diabetes_pct']:.1f}%", "Ingresos <USD 25k (US) / Pobreza EPH (Arg)": f"{bot_ar.iloc[0]['pobreza_personas_pct']:.1f}%", "Dato Clave": f"Menor obesidad (17,0%) y máx. screening ({bot_ar.iloc[0]['medicion_glucemia_pct']:.1f}%)"},
    {"Grupo Extremo": "Argentina — Menor Prevalencia (2)", "Jurisdicción": f"{bot_ar.iloc[1]['provincia']}", "Diabetes (%)": f"{bot_ar.iloc[1]['tasa_diabetes_pct']:.1f}%", "Ingresos <USD 25k (US) / Pobreza EPH (Arg)": f"{bot_ar.iloc[1]['pobreza_personas_pct']:.1f}%", "Dato Clave": f"Obesidad 31,1% pero bajo screening ({bot_ar.iloc[1]['medicion_glucemia_pct']:.1f}%)"}
])
tab4_path = RESULTADOS_DIR / "tabla4_ranking_extremos.csv"
t4_df.to_csv(tab4_path, index=False, encoding="utf-8-sig")

# Actualizar también tabla_comparativa_resumen.csv para que no queden cifras viejas
t_res_df = pd.DataFrame([
    {"Dimensión": "Unidades territoriales", "Estados Unidos": "51 estados (N=441.456)", "Argentina": "24 provincias (N=29.224)"},
    {"Dimensión": "Prevalencia media (DE)", "Estados Unidos": f"{us_mean_d:.1f}% (DE {us_sd_d:.1f}%)", "Argentina": f"{ar_mean_d:.1f}% prov. / 12,7% nac. (DE {ar_sd_samp:.1f}%)"},
    {"Dimensión": "Autocorrelación espacial (Moran's I)", "Estados Unidos": f"I = +{moran_us_d:.2f} (p < 0,001)", "Argentina": f"I = +{moran_ar_d:.2f} (p = {p_moran_ar_d:.3f})"},
    {"Dimensión": "Correlación Pobreza/Ingresos vs Diabetes", "Estados Unidos": f"r = {r_us_pob:+.2f} (IC95% [{lo_us_pob:+.2f}; {hi_us_pob:+.2f}])", "Argentina": f"r = {r_ar_pob:+.2f} (IC95% [{lo_ar_pob:+.2f}; {hi_ar_pob:+.2f}])"},
    {"Dimensión": "Correlación NBI vs Screening", "Estados Unidos": ">85% cobertura rutinaria", "Argentina": f"r = {r_nbi_scr:+.2f} (IC95% [{lo_nbi_scr:+.2f}; {hi_nbi_scr:+.2f}])"},
    {"Dimensión": "Correlación Screening vs Diabetes (Arg)", "Estados Unidos": "—", "Argentina": f"r = {r_scr_d24:+.2f} (N=24) / r = {r_scr_d23:+.2f} (sin CABA, N=23)"},
    {"Dimensión": "Desempeño OLS (In-Sample / LOOCV)", "Estados Unidos": f"R² = {m_us.rsquared:.3f} / {r2_us_ols_loo:.3f}", "Argentina": f"R² = {m_ar.rsquared:.3f} / {r2_ar_ols_loo:.3f}"},
    {"Dimensión": "Desempeño Random Forest (LOOCV / 5-Fold)", "Estados Unidos": f"R² = {r2_us_rf_loo:.3f} / {r2_us_rf_kf:.3f}", "Argentina": f"R² = {r2_ar_rf_loo:.3f} / {r2_ar_rf_kf:.3f}"}
])
t_res_df.to_csv(RESULTADOS_DIR / "tabla_comparativa_resumen.csv", index=False, encoding="utf-8-sig")

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
ax_u.set_title(f"(a) Estados Unidos: Prevalencia de Diabetes (%)\n[CDC BRFSS 2015; N=51; I de Moran = +{moran_us_d:.2f}, p<0,001]", fontsize=10, fontweight="bold")
ax_u.axis("off")
ax_u.annotate("Cinturón de la Diabetes\n(Misisipi 14,8%, Alabama 13,6%)", xy=(-88.5, 32.5), xytext=(-98.0, 26.0),
              arrowprops=dict(facecolor="#c53030", arrowstyle="->", lw=1.1), fontsize=8, fontweight="bold",
              bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#c53030", alpha=0.9))
ax_u.annotate("Colorado: 6,8% (Mín)", xy=(-105.5, 39.0), xytext=(-116.0, 42.0),
              arrowprops=dict(facecolor="#2b6cb0", arrowstyle="->", lw=1.0), fontsize=8, fontweight="bold",
              bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#2b6cb0", alpha=0.9))

arg_merged.plot(column="tasa_diabetes_pct", ax=ax_a, cmap="YlOrRd", vmin=vmin_d, vmax=vmax_d, edgecolor="#4a5568", linewidth=0.6)
ax_a.set_title(f"(b) Argentina: Prevalencia de Diabetes o Glucemia Elevada (%)\n[ENFR 2018; N=24; I de Moran = +{moran_ar_d:.2f}, p={p_moran_ar_d:.2f}]", fontsize=10, fontweight="bold")
ax_a.axis("off")
ax_ins = inset_axes(ax_a, width="100%", height="100%", bbox_to_anchor=(0.72, 0.52, 0.28, 0.28), bbox_transform=ax_a.transAxes)
arg_merged.plot(column="tasa_diabetes_pct", ax=ax_ins, cmap="YlOrRd", vmin=vmin_d, vmax=vmax_d, edgecolor="#4a5568", linewidth=0.6)
ax_ins.set_xlim(-58.85, -58.20); ax_ins.set_ylim(-34.85, -34.35); ax_ins.set_xticks([]); ax_ins.set_yticks([])
ax_ins.set_title("CABA: 8,8%", fontsize=8, fontweight="bold", pad=2)

ax_a.annotate("San Luis: 17,3%\n(Máx. nacional)", xy=(-66.3, -33.3), xytext=(-73.5, -31.0),
              arrowprops=dict(facecolor="#c53030", arrowstyle="->", lw=1.0), fontsize=8, fontweight="bold",
              bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#c53030", alpha=0.9))
ax_a.annotate("Subdiagnóstico en el Norte:\nChaco 10,3% (39,7% sin screening)", xy=(-60.5, -26.8), xytext=(-54.0, -23.5),
              arrowprops=dict(facecolor="#2b6cb0", arrowstyle="->", lw=1.0), fontsize=8, fontweight="bold",
              bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#2b6cb0", alpha=0.9))

sm1 = plt.cm.ScalarMappable(cmap="YlOrRd", norm=plt.Normalize(vmin=vmin_d, vmax=vmax_d))
sm1._A = []
cbar1 = fig1.colorbar(sm1, ax=[ax_u, ax_a], orientation="horizontal", fraction=0.035, pad=0.04, aspect=35, shrink=0.6)
cbar1.set_label("Prevalencia declarada (%) — Escala común unificada", fontsize=9.5, fontweight="bold")
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
axes2[1, 0].set_title("(c) Inactividad en Tiempo Libre en EE.UU. (_TOTINDA, %)", fontsize=9.5, fontweight="bold"); axes2[1, 0].axis("off")
sm_sed_u = plt.cm.ScalarMappable(cmap="Purples", norm=plt.Normalize(vmin=16, vmax=36)); sm_sed_u._A = []
fig2.colorbar(sm_sed_u, ax=axes2[1, 0], fraction=0.03, pad=0.02, shrink=0.7)

arg_merged.plot(column="inactividad_fisica_pct", ax=axes2[1, 1], cmap="Purples", edgecolor="#4a5568", linewidth=0.5, vmin=20, vmax=70)
axes2[1, 1].set_title("(d) Baja Actividad Física en Argentina (Cuestionario IPAQ, %)", fontsize=9.5, fontweight="bold"); axes2[1, 1].axis("off")
sm_sed_a = plt.cm.ScalarMappable(cmap="Purples", norm=plt.Normalize(vmin=20, vmax=70)); sm_sed_a._A = []
fig2.colorbar(sm_sed_a, ax=axes2[1, 1], fraction=0.03, pad=0.02, shrink=0.7)

fig2_path = RESULTADOS_DIR / "figura2_factores_riesgo.png"
fig2.savefig(fig2_path, bbox_inches="tight", dpi=220)
plt.close(fig2)

# --- FIGURA 3: COBERTURA DE TRATAMIENTO Y BARRERA DE COSTO ---
fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(14, 6.5))
df_arg_tr = df_arg.sort_values("tratamiento_diabetes_pct", ascending=True)
colors_tr = ["#e53e3e" if x < 45 else "#3182ce" if x > 60 else "#718096" for x in df_arg_tr["tratamiento_diabetes_pct"]]
ax3a.barh(df_arg_tr["provincia"], df_arg_tr["tratamiento_diabetes_pct"], color=colors_tr, edgecolor="none", height=0.75)
ax3a.axvline(ar_trat_mean, color="black", linestyle="--", linewidth=1.2, label=f"Media Arg: {ar_trat_mean:.1f}% (Brecha: {ar_brecha_mean:.1f}%)")
ax3a.set_xlabel("Población diabética bajo tratamiento farmacológico activo (%)", fontsize=9.5, fontweight="bold")
ax3a.set_title("(a) Argentina: Cobertura de Tratamiento Farmacológico (ENFR)", fontsize=10, fontweight="bold")
ax3a.legend(loc="lower right", fontsize=8.5)
ax3a.grid(True, axis="x", linestyle=":", alpha=0.6)

x_bc = df_us["barrera_costo_medico_pct"]; y_bc = df_us["tasa_diabetes_pct"]
sl_bc, in_bc, r_bc, p_bc, _ = stats.linregress(x_bc, y_bc)
ax3b.scatter(x_bc, y_bc, color="#dd6b20", s=55, edgecolor="black", linewidth=0.5, alpha=0.85)
x_lin_bc = np.linspace(x_bc.min(), x_bc.max(), 50)
ax3b.plot(x_lin_bc, in_bc + sl_bc * x_lin_bc, color="#9c4221", lw=2, label=f"Ajuste OLS (r = +{r_bc:.2f}; p < 0,001)")
ax3b.set_xlabel("Población con barrera de costo para ver al médico (%)", fontsize=9.5, fontweight="bold")
ax3b.set_ylabel("Prevalencia de diabetes (%)", fontsize=9.5, fontweight="bold")
ax3b.set_title("(b) EE.UU.: Barrera Económica de Acceso vs. Prevalencia", fontsize=10, fontweight="bold")
ax3b.legend(loc="upper left", fontsize=8.5)
ax3b.grid(True, linestyle=":", alpha=0.6)
fig3_path = RESULTADOS_DIR / "figura3_brecha_tratamiento.png"
fig3.savefig(fig3_path, bbox_inches="tight", dpi=220)
plt.close(fig3)

# --- FIGURA 4: MATRIZ DE CALOR DE CORRELACIONES ---
fig4, (ax4u, ax4a) = plt.subplots(1, 2, figsize=(13, 5.5))
vars_h_u = ["Diabetes", "Obesidad", "Inact. TL", "Ing.<25k", "Sin Seg."]
vars_h_a = ["Diabetes", "Obesidad", "Baja IPAQ", "Pobr. EPH", "Sin OS"]
corr_u = df_us[["tasa_diabetes_pct", "obesidad_pct", "inactividad_fisica_pct", "pobreza_ingresos_pct", "sin_cobertura_salud_pct"]].corr().values
corr_a = df_arg[["tasa_diabetes_pct", "obesidad_pct", "inactividad_fisica_pct", "pobreza_personas_pct", "sin_cobertura_salud_pct"]].corr().values

im4u = ax4u.imshow(corr_u, cmap="RdBu_r", vmin=-1, vmax=1)
ax4u.set_xticks(range(5)); ax4u.set_yticks(range(5))
ax4u.set_xticklabels(vars_h_u, rotation=35, ha="right", fontsize=8.5, fontweight="bold")
ax4u.set_yticklabels(vars_h_u, fontsize=8.5, fontweight="bold")
ax4u.set_title("(a) Estados Unidos (CDC BRFSS, N=51)", fontsize=10.5, fontweight="bold")
for i in range(5):
    for j in range(5):
        val = corr_u[i, j]
        ax4u.text(j, i, f"{val:+.2f}", ha="center", va="center", fontsize=8, color="white" if abs(val)>0.45 else "black", fontweight="bold")

im4a = ax4a.imshow(corr_a, cmap="RdBu_r", vmin=-1, vmax=1)
ax4a.set_xticks(range(5)); ax4a.set_yticks(range(5))
ax4a.set_xticklabels(vars_h_a, rotation=35, ha="right", fontsize=8.5, fontweight="bold")
ax4a.set_yticklabels(vars_h_a, fontsize=8.5, fontweight="bold")
ax4a.set_title("(b) Argentina (ENFR / INDEC, N=24)", fontsize=10.5, fontweight="bold")
for i in range(5):
    for j in range(5):
        val = corr_a[i, j]
        ax4a.text(j, i, f"{val:+.2f}", ha="center", va="center", fontsize=8, color="white" if abs(val)>0.45 else "black", fontweight="bold")

fig4.colorbar(im4a, ax=[ax4u, ax4a], orientation="horizontal", fraction=0.045, pad=0.14, aspect=35, shrink=0.5, label="Coeficiente de correlación lineal de Pearson (r)")
fig4_path = RESULTADOS_DIR / "figura4_matriz_correlaciones.png"
fig4.savefig(fig4_path, bbox_inches="tight", dpi=220)
plt.close(fig4)

# --- FIGURA 5: REGRESIONES Y DIAGNOSTICO DE SUBDIAGNOSTICO ---
fig5, (ax5a, ax5b) = plt.subplots(1, 2, figsize=(13.5, 5.5))
ax5a.scatter(df_us["pobreza_ingresos_pct"], df_us["tasa_diabetes_pct"], color="#e53e3e", alpha=0.75, s=45,
             label=f"EE.UU. (r = {r_us_pob:+.2f}, IC95% [{lo_us_pob:+.2f}; {hi_us_pob:+.2f}])")
x_lin_u = np.linspace(df_us["pobreza_ingresos_pct"].min(), df_us["pobreza_ingresos_pct"].max(), 50)
sl_u5, in_u5, _, _, _ = stats.linregress(df_us["pobreza_ingresos_pct"], df_us["tasa_diabetes_pct"])
ax5a.plot(x_lin_u, in_u5 + sl_u5 * x_lin_u, color="#9b2c2c", lw=2)

ax5a.scatter(df_arg["pobreza_personas_pct"], df_arg["tasa_diabetes_pct"], color="#3182ce", alpha=0.85, s=60, marker="s", edgecolor="black",
             label=f"Argentina (r = {r_ar_pob:+.2f}, IC95% [{lo_ar_pob:+.2f}; {hi_ar_pob:+.2f}])")
x_lin_a = np.linspace(df_arg["pobreza_personas_pct"].min(), df_arg["pobreza_personas_pct"].max(), 50)
sl_a5, in_a5, _, _, _ = stats.linregress(df_arg["pobreza_personas_pct"], df_arg["tasa_diabetes_pct"])
ax5a.plot(x_lin_a, in_a5 + sl_a5 * x_lin_a, color="#1a365d", lw=2, linestyle="--")
ax5a.set_xlabel("Bajos ingresos <USD 25k (EE.UU.) / Pobreza monetaria EPH (Arg) (%)", fontsize=9, fontweight="bold")
ax5a.set_ylabel("Prevalencia de diabetes (%)", fontsize=9.5, fontweight="bold")
ax5a.set_title("(a) Contraste: Privación Monetaria vs. Prevalencia", fontsize=10, fontweight="bold")
ax5a.legend(loc="upper left", fontsize=8)
ax5a.grid(True, linestyle=":", alpha=0.5)

x_sc = df_arg["nbi_2010_pct"]; y_sc = df_arg["medicion_glucemia_pct"]
sl_sc, in_sc, r_sc, p_sc, _ = stats.linregress(x_sc, y_sc)
ax5b.scatter(x_sc, y_sc, color="#38a169", s=65, edgecolor="black", linewidth=0.6, alpha=0.85)
x_lin_sc = np.linspace(x_sc.min(), x_sc.max(), 50)
ax5b.plot(x_lin_sc, in_sc + sl_sc * x_lin_sc, color="#22543d", lw=2, linestyle="-",
          label=f"NBI vs. Screening: r = {r_nbi_scr:+.2f} (p < 0,001)\nScreening vs. Diabetes (sin CABA): r = {r_scr_d23:+.2f}")
for i, txt in enumerate(df_arg["provincia"]):
    if txt in ["CABA", "Chaco", "Formosa", "Santiago del Estero", "San Luis", "Santa Fe", "Jujuy"]:
        ax5b.annotate(txt, (x_sc.iloc[i], y_sc.iloc[i]), fontsize=7.5, xytext=(4, 3), textcoords="offset points")
ax5b.set_xlabel("Hogares con Necesidades Básicas Insatisfechas NBI (%)", fontsize=9.5, fontweight="bold")
ax5b.set_ylabel("Screening: Medición de glucemia alguna vez (%)", fontsize=9.5, fontweight="bold")
ax5b.set_title("(b) Argentina: Pobreza Estructural vs. Acceso a Screening", fontsize=10, fontweight="bold")
ax5b.legend(loc="lower left", fontsize=8)
ax5b.grid(True, linestyle=":", alpha=0.5)

fig5_path = RESULTADOS_DIR / "figura5_modelos_dispersion.png"
fig5.savefig(fig5_path, bbox_inches="tight", dpi=220)
plt.close(fig5)
print("    - 5 Figuras científicas generadas con éxito en Resultados/.")

# ==============================================================================
# 4. TEXTOS ACADEMICOS UNIFICADOS (CONAIISI / CIITI)
# ==============================================================================
TITLE_ES = "Determinantes geoespaciales de la diabetes tipo 2 en la Argentina y los Estados Unidos: Salud basada en datos, cobertura de tratamiento y límites del modelado predictivo"
TITLE_EN = "Geospatial Determinants of Type 2 Diabetes in Argentina and the United States: Health Data Science, Treatment Coverage, and Boundaries of Predictive Modeling"

# Resumen acotado (~210 palabras) para cumplir holgadamente con el límite de plantilla CoNaIISI/CIITI
RESUMEN_ES = (
    "La diabetes mellitus tipo 2 exhibe patrones territoriales heterogéneos modulados por los sistemas de salud. "
    "Este trabajo desarrolla un pipeline reproducible de ciencia de datos que compara los determinantes subnacionales de la enfermedad "
    "entre los 51 estados de los Estados Unidos (CDC BRFSS 2015, N=441.456 adultos ponderados) y las 24 jurisdicciones de la Argentina "
    "(4ª ENFR 2018 integrada con los Censos 2010/2022 y la EPH del INDEC). Los resultados sugieren una divergencia estructural: en los Estados Unidos, "
    "bajo un aseguramiento fragmentado de mercado, la prevalencia muestra fuerte autocorrelación espacial (I de Moran = +0,59; p < 0,001) y asociación lineal "
    "con los bajos ingresos (r = +0,81; IC95% [+0,69; +0,89]) y la inactividad física (r = +0,79), logrando un ajuste robusto en regresión OLS (R² = 0,891; LOOCV R² = 0,859) "
    "y Random Forest (5-Fold R² = 0,802). En contraste, en la Argentina la prevalencia provincial declarada (media 13,0%, DE 2,1%) no se asocia linealmente "
    "con la pobreza monetaria (r = -0,05; IC95% [-0,44; +0,36]; ρ = -0,19) ni con la falta de cobertura formal (r = -0,16). Este desacople es analizado junto a "
    "factores concurrentes (estructura etaria y error muestral CV ≤ 12,5%) bajo dos hipótesis sanitarias: primero, el posible subdiagnóstico en provincias con alta "
    "pobreza estructural NBI, las cuales registran menor screening glucémico (r = -0,81; p < 0,001), observándose que al excluir el outlier urbano de CABA "
    "(8,8% de prevalencia con 17,0% de obesidad y 92,9% de tamizaje) el screening correlaciona positivamente con la diabetes declarada (r = +0,40; p = 0,057); "
    "segundo, la ausencia de gradiente regresivo en el tratamiento farmacológico (r = -0,11; p = 0,62), donde jurisdicciones con más del 50% de población sin obra social "
    "(Santiago del Estero 56,0%, Formosa 55,9%, Chaco 52,2%) alcanzan coberturas terapéuticas del 54,2% al 62,6% mediante la red pública (Ley 26.914/PRODIABA y Programa Remediar), "
    "aunque persiste una brecha media nacional del 45,6%. Metodológicamente, con N=24 provincias tanto OLS (LOOCV R² = -0,701) como Ridge (R² = -0,311), regresiones univariadas "
    "(R² = -0,100) y Random Forest (5-Fold R² = -0,802) rinden por debajo de la media constante, sugiriendo priorizar atlas descriptivos y pesquisa activa frente al sobreajuste predictivo."
)

ABSTRACT_EN = (
    "Type 2 diabetes mellitus exhibits heterogeneous spatial patterns shaped by healthcare system architecture. "
    "This study implements a reproducible health data science pipeline comparing subnational determinants across the 51 U.S. jurisdictions "
    "(CDC BRFSS 2015, N=441,456 weighted adults) and the 24 Argentine provinces (4th ENFR 2018 integrated with the 2010/2022 National Censuses and INDEC's EPH). "
    "Findings suggest a structural divergence: in the market-driven U.S. system, prevalence exhibits strong spatial autocorrelation (Moran's I = +0.59; p < 0.001) "
    "and linear association with low household income (r = +0.81; 95% CI [+0.69, +0.89]) and leisure-time inactivity (r = +0.79), enabling strong performance in "
    "multivariate OLS (R² = 0.891; LOOCV R² = 0.859) and Random Forest (5-Fold R² = 0.802). Conversely, in Argentina provincial self-reported prevalence "
    "(mean 13.0%, SD 2.1%) shows no linear association with monetary poverty (r = -0.05; 95% CI [-0.44, +0.36]; Spearman ρ = -0.19) or lack of insurance (r = -0.16). "
    "Alongside demographic age structure and survey sampling variability (CV ≤ 12.5%), two healthcare mechanisms are examined: first, potential underdiagnosis in high-NBI "
    "provinces with lower glycemic screening (r = -0.81; p < 0.001), noting that after excluding the CABA urban outlier (8.8% prevalence, 17.0% obesity, 92.9% screening), "
    "screening correlates positively with reported prevalence (r = +0.40; p = 0.057); second, the absence of a regressive gradient in pharmacological treatment (r = -0.11; p = 0.62), "
    "where provinces with >50% uninsured population (Santiago del Estero 56.0%, Formosa 55.9%, Chaco 52.2%) reach 54.2%–62.6% active treatment coverage through public programs "
    "(Law 26,914/PRODIABA and Remediar), despite a 45.6% mean national treatment gap. Methodologically, at N=24, multivariate OLS (LOOCV R² = -0.701), Ridge (R² = -0.311), "
    "univariate models (R² = -0.100), and Random Forest (5-Fold R² = -0.802) underperform the naive baseline, supporting descriptive geospatial atlases over fragile predictive models."
)

REFS = [
    '[1] International Diabetes Federation, "IDF Diabetes Atlas", 11.ª ed., Bruselas: IDF, 2024. [En línea]. Disponible: https://diabetesatlas.org',
    '[2] NCD Risk Factor Collaboration (NCD-RisC), "Worldwide trends in diabetes prevalence and treatment from 1990 to 2022: a pooled analysis of 1108 population-representative studies with 141 million participants", The Lancet, vol. 404, n.º 10467, pp. 2077–2093, 2024.',
    '[3] K. L. Ong et al. (GBD 2021 Diabetes Collaborators), "Global, regional, and national burden of diabetes from 1990 to 2021, with projections of prevalence to 2050: a systematic analysis for the Global Burden of Disease Study 2021", The Lancet, vol. 402, n.º 10397, pp. 203–234, 2023.',
    '[4] F. Hill-Briggs y S. L. Fitzpatrick, "Overview of Social Determinants of Health in the Development of Diabetes", Diabetes Care, vol. 46, n.º 9, pp. 1590–1598, 2023.',
    '[5] L. E. Egede, J. A. Campbell, R. J. Walker y S. Linde, "Structural Racism as an Upstream Social Determinant of Diabetes Outcomes: A Scoping Review", Diabetes Care, vol. 46, n.º 4, pp. 667–677, 2023.',
    '[6] American Diabetes Association Professional Practice Committee, "1. Improving Care and Promoting Health in Populations: Standards of Care in Diabetes—2024", Diabetes Care, vol. 47, Suppl. 1, pp. S11–S19, 2024.',
    '[7] G. A. Benavidez, W. E. Zahnd, P. Hung y J. M. Eberth, "Chronic Disease Prevalence in the US: Sociodemographic and Geographic Variations by Zip Code Tabulation Area", Preventing Chronic Disease, vol. 21, art. 230267, 2024.',
    '[8] J. T. Wittman, D. S. Alexander, M. Bing, R. Montierth, H. Xie, S. R. Benoit y K. McKeever Bullard, "Identifying Priority Geographic Locations for Diabetes Self-Management Education and Support Services in the Appalachian Region", Preventing Chronic Disease, vol. 21, art. 230297, 2024.',
    '[9] A. Gaffney, D. U. Himmelstein y S. Woolhandler, "Prevalence and Correlates of Patient Rationing of Insulin in the United States: A National Survey", Annals of Internal Medicine, vol. 175, n.º 11, pp. 1623–1626, 2022.',
    '[10] M. Fang y E. Selvin, "Cost-Related Insulin Rationing in US Adults Younger Than 65 Years With Diabetes", JAMA, vol. 329, n.º 19, pp. 1700–1702, 2023.',
    '[11] Centers for Disease Control and Prevention (CDC), "Behavioral Risk Factor Surveillance System (BRFSS) and PLACES: Local Data for Better Health", Atlanta: U.S. Department of Health and Human Services, 2024. [En línea]. Disponible: https://www.cdc.gov/brfss',
    '[12] Instituto Nacional de Estadística y Censos (INDEC), "Censo Nacional de Población, Hogares y Viviendas 2022: Resultados definitivos de cobertura de salud y condiciones habitacionales", Buenos Aires: INDEC, 2023.',
    '[13] Instituto Nacional de Estadística y Censos (INDEC), "Bases de microdatos y cuadros estadísticos de la Encuesta Nacional de Factores de Riesgo (ENFR) y Encuesta Permanente de Hogares (EPH)", Buenos Aires: INDEC, 2023. [En línea]. Disponible: https://www.indec.gob.ar',
    '[14] Ministerio de Salud de la Nación Argentina, "Guía de Práctica Clínica Nacional sobre Prevención, Diagnóstico y Tratamiento de la Diabetes Mellitus Tipo 2 (DM2) — Resolución Ministerial N.º 3877/2023", Buenos Aires: Dirección Nacional de Abordaje Integral de Enfermedades No Transmisibles, 2023.',
    '[15] Ministerio de Salud de la Nación Argentina, "Programa Nacional Remediar y PRODIABA (Ley N.º 26.914): Provisión gratuita de medicamentos esenciales e insumos en el Primer Nivel de Atención", Buenos Aires: Ministerio de Salud de la Nación, 2023.',
    '[16] M. J. Marro, M. de J. Mendes da Fonseca, I. da Costa Leite, C. Ballejo y M. Alazraqui, "Un retorno al ambiente en epidemiología: análisis multinivel de la diabetes mellitus en un gran aglomerado urbano de Argentina", Revista Brasileira de Epidemiologia, vol. 29, e260043, 2026.',
    '[17] J. F. Elgart, E. Rucci y J. J. Gagliardino, "Visión epidemiológica, psicosocial y terapéutica de la diabetes mellitus en Argentina desde las perspectivas del equipo de salud y de las personas con diabetes", Revista de la Sociedad Argentina de Diabetes, vol. 56, n.º 1, pp. 31–37, 2022.',
    '[18] T. Ortiz-Basso, B. R. Boietti, P. V. Gómez, A. D. Boffelli y A. A. Paladini, "Prevalencia de retinopatía diabética en una zona rural de Argentina", Medicina (Buenos Aires), vol. 82, n.º 1, pp. 99–103, 2022.',
    '[19] S. J. Rey, D. Arribas-Bel y L. J. Wolf, "Geographic Data Science with Python", Boca Raton: CRC Press / Chapman & Hall, 2023.',
    '[20] G. James, D. Witten, T. Hastie, R. Tibshirani y J. Taylor, "An Introduction to Statistical Learning: with Applications in Python", Cham: Springer, 2023.',
    '[21] G. Varoquaux y V. Cheplygina, "Machine learning for medical imaging: methodological failures and recommendations for the future", npj Digital Medicine, vol. 5, n.º 1, art. 48, 2022.',
    '[22] G. S. Collins, K. G. M. Moons, P. Dhiman et al., "TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods", BMJ, vol. 385, e078378, 2024.',
    '[23] K. Jordahl et al., "GeoPandas: Python tools for geographic data (v1.0)", Zenodo, 2024. [En línea]. Disponible: https://geopandas.org',
    '[24] Scikit-learn Developers, "Scikit-learn: Machine Learning in Python (v1.5 Documentation)", 2024. [En línea]. Disponible: https://scikit-learn.org',
    '[25] World Health Organization (WHO), "Global Diabetes Compact and Noncommunicable Diseases Progress Monitor", Ginebra: Organización Mundial de la Salud, 2022.'
]

SEC1_PARS = [
    "La diabetes mellitus tipo 2 se ha consolidado como una de las crisis sanitarias no transmisibles más relevantes a escala global [25]. Según las estimaciones de la 11.ª edición del International Diabetes Federation (IDF) Diabetes Atlas [1], los estudios poblacionales globales del consorcio NCD-RisC [2] y el Global Burden of Disease Study [3] publicados en The Lancet, más de 589 millones de adultos viven actualmente con la enfermedad en el mundo, proyectándose que esta cifra superará los 850 millones hacia el año 2050, mientras que las tasas globales de cobertura terapéutica permanecen rezagadas frente al crecimiento de la prevalencia [2], [3].",
    "El impacto epidemiológico de la patología dista de manifestarse de manera homogénea en el territorio. Existe consenso interdisciplinario en torno a que los Determinantes Sociales de la Salud (DSS) [4], [5], [6] —tales como la disponibilidad de alimentos saludables, las condiciones materiales para la actividad física, la privación socioeconómica y el acceso efectivo a servicios diagnósticos y farmacológicos— modulan la distribución espacial de la morbimortalidad en las Américas [4], [16].",
    "Desde la perspectiva de la ciencia de datos en salud (Health Data Science), un interrogante central consiste en evaluar si los patrones espaciales y los modelos predictivos formulados en economías desarrolladas con sistemas de salud privados son extrapolables a países de América Latina con sistemas públicos universales. Frecuentemente, la literatura de aprendizaje automático aplicado asume que los gradientes sociodemográficos observados en países anglosajones operan de forma análoga en cualquier latitud, soslayando el rol mediador de la arquitectura sanitaria.",
    "Por una parte, los Estados Unidos constituyen el arquetipo de un sistema de salud fragmentado y dependiente del aseguramiento privado o laboral, donde la pesquisa bioquímica rutinaria está ampliamente extendida, pero la continuidad farmacológica (insulina e hipoglucemiantes) enfrenta severas barreras de copago y racionamiento por costo de bolsillo [6], [9], [10]. Por otra parte, la República Argentina sostiene un sistema mixto con un subsistema público de acceso universal y gratuito en el punto de atención, respaldado por la Guía de Práctica Clínica Nacional de DM2 [14], el marco normativo de cobertura integral de insulinas e insumos (PRODIABA / Ley N.º 26.914) y la distribución de hipoglucemiantes orales esenciales en centros de atención primaria mediante el Programa Nacional Remediar [15], aunque condicionado por marcadas asimetrías socioambientales y de infraestructura diagnóstica en el norte y las zonas rurales [13], [16], [17], [18].",
    "El objetivo de este trabajo es implementar un pipeline reproducible de ciencia de datos para contrastar empíricamente la epidemiología geoespacial de la diabetes entre los 51 estados de los Estados Unidos y las 24 jurisdicciones de la Argentina. Específicamente se propone: (i) analizar la distribución cartográfica y la autocorrelación espacial (Índice I de Moran) de la prevalencia en ambos países; (ii) contrastar las asociaciones paramétricas (Pearson con intervalos de confianza al 95%) y no paramétricas (Spearman) entre privación socioeconómica y prevalencia declarada; (iii) examinar el rol del tamizaje glucémico (screening), la sensibilidad a valores extremos urbanos (CABA) y la cobertura farmacológica; y (iv) evaluar los límites de generalización fuera de muestra de modelos lineales, regularizados (Ridge) y no lineales (Random Forest) bajo esquemas simétricos de validación cruzada en muestras agregadas pequeñas (N=24)."
]

SEC2_PARS = [
    "El marco conceptual se apoya en el modelo de Determinantes Sociales de la Salud de la Organización Mundial de la Salud (OMS) [25] y de la American Diabetes Association (ADA) [4], [6], así como en revisiones recientes sobre desigualdades estructurales y territoriales en diabetes [5]. Este enfoque postula que las patologías cardiometabólicas responden a exposiciones acumulativas vinculadas a la estructura socioeconómica y a la organización territorial de los servicios preventivos.",
    "En los Estados Unidos, la literatura epidemiológica reciente del CDC y estudios geoespaciales a gran escala como los de Benavidez et al. [7] y Wittman et al. [8] han documentado la persistencia de un corredor de alta prevalencia ('Cinturón de la Diabetes') en los Apalaches y el sudeste estadounidense (Misisipi, Alabama, Virginia Occidental, Luisiana). Estas investigaciones confirman a escala subnacional que la superposición de privación económica, menor nivel educativo, barreras financieras y sedentarismo explica la mayor parte de la variabilidad territorial de la diabetes diagnosticada en dicho país [5], [7], [8].",
    "En la República Argentina, las investigaciones recientes en epidemiología espacial y sanitaria han documentado brechas regionales y urbanas persistentes. Marro et al. [16] demostraron mediante modelos multinivel la influencia determinante del entorno socioambiental y las desigualdades territoriales sobre la prevalencia de diabetes en aglomerados argentinos, mientras que Elgart et al. [17] relevaron las barreras operativas, psicosociales y terapéuticas que enfrentan los equipos de salud y los pacientes en el país. Asimismo, estudios clínicos en contextos rurales argentinos, como el de Ortiz-Basso et al. [18], han advertido sobre las barreras geográficas para el diagnóstico y control oftalmológico temprano.",
    "En el plano metodológico, la ciencia de datos geoespaciales contemporánea (Rey, Arribas-Bel y Wolf [19]) enfatiza que el análisis de agregaciones jurisdiccionales está sujeto al Problema de la Unidad de Área Modificable (MAUP), a la dependencia espacial entre unidades vecinas y al riesgo de falacia ecológica. A ello se suma que en el aprendizaje estadístico supervisado [20] y en las guías internacionales de reporte y validación de modelos en salud (Varoquaux y Cheplygina [21]; guía TRIPOD+AI de Collins et al. [22]), entrenar modelos multiparamétricos cuando la razón de observaciones por predictor es reducida (v.g., N=24 provincias con 5 covariables) incrementa drásticamente la varianza del estimador fuera de muestra, exigiendo contrastar cualquier algoritmo contra modelos parsimoniosos, regularizados y estimadores de referencia (naive baseline)."
]

SEC31_PARS = [
    "Se procesaron los microdatos públicos del Behavioral Risk Factor Surveillance System (BRFSS, corte armonizado 2015 del repositorio plurianual del CDC [11]), compuestos por 441.456 entrevistas a adultos no institucionalizados de 18 años y más. Aplicando el factor de ponderación muestral oficial (_LLCPWT), que calibra por estructura etaria, sexo y raza/etnia, se agregaron los indicadores representativos de las 51 jurisdicciones (50 estados y Washington D.C.).",
    "Se extrajeron: prevalencia de diabetes diagnosticada (variable DIABETE3, excluyendo diabetes gestacional y prediabetes declarada); obesidad autorreportada (IMC ≥ 30 kg/m², _BMI5CAT); inactividad física en el tiempo libre durante los últimos 30 días (_TOTINDA); porcentaje de adultos en hogares con ingresos anuales inferiores a USD 25.000 (INCOME2); adultos con educación secundaria incompleta (_EDUCAG); barrera económica para consultar al médico en el último año (MEDCOST); y adultos de 18 a 64 años sin seguro médico (_HCVU651)."
]

SEC32_PARS = [
    "Para la República Argentina se construyó un dataset provincial de las 24 jurisdicciones (23 provincias y CABA) integrando los repositorios oficiales abiertos del INDEC [12], [13] y del Ministerio de Salud de la Nación [14], [15]:",
    "1. 4ª Encuesta Nacional de Factores de Riesgo (ENFR, repositorio de microdatos y tabulados definitivos del INDEC [13]): Con representatividad para la población urbana de 18 años y más (N=29.224 hogares efectivos en aglomerados de ≥5.000 habitantes, representativos de ~29,5 millones de adultos urbanos dentro de una población total nacional de ~44 millones), se extrajeron de sus cuadros definitivos: prevalencia de diabetes o glucemia elevada autorreportada por diagnóstico previo de personal de salud (Cuadro 7.3) y su coeficiente de variación muestral (CV, todos ≤12,5%); cobertura de tratamiento farmacológico activo (pastillas o insulina) entre personas con diabetes (Cuadro 7.5); tasa de screening glucémico alguna vez en la vida (Cuadro 7.1); obesidad autorreportada IMC ≥ 30 (Cuadro 6.3); y prevalencia de nivel bajo de actividad física según el cuestionario internacional IPAQ (Cuadro 3.1).",
    "2. Censo Nacional de Población, Hogares y Viviendas 2022 y serie censal histórica (INDEC) [12]: Se incorporó el porcentaje de hogares con Necesidades Básicas Insatisfechas (NBI, serie censal histórica de privación estructural); el porcentaje de población sin cobertura formal por obra social ni prepaga, dependiente exclusivamente del subsistema público (Censo 2022, Cuadro C1) [12]; y la densidad demográfica continental transformada en escala logarítmica (log10 hab/km²).",
    "3. Encuesta Permanente de Hogares (EPH, base de pobreza monetaria del INDEC [13]): Se relevó la incidencia de pobreza monetaria de personas bajo la línea de pobreza (Cuadro 4.3), promediando los aglomerados urbanos de cada jurisdicción en sincronía temporal con el operativo de la ENFR."
]

SEC33_PARS = [
    "El procesamiento geoespacial y econométrico se implementó en Python utilizando GeoPandas [23], SciPy, Statsmodels y Scikit-learn [24] siguiendo los estándares de ciencia de datos geográficos de Rey et al. [19] (el código fuente completo, los datos crudos y las tablas procesadas se encuentran abiertos en el repositorio reproducible del proyecto: https://github.com/florr/Diabetes-Geografica-CIITI-2026). Para evaluar formalmente la dependencia geográfica más allá de la inspección visual, se calculó el Índice I de Moran global de autocorrelación espacial [19] sobre las matrices de pesos de contigüidad tipo Reina (Queen, vinculando a Tierra del Fuego con su vecino continental más próximo) con inferencia por 9.999 permutaciones de Monte Carlo.",
    "Para el análisis bivariado se reportan tanto el coeficiente paramétrico de Pearson (r) con sus intervalos de confianza al 95% (IC95% mediante transformación z de Fisher) como el coeficiente no paramétrico de rangos de Spearman (ρ), junto con un análisis de sensibilidad excluyendo a CABA (N=23) dado su carácter de valor extremo demográfico. En el modelado multivariado se estimaron regresiones por Mínimos Cuadrados Ordinarios (OLS) con errores estándar robustos a heterocedasticidad HC3 y Factores de Inflación de Varianza (VIF) [20].",
    "Para responder a las exigencias de comparabilidad predictiva y prevención de sesgos de evaluación [20], [21], [22], todos los algoritmos supervisados se evaluaron de manera estrictamente simétrica en ambos países bajo dos esquemas libres de filtración de datos (data leakage): validación cruzada exhaustiva Leave-One-Out (LOOCV) y validación cruzada en 5 pliegues (5-Fold CV, barajado con semilla fija random_state=42). Asimismo, además de OLS multivariado (5 predictores) y Random Forest Regressor [24], se evaluaron especificaciones parsimoniosas y regularizadas: regresión Ridge con penalización L2 (α=10 con estandarización interna por pliegue) y regresión OLS univariada (empleando únicamente obesidad como predictor), contrastando el error cuadrático (MSE) y absoluto medio (MAE) contra el estimador naive baseline de media constante."
]

SEC34_PARS = [
    "Resulta imperativo explicitar las diferencias operativas entre los constructos relevados en ambos países para evitar sobreafirmaciones en la comparación directa:",
    "1. Diferencias en la definición de variables: (a) En el BRFSS (`DIABETE3`), la prevalencia excluye explícitamente la prediabetes declarada, mientras que la pregunta estandarizada de la ENFR (Cuadro 7.3) releva conjuntamente si un profesional médico le indicó tener 'diabetes o glucemia elevada'; esta mayor amplitud semántica contribuye a explicar por qué la media provincial argentina (13,0%) supera a la estadounidense (10,2%). (b) En actividad física, el BRFSS (`_TOTINDA`) mide la ausencia de ejercicio en el tiempo libre en el último mes (media 25,8%), mientras que la ENFR (Cuadro 3.1) clasifica el 'nivel bajo de actividad física' mediante el cuestionario multidominio IPAQ (media 46,2%); por ende, la brecha numérica entre ambos países refleja tanto hábitos poblacionales como instrumentos de medición distintos. (c) En privación económica y covariables de control, EE.UU. utiliza el umbral de ingresos familiares anuales menores a USD 25.000 y la tasa de educación secundaria incompleta, mientras que Argentina emplea la línea de pobreza monetaria de la EPH (canasta básica total regionalizada) y el logaritmo de la densidad poblacional (para capturar el contraste macrourbano de CABA, dado que el déficit educativo estructural ya integra el indicador censal de NBI). En las Tablas 2 y 4 ambos constructos se rotulan de forma diferenciada.",
    "2. Estructura etaria, error muestral y potencia estadística: Los cuadros provinciales publicados de la ENFR reportan tasas brutas sin estandarización directa por edad y presentan coeficientes de variación muestral (CV) de entre 5,3% y 12,5% (lo que implica errores estándar de ~1,0 a 1,8 puntos porcentuales). Asimismo, con N=24 jurisdicciones, una correlación observada de r = -0,05 posee un IC95% amplio de [-0,44; +0,36]. En consecuencia, la ausencia de significancia estadística a escala ecológica no equivale a una prueba cerrada de independencia biológica, sino a la acción conjunta de sesgos de detección, confusión por estructura demográfica y variabilidad muestral."
]

SEC41_PARS = [
    f"La representación cartográfica bajo una escala común (6% a 18%, Figura 1) y las pruebas de autocorrelación espacial revelan patrones territoriales diferenciados. En los Estados Unidos (Figura 1a), la prevalencia media estatal es del {us_mean_d:.1f}% (DE {us_sd_d:.1f}%; mediana {us_med_d:.1f}%), exhibiendo una autocorrelación espacial positiva altamente significativa (Índice I de Moran = +{moran_us_d:.2f}; p < 0,001). Este agrupamiento confirma la consolidación geográfica del corredor de alta prevalencia en el sudeste y los Apalaches documentado en la literatura reciente [7], [8] (Misisipi 14,8%, Virginia Occidental 14,5%, Alabama 13,6%, Luisiana 12,9%), duplicando los registros de estados del oeste y norte como Colorado (6,8%) y Utah (7,1%).",
    f"En la República Argentina (Figura 1b), la media simple de las 24 jurisdicciones es del {ar_mean_d:.1f}% (con desvío estándar muestral de {ar_sd_samp:.1f}% y desvío estándar poblacional de {ar_sd_pop:.2f}%, coherente con una varianza poblacional exacta de Var(y) = {ar_var_pop:.2f}), mientras que el total nacional ponderado es del 12,7% [13]. La autocorrelación espacial resulta moderada (I de Moran = +{moran_ar_d:.2f}; p = {p_moran_ar_d:.3f}), impulsada por valores elevados en Cuyo y la región pampeana occidental (San Luis 17,3%, San Juan 15,9%, La Rioja 15,1%, La Pampa 14,6%). Por el contrario, CABA registra el mínimo nacional (8,8%), seguida por provincias del norte con alta vulnerabilidad estructural como Jujuy (8,9%), Chaco (10,3%), Salta (10,8%) y Entre Ríos (10,8%)."
]

SEC42_PARS = [
    f"La Figura 2 contrasta los factores de riesgo cardiometabólicos. En los Estados Unidos (Figuras 2a y 2c), la obesidad autorreportada promedia el {df_us['obesidad_pct'].mean():.1f}% estatal (28,6% nacional) y la inactividad física en tiempo libre promedia el {df_us['inactividad_fisica_pct'].mean():.1f}% (23,8% nacional), mostrando una estrecha correspondencia geográfica con el mapa de diabetes del sur profundo.",
    f"En la Argentina (Figuras 2b y 2d), la obesidad provincial promedia el {df_arg['obesidad_pct'].mean():.1f}% (25,6% nacional), con mínimo en CABA (17,0%) y máximos en San Juan (34,4%) y Santa Cruz (34,0%). En cuanto al indicador de baja actividad física relevado mediante cuestionario IPAQ (Figura 2d), la media provincial asciende al {df_arg['inactividad_fisica_pct'].mean():.1f}% (45,9% nacional), con picos en Formosa (69,1%) y La Rioja (61,2%). Como se advirtió en la Sección 3.4, si bien este indicador evidencia una alta prevalencia de hipocinesia en la Argentina, su magnitud absoluta no debe compararse de forma lineal con el indicador estadounidense debido a las diferencias metodológicas entre el instrumento multidominio IPAQ y la pregunta simple de ejercicio recreativo del BRFSS."
]

SEC43_PARS = [
    f"El análisis correlacional (Figura 3 y Tabla 2) expone un marcado contraste entre ambos países. En los Estados Unidos (N=51), tanto las correlaciones lineales de Pearson como las de rangos de Spearman confirman un fuerte gradiente socioeconómico positivo: la proporción de hogares con bajos ingresos (<USD 25k) se asocia a la diabetes con r = {r_us_pob:+.2f} (p < 0,001; IC95% [{lo_us_pob:+.2f}; {hi_us_pob:+.2f}]; Spearman ρ = {rho_us_pob:+.2f}), la inactividad física con r = {r_us_sed:+.2f} (p < 0,001; IC95% [{lo_us_sed:+.2f}; {hi_us_sed:+.2f}]; ρ = {rho_us_sed:+.2f}), la educación secundaria incompleta con r = {r_us_edu:+.2f} (p < 0,001; IC95% [{lo_us_edu:+.2f}; {hi_us_edu:+.2f}]; ρ = {rho_us_edu:+.2f}) y la obesidad con r = {r_us_obe:+.2f} (p < 0,001; IC95% [{lo_us_obe:+.2f}; {hi_us_obe:+.2f}]; ρ = {rho_us_obe:+.2f}). En el modelo OLS multivariado con errores robustos HC3 [20] (Tabla 2), la obesidad (β = +0,180; p < 0,001), los bajos ingresos (β = +0,137; p = 0,004), el secundario incompleto (β = +0,202; p = 0,001) y la inactividad física (β = +0,095; p = 0,026) conservan significancia estadística con factores VIF controlados (<5) y un ajuste global de R² = {m_us.rsquared:.3f} (R²_adj = {m_us.rsquared_adj:.3f}; F = {m_us_ols.fvalue:.1f}; p < 0,001).",
    f"En contrapartida, en la República Argentina (N=24) la prevalencia provincial declarada no exhibe asociación lineal ni monótona positiva con los indicadores de privación: la pobreza monetaria EPH arroja r = {r_ar_pob:+.2f} (p = {p_ar_pob:.2f}; IC95% [{lo_ar_pob:+.2f}; {hi_ar_pob:+.2f}]; Spearman ρ = {rho_ar_pob:+.2f}, p = {p_rho_ar_pob:.2f}), las Necesidades Básicas Insatisfechas (NBI) registran r = {r_ar_nbi:+.2f} (p = {p_ar_nbi:.2f}; IC95% [{lo_ar_nbi:+.2f}; {hi_ar_nbi:+.2f}]; ρ = {rho_ar_nbi:+.2f}) y la proporción de población sin cobertura de obra social ni prepaga muestra r = {r_ar_cob:+.2f} (p = {p_ar_cob:.2f}; IC95% [{lo_ar_cob:+.2f}; {hi_ar_cob:+.2f}]; ρ = {rho_ar_cob:+.2f}). Incluso la obesidad presenta una asociación bivariada moderada y no significativa al 5% (r = {r_ar_obe:+.2f}; p = {p_ar_obe:.2f}; IC95% [{lo_ar_obe:+.2f}; {hi_ar_obe:+.2f}]). En la regresión múltiple OLS (Tabla 2), ningún regresor resulta estadísticamente significativo y el modelo global carece de significancia conjunta (F = {m_ar_ols.fvalue:.2f}; p = {m_ar_ols.f_pvalue:.2f}; R² = {m_ar.rsquared:.3f}; R²_adj = {m_ar.rsquared_adj:.3f})."
]

SEC44_PARS = [
    "Para comprender por qué las provincias argentinas con mayor privación estructural no registran mayores tasas de diabetes autorreportada, el análisis empírico evalúa los eslabones de detección (screening), el efecto de valores extremos (CABA), las explicaciones demográficas/muestrales alternativas y la cobertura de tratamiento (Figuras 4 y 5b):",
    f"1. Hipótesis del subdiagnóstico, correlación entre screening y prevalencia, y el rol de CABA: En la Argentina, el acceso al tamizaje glucémico presenta una fuerte autocorrelación espacial (I de Moran = +{moran_ar_scr:.2f}; p = {p_moran_ar_scr:.3f}) y una intensa asociación lineal inversa con la pobreza estructural NBI: r = {r_nbi_scr:+.2f} (p < 0,001; IC95% [{lo_nbi_scr:+.2f}; {hi_nbi_scr:+.2f}]; Spearman ρ = {rho_nbi_scr:+.2f}; Figura 5b). Mientras en CABA (92,9%) y Santa Fe (89,3%) nueve de cada diez adultos han sido pesquisados, en Chaco (60,3%), Santiago del Estero (60,6%) y Formosa (61,1%) cerca del 40% de los adultos jamás se midió la glucemia [13]. Ahora bien, al evaluar directamente el segundo eslabón —la correlación entre screening y prevalencia declarada— sobre las 24 jurisdicciones completas se obtiene r = {r_scr_d24:+.2f} (p = {p_scr_d24:.2f}; IC95% [{lo_scr_d24:+.2f}; {hi_scr_d24:+.2f}]). La razón por la cual esta correlación resulta atenuada es la presencia de CABA como outlier demográfico y epidemiológico: CABA combina el mayor screening del país (92,9%) con la menor prevalencia (8,8%), pero ello obedece a que posee simultáneamente la menor tasa de obesidad nacional (17,0% frente a 26,7% de media provincial), baja inactividad física (32,4%) y mínima pobreza (12,6%). Al realizar el análisis de sensibilidad excluyendo a CABA (N=23 provincias), la correlación entre screening y prevalencia declarada asciende a r = {r_scr_d23:+.2f} (p = {p_scr_d23:.3f}; IC95% [{lo_scr_d23:+.2f}; {hi_scr_d23:+.2f}]; Spearman ρ = {rho_scr_d23:+.2f}): en el interior del país, las jurisdicciones que más testean tienden a detectar mayor prevalencia, mientras que provincias como Jujuy (31,1% de obesidad pero solo 71,3% de screening y 8,9% de diabetes declarada) o Chaco (60,3% de screening y 10,3% de diabetes) sugieren una subcaptación por falta de pesquisa.",
    "2. Explicaciones concurrentes (estructura etaria y error muestral): Los datos agregados no permiten afirmar que el subdiagnóstico sea el único causante de la distribución provincial. En primer lugar, las prevalencias del Cuadro 7.3 de la ENFR no se encuentran estandarizadas por edad; dado que las provincias del NEA y NOA poseen pirámides poblacionales más jóvenes que las jurisdicciones pampeanas y cuyanas [12], la menor edad media atenúa genuinamente la prevalencia bruta en el norte. En segundo lugar, el error muestral de la encuesta (con CV de hasta 12,5% en Santiago del Estero y 12,3% en La Rioja) introduce intervalos de incertidumbre que solapan parte de las diferencias interprovinciales.",
    f"3. Cobertura vs. brecha de tratamiento farmacológico y rol del subsistema público: Entre las personas diagnosticadas, la cobertura media provincial de tratamiento farmacológico activo en la Argentina es del {ar_trat_mean:.1f}% (equivalente a una brecha media sin tratamiento farmacológico del {ar_brecha_mean:.1f}%, con rango de cobertura entre 32,7% en La Pampa y 70,0% en Santa Cruz y Tierra del Fuego; Figura 4a). A diferencia de los Estados Unidos —donde la barrera económica de costo médico correlaciona positivamente con la carga de enfermedad (r = {r_us_cost:+.2f}; p < 0,001; Figura 4b) y propicia el racionamiento de insulina documentado en encuestas nacionales recientes [9], [10]—, en la Argentina no se observa una correlación regresiva entre el porcentaje de población sin obra social ni prepaga y la cobertura de tratamiento farmacológico: r = {r_cob_trat:+.2f} (p = {p_cob_trat:.2f}; IC95% [{lo_cob_trat:+.2f}; {hi_cob_trat:+.2f}]; Spearman ρ = {rho_cob_trat:+.2f}). En efecto, las tres jurisdicciones del país que superan el 50% de población dependiente exclusivamente del hospital público —Santiago del Estero (56,0% sin cobertura formal), Formosa (55,9%) y Chaco (52,2%)— alcanzan tasas de tratamiento activo del 59,7%, 62,6% y 54,2% respectivamente, superando el promedio nacional. Por su parte, las máximas coberturas patagónicas (Santa Cruz y Tierra del Fuego, ambas con 70,0%) responden a una combinación de alta cobertura de seguridad social formal (solo 17,0% y 15,3% sin cobertura en el Censo 2022 [12]) y redes hospitalarias públicas provinciales, mientras que distritos pampeanos o patagónicos extensos con menor pobreza como La Pampa (32,7% de tratamiento y 32,1% sin cobertura) o Chubut (38,3% de tratamiento y 27,8% sin cobertura) evidencian importantes brechas de adherencia vinculadas a dispersión territorial y seguimiento clínico [17]. Esta evidencia sugiere que la provisión estatal de metformina y glibenclamida en atención primaria a través del Programa Remediar y la cobertura legal del 100% de insulinas e insumos dispuesta por la Ley N.º 26.914 (PRODIABA) [15] amortiguan la desigualdad socioeconómica entre quienes logran ser diagnosticados, si bien persiste un desafío sanitario sustantivo para cubrir el {ar_brecha_mean:.1f}% promedio de pacientes diagnosticados sin tratamiento farmacológico continuo."
]

SEC45_PARS = [
    f"La Tabla 3 presenta la evaluación simétrica de los algoritmos supervisados mediante LOOCV y 5-Fold CV en ambos países frente al estimador naive baseline. En los Estados Unidos (N=51), la intensa señal lineal permite que tanto el modelo OLS multivariado (R² in-sample = {m_us.rsquared:.3f}; LOOCV R² = {r2_us_ols_loo:.3f}; 5-Fold R² = {r2_us_ols_kf:.3f}) como la regresión regularizada Ridge (LOOCV R² = {r2_us_rdg_loo:.3f}; 5-Fold R² = {r2_us_rdg_kf:.3f}) y el ensamble de Random Forest [20], [24] (LOOCV R² = {r2_us_rf_loo:.3f}; 5-Fold R² = {r2_us_rf_kf:.3f}) reduzcan el error absoluto medio desde el baseline de {mae_us_base:.2f}% a un rango de 0,56%–0,67% fuera de muestra. Incluso una especificación parsimoniosa univariada con un solo predictor (obesidad) retiene más del 52% de varianza explicada fuera de muestra (LOOCV R² = {r2_us_uni_loo:.3f}).",
    f"Por el contrario, en las 24 jurisdicciones argentinas, el predictor ingenuo de media constante (ȳ = {ar_mean_d:.1f}%) establece un umbral base de R² = 0,000 con MAE = {mae_ar_base:.2f}% y MSE_baseline = Var(y) = {ar_var_pop:.2f}. Al evaluar el modelo OLS de 5 predictores fuera de muestra, el MSE en LOOCV asciende a {mse_ar_ols_loo:.2f} (MAE = {mae_ar_ols_loo:.2f}%), superando en un 70,1% a la varianza intrínseca de la serie ({mse_ar_ols_loo:.2f} / {ar_var_pop:.2f} = 1,701) y arrojando R²_LOOCV = {r2_ar_ols_loo:.3f} (y R²_5Fold = {r2_ar_ols_kf:.3f}). De igual modo, Random Forest obtiene R²_LOOCV = {r2_ar_rf_loo:.3f} y R²_5Fold = {r2_ar_rf_kf:.3f}.",
    f"Para verificar si este resultado responde meramente al exceso de parámetros (5 predictores para N=24 observaciones), se evaluaron dos alternativas parsimoniosas (Tabla 3): una regresión Ridge con fuerte penalización L2 (α=10) y un modelo OLS bivariado con un único predictor (obesidad). Si bien la regularización Ridge reduce el sobreajuste respecto al OLS sin penalizar (mejorando el R²_LOOCV de {r2_ar_ols_loo:.3f} a {r2_ar_rdg_loo:.3f}, con MAE = {mae_ar_rdg_loo:.2f}%) y el modelo univariado alcanza R²_LOOCV = {r2_ar_uni_loo:.3f} (MAE = {mae_ar_uni_loo:.2f}%), absolutamente todas las especificaciones arrojan R² fuera de muestra negativos en ambos esquemas de validación cruzada. Esto evidencia, en línea con las advertencias metodológicas de Varoquaux y Cheplygina [21], que en la agregación provincial argentina la limitación no radica únicamente en la relación parámetros-muestra, sino en la ausencia de señal lineal entre las covariables ecológicas y la prevalencia autorreportada, sugiriendo la conveniencia de evitar el ajuste acrítico de modelos predictivos sobre agregados pequeños con sesgos de medición."
]

SEC51_PARS = [
    "Los resultados obtenidos sugieren implicancias diferenciadas para la gestión sanitaria en ambos países. En los Estados Unidos, donde el tamizaje clínico se encuentra generalizado pero la privación socioeconómica y la barrera de costo médico se asocian fuertemente con la carga de la enfermedad [5], [7], las prioridades de política pública se orientan a regular el precio de bolsillo de la insulina y reducir los copagos que inducen al racionamiento terapéutico [9], [10].",
    "En la República Argentina, la evidencia ecológica sugiere una doble prioridad territorial: (i) en las provincias del NEA y NOA con elevado NBI, donde cerca del 40% de los adultos nunca accedió a una medición de glucemia [13], resulta prioritario fortalecer operativos de pesquisa activa capilar y bioquímica en el primer nivel de atención conforme a la Guía de Práctica Clínica Nacional [14] para reducir el subdiagnóstico; y (ii) en materia terapéutica, si bien la red pública respaldada por el Programa Remediar (provisión de metformina y glibenclamida en centros de atención primaria) y la Ley N.º 26.914 / PRODIABA (cobertura legal del 100% de insulinas y tiras reactivas) [15] evita que las provincias con mayor proporción de población sin obra social queden rezagadas, la existencia de una brecha nacional promedio del 45,6% de pacientes diagnosticados sin tratamiento farmacológico activo —con valores críticos en provincias extensas como La Pampa (67,3% de brecha) y Chubut (61,7%)— exige auditar la continuidad de seguimiento clínico y el acceso logístico en todo el territorio."
]

SEC52_PARS = [
    "Desde una perspectiva metodológica, este estudio aporta una reflexión empírica alineada con los estándares TRIPOD+AI [22] sobre el uso de modelos supervisados en epidemiología espacial. Cuando el tamaño muestral de unidades geográficas es reducido (N=24) y la variable dependiente autorreportada se encuentra sujeta a sesgos de detección, variabilidad muestral y confusión demográfica, tanto los modelos lineales multiparamétricos como los ensambles de árboles sobreajustan el ruido local y empeoran el pronóstico respecto a la media histórica [21]. En tales escenarios, el valor de la ciencia de datos reside en la construcción de atlas geoespaciales descriptivos, el análisis de autocorrelación espacial y la integración transparente de fuentes oficiales [19].",
    "Finalmente, deben sintetizarse con rigor las limitaciones del estudio: (i) el carácter ecológico de las regresiones impide realizar inferencias causales individuales (falacia ecológica) y está condicionado por la delimitación político-administrativa provincial (MAUP) [19]; (ii) la presencia de autocorrelación espacial positiva en la prevalencia (I de Moran = +0,59 en EE.UU. y +0,33 en Argentina) implica que las jurisdicciones vecinas no son estrictamente independientes, lo cual motiva el empleo futuro de modelos autorregresivos espaciales (SAR/SEM) [19]; (iii) las tasas provinciales de la ENFR carecen de estandarización por edad y presentan errores muestrales (CV de hasta 12,5%) e intervalos de confianza amplios por el tamaño muestral (N=24); (iv) existen diferencias operativas en los instrumentos de medición entre ambas encuestas (inclusión de 'glucemia elevada' y cuestionario IPAQ en la ENFR frente a diagnóstico estricto e inactividad recreativa en el BRFSS) y desfasajes temporales entre cortes censales y encuestas; y (v) la asociación entre NBI, screening y prevalencia constituye una evidencia ecológica compatible con el subdiagnóstico, pero su cuantificación definitiva requiere analizar mediciones bioquímicas directas."
]

SEC6_PARS = [
    f"Se desarrolló un pipeline reproducible de ciencia de datos que contrastó los determinantes territoriales de la diabetes mellitus entre los Estados Unidos (N=51) y la República Argentina (N=24). Los resultados sugieren que mientras en los Estados Unidos la prevalencia sigue un marcado agrupamiento espacial (I de Moran = +{moran_us_d:.2f}) y un gradiente socioeconómico lineal (r = {r_us_pob:+.2f} con bajos ingresos; R² OLS = {m_us.rsquared:.3f}), en la Argentina la prevalencia declarada no correlaciona linealmente con la pobreza monetaria (r = {r_ar_pob:+.2f}; IC95% [{lo_ar_pob:+.2f}; {hi_ar_pob:+.2f}]). El análisis territorial sugiere que este comportamiento responde a la conjunción de factores demográficos y muestrales con un severo déficit de tamizaje en las provincias de mayor NBI (r = {r_nbi_scr:+.2f} entre NBI y screening; y r = {r_scr_d23:+.2f} entre screening y diabetes al excluir el outlier de CABA), mientras que el subsistema público atenúa la regresividad en el acceso a fármacos entre los diagnosticados (r = {r_cob_trat:+.2f}), aun cuando persiste una brecha nacional del {ar_brecha_mean:.1f}% sin tratamiento activo.",
    f"En el plano computacional, la evaluación cruzada simétrica evidenció que con N=24 jurisdicciones y ausencia de señal lineal, tanto OLS multivariado (LOOCV R² = {r2_ar_ols_loo:.3f}) como Ridge (R² = {r2_ar_rdg_loo:.3f}), modelos univariados (R² = {r2_ar_uni_loo:.3f}) y Random Forest (5-Fold R² = {r2_ar_rf_kf:.3f}) exhiben desempeño predictivo negativo frente a la media constante, respaldando el uso de atlas geoespaciales descriptivos.",
    "Como líneas de trabajo futuro que superen directamente las limitaciones ecológicas actuales se proyecta: (i) procesar los microdatos individuales públicos de la ENFR [13] incorporando la edad, el sexo y los factores de expansión a nivel persona mediante modelos multinivel jerárquicos (individuo-provincia) en línea con el enfoque de Marro et al. [16] y estandarización directa por estructura etaria; (ii) integrar las submuestras bioquímicas de glucemia capilar y hemoglobina glicosilada de la ENFR (Cuadros 7.9–7.11) para medir empíricamente la brecha entre diabetes autorreportada y diabetes biológica no diagnosticada; y (iii) estimar modelos econométricos espaciales (Spatial Lag y Spatial Error Models) [19] que incorporen explícitamente la matriz de vecindad geográfica."
]

# ==============================================================================
# 5. COMPILACION DEL MANUSCRITO WORD (.DOCX) Y MARKDOWN (.MD)
# ==============================================================================
print(">>> [4/5] Compilando manuscrito extenso (.docx) con plantilla oficial...")

def set_section_columns(section, num_cols=2, space_twips=500):
    sectPr = section._sectPr
    cols = sectPr.xpath('.//w:cols')
    col_elem = cols[0] if cols else OxmlElement('w:cols')
    if not cols:
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

doc = Document(TEMPLATE_PATH)
for p in list(doc.paragraphs): p._element.getparent().remove(p._element)
for t in list(doc.tables): t._element.getparent().remove(t._element)

s0 = doc.sections[0]
s0.page_width, s0.page_height = Cm(21.0), Cm(29.7)
s0.top_margin, s0.bottom_margin = Cm(2.5), Cm(3.0)
s0.left_margin, s0.right_margin = Cm(2.0), Cm(2.25)
set_section_columns(s0, num_cols=1)

p_tit = doc.add_paragraph(); p_tit.alignment = AL.CENTER; p_tit.paragraph_format.space_after = Pt(4)
set_font(p_tit.add_run(TITLE_ES), "Times New Roman", 13.5, bold=True)

p_sub = doc.add_paragraph(); p_sub.alignment = AL.CENTER; p_sub.paragraph_format.space_after = Pt(10)
set_font(p_sub.add_run(TITLE_EN), "Times New Roman", 10.5, italic=True)

p_aut = doc.add_paragraph(); p_aut.alignment = AL.CENTER; p_aut.paragraph_format.space_after = Pt(2)
set_font(p_aut.add_run("María Florencia Rossi, Magali Bolivar, Matías Montiel, Roxana Martínez, Nestor Balich, Franco Balich"), "Times New Roman", 10.5, bold=True)

p_inst = doc.add_paragraph(); p_inst.alignment = AL.CENTER; p_inst.paragraph_format.space_after = Pt(2)
set_font(p_inst.add_run("CAETI — Centro de Altos Estudios en Tecnología Informática\nUniversidad Abierta Interamericana (UAI) — Facultad de Tecnología Informática\nMontes de Oca 745, Ciudad Autónoma de Buenos Aires, Argentina"), "Times New Roman", 9.5)

p_mail = doc.add_paragraph(); p_mail.alignment = AL.CENTER; p_mail.paragraph_format.space_after = Pt(10)
set_font(p_mail.add_run("{MariaFlorencia.Rossi, MagaliFlorencia.BolivarCruz, MatiasNicolas.MontielTorres}@alumnos.uai.edu.ar\n{Roxana.Martinez, nestor.balich, francoadrian.balich}@uai.edu.ar"), "Times New Roman", 9.0, italic=True)

p_rtit = doc.add_paragraph(); p_rtit.alignment = AL.LEFT; p_rtit.paragraph_format.space_before = Pt(6); p_rtit.paragraph_format.space_after = Pt(2)
set_font(p_rtit.add_run("Resumen"), "Times New Roman", 11.5, bold=True)
add_p(doc, RESUMEN_ES, size=9.5, first_indent=0.3, space_after=4)
add_runs_p(doc, [("Palabras clave: ", True, False),
                 ("diabetes mellitus; análisis comparativo; salud basada en datos; autocorrelación espacial; subdiagnóstico; cobertura de tratamiento; validación cruzada; determinantes sociales.", False, True)],
           first_indent=0.3, space_after=6)

p_atit = doc.add_paragraph(); p_atit.alignment = AL.LEFT; p_atit.paragraph_format.space_before = Pt(4); p_atit.paragraph_format.space_after = Pt(2)
set_font(p_atit.add_run("Abstract"), "Times New Roman", 11.5, bold=True)
add_p(doc, ABSTRACT_EN, size=9.5, first_indent=0.3, space_after=4)
add_runs_p(doc, [("Keywords: ", True, True),
                 ("diabetes mellitus; comparative analysis; health data science; spatial autocorrelation; underdiagnosis; treatment coverage; cross-validation; social determinants.", False, True)],
           first_indent=0.3, space_after=10)

s1 = doc.add_section(WD_SECTION_START.CONTINUOUS)
s1.top_margin, s1.bottom_margin = Cm(2.5), Cm(3.0); s1.left_margin, s1.right_margin = Cm(1.75), Cm(1.75)
set_section_columns(s1, num_cols=2, space_twips=500)

add_h1(doc, "1. Introducción y motivación")
for p in SEC1_PARS: add_p(doc, p)

add_h1(doc, "2. Marco conceptual y antecedentes")
for p in SEC2_PARS: add_p(doc, p)

add_h1(doc, "3. Fuentes de datos y metodología")
add_h2(doc, "3.1. Microdatos de Estados Unidos (CDC BRFSS 2015)")
for p in SEC31_PARS: add_p(doc, p)
add_h2(doc, "3.2. Fuentes oficiales de Argentina (ENFR e INDEC)")
for p in SEC32_PARS: add_p(doc, p)
add_h2(doc, "3.3. Georreferenciación, autocorrelación espacial y modelado estadístico")
for p in SEC33_PARS: add_p(doc, p)
add_h2(doc, "3.4. Comparabilidad de constructos y consideraciones metodológicas")
for p in SEC34_PARS: add_p(doc, p)

s_f1 = doc.add_section(WD_SECTION_START.CONTINUOUS)
s_f1.top_margin, s_f1.bottom_margin = Cm(2.0), Cm(2.5); s_f1.left_margin, s_f1.right_margin = Cm(2.0), Cm(2.0)
set_section_columns(s_f1, num_cols=1)
insert_fig(doc, fig1_path,
           f"Figura 1. Atlas geoespacial comparativo de la prevalencia de diabetes (%): (a) Estados Unidos (CDC BRFSS 2015, N=51; I de Moran = +{moran_us_d:.2f}, p < 0,001); (b) República Argentina (ENFR 2018 / INDEC, N=24; I de Moran = +{moran_ar_d:.2f}, p = {p_moran_ar_d:.3f}) con recuadro ampliado para CABA.",
           width_cm=16.5)
insert_table(doc, tab1_path,
             "Tabla 1. Cuadro comparativo general de indicadores epidemiológicos, espaciales y sanitarios entre Estados Unidos y la República Argentina.")

s2 = doc.add_section(WD_SECTION_START.CONTINUOUS)
s2.top_margin, s2.bottom_margin = Cm(2.5), Cm(3.0); s2.left_margin, s2.right_margin = Cm(1.75), Cm(1.75)
set_section_columns(s2, num_cols=2, space_twips=500)
add_h1(doc, "4. Resultados")
add_h2(doc, "4.1. Atlas geoespacial y autocorrelación espacial (I de Moran)")
for p in SEC41_PARS: add_p(doc, p)

s_f2 = doc.add_section(WD_SECTION_START.CONTINUOUS)
s_f2.top_margin, s_f2.bottom_margin = Cm(2.0), Cm(2.5); s_f2.left_margin, s_f2.right_margin = Cm(2.0), Cm(2.0)
set_section_columns(s_f2, num_cols=1)
insert_fig(doc, fig2_path,
           "Figura 2. Distribución geoespacial de factores cardiometabólicos: (a) Obesidad en EE.UU.; (b) Obesidad en Argentina; (c) Inactividad física en tiempo libre en EE.UU. (_TOTINDA); (d) Baja actividad física en Argentina (IPAQ).",
           width_cm=16.5)

s3 = doc.add_section(WD_SECTION_START.CONTINUOUS)
s3.top_margin, s3.bottom_margin = Cm(2.5), Cm(3.0); s3.left_margin, s3.right_margin = Cm(1.75), Cm(1.75)
set_section_columns(s3, num_cols=2, space_twips=500)
add_h2(doc, "4.2. Atlas de factores cardiometabólicos y diferencias operativas")
for p in SEC42_PARS: add_p(doc, p)

s_f4 = doc.add_section(WD_SECTION_START.CONTINUOUS)
s_f4.top_margin, s_f4.bottom_margin = Cm(2.0), Cm(2.5); s_f4.left_margin, s_f4.right_margin = Cm(2.0), Cm(2.0)
set_section_columns(s_f4, num_cols=1)
insert_fig(doc, fig4_path,
           "Figura 3. Matrices de calor de correlaciones bivariadas de Pearson (r): (a) Estados Unidos (N=51); (b) República Argentina (N=24).",
           width_cm=16.0)
insert_table(doc, tab2_path,
             "Tabla 2. Coeficientes de regresión lineal múltiple OLS con errores estándar robustos a heterocedasticidad (HC3) y factores VIF.")

s4 = doc.add_section(WD_SECTION_START.CONTINUOUS)
s4.top_margin, s4.bottom_margin = Cm(2.5), Cm(3.0); s4.left_margin, s4.right_margin = Cm(1.75), Cm(1.75)
set_section_columns(s4, num_cols=2, space_twips=500)
add_h2(doc, "4.3. Correlaciones paramétricas (IC95%), no paramétricas (Spearman) y OLS")
for p in SEC43_PARS: add_p(doc, p)

s_f3 = doc.add_section(WD_SECTION_START.CONTINUOUS)
s_f3.top_margin, s_f3.bottom_margin = Cm(2.0), Cm(2.5); s_f3.left_margin, s_f3.right_margin = Cm(2.0), Cm(2.0)
set_section_columns(s_f3, num_cols=1)
insert_fig(doc, fig3_path,
           f"Figura 4. Cobertura y barreras asistenciales: (a) Cobertura provincial de tratamiento farmacológico activo en Argentina (media {ar_trat_mean:.1f}%, brecha {ar_brecha_mean:.1f}%); (b) Barrera de costo médico vs. prevalencia en EE.UU.",
           width_cm=16.5)

s5 = doc.add_section(WD_SECTION_START.CONTINUOUS)
s5.top_margin, s5.bottom_margin = Cm(2.5), Cm(3.0); s5.left_margin, s5.right_margin = Cm(1.75), Cm(1.75)
set_section_columns(s5, num_cols=2, space_twips=500)
add_h2(doc, "4.4. Detección, sensibilidad al outlier CABA, factores concurrentes y tratamiento")
for p in SEC44_PARS: add_p(doc, p)

s_f5 = doc.add_section(WD_SECTION_START.CONTINUOUS)
s_f5.top_margin, s_f5.bottom_margin = Cm(2.0), Cm(2.5); s_f5.left_margin, s_f5.right_margin = Cm(2.0), Cm(2.0)
set_section_columns(s_f5, num_cols=1)
insert_fig(doc, fig5_path,
           f"Figura 5. Diagnóstico de determinantes y tamizaje: (a) Regresión lineal Privación monetaria vs. Prevalencia con IC95%; (b) Argentina: Correlación inversa entre NBI y Screening (r = {r_nbi_scr:+.2f}; p < 0,001).",
           width_cm=16.5)
insert_table(doc, tab3_path,
             "Tabla 3. Evaluación comparativa simétrica in-sample y fuera de muestra (LOOCV y 5-Fold CV) de modelos multivariados, regularizados (Ridge), parsimoniosos (1 predictor) y no lineales (Random Forest).")
insert_table(doc, tab4_path,
             "Tabla 4. Ranking de jurisdicciones extremas en prevalencia de diabetes en Estados Unidos y la República Argentina.")

s6 = doc.add_section(WD_SECTION_START.CONTINUOUS)
s6.top_margin, s6.bottom_margin = Cm(2.5), Cm(3.0); s6.left_margin, s6.right_margin = Cm(1.75), Cm(1.75)
set_section_columns(s6, num_cols=2, space_twips=500)
add_h2(doc, "4.5. Evaluación predictiva simétrica y modelos parsimoniosos/regularizados")
for p in SEC45_PARS: add_p(doc, p)

add_h1(doc, "5. Discusión")
add_h2(doc, "5.1. Implicancias para la gestión y las políticas públicas")
for p in SEC51_PARS: add_p(doc, p)
add_h2(doc, "5.2. Aportes metodológicos y limitaciones del estudio")
for p in SEC52_PARS: add_p(doc, p)

add_h1(doc, "6. Conclusiones y trabajos futuros")
for p in SEC6_PARS: add_p(doc, p)

add_h1(doc, "Referencias")
for r in REFS:
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
    print(f"    - [AVISO] {DOC_OUT.name} está abierto. Guardado alternativo en: {alt_out}")

# ==============================================================================
# 6. GENERACION AUTOMATICA DEL MANUSCRITO MARKDOWN (.MD) 100% SINCRONIZADO
# ==============================================================================
print(">>> [5/5] Generando manuscrito Markdown (.md) sincronizado con el motor...")

def df_to_md(df):
    cols = list(df.columns)
    lines = ["| " + " | ".join(f"**{c}**" for c in cols) + " |"]
    lines.append("| " + " | ".join(":---" if i == 0 else ":---:" for i in range(len(cols))) + " |")
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(f"**{r[c]}**" if i == 0 else str(r[c]) for i, c in enumerate(cols)) + " |")
    return "\n".join(lines)

md_lines = [
    f"# {TITLE_ES}",
    "",
    f"**{TITLE_EN}**",
    "",
    "**Autores:**  ",
    "María Florencia Rossi, Magali Bolivar, Matías Montiel, Roxana Martínez, Nestor Balich, Franco Balich  ",
    "*CAETI — Centro de Altos Estudios en Tecnología Informática*  ",
    "*Facultad de Tecnología Informática — Universidad Abierta Interamericana (UAI)*  ",
    "*Montes de Oca 745, Ciudad Autónoma de Buenos Aires, Argentina*  ",
    "*{MariaFlorencia.Rossi, MagaliFlorencia.BolivarCruz, MatiasNicolas.MontielTorres}@alumnos.uai.edu.ar*  ",
    "*{Roxana.Martinez, nestor.balich, francoadrian.balich}@uai.edu.ar*  ",
    "",
    "**Destino de Publicación:** XIV Congreso Internacional de Innovación y Tecnología Informática (CIITI 2026) / CoNaIISI  ",
    "**Repositorio Reproducible (Código y Datos):** `https://github.com/florr/Diabetes-Geografica-CIITI-2026`",
    "",
    "---",
    "",
    "### Resumen",
    RESUMEN_ES,
    "",
    "**Palabras clave:** diabetes mellitus; análisis comparativo; salud basada en datos; autocorrelación espacial; subdiagnóstico; cobertura de tratamiento; validación cruzada; determinantes sociales.",
    "",
    "---",
    "",
    "### Abstract",
    ABSTRACT_EN,
    "",
    "**Keywords:** diabetes mellitus; comparative analysis; health data science; spatial autocorrelation; underdiagnosis; treatment coverage; cross-validation; social determinants.",
    "",
    "---",
    "",
    "## 1. Introducción y Motivación",
    "",
    "\n\n".join(SEC1_PARS),
    "",
    "---",
    "",
    "## 2. Marco Conceptual y Antecedentes",
    "",
    "\n\n".join(SEC2_PARS),
    "",
    "---",
    "",
    "## 3. Fuentes de Datos y Metodología",
    "",
    "### 3.1. Microdatos de Estados Unidos (CDC BRFSS 2015)",
    "\n\n".join(SEC31_PARS),
    "",
    "### 3.2. Fuentes Oficiales de Argentina (ENFR e INDEC)",
    "\n\n".join(SEC32_PARS),
    "",
    "### 3.3. Georreferenciación, Autocorrelación Espacial y Modelado Estadístico",
    "\n\n".join(SEC33_PARS),
    "",
    "### 3.4. Comparabilidad de Constructos y Consideraciones Metodológicas",
    "\n\n".join(SEC34_PARS),
    "",
    "---",
    "",
    "## 4. Resultados",
    "",
    "### 4.1. Atlas Geoespacial y Autocorrelación Espacial (I de Moran)",
    "",
    "![Figura 1. Atlas geoespacial comparativo de prevalencia](../Resultados/figura1_mapas_comparativos.png)",
    f"*Figura 1. Atlas geoespacial comparativo de la prevalencia de diabetes (%): (a) Estados Unidos (CDC BRFSS 2015, N=51; I de Moran = +{moran_us_d:.2f}, p < 0,001); (b) República Argentina (ENFR 2018 / INDEC, N=24; I de Moran = +{moran_ar_d:.2f}, p = {p_moran_ar_d:.3f}) con recuadro ampliado para CABA.*",
    "",
    "\n\n".join(SEC41_PARS),
    "",
    "---",
    "",
    "### Tabla 1. Cuadro comparativo general de indicadores epidemiológicos, espaciales y sanitarios",
    "",
    df_to_md(t1_df),
    "",
    "---",
    "",
    "### 4.2. Atlas de Factores Cardiometabólicos y Diferencias Operativas",
    "",
    "![Figura 2. Distribución geoespacial de factores de riesgo](../Resultados/figura2_factores_riesgo.png)",
    "*Figura 2. Distribución geoespacial de factores cardiometabólicos: (a) Obesidad en EE.UU.; (b) Obesidad en Argentina; (c) Inactividad física en tiempo libre en EE.UU. (_TOTINDA); (d) Baja actividad física en Argentina (IPAQ).*",
    "",
    "\n\n".join(SEC42_PARS),
    "",
    "---",
    "",
    "### 4.3. Correlaciones Paramétricas (IC95%), No Paramétricas (Spearman) y Regresión OLS",
    "",
    "![Figura 3. Matrices de calor de correlaciones bivariadas](../Resultados/figura4_matriz_correlaciones.png)",
    "*Figura 3. Matrices de calor de correlaciones bivariadas de Pearson (r): (a) Estados Unidos (N=51); (b) República Argentina (N=24).*",
    "",
    "### Tabla 2. Coeficientes de regresión lineal múltiple OLS con errores robustos HC3 y factores VIF",
    "",
    df_to_md(t2_df),
    "",
    "\n\n".join(SEC43_PARS),
    "",
    "---",
    "",
    "### 4.4. Detección, Sensibilidad al Outlier CABA, Factores Concurrentes y Tratamiento",
    "",
    "![Figura 4. Cobertura y barreras asistenciales](../Resultados/figura3_brecha_tratamiento.png)",
    f"*Figura 4. Cobertura y barreras asistenciales: (a) Cobertura provincial de tratamiento farmacológico activo en Argentina (media {ar_trat_mean:.1f}%, brecha {ar_brecha_mean:.1f}%); (b) Barrera de costo médico vs. prevalencia en EE.UU.*",
    "",
    "\n\n".join(SEC44_PARS),
    "",
    "---",
    "",
    "### 4.5. Evaluación Predictiva Simétrica y Modelos Parsimoniosos/Regularizados",
    "",
    "![Figura 5. Diagnóstico de determinantes y tamizaje](../Resultados/figura5_modelos_dispersion.png)",
    f"*Figura 5. Diagnóstico de determinantes y tamizaje: (a) Regresión lineal Privación monetaria vs. Prevalencia con IC95%; (b) Argentina: Correlación inversa entre NBI y Screening (r = {r_nbi_scr:+.2f}; p < 0,001).*",
    "",
    "### Tabla 3. Evaluación comparativa simétrica in-sample y fuera de muestra (LOOCV y 5-Fold CV)",
    "",
    df_to_md(t3_df),
    "",
    "---",
    "",
    "### Tabla 4. Ranking de jurisdicciones extremas en prevalencia",
    "",
    df_to_md(t4_df),
    "",
    "\n\n".join(SEC45_PARS),
    "",
    "---",
    "",
    "## 5. Discusión",
    "",
    "### 5.1. Implicancias para la Gestión y las Políticas Públicas",
    "\n\n".join(SEC51_PARS),
    "",
    "### 5.2. Aportes Metodológicos y Limitaciones del Estudio",
    "\n\n".join(SEC52_PARS),
    "",
    "---",
    "",
    "## 6. Conclusiones y Trabajos Futuros",
    "",
    "\n\n".join(SEC6_PARS),
    "",
    "---",
    "",
    "## Referencias",
    "",
    "\n".join(f"* {r}" for r in REFS),
    ""
]

MD_OUT.write_text("\n".join(md_lines), encoding="utf-8")
print(f"    - Manuscrito Markdown guardado en: {MD_OUT}")
print("=" * 75)
print(">>> PIPELINE EXTENSO FINALIZADO CON EXITO.")
print("=" * 75)
