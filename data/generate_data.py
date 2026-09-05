"""
Paranice — Generador de datos demo
Corre una vez:  python3 data/generate_data.py

TODOS los datos transaccionales son SINTÉTICOS (creados para una demostración
comercial de Calybrat). Lo que NO es sintético y viene de fuentes públicas:

  · Catálogo real y precios PVP de paranice.co (WooCommerce Store API, ago-2026)
  · Categorías reales: GranOLAS · Esparcibles · Pancakes & Waffles ·
    Avena & Harinas · Combos · Merch
  · Canales reales: e-commerce propio (pedido mínimo $50.000), Éxito, Carulla,
    Rappi, Fithub, tiendas naturistas, y los sitios de Costa Rica y EE.UU.
  · Referencias de PVP por canal observadas: GranOLA Pistacho 300 g →
    $44.950 en paranice.co · $49.900 en Éxito · $55.400 en Fithub
  · Empresa fundada en 2019 en Bogotá, 51-200 empleados (LinkedIn)
"""

import numpy as np
import pandas as pd
from pathlib import Path
from datetime import date, timedelta

RNG = np.random.default_rng(11)
OUT = Path(__file__).parent

HOY = date(2026, 8, 31)
INICIO = date(2025, 1, 1)
TRM = 4100  # COP por USD (referencia demo)

# ── CATÁLOGO REAL ────────────────────────────────────────────────────────────
# (sku, nombre comercial, nombre largo, categoría, gramaje, PVP propio COP,
#  costo unitario COP, sin_gluten, vegano, sin_azucar, keto, lanzamiento)
PRODUCTOS = [
    ("GRA-VAN", "Vanilla Shortbread",      "GranOLA Gluten Free Sabor a Classic Vanilla Shortbread", "GranOLAS", "300 g", 37950, 14100, 1,1,1,1, "2021-03-01"),
    ("GRA-CHI", "Chip Cookie",             "GranOLA Gluten Free Sabor a Chocolate Chip Cookie",      "GranOLAS", "300 g", 37950, 14350, 1,1,1,1, "2021-03-01"),
    ("GRA-FUD", "Fudge Cake",              "GranOLA Gluten Free Sabor a Cocoa Fudge Cake",           "GranOLAS", "300 g", 37950, 14500, 1,1,1,1, "2021-08-15"),
    ("GRA-PIS", "Pistachio Cookie",        "GranOLA Gluten Free Sabor a Galleta de Pistacho",        "GranOLAS", "300 g", 44950, 18600, 1,1,1,1, "2025-08-01"),

    ("ESP-PIS", "Buttery Pistachio Cookie","Crema a base de Pistachos & Almendras",                  "Esparcibles", "200 g", 63500, 27400, 1,1,1,0, "2024-02-01"),
    ("ESP-BUT", "Golden Butter Cookie",    "Crema a base de Almendras & Marañones",                  "Esparcibles", "200 g", 59900, 25100, 1,1,0,0, "2026-03-01"),
    ("ESP-PB",  "Peanutty Banana Shake",   "Crema a base de Almendras & Maní",                       "Esparcibles", "200 g", 48590, 19400, 1,1,1,0, "2022-11-01"),
    ("ESP-CRE", "Creamy Cocoa Hazelnut",   "Crema a base de Almendras & Avellanas",                  "Esparcibles", "200 g", 48590, 19900, 1,1,1,0, "2021-06-01"),
    ("ESP-CRU", "Crunchy Cocoa Hazelnut",  "Crema a base de Almendras & Avellanas crocante",         "Esparcibles", "200 g", 48590, 20100, 1,1,1,0, "2021-06-01"),
    ("ESP-CIN", "Golden Cinnamon Roll",    "Crema a base de Almendras & Macadamias",                 "Esparcibles", "200 g", 48590, 19700, 1,1,1,0, "2022-04-01"),
    ("ESP-BABY","Baby Spreads",            "Mini esparcibles surtidos",                              "Esparcibles", "45 g",  19500,  7600, 1,1,1,0, "2025-05-01"),

    ("PAN-ALM-VAN","Almendra Vainilla",    "Mezcla para Pancakes & Waffles a base de almendra",      "Pancakes & Waffles", "285 g", 41690, 16200, 1,0,0,0, "2021-01-15"),
    ("PAN-ALM-CHO","Almendra Choco Chips", "Mezcla para Pancakes & Waffles con chips de chocolate",  "Pancakes & Waffles", "285 g", 41690, 16600, 1,0,0,0, "2021-01-15"),
    ("PAN-ALM-CHU","Almendra Churro",      "Mezcla para Pancakes & Waffles sabor a churro",          "Pancakes & Waffles", "285 g", 41690, 16400, 1,0,0,0, "2022-09-01"),
    ("PAN-AVE-BAN","Avena Banano",         "Mezcla para Pancakes & Waffles a base de avena",         "Pancakes & Waffles", "300 g", 32890, 12500, 1,1,1,0, "2022-02-01"),
    ("PAN-AVE-BRO","Avena Brownie",        "Mezcla para Pancakes & Waffles sabor a brownie",         "Pancakes & Waffles", "300 g", 32890, 12800, 1,1,0,0, "2022-02-01"),
    ("PAN-AVE-VAN","Avena Vainilla",       "Mezcla para Pancakes & Waffles sabor a vainilla",        "Pancakes & Waffles", "300 g", 32890, 12400, 1,1,1,0, "2022-02-01"),

    ("AVE-HOJ", "Avena en Hojuelas",       "Avena en hojuelas libre de gluten",                      "Avena & Harinas", "1000 g", 31350, 11800, 1,1,1,0, "2021-01-15"),
    ("HAR-AVE", "Harina de Avena",         "Harina de avena libre de gluten",                        "Avena & Harinas", "1000 g", 31350, 11600, 1,1,1,0, "2021-01-15"),
    ("HAR-ALM", "Harina de Almendra",      "Harina de almendra",                                     "Avena & Harinas", "250 g",  34650, 15400, 1,1,1,1, "2021-04-01"),

    ("COM-3GRA","Three Pack GranOLA",      "Combo 3 GranOLAS a elección",                            "Combos", "3x300 g", 96773, 43000, 1,1,1,1, "2022-05-01"),
    ("COM-3SPR","Three Pack Spread",       "Combo 3 esparcibles a elección",                         "Combos", "3x200 g", 128774, 59500, 1,1,1,0, "2023-07-01"),
    ("COM-3MEZ","Three Pack Mezclas",      "Combo 3 mezclas a elección",                             "Combos", "3x300 g", 95000, 40200, 1,1,0,0, "2025-11-01"),
    ("COM-MIX", "Perfect Mix & Match",     "Combo mixto a elección",                                 "Combos", "surtido", 69258, 30100, 1,1,0,0, "2025-11-01"),
    ("COM-WAF", "Mini Wafflera",           "Mini wafflera Paranice + mezcla",                        "Combos", "kit",     100000, 58000, 0,0,0,0, "2024-11-01"),
    ("COM-DECK","Deck de Cartas",          "Deck de cartas Paranice + producto",                     "Combos", "kit",     100000, 44000, 0,0,0,0, "2025-12-01"),
    ("COM-ROMP","Rompecabezas",            "Rompecabezas Paranice + producto",                       "Combos", "kit",     100000, 45000, 0,0,0,0, "2025-12-01"),
    ("MER-NYR", "New Year Resolution",     "Kit de año nuevo (merch + producto)",                    "Merch",  "kit",     100000, 47000, 0,0,0,0, "2025-12-15"),
]
PROD_COLS = ["sku","nombre","nombre_largo","categoria","presentacion","pvp_propio_cop",
             "costo_unitario_cop","sin_gluten","vegano","sin_azucar","keto","fecha_lanzamiento"]

# ── CANALES ──────────────────────────────────────────────────────────────────
# margen_canal = lo que se queda el canal sobre el PVP (0 en venta directa).
# factor_pvp   = cuánto cuesta el producto al consumidor en ese canal vs. PVP propio.
CANALES = [
    # canal, tipo, país, factor_pvp, margen_canal, plazo_pago_dias, peso_mix
    ("E-commerce propio",  "D2C",           "Colombia",       1.00, 0.00,  0, 0.175),
    ("Éxito",              "Retail",        "Colombia",       1.11, 0.32, 60, 0.230),
    ("Carulla",            "Retail",        "Colombia",       1.13, 0.32, 60, 0.150),
    ("Rappi",              "Marketplace",   "Colombia",       1.15, 0.25, 30, 0.075),
    ("Fithub",             "Especializado", "Colombia",       1.23, 0.30, 45, 0.070),
    ("Tiendas naturistas", "Especializado", "Colombia",       1.18, 0.28, 45, 0.075),
    ("Paranice US",        "Internacional", "Estados Unidos", 1.30, 0.00, 15, 0.115),
    ("Distribuidor CR",    "Internacional", "Costa Rica",     1.22, 0.30, 45, 0.055),
]
CAN_COLS = ["canal","tipo_canal","pais","factor_pvp","margen_canal","plazo_pago_dias","peso_mix"]

LANZAMIENTO_CANAL = {
    "E-commerce propio":  date(2025, 1, 1),
    "Éxito":              date(2025, 1, 1),
    "Carulla":            date(2025, 4, 1),
    "Rappi":              date(2025, 1, 1),
    "Fithub":             date(2025, 6, 1),
    "Tiendas naturistas": date(2025, 1, 1),
    "Distribuidor CR":    date(2025, 5, 1),
    "Paranice US":        date(2025, 10, 1),
}

CIUDADES_CO = [("Bogotá", 0.42), ("Medellín", 0.19), ("Cali", 0.12), ("Barranquilla", 0.09),
               ("Bucaramanga", 0.07), ("Cartagena", 0.05), ("Pereira", 0.04), ("Manizales", 0.02)]
CIUDADES_US = [("Miami", 0.45), ("Orlando", 0.20), ("Houston", 0.20), ("Nueva York", 0.15)]
CIUDADES_CR = [("San José", 0.55), ("Heredia", 0.20), ("Alajuela", 0.15), ("Cartago", 0.10)]

# Puntos de venta por cadena (cantidad y formato)
CADENAS_PDV = [
    ("Éxito",              ["Éxito WOW", "Éxito Superior", "Éxito Vecino"],   46),
    ("Carulla",            ["Carulla FreshMarket", "Carulla Express"],        28),
    ("Fithub",             ["Fithub"],                                        14),
    ("Tiendas naturistas", ["Naturista independiente", "Cadena naturista"],   62),
]

PROVEEDORES = [
    ("PRO-001","Avena certificada GF (Finlandia)","Finlandia","EUR",50,"Avena libre de gluten <20 ppm",9.5,8.6,7.0),
    ("PRO-002","California Almond Co.",           "EEUU",     "USD",32,"Almendra y harina de almendra",9.1,8.8,7.5),
    ("PRO-003","Andes Nuts",                      "Perú",     "USD",28,"Pistacho y macadamia",         9.0,8.1,7.0),
    ("PRO-004","Ecuacacao",                       "Ecuador",  "USD",25,"Cacao y chocolate",            8.8,8.5,8.2),
    ("PRO-005","Maní del Llano",                  "Colombia", "COP", 8,"Maní tostado",                 8.4,9.0,8.9),
    ("PRO-006","Endulzantes Naturales S.A.S.",    "Colombia", "COP",10,"Eritritol, stevia, monk fruit",8.3,8.8,8.6),
    ("PRO-007","EmpaqSostenible",                 "Colombia", "COP",14,"Empaque flexible y doypacks",  8.2,8.9,8.4),
    ("PRO-008","Marañón Caribe",                  "Colombia", "COP",12,"Marañón y avellana",           8.6,8.4,8.1),
]
PRO_COLS = ["proveedor_id","proveedor","pais","moneda","lead_time_dias","especialidad",
            "score_calidad","score_puntualidad","score_precio"]

CEDIS = [
    {"cedi_id":"CEDI-BOG", "nombre":"CEDI Bogotá (planta)", "ciudad":"Bogotá", "pais":"Colombia", "peso":0.70},
    {"cedi_id":"CD-MED",   "nombre":"Cross-dock Medellín",  "ciudad":"Medellín","pais":"Colombia", "peso":0.12},
    {"cedi_id":"3PL-MIA",  "nombre":"3PL Miami",            "ciudad":"Miami",   "pais":"Estados Unidos","peso":0.12},
    {"cedi_id":"DIST-SJO", "nombre":"Distribuidor San José","ciudad":"San José","pais":"Costa Rica","peso":0.06},
]

# Headcount dentro de la banda declarada en LinkedIn (51-200 empleados)
AREAS = [
    ("Producción",        41, (1_500_000, 3_200_000)),
    ("Logística",         16, (1_600_000, 3_800_000)),
    ("Comercial & Trade", 18, (2_400_000, 8_500_000)),
    ("Marketing",         10, (2_800_000, 9_000_000)),
    ("Calidad",            7, (2_600_000, 6_500_000)),
    ("Servicio al cliente", 8, (1_500_000, 3_200_000)),
    ("Administración",     8, (2_200_000, 7_500_000)),
    ("Dirección",          4, (9_000_000,22_000_000)),
]

CANALES_MKT = ["Meta Ads", "Google Ads", "TikTok Ads", "Email (Omnisend)",
               "WhatsApp", "Influencers", "Orgánico/SEO"]
MKT_ROAS_OBJ = {"Meta Ads": 3.2, "Google Ads": 4.3, "TikTok Ads": 2.4,
                "Email (Omnisend)": 11.0, "WhatsApp": 9.0, "Influencers": 2.9}


def estacional(mes: int) -> float:
    """Enero fuerte (propósitos saludables), Nov-Dic regalo, julio bajo."""
    return {1:1.28, 2:1.06, 3:0.97, 4:0.93, 5:1.09, 6:1.00,
            7:0.86, 8:0.93, 9:0.97, 10:1.07, 11:1.32, 12:1.20}.get(mes, 1.0)


def rampa(d: date, lanzamiento: date, dias: int = 240) -> float:
    delta = (d - lanzamiento).days
    if delta < 0:
        return 0.0
    return float(min(1.0, 0.45 + 0.55 * min(1.0, delta / dias)))


def ciudad_de(pais: str) -> str:
    tabla = {"Colombia": CIUDADES_CO, "Estados Unidos": CIUDADES_US, "Costa Rica": CIUDADES_CR}[pais]
    nombres = [c for c, _ in tabla]
    pesos = np.array([p for _, p in tabla], dtype=float)
    return str(RNG.choice(nombres, p=pesos / pesos.sum()))


# ── MAESTROS ─────────────────────────────────────────────────────────────────

def gen_maestros():
    prods = pd.DataFrame(PRODUCTOS, columns=PROD_COLS)
    prods["margen_bruto_pct"] = ((prods["pvp_propio_cop"] - prods["costo_unitario_cop"])
                                 / prods["pvp_propio_cop"] * 100).round(1)
    prods.to_csv(OUT/"productos.csv", index=False)

    can = pd.DataFrame(CANALES, columns=CAN_COLS)
    can["fecha_lanzamiento"] = can["canal"].map(lambda c: LANZAMIENTO_CANAL[c].isoformat())
    can.to_csv(OUT/"canales.csv", index=False)

    pro = pd.DataFrame(PROVEEDORES, columns=PRO_COLS)
    pro["score_general"] = (pro["score_calidad"]*0.4 + pro["score_puntualidad"]*0.35
                            + pro["score_precio"]*0.25).round(2)
    pro.to_csv(OUT/"proveedores.csv", index=False)

    pd.DataFrame(CEDIS).to_csv(OUT/"cedis.csv", index=False)
    print(f"  productos.csv → {len(prods)} SKUs · canales.csv → {len(can)} · proveedores.csv → {len(pro)}")
    return prods, can


def gen_precios_canal(prods: pd.DataFrame, canales: pd.DataFrame):
    """Arquitectura de precios: PVP por canal y precio facturado por Paranice."""
    filas = []
    for _, p in prods.iterrows():
        for _, c in canales.iterrows():
            pvp = round(p["pvp_propio_cop"] * c["factor_pvp"] / 50) * 50
            precio_paranice = round(pvp * (1 - c["margen_canal"]))
            margen = (precio_paranice - p["costo_unitario_cop"]) / precio_paranice * 100
            filas.append({
                "sku": p["sku"], "nombre": p["nombre"], "categoria": p["categoria"],
                "canal": c["canal"], "tipo_canal": c["tipo_canal"], "pais": c["pais"],
                "pvp_consumidor_cop": pvp,
                "precio_factura_paranice_cop": precio_paranice,
                "costo_unitario_cop": p["costo_unitario_cop"],
                "margen_paranice_pct": round(margen, 1),
                "brecha_vs_propio_pct": round((pvp / p["pvp_propio_cop"] - 1) * 100, 1),
            })
    df = pd.DataFrame(filas)
    df.to_csv(OUT/"precios_canal.csv", index=False)
    print(f"  precios_canal.csv → {len(df)} filas")
    return df


def gen_puntos_venta():
    filas = []
    i = 1
    zonas = {"Bogotá":["Chapinero","Usaquén","Suba","Chicó","Salitre","Cedritos"],
             "Medellín":["El Poblado","Laureles","Envigado","Belén"],
             "Cali":["Granada","Ciudad Jardín","Sur"],
             "Barranquilla":["Alto Prado","Villa Country"],
             "Bucaramanga":["Cabecera","Cañaveral"],
             "Cartagena":["Bocagrande","Manga"],
             "Pereira":["Circunvalar"], "Manizales":["Palermo"]}
    ciudades = [c for c, _ in CIUDADES_CO]
    pesos = np.array([p for _, p in CIUDADES_CO]); pesos = pesos / pesos.sum()
    for cadena, formatos, n in CADENAS_PDV:
        for _ in range(n):
            ciudad = str(RNG.choice(ciudades, p=pesos))
            filas.append({
                "pdv_id": f"PDV-{i:04d}",
                "cadena": cadena,
                "formato": str(RNG.choice(formatos)),
                "ciudad": ciudad,
                "zona": str(RNG.choice(zonas.get(ciudad, ["Centro"]))),
                "fecha_apertura": (date(2025,1,1) + timedelta(days=int(RNG.integers(0, 480)))).isoformat(),
            })
            i += 1
    df = pd.DataFrame(filas)
    df.to_csv(OUT/"puntos_venta.csv", index=False)
    print(f"  puntos_venta.csv → {len(df)} PDV")
    return df


# ── VENTAS ───────────────────────────────────────────────────────────────────

def gen_ventas(prods: pd.DataFrame, canales: pd.DataFrame, precios: pd.DataFrame):
    """
    Ventas facturadas por Paranice (líneas):
      · D2C  → un pedido por transacción de consumidor (con pedido mínimo $50.000)
      · Retail / Especializado / Internacional → órdenes de compra por cliente
    """
    px = {(r["sku"], r["canal"]): r for _, r in precios.iterrows()}
    base_mensual_cop = 1_950_000_000  # facturación base mes 1, crece con el tiempo

    filas = []
    ped_id = 500000
    oc_id = 90000

    prods_idx = prods.set_index("sku")
    lanz = {r["sku"]: pd.Timestamp(r["fecha_lanzamiento"]).date() for _, r in prods.iterrows()}

    # Base de clientes D2C que se construye con el tiempo (nuevos vs. recurrentes)
    base_clientes = []          # cada item: (cliente_id, pais, ciudad, canal_captacion)
    canales_captacion = ["Meta Ads","Google Ads","TikTok Ads","Email (Omnisend)",
                         "WhatsApp","Influencers","Orgánico/SEO"]
    pesos_captacion = [0.29, 0.17, 0.11, 0.10, 0.07, 0.11, 0.15]
    contador_cli = 0

    def cliente_para(dia_actual: date):
        """Devuelve un cliente: nuevo (adquisición) o uno que vuelve (recompra)."""
        nonlocal contador_cli
        avance = (dia_actual - INICIO).days / max((HOY - INICIO).days, 1)
        p_nuevo = 0.78 - 0.22 * avance          # la base madura con el tiempo
        if not base_clientes or RNG.random() < p_nuevo:
            contador_cli += 1
            pais = str(RNG.choice(["Colombia","Estados Unidos","Costa Rica"], p=[0.86,0.10,0.04]))
            nuevo = (f"CLI-{contador_cli:05d}", pais, ciudad_de(pais),
                     str(RNG.choice(canales_captacion, p=pesos_captacion)))
            base_clientes.append(nuevo)
            return nuevo
        n = len(base_clientes)
        # los compradores recientes tienen más probabilidad de volver
        if RNG.random() < 0.7:
            idx = int(RNG.integers(int(n * 0.45), n))
        else:
            idx = int(RNG.integers(0, n))
        return base_clientes[idx]

    mes_actual = None
    dia = INICIO
    while dia <= HOY:
        mes_key = dia.strftime("%Y-%m")
        if mes_key != mes_actual:
            mes_actual = mes_key
            # objetivo de facturación del mes
            meses_transcurridos = (dia.year - INICIO.year) * 12 + (dia.month - INICIO.month)
            crecimiento = (1.016) ** meses_transcurridos
            objetivo_mes = base_mensual_cop * crecimiento * estacional(dia.month) * float(RNG.uniform(0.96, 1.04))
            dias_mes = (pd.Timestamp(dia) + pd.offsets.MonthEnd(0)).day
            objetivo_dia = objetivo_mes / dias_mes

        # reparto del día por canal
        for _, c in canales.iterrows():
            canal = c["canal"]
            r = rampa(dia, LANZAMIENTO_CANAL[canal])
            if r <= 0:
                continue
            monto_canal = objetivo_dia * c["peso_mix"] * r * float(RNG.uniform(0.80, 1.20))
            if monto_canal < 50_000:
                continue

            skus_disp = [s for s in prods_idx.index if lanz[s] <= dia]
            if not skus_disp:
                continue

            if c["tipo_canal"] == "D2C":
                # pedidos de consumidor final
                acumulado = 0.0
                while acumulado < monto_canal:
                    cli_id, cli_pais, cli_ciudad, cli_capt = cliente_para(dia)
                    n_items = int(RNG.choice([1, 2, 3], p=[0.46, 0.38, 0.16]))
                    elegidos = list(RNG.choice(skus_disp, size=min(n_items, len(skus_disp)), replace=False))
                    descuento = float(RNG.choice([0,0,0,0.05,0.10,0.15], p=[0.56,0.14,0.10,0.10,0.06,0.04]))
                    total_pedido = 0.0
                    buffer = []
                    for sku in elegidos:
                        info = px[(sku, canal)]
                        qty = int(RNG.choice([1, 2], p=[0.82, 0.18]))
                        total = round(qty * info["precio_factura_paranice_cop"] * (1 - descuento))
                        total_pedido += total
                        buffer.append((sku, info, qty, total))
                    # regla real del sitio: pedido mínimo $50.000
                    if total_pedido < 50_000:
                        sku_extra = str(RNG.choice(skus_disp))
                        info = px[(sku_extra, canal)]
                        total = round(info["precio_factura_paranice_cop"] * (1 - descuento))
                        buffer.append((sku_extra, info, 1, total))
                        total_pedido += total
                    for sku, info, qty, total in buffer:
                        filas.append({
                            "fecha": dia.isoformat(), "mes": mes_key,
                            "documento_id": f"PED-{ped_id}", "tipo_documento": "Pedido web",
                            "canal": canal, "tipo_canal": c["tipo_canal"], "pais": cli_pais,
                            "ciudad": cli_ciudad, "cliente_id": cli_id,
                            "canal_captacion": cli_capt,
                            "sku": sku, "producto": info["nombre"], "categoria": info["categoria"],
                            "unidades": qty,
                            "precio_unitario_cop": info["precio_factura_paranice_cop"],
                            "descuento_pct": descuento,
                            "venta_cop": total,
                            "costo_cop": round(qty * info["costo_unitario_cop"]),
                        })
                    ped_id += 1
                    acumulado += total_pedido
            else:
                # órdenes de compra de cadenas / distribuidores (menos y más grandes)
                n_oc = max(1, int(RNG.poisson(2.2)))
                for _ in range(n_oc):
                    monto_oc = monto_canal / n_oc
                    n_skus = int(RNG.integers(3, min(9, len(skus_disp)) + 1))
                    elegidos = list(RNG.choice(skus_disp, size=n_skus, replace=False))
                    pesos_sku = RNG.dirichlet(np.ones(n_skus) * 2.0)
                    pais = c["pais"]
                    ciudad = ciudad_de(pais)
                    for sku, w in zip(elegidos, pesos_sku):
                        info = px[(sku, canal)]
                        monto_linea = monto_oc * float(w)
                        qty = max(1, int(round(monto_linea / info["precio_factura_paranice_cop"])))
                        total = round(qty * info["precio_factura_paranice_cop"])
                        filas.append({
                            "fecha": dia.isoformat(), "mes": mes_key,
                            "documento_id": f"OC-{oc_id}", "tipo_documento": "Orden de compra",
                            "canal": canal, "tipo_canal": c["tipo_canal"], "pais": pais,
                            "ciudad": ciudad, "cliente_id": canal,
                            "canal_captacion": "—",
                            "sku": sku, "producto": info["nombre"], "categoria": info["categoria"],
                            "unidades": qty,
                            "precio_unitario_cop": info["precio_factura_paranice_cop"],
                            "descuento_pct": 0.0,
                            "venta_cop": total,
                            "costo_cop": round(qty * info["costo_unitario_cop"]),
                        })
                    oc_id += 1
        dia += timedelta(days=1)

    df = pd.DataFrame(filas)
    df["margen_cop"] = df["venta_cop"] - df["costo_cop"]
    df["margen_pct"] = (df["margen_cop"] / df["venta_cop"] * 100).round(1)
    df.to_csv(OUT/"ventas.csv.gz", index=False, compression="gzip")
    print(f"  ventas.csv → {len(df):,} líneas · {df['documento_id'].nunique():,} documentos "
          f"· ${df['venta_cop'].sum()/1e9:.1f}B COP")
    return df


def gen_clientes_d2c(ventas: pd.DataFrame):
    d2c = ventas[ventas["tipo_canal"] == "D2C"]
    agg = d2c.groupby("cliente_id").agg(
        pais=("pais","first"), ciudad=("ciudad","first"),
        canal_captacion=("canal_captacion","first"),
        primera_compra=("fecha","min"), ultima_compra=("fecha","max"),
        pedidos=("documento_id","nunique"),
        unidades=("unidades","sum"),
        ltv_cop=("venta_cop","sum"),
        margen_generado_cop=("margen_cop","sum"),
    ).reset_index()
    agg["ticket_promedio_cop"] = (agg["ltv_cop"] / agg["pedidos"]).round()
    agg["recurrente"] = agg["pedidos"] > 1
    agg["nps"] = np.clip(RNG.normal(8.6, 1.6, len(agg)).round(), 0, 10).astype(int)
    agg["segmento"] = np.select(
        [agg["pedidos"] >= 4, agg["pedidos"] == 3, agg["pedidos"] == 2],
        ["Embajador", "Fiel", "Repite"], default="Primera compra")
    hoy_ts = pd.Timestamp(HOY)
    agg["dias_sin_comprar"] = (hoy_ts - pd.to_datetime(agg["ultima_compra"])).dt.days
    agg["en_riesgo_fuga"] = (agg["dias_sin_comprar"] > 120) & (agg["pedidos"] > 1)
    agg.to_csv(OUT/"clientes_d2c.csv.gz", index=False, compression="gzip")
    print(f"  clientes_d2c.csv → {len(agg):,} clientes")
    return agg


def gen_sellout(ventas: pd.DataFrame, pdv: pd.DataFrame, precios: pd.DataFrame):
    """Rotación en góndola por cadena/ciudad/SKU/mes + quiebres de stock."""
    retail = ventas[ventas["canal"].isin([c for c, _, _ in CADENAS_PDV])]
    pdv_por_cadena_ciudad = pdv.groupby(["cadena","ciudad"]).size().to_dict()
    filas = []
    for (mes, canal, ciudad, sku), g in retail.groupby(["mes","canal","ciudad","sku"]):
        sell_in = int(g["unidades"].sum())
        if sell_in <= 0:
            continue
        n_pdv = pdv_por_cadena_ciudad.get((canal, ciudad), 1)
        # el sell-out suele ir por debajo del sell-in (inventario en cadena)
        sell_out = int(sell_in * float(RNG.uniform(0.72, 1.02)))
        info = precios[(precios["sku"] == sku) & (precios["canal"] == canal)]
        pvp = float(info["pvp_consumidor_cop"].iloc[0]) if len(info) else 0
        dias_quiebre = int(max(0, RNG.normal(2.6, 3.0)))
        filas.append({
            "mes": mes, "cadena": canal, "ciudad": ciudad, "sku": sku,
            "producto": g["producto"].iloc[0], "categoria": g["categoria"].iloc[0],
            "pdv_activos": n_pdv,
            "unidades_sell_in": sell_in,
            "unidades_sell_out": sell_out,
            "valor_sell_out_cop": round(sell_out * pvp),
            "rotacion_und_pdv_mes": round(sell_out / max(n_pdv, 1), 2),
            "dias_sin_stock": min(dias_quiebre, 20),
            "inventario_cadena_und": max(0, sell_in - sell_out),
        })
    df = pd.DataFrame(filas)
    df.to_csv(OUT/"sellout.csv", index=False)
    print(f"  sellout.csv → {len(df):,} filas")
    return df


def gen_despachos(ventas: pd.DataFrame):
    """Cumplimiento: OTIF a cadenas y entregas D2C."""
    docs = ventas.groupby(["documento_id","tipo_documento","canal","tipo_canal","pais","ciudad","fecha"]).agg(
        unidades=("unidades","sum"), valor_cop=("venta_cop","sum")).reset_index()
    filas = []
    hoy_ts = pd.Timestamp(HOY)
    for _, d in docs.iterrows():
        f_ped = pd.Timestamp(d["fecha"])
        if d["tipo_canal"] == "D2C":
            sla = {"Colombia":3, "Estados Unidos":7, "Costa Rica":6}.get(d["pais"], 4)
            transportadora = str(RNG.choice(
                {"Colombia":["Coordinadora","Servientrega","TCC","Envía"],
                 "Estados Unidos":["USPS","FedEx"],
                 "Costa Rica":["Correos de Costa Rica"]}.get(d["pais"], ["Coordinadora"])))
            p_ok = {"Colombia":0.93, "Estados Unidos":0.86, "Costa Rica":0.88}.get(d["pais"], 0.9)
            costo = {"Colombia": RNG.integers(9000,17000), "Estados Unidos": RNG.integers(26000,52000),
                     "Costa Rica": RNG.integers(18000,34000)}.get(d["pais"], 12000)
            fill = 1.0
        else:
            sla = {"Retail":4, "Marketplace":3, "Especializado":5, "Internacional":12}[d["tipo_canal"]]
            transportadora = "Flota propia" if d["pais"] == "Colombia" else "Operador de comercio exterior"
            p_ok = {"Retail":0.93, "Marketplace":0.95, "Especializado":0.94, "Internacional":0.88}[d["tipo_canal"]]
            costo = int(d["valor_cop"] * float(RNG.uniform(0.012, 0.03)))
            # fill rate: qué % de lo pedido por la cadena se logró despachar completo
            fill = 1.0 if RNG.random() < 0.94 else float(np.clip(RNG.normal(0.86, 0.10), 0.45, 0.99))

        sla_dias = int(RNG.integers(max(1, sla-1), sla+2))
        f_prom = f_ped + pd.Timedelta(days=sla_dias)
        a_tiempo = bool(RNG.random() < p_ok)
        retraso = 0 if a_tiempo else int(RNG.integers(1, 7))
        f_real = f_prom + pd.Timedelta(days=retraso)
        if f_real <= hoy_ts:
            estado = "Entregado"
        elif f_ped <= hoy_ts:
            estado = "En tránsito"; f_real = pd.NaT
        else:
            estado = "Generado"; f_real = pd.NaT

        filas.append({
            "despacho_id": f"DES-{d['documento_id'].split('-')[1]}",
            "documento_id": d["documento_id"], "tipo_documento": d["tipo_documento"],
            "canal": d["canal"], "tipo_canal": d["tipo_canal"],
            "pais": d["pais"], "ciudad": d["ciudad"],
            "fecha_pedido": f_ped.date().isoformat(),
            "fecha_prometida": f_prom.date().isoformat(),
            "fecha_entrega": f_real.date().isoformat() if pd.notna(f_real) else None,
            "dias_transito": int((f_real - f_ped).days) if pd.notna(f_real) else sla_dias,
            "transportadora": transportadora,
            "estado": estado,
            "entregado_a_tiempo": a_tiempo if estado == "Entregado" else None,
            "fill_rate": round(fill, 3),
            "otif": bool(a_tiempo and fill >= 0.98) if estado == "Entregado" else None,
            "unidades": int(d["unidades"]),
            "valor_cop": int(d["valor_cop"]),
            "costo_logistico_cop": int(costo),
        })
    df = pd.DataFrame(filas)
    df.to_csv(OUT/"despachos.csv.gz", index=False, compression="gzip")
    print(f"  despachos.csv → {len(df):,} filas")
    return df


def gen_cartera(ventas: pd.DataFrame, canales: pd.DataFrame):
    """Cartera: las cadenas pagan a plazo; el D2C se cobra al instante."""
    plazos = {r["canal"]: int(r["plazo_pago_dias"]) for _, r in canales.iterrows()}
    b2b = ventas[ventas["tipo_canal"] != "D2C"]
    docs = b2b.groupby(["documento_id","canal","tipo_canal","pais","fecha"]).agg(
        valor_cop=("venta_cop","sum")).reset_index()
    docs = docs[pd.to_datetime(docs["fecha"]) >= pd.Timestamp(HOY) - pd.Timedelta(days=200)]
    filas = []
    hoy_ts = pd.Timestamp(HOY)
    for _, d in docs.iterrows():
        f_fac = pd.Timestamp(d["fecha"]) + pd.Timedelta(days=int(RNG.integers(0, 5)))
        plazo = plazos.get(d["canal"], 45)
        f_ven = f_fac + pd.Timedelta(days=plazo)
        # la probabilidad de estar pagada crece a medida que pasa el vencimiento
        dias_desde_venc = (hoy_ts - f_ven).days
        if dias_desde_venc < 0:            # aún dentro del plazo pactado
            p_pagada = 0.12
        elif dias_desde_venc <= 15:
            p_pagada = 0.70
        elif dias_desde_venc <= 45:
            p_pagada = 0.92
        else:
            p_pagada = 0.97
        pagada = bool(RNG.random() < p_pagada)
        mora = 0 if pagada else max(0, dias_desde_venc)
        estado = ("Pagada" if pagada else
                  "Vigente" if mora == 0 else
                  "Vencida 1-30" if mora <= 30 else
                  "Vencida 31-60" if mora <= 60 else
                  "Vencida 61-90" if mora <= 90 else "Vencida +90")
        filas.append({
            "factura_id": f"FV-{d['documento_id'].split('-')[1]}",
            "documento_id": d["documento_id"],
            "cliente": d["canal"], "tipo_canal": d["tipo_canal"], "pais": d["pais"],
            "fecha_factura": f_fac.date().isoformat(),
            "fecha_vencimiento": f_ven.date().isoformat(),
            "plazo_dias": plazo,
            "valor_cop": int(d["valor_cop"]),
            "dias_mora": int(mora),
            "estado": estado,
            "pagada": bool(pagada),
        })
    df = pd.DataFrame(filas)
    df.to_csv(OUT/"cartera.csv", index=False)
    print(f"  cartera.csv → {len(df):,} facturas")
    return df


def gen_produccion(prods: pd.DataFrame, ventas: pd.DataFrame):
    """Lotes de planta: rendimiento, merma y ensayo de gluten (ppm)."""
    demanda = ventas.groupby("sku")["unidades"].sum()
    filas = []
    lote = 7000
    dia = date(2025, 7, 1)
    skus = prods[prods["categoria"] != "Merch"]["sku"].tolist()
    pesos = np.array([demanda.get(s, 1) for s in skus], dtype=float)
    pesos = pesos / pesos.sum()
    while dia <= HOY:
        if dia.weekday() < 5:
            for _ in range(int(RNG.integers(2, 6))):
                sku = str(RNG.choice(skus, p=pesos))
                p = prods[prods["sku"] == sku].iloc[0]
                es_gf = bool(p["sin_gluten"])
                planeadas = int(RNG.integers(400, 2600))
                merma = float(np.clip(RNG.normal(0.028, 0.018), 0.002, 0.14))
                producidas = int(planeadas * (1 - merma))
                ppm = round(float(RNG.uniform(0, 12)), 1) if es_gf else None
                if es_gf and RNG.random() < 0.016:
                    ppm = round(float(RNG.uniform(16, 42)), 1)
                estado = ("Rechazado" if es_gf and ppm and ppm > 20 else
                          "Cuarentena" if es_gf and ppm and ppm > 15 else "Aprobado")
                filas.append({
                    "lote_id": f"L-{lote}",
                    "fecha": dia.isoformat(), "mes": dia.strftime("%Y-%m"),
                    "sku": sku, "producto": p["nombre"], "categoria": p["categoria"],
                    "unidades_planeadas": planeadas,
                    "unidades_producidas": producidas,
                    "merma_pct": round(merma * 100, 2),
                    "cumplimiento_plan_pct": round(producidas / planeadas * 100, 1),
                    "turno": str(RNG.choice(["Mañana","Tarde"])),
                    "linea": str(RNG.choice(["Línea 1 · Hornos","Línea 2 · Molienda","Línea 3 · Cremas"])),
                    "es_sin_gluten": es_gf,
                    "gluten_ppm": ppm,
                    "estado_calidad": estado,
                    "costo_lote_cop": int(producidas * p["costo_unitario_cop"]),
                    "vida_util_dias": int(RNG.integers(180, 365)),
                })
                lote += 1
        dia += timedelta(days=1)
    df = pd.DataFrame(filas)
    df.to_csv(OUT/"produccion.csv", index=False)
    print(f"  produccion.csv → {len(df):,} lotes")
    return df


def gen_inventario(prods: pd.DataFrame, ventas: pd.DataFrame):
    ult90 = ventas[pd.to_datetime(ventas["fecha"]) >= pd.Timestamp(HOY) - pd.Timedelta(days=90)]
    venta_diaria = (ult90.groupby("sku")["unidades"].sum() / 90).to_dict()
    filas = []
    for cedi in CEDIS:
        for _, p in prods.iterrows():
            vd = venta_diaria.get(p["sku"], 1) * cedi["peso"]
            objetivo = vd * 45
            stock = max(0, int(objetivo * float(RNG.uniform(0.25, 1.9))))
            cobertura = stock / vd if vd > 0 else 999
            estado = ("Crítico" if cobertura < 12 else "Bajo" if cobertura < 25
                      else "Normal" if cobertura < 75 else "Sobre-stock")
            filas.append({
                "cedi_id": cedi["cedi_id"], "cedi": cedi["nombre"], "pais": cedi["pais"],
                "sku": p["sku"], "producto": p["nombre"], "categoria": p["categoria"],
                "stock_unidades": stock,
                "venta_diaria_prom": round(vd, 1),
                "dias_cobertura": round(min(cobertura, 180), 1),
                "stock_objetivo_und": int(objetivo),
                "valor_inventario_cop": int(stock * p["costo_unitario_cop"]),
                "estado": estado,
                "lotes_por_vencer_90d": int(RNG.integers(0, 4)),
            })
    df = pd.DataFrame(filas)
    df.to_csv(OUT/"inventario.csv", index=False)
    print(f"  inventario.csv → {len(df)} filas")
    return df


def gen_marketing(ventas: pd.DataFrame, clientes: pd.DataFrame):
    d2c = ventas[ventas["tipo_canal"] == "D2C"].drop_duplicates("documento_id")
    clientes = clientes.copy()
    clientes["mes_alta"] = pd.to_datetime(clientes["primera_compra"]).dt.strftime("%Y-%m")
    nuevos = clientes.groupby(["mes_alta","canal_captacion"]).size().to_dict()

    filas = []
    for (mes, canal), g in d2c.groupby(["mes","canal_captacion"]):
        ingresos = g["venta_cop"].sum()
        pedidos = g["documento_id"].nunique()
        n_nuevos = nuevos.get((mes, canal), 0)
        if canal == "Orgánico/SEO":
            inversion = 0
        else:
            roas = MKT_ROAS_OBJ.get(canal, 3.0) * float(RNG.uniform(0.85, 1.15))
            inversion = int(ingresos / max(roas, 0.5))
        clics = int(inversion / 780) if inversion else int(pedidos * RNG.uniform(9, 16))
        impresiones = int(clics * RNG.uniform(26, 52)) if clics else 0
        filas.append({
            "mes": mes, "canal": canal,
            "inversion_cop": inversion,
            "impresiones": impresiones, "clics": clics,
            "pedidos": pedidos, "clientes_nuevos": int(n_nuevos),
            "ingresos_cop": int(ingresos),
            "cac_cop": int(inversion / n_nuevos) if n_nuevos else 0,
            "roas": round(ingresos / inversion, 2) if inversion else None,
        })
    df = pd.DataFrame(filas)
    df.to_csv(OUT/"marketing.csv", index=False)

    # contenido: blog de recetas + redes (activo real de la marca)
    cont = []
    secciones = ["Baked Goods","Brunch","Desserts","Bebidas y Helados","Recipe","Snacks","The Paranice Lab"]
    for mes in sorted(d2c["mes"].unique()):
        for s in secciones:
            visitas = int(RNG.integers(600, 5200))
            cont.append({
                "mes": mes, "seccion": s,
                "publicaciones": int(RNG.integers(1, 5)),
                "visitas": visitas,
                "pedidos_asistidos": int(visitas * float(RNG.uniform(0.008, 0.035))),
                "tiempo_medio_seg": int(RNG.integers(45, 210)),
            })
    pd.DataFrame(cont).to_csv(OUT/"contenido.csv", index=False)
    print(f"  marketing.csv → {len(df)} filas · contenido.csv → {len(cont)} filas")
    return df


def gen_empleados():
    nombres_m = ["Andrés","Camilo","Juan","Diego","Santiago","Nicolás","Felipe","Julián","Sebastián","Mateo"]
    nombres_f = ["María","Daniela","Laura","Juliana","Paula","Andrea","Valentina","Natalia","Mónica","Sara"]
    apellidos = ["Guzmán","Coral","Rodríguez","Gómez","Martínez","López","Ramírez","Torres","Vargas","Castro",
                 "Moreno","Rojas","Díaz","Herrera","Sánchez","Jiménez","Peña","Cárdenas"]
    filas = []
    i = 1
    for area, n, (smin, smax) in AREAS:
        for _ in range(n):
            genero = str(RNG.choice(["M","F"]))
            nombre = str(RNG.choice(nombres_m if genero == "M" else nombres_f))
            ingreso = HOY - timedelta(days=int(RNG.integers(20, 2400)))
            filas.append({
                "empleado_id": f"EMP-{i:03d}",
                "nombre": f"{nombre} {RNG.choice(apellidos)} {RNG.choice(apellidos)}",
                "area": area,
                "genero": genero,
                "sede": str(RNG.choice(["Planta Bogotá","Oficina Bogotá","Cross-dock Medellín"],
                                        p=[0.55,0.35,0.10])),
                "tipo_contrato": str(RNG.choice(["Indefinido","Fijo","Obra labor","Aprendiz"],
                                                 p=[0.62,0.20,0.12,0.06])),
                "fecha_ingreso": ingreso.isoformat(),
                "antiguedad_anios": round((HOY - ingreso).days / 365, 1),
                "salario_cop": int(RNG.integers(smin, smax)),
                "rotacion_riesgo": str(RNG.choice(["Bajo","Medio","Alto"], p=[0.68,0.24,0.08])),
                "activo": bool(RNG.random() > 0.05),
            })
            i += 1
    df = pd.DataFrame(filas)
    df.to_csv(OUT/"empleados.csv", index=False)
    print(f"  empleados.csv → {len(df)} empleados")
    return df


def gen_finanzas(ventas: pd.DataFrame, marketing: pd.DataFrame, empleados: pd.DataFrame,
                 despachos: pd.DataFrame):
    # La nómina de planta ya está incluida en el costo del producto (COGS):
    # aquí solo va la nómina administrativa y comercial, para no contarla dos veces.
    activos = empleados[empleados["activo"]]
    nomina_mes = activos[activos["area"] != "Producción"]["salario_cop"].sum() * 1.52  # + prestaciones
    filas = []
    desp = despachos.copy()
    desp["mes"] = pd.to_datetime(desp["fecha_pedido"]).dt.strftime("%Y-%m")
    log_mes = desp.groupby("mes")["costo_logistico_cop"].sum().to_dict()
    mkt_mes = marketing.groupby("mes")["inversion_cop"].sum().to_dict()
    for mes, g in ventas.groupby("mes"):
        ingresos = g["venta_cop"].sum()
        costo = g["costo_cop"].sum()
        mkt = mkt_mes.get(mes, 0)
        log = log_mes.get(mes, 0)
        nomina = nomina_mes * float(RNG.uniform(0.97, 1.03))
        otros = ingresos * float(RNG.uniform(0.045, 0.065))
        ebitda = ingresos - costo - mkt - log - nomina - otros
        filas.append({
            "mes": mes,
            "ingresos_cop": int(ingresos),
            "costo_ventas_cop": int(costo),
            "margen_bruto_cop": int(ingresos - costo),
            "margen_bruto_pct": round((ingresos - costo) / ingresos * 100, 1),
            "gasto_marketing_cop": int(mkt),
            "gasto_logistica_cop": int(log),
            "nomina_cop": int(nomina),
            "otros_gastos_cop": int(otros),
            "ebitda_cop": int(ebitda),
            "ebitda_pct": round(ebitda / ingresos * 100, 1),
        })
    df = pd.DataFrame(filas).sort_values("mes")
    df.to_csv(OUT/"finanzas_mensual.csv", index=False)
    print(f"  finanzas_mensual.csv → {len(df)} meses")
    return df


if __name__ == "__main__":
    print("Generando datos demo de Paranice…")
    prods, canales = gen_maestros()
    precios = gen_precios_canal(prods, canales)
    pdv = gen_puntos_venta()
    ventas = gen_ventas(prods, canales, precios)
    clientes = gen_clientes_d2c(ventas)
    gen_sellout(ventas, pdv, precios)
    despachos = gen_despachos(ventas)
    gen_cartera(ventas, canales)
    gen_produccion(prods, ventas)
    gen_inventario(prods, ventas)
    mkt = gen_marketing(ventas, clientes)
    emp = gen_empleados()
    gen_finanzas(ventas, mkt, emp, despachos)
    print("✓ Listo — CSVs generados en data/")
