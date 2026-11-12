#Grupo 8
#Integrantes:
import csv
import pandas as pd
import csv
import matplotlib.pyplot as plt
import urllib.request
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#FASE 1: Lectura con with open y filtro del Biobío
#1.1 Encabezado y separador
with open('datos/2026-8.csv', encoding="latin-1") as archivo:
encabezado = archivo.readline()
print("Puntos y coma:", encabezado.count(";"))
print("Comas:", encabezado.count(","))
print("Columnas:", len(encabezado.split(";")))
#1.2 Líneas físicas
lineas = 0
with open(RUTA, encoding="latin-1") as archivo:
for linea in archivo:
lineas += 1
print("Líneas:", lineas)
#1.3 Registros con csv.reader
registros = 0
regiones = set()
with open(RUTA, encoding="latin-1", newline="") as archivo:
lector = csv.reader(archivo, delimiter=";")
encabezado = next(lector)
col_region = encabezado.index("RegionUnidadCompra")
for fila in lector:
registros += 1
regiones.add(fila[col_region].strip())
print("Registros:", registros)
#R: no coinciden porque algunas descripciones tienen saltos de línea
#dentro del texto. csv.reader los junta en un solo registro.
#1.4 Nombre de la región: se imprime el set y se copia el nombre exacto
print(regiones)
#Copiar aquí el nombre tal como aparece (Ñuble es OTRA región).
#Si aparece escrito de dos formas, se ponen las dos en la lista.
regiones_biobio = ["Región del Biobío"]
#1.5 Archivo filtrado
registros_biobio = 0
with open(RUTA, encoding="latin-1", newline="") as entrada, \
open(RUTA_BIOBIO, "w", encoding="latin-1", newline="") as salida:
lector = csv.reader(entrada, delimiter=";")
escritor = csv.writer(salida, delimiter=";")
encabezado = next(lector)
escritor.writerow(encabezado)
col_region = encabezado.index("RegionUnidadCompra")
for fila in lector:
if fila[col_region].strip() in regiones_biobio:
escritor.writerow(fila)
registros_biobio += 1
print("Registros Biobío:", registros_biobio)
print("Porcentaje:", round(registros_biobio / registros * 100, 1))
#FASE 2: Carga y exploración con pandas
#2.1 Solo con sep=";" -> da UnicodeDecodeError
compras = pd.read_csv(RUTA_BIOBIO, sep=";")
#R: pandas asume UTF-8 y el archivo está en latin-1; falla en tildes y ñ.
#2.2 Sin decimal -> el monto queda como texto
compras = pd.read_csv(RUTA_BIOBIO, sep=";", encoding="latin-1",
low_memory=False) # lee todo de una vez: evita el DtypeWarning
print(compras["MontoTotalOC_PesosChilenos"].dtype)
#R: queda object/str porque "11118319327,7" no se reconoce como número.
#2.3 Lectura correcta
compras = pd.read_csv(RUTA_BIOBIO, sep=";", decimal=",",
encoding="latin-1", na_values=["NA"])
print(compras["MontoTotalOC_PesosChilenos"].dtype) # float64
2.4 a 2.7 Exploración
print(compras.shape)
print(compras.columns.tolist())
print(compras.head())
print(compras.tail())
compras.info()
R: Non-Null Count menor al total = columnas con vacíos.
Las fechas quedaron como texto.
print(compras[["MontoTotalOC_PesosChilenos", "totalLineaNeto",
"PromedioCalificacion"]].describe())
R: promedio del monto >> mediana: pocas compras muy grandes.
print(compras["Estado"].value_counts())
print(compras["sector"].value_counts())
print(compras["ProcedenciaOC"].value_counts())
print(compras["EsCompraAgil"].value_counts())
print(compras["sector"].value_counts(normalize=True))
2.8 Preguntas
n_items = compras.shape[0]
n_oc = compras["Codigo"].nunique()
print("Ítems:", n_items)
print("OC distintas:", n_oc)
print("Ítems por OC:", round(n_items / n_oc, 2))
print("Organismos:", compras["OrganismoPublico"].nunique())
print("Proveedores:", compras["NombreProveedor"].nunique())
R: hay más filas que OC porque cada fila es un ítem; una OC con varios
productos se repite. Las OC se cuentan con nunique() sobre "Codigo".
=====================================================================
FASE 3: Limpieza y tipos de datos
=====================================================================
3.1 Vacíos
print(compras.isna().sum())
print(compras.isna().mean() * 100)
compras_texto = pd.read_csv(RUTA_BIOBIO, sep=";", decimal=",",
encoding="latin-1", keep_default_na=False)
print(compras_texto["EsCompraAgil"].isna().sum()) # 0
print((compras_texto["EsCompraAgil"] == "NA").sum()) # > 0
print(compras_texto["PromedioCalificacion"].dtype) # object
R: si "NA" no se considera vacío, isna() no lo detecta, aparece como
categoría en value_counts() y las columnas numéricas quedan como texto.
3.2 Espacios sobrantes
compras["RegionUnidadCompra"] = compras["RegionUnidadCompra"].str.strip()
compras["RegionProveedor"] = compras["RegionProveedor"].str.strip()
R: "Biobío " y "Biobío" son textos distintos; sin strip() falla el ==.
3.3 Fechas
compras["FechaEnvio"] = pd.to_datetime(compras["FechaEnvio"], format="%Y-%m-%d")
compras["FechaAceptacion"] = pd.to_datetime(compras["FechaAceptacion"], format="%Y-%m-%d")
3.4 Días de aceptación
compras["dias_aceptacion"] = (compras["FechaAceptacion"] - compras["FechaEnvio"]).dt.days
print("Sin aceptar:", compras["dias_aceptacion"].isna().sum())
print("Negativos:", (compras["dias_aceptacion"] < 0).sum())
R: NaN = OC no aceptada o cancelada (se deja). Negativos = error de
registro (se excluyen en la Fase 4).
3.5 Proveedor local
compras["proveedor_local"] = compras["RegionProveedor"].isin(regiones_biobio)
print(compras["proveedor_local"].value_counts())
3.6 Mecanismo de compra
Primero se mira cómo vienen escritos los valores y se copian tal cual:
print(compras["ProcedenciaOC"].value_counts())
es_agil = compras["EsCompraAgil"] == "Si"
.str.contains busca el texto dentro del valor, sin importar cómo
siga escrito (mayúsculas, "Pública", "Privada", etc.).
es_convenio = compras["ProcedenciaOC"].str.contains("Convenio", case=False, na=False)
es_licitacion = compras["ProcedenciaOC"].str.contains("Licitaci", case=False, na=False)
compras["mecanismo"] = np.select([es_agil, es_convenio, es_licitacion],
["Compra Ágil", "Convenio Marco", "Licitación"],
default="Otro")
print(compras["mecanismo"].value_counts())
R: el orden importa: np.select usa la primera condición que se cumple.
3.7 Categóricas
compras["Estado"] = compras["Estado"].astype("category")
compras["sector"] = compras["sector"].astype("category")
compras["ProcedenciaOC"] = compras["ProcedenciaOC"].astype("category")
compras["RubroN1"] = compras["RubroN1"].astype("category")
R: category guarda cada valor una sola vez -> menos memoria.
3.8 Una fila por OC
oc = compras.drop_duplicates("Codigo").copy() # .copy() evita el aviso SettingWithCopyWarning
print("Ítems:", compras.shape[0], " OC:", oc.shape[0])
suma_mal = compras["MontoTotalOC_PesosChilenos"].sum()
suma_bien = oc["MontoTotalOC_PesosChilenos"].sum()
print("Suma MAL:", suma_mal)
print("Suma BIEN:", suma_bien)
print("Se infla:", round(suma_mal / suma_bien, 1), "veces")
R: el monto total de la OC se repite en cada ítem; sumar sobre compras
lo cuenta varias veces.
3.9 Tamaño de compra
monto = oc["MontoTotalOC_PesosChilenos"]
oc["tamano_compra"] = np.select([monto < 1_000_000, monto <= 10_000_000],
["pequeña", "mediana"], default="grande")
print(oc["tamano_compra"].value_counts())
=====================================================================
FASE 4: Filtrado con máscaras booleanas
=====================================================================
4.1 Proveedores del Biobío
locales = oc[oc["proveedor_local"]]
otras_regiones = oc[~oc["proveedor_local"]]
pct_oc_local = locales.shape[0] / oc.shape[0] * 100
pct_monto_local = (locales["MontoTotalOC_PesosChilenos"].sum()
/ oc["MontoTotalOC_PesosChilenos"].sum() * 100)
print("% OC locales:", round(pct_oc_local, 1))
print("% monto local:", round(pct_monto_local, 1))
print("% monto a otras regiones:", round(100 - pct_monto_local, 1))
R: si % monto < % OC, los locales ganan muchas compras pero chicas.
4.2 Monto por mecanismo
for nombre in ["Compra Ágil", "Convenio Marco", "Licitación", "Otro"]:
grupo = oc[oc["mecanismo"] == nombre]["MontoTotalOC_PesosChilenos"]
print(nombre, "| OC:", grupo.shape[0],
"| mediana:", grupo.median(),
"| promedio:", grupo.mean())
R: se usa la mediana porque las OC gigantes inflan el promedio.
4.3 Días de aceptación y calificación
dias_validos = oc[oc["dias_aceptacion"] >= 0]
dias_locales = dias_validos[dias_validos["proveedor_local"]]["dias_aceptacion"]
dias_otros = dias_validos[~dias_validos["proveedor_local"]]["dias_aceptacion"]
print("Días locales:", dias_locales.mean(), dias_locales.median())
print("Días otras regiones:", dias_otros.mean(), dias_otros.median())
calif_locales = locales["PromedioCalificacion"]
calif_otros = otras_regiones["PromedioCalificacion"]
print("Con 0:", calif_locales.mean(), calif_otros.mean())
print("Sin 0:", calif_locales[calif_locales > 0].mean(),
calif_otros[calif_otros > 0].mean())
R: 0 = sin evaluaciones, no nota 0. Incluirlo baja el promedio.
4.4 Gasto neto por rubro (tabla de ítems, solo CLP)
items_clp = compras[compras["monedaItem"] == "CLP"]
Para cada rubro se filtra con una máscara y se suma (listas + for).
rubros = []
gastos = []
for rubro in items_clp["RubroN1"].dropna().unique():
rubros.append(rubro)
gastos.append(items_clp[items_clp["RubroN1"] == rubro]["totalLineaNeto"].sum())
gasto_rubro = pd.DataFrame({"rubro": rubros, "gasto": gastos})
gasto_rubro["gasto_millones"] = gasto_rubro["gasto"] / 1_000_000
top10_rubros = gasto_rubro.sort_values("gasto", ascending=False).head(10)
print(top10_rubros)
print("% top 10:", round(top10_rubros["gasto"].sum() / gasto_rubro["gasto"].sum() * 100, 1))
R: aquí se usa compras (ítems) porque cada ítem tiene su propio rubro y
su propio totalLineaNeto; no hay montos repetidos.
4.5 Compra Ágil a proveedor local
agil_total = oc[oc["mecanismo"] == "Compra Ágil"]
agil_local = oc[(oc["mecanismo"] == "Compra Ágil") & (oc["proveedor_local"])]
print("Compras Ágiles:", agil_total.shape[0])
print("Locales:", agil_local.shape[0])
print("% local:", round(agil_local.shape[0] / agil_total.shape[0] * 100, 1))
R: comparar con el % de OC locales de 4.1. Si es mayor, la Compra Ágil
favorece a las empresas de la región.
=====================================================================
FASE 5: Visualización con seaborn
=====================================================================
os.makedirs("graficos", exist_ok=True)
Gráfico 1: barras horizontales, top 10 rubros
sns.barplot(data=top10_rubros, x="gasto_millones", y="rubro")
plt.title("Top 10 rubros por gasto neto (CLP)")
plt.xlabel("Gasto neto (millones de pesos)")
plt.ylabel("Rubro")
plt.savefig("graficos/grafico1.png", dpi=150, bbox_inches="tight")
plt.close()
Gráfico 2: caja del monto por mecanismo (escala logarítmica)
oc_positivas = oc[oc["MontoTotalOC_PesosChilenos"] > 0] # log(0) no existe
sns.boxplot(data=oc_positivas, x="mecanismo", y="MontoTotalOC_PesosChilenos")
plt.yscale("log")
plt.title("Monto de la OC por mecanismo de compra")
plt.xlabel("Mecanismo de compra")
plt.ylabel("Monto de la OC (pesos, escala log)")
plt.savefig("graficos/grafico2.png", dpi=150, bbox_inches="tight")
plt.close()
R: los montos van de miles a miles de millones. Sin escala log, las OC
gigantes estiran el eje y todas las cajas quedan aplastadas abajo.
Gráfico 3: OC por sector, coloreado por origen del proveedor
oc["origen_proveedor"] = np.select([oc["proveedor_local"]], ["Biobío"],
default="Otra región")
sns.countplot(data=oc, y="sector", hue="origen_proveedor")
plt.title("Órdenes de compra por sector y origen del proveedor")
plt.xlabel("Cantidad de OC")
plt.ylabel("Sector")
plt.legend(title="Proveedor")
plt.savefig("graficos/grafico3.png", dpi=150, bbox_inches="tight")
plt.close()
Gráfico 4: histograma de días de aceptación (0 a 30 días)
dias_0_30 = oc[(oc["dias_aceptacion"] >= 0) & (oc["dias_aceptacion"] <= 30)]
sns.histplot(data=dias_0_30, x="dias_aceptacion", binwidth=1)
plt.xlim(0, 30)
plt.title("Días que tardan los proveedores en aceptar una OC")
plt.xlabel("Días")
plt.ylabel("Cantidad de OC")
plt.savefig("graficos/grafico4.png", dpi=150, bbox_inches="tight")
plt.close()
print("Gráficos guardados en la carpeta graficos/"