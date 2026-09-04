# -*- coding: utf-8 -*-
"""
03 - Pipeline de analisis sobre DATOS REALES.

PARTE A - Estados de EE.UU. (BRFSS 2015): correlacion -> OLS -> Random Forest (CV)
          -> PCA/K-Means -> mapas coropleticos.
PARTE B - Paises del mundo (incluye Argentina): correlacion -> OLS -> mapa mundial
          -> dispersion prevalencia vs PBI.

Entradas: data/processed/*.csv, geo/*.geojson
Salidas:  figures/*.png, tables/*.csv
"""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np, pandas as pd, geopandas as gpd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from statsmodels.stats.outliers_influence import variance_inflation_factor

ROOT = Path(__file__).resolve().parent.parent
DATA, GEO = ROOT / "data" / "processed", ROOT / "geo"
FIG, TAB = ROOT / "figures", ROOT / "tables"
FIG.mkdir(exist_ok=True); TAB.mkdir(exist_ok=True)
plt.rcParams.update({"figure.dpi":150,"font.size":10,"axes.titlesize":12,"axes.titleweight":"bold"})

# ======================= PARTE A - ESTADOS DE EE.UU. =======================
FEATURES = ["indice_ruralidad","sin_cobertura_salud_pct","secundario_incompleto_pct",
            "barrera_costo_medico_pct","obesidad_pct","inactividad_fisica_pct","pobreza_ingresos_pct"]
TARGET = "tasa_diabetes_pct"
LAB = {"indice_ruralidad":"Indice de ruralidad (no-MSA)","sin_cobertura_salud_pct":"Sin cobertura de salud (%)",
 "secundario_incompleto_pct":"Secundario incompleto (%)","barrera_costo_medico_pct":"Barrera economica al medico (%)",
 "obesidad_pct":"Obesidad (%)","inactividad_fisica_pct":"Inactividad fisica (%)",
 "pobreza_ingresos_pct":"Ingresos bajos <$20k (%)","tasa_diabetes_pct":"Prevalencia de diabetes (%)"}

df = pd.read_csv(DATA/"brfss2015_estados.csv")
gdf = gpd.read_file(GEO/"us_states.geojson").rename(columns={"name":"estado"}).merge(df, on="estado", how="inner")
print(f"[US] estados con geometria y datos: {len(gdf)}/{len(df)}")

corr = df[[TARGET]+FEATURES].corr().round(2).rename(index=LAB, columns=LAB)
corr.to_csv(TAB/"us_tabla1_correlacion.csv", encoding="utf-8")
fig, ax = plt.subplots(figsize=(8,6.5)); im=ax.imshow(corr.values,cmap="RdBu_r",vmin=-1,vmax=1)
ax.set_xticks(range(len(corr.columns))); ax.set_yticks(range(len(corr.index)))
ax.set_xticklabels(corr.columns,rotation=45,ha="right"); ax.set_yticklabels(corr.index)
for i in range(len(corr.index)):
    for j in range(len(corr.columns)):
        ax.text(j,i,f"{corr.values[i,j]:.2f}",ha="center",va="center",fontsize=8,
                color="white" if abs(corr.values[i,j])>0.5 else "black")
fig.colorbar(im,ax=ax,shrink=0.8,label="Coeficiente de Pearson")
ax.set_title("Correlación entre prevalencia de diabetes y\ndeterminantes territoriales — estados de EE.UU. (BRFSS 2015)")
fig.tight_layout(); fig.savefig(FIG/"us_tabla1_correlacion.png",bbox_inches="tight"); plt.close(fig)

X=df[FEATURES].values; y=df[TARGET].values; Xs=StandardScaler().fit_transform(X)
Xc=sm.add_constant(df[FEATURES])
ols=sm.OLS(y,Xc).fit()                         # OLS clasico
ols_hc=sm.OLS(y,Xc).fit(cov_type="HC3")        # errores robustos a heterocedasticidad (HC3)
# --- VIF (factor de inflacion de varianza) por variable ---
vif=[variance_inflation_factor(Xc.values,i) for i in range(Xc.shape[1])]
def pfmt(p): return "<0.001" if p<0.001 else f"{p:.3f}"
# --- Tabla de coeficientes: OLS + EE robustos HC3 + VIF ---
pd.DataFrame({
    "variable":["Intercepto"]+[LAB[f] for f in FEATURES],
    "coeficiente":ols.params.round(3).values,
    "EE_robusto_HC3":ols_hc.bse.round(3).values,
    "p_valor":[pfmt(p) for p in ols.pvalues],
    "p_robusto_HC3":[pfmt(p) for p in ols_hc.pvalues],
    "VIF":[float("nan")]+[round(v,2) for v in vif[1:]],
    "signif_robusto_p<0.05":(ols_hc.pvalues<0.05).values,
}).to_csv(TAB/"us_tabla2b_ols_coeficientes.csv",index=False,encoding="utf-8")

# --- Especificaciones de robustez: completo / sin DC / reducido (sin las 2 de mayor VIF) ---
vif_feat=pd.Series(vif[1:],index=FEATURES).sort_values(ascending=False)
drop2=list(vif_feat.index[:2])                 # las dos variables mas colineales
FEAT_RED=[f for f in FEATURES if f not in drop2]
def _fit(dsub,feats):
    m=sm.OLS(dsub[TARGET].values,sm.add_constant(dsub[feats])).fit()
    return m
specs={"Completo (N=51)":(df,FEATURES),
       "Sin DC (N=50)":(df[df.estado!="District of Columbia"],FEATURES),
       f"Reducido (−{len(drop2)} colineales)":(df,FEAT_RED)}
rob={}
for name,(dsub,feats) in specs.items():
    m=_fit(dsub,feats)
    col={"N":int(m.nobs),"R2":round(m.rsquared,3),"R2 ajustado":round(m.rsquared_adj,3),
         "F":round(m.fvalue,2),"p(F)":f"{m.f_pvalue:.1e}"}
    for f,lab in [("obesidad_pct","β Obesidad"),("pobreza_ingresos_pct","β Ingresos bajos"),
                  ("inactividad_fisica_pct","β Inactividad"),("indice_ruralidad","β Ruralidad")]:
        if f in feats:
            pv=m.pvalues[f]; ptxt="p<0.001" if pv<0.001 else f"p={pv:.3f}"
            col[lab]=f"{m.params[f]:+.3f} ({ptxt})"
        else:
            col[lab]="—"
    rob[name]=col
rob_df=pd.DataFrame(rob); rob_df.index.name="Métrica / coeficiente"
rob_df.to_csv(TAB/"us_tabla_robustez.csv",encoding="utf-8")

# --- Figura de diagnostico de residuos (residuos vs ajustados + Q-Q) ---
import scipy.stats as _st
resid=ols.resid; fitted=ols.fittedvalues
figd,axd=plt.subplots(1,2,figsize=(11,4.3))
axd[0].scatter(fitted,resid,color="#2b6cb0",edgecolor="white",s=45)
axd[0].axhline(0,ls="--",color="gray",lw=1)
axd[0].set_xlabel("Valores ajustados (%)"); axd[0].set_ylabel("Residuos")
axd[0].set_title("Residuos vs. valores ajustados")
_st.probplot(resid,dist="norm",plot=axd[1]); axd[1].set_title("Q-Q plot de residuos")
axd[1].get_lines()[0].set(marker="o",markerfacecolor="#2b6cb0",markeredgecolor="white",markersize=6,ls="")
axd[1].get_lines()[1].set(color="gray",ls="--")
figd.suptitle("Diagnóstico de residuos del modelo OLS — estados de EE.UU.",fontweight="bold",y=1.02)
figd.tight_layout(); figd.savefig(FIG/"us_figura_diagnostico_residuos.png",bbox_inches="tight"); plt.close(figd)

rf=RandomForestRegressor(n_estimators=500,max_depth=5,random_state=42)
y_cv=cross_val_predict(rf,X,y,cv=KFold(5,shuffle=True,random_state=42)); rf.fit(X,y)
r2_ols,r2_rf=ols.rsquared,r2_score(y,y_cv)
pd.DataFrame({"modelo":["OLS (in-sample)","Random Forest (5-fold CV)"],
    "R2":[round(r2_ols,3),round(r2_rf,3)],
    "MAE":[round(mean_absolute_error(y,ols.fittedvalues),3),round(mean_absolute_error(y,y_cv),3)],
    "RMSE":[round(np.sqrt(mean_squared_error(y,ols.fittedvalues)),3),round(np.sqrt(mean_squared_error(y,y_cv)),3)]
    }).to_csv(TAB/"us_tabla2_rendimiento_modelos.csv",index=False,encoding="utf-8")

imp=pd.Series(rf.feature_importances_,index=[LAB[f] for f in FEATURES]).sort_values()
fig,ax=plt.subplots(1,2,figsize=(11.5,4.6))
ax[0].barh(imp.index,imp.values,color="#2b6cb0"); ax[0].set_title("Importancia de variables (Random Forest)"); ax[0].set_xlabel("Importancia relativa")
ax[1].scatter(y,y_cv,color="#2b6cb0",edgecolor="white",s=60)
lims=[min(y.min(),y_cv.min())-0.5,max(y.max(),y_cv.max())+0.5]; ax[1].plot(lims,lims,"--",color="gray",lw=1); ax[1].set_xlim(lims); ax[1].set_ylim(lims)
ax[1].set_xlabel("Prevalencia observada (%)"); ax[1].set_ylabel("Prevalencia predicha (%) — CV"); ax[1].set_title(f"Real vs. predicho (RF, R2_CV={r2_rf:.2f})")
fig.suptitle("Desempeño e interpretabilidad del modelo — estados de EE.UU.",y=1.03,fontweight="bold")
fig.tight_layout(); fig.savefig(FIG/"us_figura1_importancia_desempeno.png",bbox_inches="tight"); plt.close(fig)

Xp=PCA(n_components=2,random_state=42).fit(Xs); Xpca=Xp.transform(Xs)
cl=KMeans(n_clusters=3,n_init=20,random_state=42).fit_predict(Xs); df["cluster"]=cl
gdf=gdf.merge(df[["estado","cluster"]],on="estado",how="left")
prof=df.groupby("cluster")[FEATURES+[TARGET]].mean().round(2).rename(columns=LAB); prof["n_estados"]=df.groupby("cluster").size()
prof.to_csv(TAB/"us_tabla3_perfil_clusters.csv",encoding="utf-8")
ve=Xp.explained_variance_ratio_; pal=["#2b6cb0","#dd6b20","#38a169"]
fig,ax=plt.subplots(figsize=(7,5.5))
for c in range(3):
    m=cl==c; ax.scatter(Xpca[m,0],Xpca[m,1],s=70,color=pal[c],label=f"Cluster {c} (n={m.sum()})",edgecolor="white")
for i,s in enumerate(df.estado): ax.annotate(s[:4],(Xpca[i,0],Xpca[i,1]),fontsize=6,alpha=0.7,xytext=(3,3),textcoords="offset points")
ax.set_xlabel(f"Componente 1 ({ve[0]*100:.0f}% var.)"); ax.set_ylabel(f"Componente 2 ({ve[1]*100:.0f}% var.)")
ax.set_title("Segmentacion no supervisada de estados\n(K-Means, k=3)"); ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(FIG/"us_figura_clusters_pca.png",bbox_inches="tight"); plt.close(fig)

cont=gdf[~gdf.estado.isin(["Alaska","Hawaii"])]
fig,axes=plt.subplots(1,2,figsize=(15,6.2))
cont.plot(column=TARGET,cmap="OrRd",linewidth=0.4,edgecolor="0.5",legend=True,ax=axes[0],legend_kwds={"label":"Prevalencia de diabetes (%)","shrink":0.6})
axes[0].set_title("(a) Prevalencia de diabetes por estado\n(BRFSS 2015, ponderada)"); axes[0].axis("off")
cont.plot(column="cluster",cmap=plt.matplotlib.colors.ListedColormap(pal),linewidth=0.4,edgecolor="0.5",legend=True,ax=axes[1],categorical=True,legend_kwds={"title":"Cluster","loc":"lower left"})
axes[1].set_title("(b) Perfiles de riesgo territorial\n(K-Means, k=3)"); axes[1].axis("off")
fig.suptitle("Distribución geoespacial de la prevalencia de diabetes y clusters de riesgo — EE.UU.",fontweight="bold",y=0.99)
fig.tight_layout(); fig.savefig(FIG/"us_figura2_mapas.png",bbox_inches="tight",dpi=170); plt.close(fig)
print(f"[US] OLS R2={r2_ols:.3f} (R2aj={ols.rsquared_adj:.3f}) | F({ols.df_model:.0f},{ols.df_resid:.0f})={ols.fvalue:.2f} p={ols.f_pvalue:.1e} | RF R2_CV={r2_rf:.3f}")
print(f"[US] VIF máx={vif_feat.iloc[0]:.1f} ({LAB[vif_feat.index[0]]}) | reducido quita: {[LAB[d] for d in drop2]}")

# ======================= PARTE B - PAISES DEL MUNDO =======================
GF=["poblacion_rural_pct","gasto_bolsillo_salud_pct","pib_per_capita_usd","poblacion_65mas_pct"]; GT="prevalencia_diabetes_pct"
GLAB={"poblacion_rural_pct":"Poblacion rural (%)","gasto_bolsillo_salud_pct":"Gasto de bolsillo en salud (%)",
      "pib_per_capita_usd":"PBI per capita (USD)","poblacion_65mas_pct":"Poblacion 65+ (%)","prevalencia_diabetes_pct":"Prevalencia de diabetes (%)"}
g=pd.read_csv(DATA/"global_paises.csv")
g[[GT]+GF].corr().round(2).rename(index=GLAB,columns=GLAB).to_csv(TAB/"global_tabla1_correlacion.csv",encoding="utf-8")
gols=sm.OLS(g[GT].values,sm.add_constant(g[GF])).fit()
pd.DataFrame({"variable":["Intercepto"]+[GLAB[f] for f in GF],"coeficiente":gols.params.round(4).values,
    "p_valor":gols.pvalues.round(4).values,"significativo_p<0.05":(gols.pvalues<0.05).values}).to_csv(TAB/"global_tabla_ols.csv",index=False,encoding="utf-8")

world=gpd.read_file(GEO/"world_countries.geojson").rename(columns={"ISO3166-1-Alpha-3":"iso3"}).merge(g,on="iso3",how="left")
fig,ax=plt.subplots(figsize=(14,7))
world.plot(column=GT,cmap="OrRd",linewidth=0.2,edgecolor="0.6",legend=True,ax=ax,
           missing_kwds={"color":"#eeeeee","label":"Sin datos"},legend_kwds={"label":"Prevalencia de diabetes (%)","shrink":0.5})
arg=world[world.iso3=="ARG"]
if len(arg):
    arg.boundary.plot(ax=ax,color="#1a202c",linewidth=1.4)
    c=arg.geometry.representative_point().iloc[0]
    ax.annotate("Argentina 14,0%",(c.x,c.y),fontsize=9,fontweight="bold",color="#1a202c",ha="right",
                xytext=(c.x-14,c.y+2),arrowprops=dict(arrowstyle="->",color="#1a202c",lw=1.2))
ax.set_title("Prevalencia de diabetes por país (IDF / Our World in Data, 2024)",fontweight="bold"); ax.axis("off")
fig.tight_layout(); fig.savefig(FIG/"global_figura_mapa.png",bbox_inches="tight",dpi=170); plt.close(fig)

fig,ax=plt.subplots(figsize=(8,5.8))
ax.scatter(g.pib_per_capita_usd,g[GT],s=28,color="#2b6cb0",alpha=0.6,edgecolor="white")
for _,r in g.iterrows():
    if r.iso3 in ["ARG","USA","PAK","JPN","IND","BRA","MEX","CHL"]: ax.annotate(r.iso3,(r.pib_per_capita_usd,r[GT]),fontsize=8,fontweight="bold")
a=g[g.iso3=="ARG"].iloc[0]
ax.scatter([a.pib_per_capita_usd],[a[GT]],s=120,color="#dd6b20",edgecolor="black",zorder=5,label="Argentina")
ax.set_xscale("log"); ax.set_xlabel("PBI per capita (USD, escala log)"); ax.set_ylabel("Prevalencia de diabetes (%)")
ax.set_title("Prevalencia de diabetes vs. PBI per cápita (países, 2024)"); ax.legend()
fig.tight_layout(); fig.savefig(FIG/"global_figura_scatter.png",bbox_inches="tight"); plt.close(fig)
print(f"[GLOBAL] OLS R2={gols.rsquared:.3f} | N={len(g)} paises | Argentina={a[GT]}%")

# ============= PARTE C - CARGA ABSOLUTA, EVOLUCION Y BRECHA DE TRATAMIENTO =============
nc = pd.read_csv(DATA/"ncdrisc_mundo_tendencia.csv")
tot = pd.read_csv(DATA/"idf_totales_globales.csv")
carga = pd.read_csv(DATA/"idf_carga_paises.csv")

# --- Figura 5b: tendencia mundial (NCD-RisC) + totales globales (IDF, con proyeccion) ---
fig, ax = plt.subplots(1, 2, figsize=(13, 4.8))
for sx, cc in [("Men", "#2b6cb0"), ("Women", "#dd6b20")]:
    s = nc[nc.sexo == sx].sort_values("anio")
    ax[0].plot(s.anio, s.prevalencia_18mas_pct, color=cc, lw=2, label=f"Prevalencia — {sx}")
    ax[0].plot(s.anio, s.tratados_pct, color=cc, lw=2, ls="--", label=f"% tratados — {sx}")
ax[0].set_title("(a) Prevalencia mundial (18+) vs. % tratados (30+)\n(NCD-RisC, 1990–2022)")
ax[0].set_xlabel("Año"); ax[0].set_ylabel("%"); ax[0].legend(fontsize=7); ax[0].grid(alpha=0.3)
bars = ax[1].bar(tot.anio.astype(str), tot.millones, color=["#90cdf4","#63b3ed","#dd6b20","#a0aec0"])
for b, v in zip(bars, tot.millones):
    ax[1].text(b.get_x()+b.get_width()/2, v+8, f"{v:.0f}M", ha="center", fontsize=9, fontweight="bold")
ax[1].set_title("(b) Personas con diabetes en el mundo\n(IDF; 2050 = proyección)")
ax[1].set_ylabel("Millones (20–79 años)"); ax[1].set_ylim(0, tot.millones.max()*1.15)
fig.suptitle("Evolución mundial de la diabetes y brecha de tratamiento", fontweight="bold", y=1.02)
fig.tight_layout(); fig.savefig(FIG/"global_figura_tendencia.png", bbox_inches="tight"); plt.close(fig)
nc.to_csv(TAB/"global_tabla_ncdrisc.csv", index=False)  # respaldo
tot.to_csv(TAB/"global_tabla_totales.csv", index=False)

# --- Figura 6b: carga absoluta - top 15 paises + Argentina ---
top = carga.head(15).copy()
arg_c = carga[carga.pais == "Argentina"]
if len(arg_c) and "Argentina" not in top.pais.values:
    top = pd.concat([top, arg_c], ignore_index=True)
top = top.sort_values("millones")
colors = ["#dd6b20" if p == "Argentina" else "#2b6cb0" for p in top.pais]
fig, ax = plt.subplots(figsize=(8.5, 6))
ax.barh(top.pais, top.millones, color=colors)
for i, v in enumerate(top.millones):
    ax.text(v+1, i, f"{v:.1f}", va="center", fontsize=8)
ax.set_xlabel("Millones de adultos con diabetes (20–79 años)")
ax.set_title("Carga absoluta de diabetes por país (IDF, 2024)\nTop 15 + Argentina (naranja)")
fig.tight_layout(); fig.savefig(FIG/"global_figura_carga.png", bbox_inches="tight"); plt.close(fig)
carga.head(10)[["pais","millones"]].to_csv(TAB/"global_tabla_carga_top10.csv", index=False)

# --- Figura 7: cambio 2011 -> 2024 (puntos porcentuales), top aumentos + Argentina ---
ch = g.dropna(subset=["cambio_2011_2024_pp"]).copy()
topc = ch.nlargest(15, "cambio_2011_2024_pp").copy()
argc = ch[ch.iso3 == "ARG"]
if len(argc) and "ARG" not in topc.iso3.values:
    topc = pd.concat([topc, argc], ignore_index=True)
topc = topc.sort_values("cambio_2011_2024_pp")
colors = ["#dd6b20" if x == "ARG" else "#38a169" for x in topc.iso3]
fig, ax = plt.subplots(figsize=(8.5, 6))
ax.barh(topc.pais, topc.cambio_2011_2024_pp, color=colors)
for i, v in enumerate(topc.cambio_2011_2024_pp):
    ax.text(v+0.1, i, f"+{v:.1f}", va="center", fontsize=8)
ax.set_xlabel("Cambio en la prevalencia 2011 → 2024 (puntos porcentuales)")
ax.set_title("Mayores aumentos de prevalencia entre rondas IDF\n(2011 vs. 2024) + Argentina (naranja)")
fig.tight_layout(); fig.savefig(FIG/"global_figura_cambio.png", bbox_inches="tight"); plt.close(fig)

print(f"[C] NCD-RisC mundo 2022: prev~{nc[nc.anio==2022].prevalencia_18mas_pct.mean():.1f}% | "
      f"tratados~{nc[nc.anio==2022].tratados_pct.mean():.1f}%")
print(f"[C] Total mundial 2024={tot[tot.anio==2024].millones.values[0]:.0f}M -> 2050={tot[tot.anio==2050].millones.values[0]:.0f}M")
print(f"[C] Argentina carga={arg_c.millones.values[0]:.2f}M | cambio 2011-2024=+{argc.cambio_2011_2024_pp.values[0]:.1f}pp")
print("OK - figuras en figures/, tablas en tables/")
