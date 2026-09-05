"""
Paranice — Generador de datos demo
Corre una vez: python3 data/generate_data.py
Genera todos los CSVs en esta misma carpeta.

Todos los datos son SINTÉTICOS (generados para fines de demostración comercial),
calibrados sobre la información pública de paranice.co: marca colombiana de
alimentos saludables (granolas, esparcibles, mezclas para pancakes/waffles,
harinas y avena) sin gluten / sin azúcar añadida / veganas, venta D2C por
e-commerce, con presencia en Colombia, Costa Rica y Estados Unidos.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from datetime import date, timedelta

RNG = np.random.default_rng(7)
OUT = Path(__file__).parent

HOY = date(2026, 8, 31)
INICIO = date(2025, 1, 1)

# ── MASTERS ──────────────────────────────────────────────────────────────────

PRODUCTOS = [
    # id, nombre, categoria, precio_venta, costo_unitario, sin_gluten, vegano, sin_azucar, lanzamiento, stock_min, lead_time_dias
    ("GRA-001","Granola Vainilla Shortbread","GranOLAs",37950,14200,True, True, True, "2024-01-15",120,18),
    ("GRA-002","Granola Chip Cookie",        "GranOLAs",37950,14400,True, True, True, "2024-01-15",120,18),
    ("GRA-003","Granola Fudge Cake",         "GranOLAs",37950,14600,True, True, True, "2024-06-01",100,18),
    ("GRA-004","Granola Pistacho Cookie",    "GranOLAs",44950,17800,True, True, True, "2025-02-10", 80,20),
    ("PAN-001","Mix Pancake Vainilla",       "Pancakes & Waffles",41690,15900,True, False,False,"2024-03-01", 90,15),
    ("PAN-002","Mix Pancake Chocolate Chips","Pancakes & Waffles",41690,16400,True, False,False,"2024-03-01", 90,15),
    ("PAN-003","Mix Waffle Churro",          "Pancakes & Waffles",41690,16100,True, False,False,"2024-09-15", 70,15),
    ("PAN-004","Mix Pancake Banana",         "Pancakes & Waffles",32890,12600,True, True, True, "2025-01-20",100,15),
    ("PAN-005","Mix Pancake Brownie",        "Pancakes & Waffles",32890,12800,True, True, False,"2025-01-20",100,15),
    ("AVE-001","Harina de Almendra",         "Avena & Harinas",34650,15200,True, True, True, "2024-01-15",150,25),
    ("AVE-002","Harina de Avena",            "Avena & Harinas",31350,11400,True, True, True, "2024-01-15",150,22),
    ("AVE-003","Hojuelas de Avena",          "Avena & Harinas",31350,11000,True, True, True, "2024-02-01",150,22),
    ("ESP-001","Crema Pistacho Cookie",      "Esparcibles",63500,26800,True, True, True, "2025-03-10", 60,20),
    ("ESP-002","Crema Maní Banana",          "Esparcibles",48590,19600,True, True, True, "2024-04-01", 90,18),
    ("ESP-003","Crema Cacao Avellana Clásica","Esparcibles",48590,19900,True, True, True,"2024-04-01", 90,18),
    ("ESP-004","Crema Cacao Avellana Blanca","Esparcibles",48590,20200,True, True, True, "2024-11-01", 80,18),
    ("ESP-005","Crema Canela Roll",          "Esparcibles",48590,19700,True, True, True, "2025-02-01", 80,18),
    ("ESP-006","Crema Butter Cookie",        "Esparcibles",59900,24900,True, True, False,"2025-05-15", 60,18),
    ("COM-001","Combo Desayuno Saludable",   "Combos",89900,36500,True, True, True, "2024-05-01", 50,12),
    ("COM-002","Combo Sin Gluten Starter",   "Combos",119900,48200,True, True, True,"2024-08-01", 40,12),
    ("COM-003","Combo Esparcibles Trío",     "Combos",139900,58600,True, True, True,"2025-04-01", 40,12),
    ("MER-001","Termo Paranice",             "Merch",45000,21000,False,False,False,"2024-07-01", 40,30),
    ("MER-002","Tote Bag Paranice",          "Merch",28000,11500,False,False,False,"2024-07-01", 60,30),
]
PROD_COLS = ["producto_id","nombre","categoria","precio_venta","costo_unitario",
             "sin_gluten","vegano","sin_azucar","fecha_lanzamiento","stock_min","lead_time_dias"]

BODEGAS = [
    {"bodega_id":"CEDI-BOG","nombre":"CEDI Bogotá","ciudad":"Bogotá","pais":"Colombia","peso":0.68},
    {"bodega_id":"HUB-SJO", "nombre":"Hub San José","ciudad":"San José","pais":"Costa Rica","peso":0.20},
    {"bodega_id":"3PL-MIA", "nombre":"3PL Miami","ciudad":"Miami","pais":"Estados Unidos","peso":0.12},
]

CANALES = ["Instagram Ads","Google Ads","TikTok Ads","Email/WhatsApp","Orgánico/SEO","Referidos"]
CANAL_PESOS = [0.30, 0.20, 0.12, 0.13, 0.15, 0.10]

PAISES = [
    {"pais":"Colombia",       "moneda":"COP","lanzamiento":date(2025,1,1),  "peso_final":0.66,
     "ciudades":["Bogotá","Medellín","Cali","Barranquilla","Bucaramanga","Pereira"]},
    {"pais":"Costa Rica",     "moneda":"CRC","lanzamiento":date(2025,4,1),  "peso_final":0.22,
     "ciudades":["San José","Heredia","Alajuela","Cartago"]},
    {"pais":"Estados Unidos", "moneda":"USD","lanzamiento":date(2025,10,1), "peso_final":0.12,
     "ciudades":["Miami","Orlando","Doral","Houston"]},
]

PROVEEDORES = [
    ("PRO-001","Avena Foods (certificada GF)","Finlandia","EUR",45,"Avena certificada libre de gluten <20ppm",9.5,8.6,7.0),
    ("PRO-002","California Almond Co.",       "EEUU",    "USD",30,"Almendra en grano y harina de almendra",9.0,8.8,7.6),
    ("PRO-003","Ecuacacao S.A.",              "Ecuador", "USD",25,"Cacao en polvo y pasta de cacao",8.8,8.5,8.2),
    ("PRO-004","Maní del Llano",              "Colombia","COP", 8,"Maní tostado nacional",8.4,9.0,8.9),
    ("PRO-005","Ingenio La Palma",            "Colombia","COP",10,"Panela pulverizada y stevia",8.2,8.9,9.0),
    ("PRO-006","Andes Nuts Perú",             "Perú",    "USD",28,"Pistacho y frutos secos premium",9.1,8.2,7.1),
    ("PRO-007","Coco Pacífico",               "Filipinas","USD",40,"Aceite de coco prensado en frío",8.6,8.0,7.8),
    ("PRO-008","EmpaqSostenible S.A.S.",      "Colombia","COP",12,"Empaques flexibles compostables",8.3,9.1,8.5),
    ("PRO-009","Aditivos Naturales Ltda.",    "Colombia","COP", 9,"Saborizantes y colorantes naturales",8.5,8.9,8.7),
]
PRO_COLS = ["proveedor_id","proveedor","pais","moneda","lead_time_avg_dias","especialidad","score_calidad","score_puntualidad","score_precio"]

TRANSPORTADORAS = {
    "Colombia": ["Servientrega","Coordinadora","TCC"],
    "Costa Rica": ["Correos de Costa Rica","EPS Cargo"],
    "Estados Unidos": ["USPS","FedEx"],
}


def seasonal(month: int) -> float:
    m = {1:1.25,2:1.05,3:0.95,4:0.92,5:1.10,6:1.00,
         7:0.85,8:0.92,9:0.95,10:1.06,11:1.35,12:1.18}
    return m.get(month, 1.0)


def pais_activo(d: date, pais_info: dict) -> bool:
    return d >= pais_info["lanzamiento"]


def ramp(d: date, lanzamiento: date, dias_ramp: int = 240) -> float:
    """0→1 en rampa de adopción tras el lanzamiento de un país."""
    dias = (d - lanzamiento).days
    if dias < 0:
        return 0.0
    return float(min(1.0, 0.15 + 0.85 * min(1.0, dias / dias_ramp)))


# ── CLIENTES (pool) ──────────────────────────────────────────────────────────

def gen_clientes_pool(n=5200):
    pesos = [p["peso_final"] for p in PAISES]
    pesos = np.array(pesos) / sum(pesos)
    rows = []
    for i in range(n):
        pais_info = PAISES[RNG.choice(len(PAISES), p=pesos)]
        ciudad = str(RNG.choice(pais_info["ciudades"]))
        canal = str(RNG.choice(CANALES, p=CANAL_PESOS))
        rows.append({
            "cliente_id": f"CLI-{i+1:05d}",
            "pais": pais_info["pais"],
            "ciudad": ciudad,
            "canal_adquisicion": canal,
            "nps_score": int(RNG.integers(0, 11)),
        })
    return pd.DataFrame(rows)


CLIENTES_POOL = gen_clientes_pool()


def clientes_disponibles(d: date) -> pd.DataFrame:
    paises_activos = [p["pais"] for p in PAISES if pais_activo(d, p)]
    return CLIENTES_POOL[CLIENTES_POOL["pais"].isin(paises_activos)]


# ── PEDIDOS (line items) ─────────────────────────────────────────────────────

def gen_pedidos():
    prods = pd.DataFrame(PRODUCTOS, columns=PROD_COLS)
    prods_activos_cache = {}

    def prods_disponibles(d: date) -> pd.DataFrame:
        key = d.isoformat()
        if key not in prods_activos_cache:
            prods_activos_cache[key] = prods[pd.to_datetime(prods["fecha_lanzamiento"]).dt.date <= d]
        return prods_activos_cache[key]

    rows = []
    pedido_id = 100000
    d = INICIO
    n_dias = (HOY - INICIO).days
    while d <= HOY:
        factor_estacional = seasonal(d.month)
        factor_crecimiento = 1 + 0.021 * ((d - INICIO).days / 30)  # ~2.1%/mes compuesto simplificado
        base_orders = 16 * factor_estacional * factor_crecimiento
        # Costa Rica y USA amplían el volumen total una vez lanzados (rampa)
        boost_expansion = 1.0
        for p in PAISES[1:]:
            if pais_activo(d, p):
                boost_expansion += 0.18 * ramp(d, p["lanzamiento"])
        n_orders = max(6, int(RNG.poisson(base_orders * boost_expansion)))

        cand_clientes = clientes_disponibles(d)
        cand_productos = prods_disponibles(d)
        if cand_clientes.empty or cand_productos.empty:
            d += timedelta(days=1)
            continue

        for _ in range(n_orders):
            cli = cand_clientes.sample(1, random_state=int(RNG.integers(0, 1_000_000))).iloc[0]
            n_items = int(RNG.choice([1,1,1,2,2,3], p=[0.45,0.2,0.15,0.12,0.05,0.03]))
            items = cand_productos.sample(n=min(n_items, len(cand_productos)),
                                           random_state=int(RNG.integers(0, 1_000_000)))
            descuento = float(RNG.choice([0,0,0,0.05,0.10,0.15], p=[0.55,0.15,0.1,0.1,0.06,0.04]))
            canal = str(RNG.choice(CANALES, p=CANAL_PESOS))
            metodo_pago = str(RNG.choice(["Tarjeta crédito","PSE","Tarjeta débito","Contraentrega","PayPal"],
                                          p=[0.42,0.22,0.16,0.12,0.08]))
            for _, prod in items.iterrows():
                qty = int(RNG.integers(1, 4))
                precio = prod["precio_venta"]
                total = round(qty * precio * (1 - descuento))
                margen = (prod["precio_venta"] - prod["costo_unitario"]) / prod["precio_venta"]
                rows.append({
                    "fecha": d.isoformat(), "mes": d.strftime("%Y-%m"),
                    "pedido_id": f"PED-{pedido_id}",
                    "cliente_id": cli["cliente_id"], "pais": cli["pais"], "ciudad": cli["ciudad"],
                    "canal": canal, "metodo_pago": metodo_pago,
                    "producto_id": prod["producto_id"], "producto": prod["nombre"],
                    "categoria": prod["categoria"],
                    "cantidad": qty, "precio_unitario": precio,
                    "descuento_pct": descuento, "total_cop": total,
                    "margen_pct": round(margen, 3),
                })
            pedido_id += 1
        d += timedelta(days=1)

    df = pd.DataFrame(rows)
    df.to_csv(OUT/"pedidos.csv", index=False)
    print(f"  pedidos.csv → {len(df):,} líneas · {df['pedido_id'].nunique():,} pedidos")
    return df


def gen_clientes(pedidos: pd.DataFrame):
    agg = pedidos.groupby("cliente_id").agg(
        pais=("pais","first"), ciudad=("ciudad","first"),
        canal_adquisicion=("canal", lambda s: s.iloc[0]),
        fecha_primera_compra=("fecha","min"),
        fecha_ultima_compra=("fecha","max"),
        n_pedidos=("pedido_id","nunique"),
        ltv_cop=("total_cop","sum"),
    ).reset_index()
    agg = agg.merge(CLIENTES_POOL[["cliente_id","nps_score"]], on="cliente_id", how="left")
    agg["cliente_recurrente"] = agg["n_pedidos"] > 1
    vip_threshold = agg["ltv_cop"].quantile(0.80)
    agg["segmento"] = np.select(
        [agg["ltv_cop"] >= vip_threshold, agg["n_pedidos"] > 1],
        ["VIP", "Recurrente"], default="Compra única",
    )
    agg.to_csv(OUT/"clientes.csv", index=False)
    print(f"  clientes.csv → {len(agg):,} clientes con al menos 1 compra")
    return agg


def gen_marketing(pedidos: pd.DataFrame):
    rows = []
    ped_unicos = pedidos.drop_duplicates("pedido_id")
    meses = sorted(pedidos["mes"].unique())
    for mes in meses:
        m_ped = ped_unicos[ped_unicos["mes"] == mes]
        for pais in m_ped["pais"].unique():
            mp = m_ped[m_ped["pais"] == pais]
            for canal, peso in zip(CANALES, CANAL_PESOS):
                mc = mp[mp["canal"] == canal]
                ingresos_atrib = mc["total_cop"].sum()
                pedidos_atrib = mc["pedido_id"].nunique()
                if canal == "Orgánico/SEO":
                    inversion = 0
                elif canal == "Referidos":
                    inversion = round(ingresos_atrib * float(RNG.uniform(0.11, 0.17)))
                else:
                    roas_obj = {"Instagram Ads": 3.4, "Google Ads": 4.1, "TikTok Ads": 2.6,
                                "Email/WhatsApp": 8.5}.get(canal, 3.0)
                    inversion = round(ingresos_atrib / max(roas_obj * float(RNG.uniform(0.85,1.15)), 0.5)) if ingresos_atrib else 0
                clics = int(inversion / 850) if inversion else int(pedidos_atrib * RNG.uniform(8,15))
                impresiones = int(clics * RNG.uniform(28, 55)) if clics else 0
                rows.append({
                    "mes": mes, "pais": pais, "canal": canal,
                    "inversion_cop": inversion, "impresiones": impresiones,
                    "clics": clics, "pedidos_atribuidos": pedidos_atrib,
                    "ingresos_atribuidos_cop": round(ingresos_atrib),
                })
    df = pd.DataFrame(rows)
    df.to_csv(OUT/"marketing.csv", index=False)
    print(f"  marketing.csv → {len(df):,} filas")


def gen_inventario():
    prods = pd.DataFrame(PRODUCTOS, columns=PROD_COLS)
    rows = []
    for bod in BODEGAS:
        mult = 2.5 if bod["bodega_id"] == "CEDI-BOG" else 1.0
        for _, prod in prods.iterrows():
            stock_max = prod["stock_min"] * RNG.uniform(3, 8) * mult
            stock_act = prod["stock_min"] * RNG.uniform(0.3, 5.5) * mult
            dias_cob = (stock_act / max(1, prod["stock_min"] / 30)) if prod["stock_min"] > 0 else 0
            rows.append({
                "bodega_id": bod["bodega_id"], "bodega": bod["nombre"], "pais": bod["pais"],
                "producto_id": prod["producto_id"], "producto": prod["nombre"],
                "categoria": prod["categoria"],
                "stock_actual": round(stock_act), "stock_minimo": prod["stock_min"],
                "stock_maximo": round(stock_max),
                "costo_unitario": prod["costo_unitario"],
                "valor_inventario": round(stock_act * prod["costo_unitario"]),
                "dias_cobertura": round(min(dias_cob, 150), 1),
                "estado": ("Crítico" if stock_act < prod["stock_min"] * 0.5 else
                           "Bajo"    if stock_act < prod["stock_min"] else
                           "Normal"  if stock_act < prod["stock_min"] * 3 else "Alto"),
            })
    df = pd.DataFrame(rows)
    df.to_csv(OUT/"inventario.csv", index=False)
    print(f"  inventario.csv → {len(df)} filas")


def gen_produccion():
    prods = pd.DataFrame(PRODUCTOS, columns=PROD_COLS)
    rows = []
    lote_id = 4000
    d = date(2026, 1, 1)
    while d <= HOY:
        n_lotes = int(RNG.integers(2, 6))
        for _ in range(n_lotes):
            prod = prods.sample(1, random_state=int(RNG.integers(0, 1_000_000))).iloc[0]
            es_gf = bool(prod["sin_gluten"])
            ppm = round(float(RNG.uniform(0, 13)) if es_gf else float(RNG.uniform(0, 3)), 1)
            if es_gf and RNG.random() < 0.035:
                ppm = round(float(RNG.uniform(17, 45)), 1)  # falla puntual de contaminación cruzada
            estado = "Rechazado" if (es_gf and ppm > 20) else ("Cuarentena" if es_gf and ppm > 15 else "Aprobado")
            cantidad_kg = int(RNG.integers(80, 650))
            rows.append({
                "lote_id": f"LOTE-{lote_id}",
                "fecha_produccion": d.isoformat(),
                "producto_id": prod["producto_id"], "producto": prod["nombre"],
                "categoria": prod["categoria"],
                "cantidad_kg": cantidad_kg,
                "turno": str(RNG.choice(["Mañana","Tarde"])),
                "es_sin_gluten": es_gf,
                "resultado_gluten_ppm": ppm if es_gf else None,
                "estado_calidad": estado,
                "vida_util_dias": int(RNG.integers(150, 365)),
            })
            lote_id += 1
        d += timedelta(days=1)
    df = pd.DataFrame(rows)
    df.to_csv(OUT/"produccion.csv", index=False)
    print(f"  produccion.csv → {len(df)} filas")


def gen_envios(pedidos: pd.DataFrame):
    ped = pedidos.drop_duplicates("pedido_id")[["pedido_id","fecha","pais","ciudad","total_cop"]].copy()
    ped["fecha"] = pd.to_datetime(ped["fecha"])
    rows = []
    hoy_ts = pd.Timestamp(HOY)
    for _, p in ped.iterrows():
        transp = str(RNG.choice(TRANSPORTADORAS.get(p["pais"], ["Servientrega"])))
        sla = {"Colombia": 3, "Costa Rica": 5, "Estados Unidos": 7}.get(p["pais"], 5)
        sla_dias = int(RNG.integers(max(1,sla-1), sla+2))
        f_prometida = p["fecha"] + timedelta(days=sla_dias)
        cumplido = RNG.random() < {"Colombia":0.91, "Costa Rica":0.86, "Estados Unidos":0.82}.get(p["pais"], 0.88)
        delay = 0 if cumplido else int(RNG.integers(1, 6))
        f_entrega = f_prometida + timedelta(days=delay) if f_prometida <= hoy_ts else pd.NaT
        estado = ("Entregado" if pd.notna(f_entrega) and f_entrega <= hoy_ts else
                  "En tránsito" if p["fecha"] <= hoy_ts else "Generado")
        costo_envio = {"Colombia": RNG.integers(9000,16000), "Costa Rica": RNG.integers(18000,32000),
                       "Estados Unidos": RNG.integers(28000,48000)}[p["pais"]]
        transito = (f_entrega - p["fecha"]).days if pd.notna(f_entrega) else sla_dias
        rows.append({
            "envio_id": f"ENV-{p['pedido_id'].split('-')[1]}",
            "pedido_id": p["pedido_id"],
            "fecha_pedido": p["fecha"].date().isoformat(),
            "fecha_entrega_prometida": f_prometida.date().isoformat(),
            "fecha_entrega_real": f_entrega.date().isoformat() if pd.notna(f_entrega) else None,
            "dias_transito": int(transito),
            "pais_destino": p["pais"], "ciudad_destino": p["ciudad"],
            "transportadora": transp,
            "estado": estado,
            "entregado_a_tiempo": bool(cumplido) if pd.notna(f_entrega) else None,
            "costo_envio_cop": int(costo_envio),
            "valor_pedido_cop": p["total_cop"],
        })
    df = pd.DataFrame(rows)
    df.to_csv(OUT/"envios.csv", index=False)
    print(f"  envios.csv → {len(df):,} filas")


def gen_proveedores():
    pr = pd.DataFrame(PROVEEDORES, columns=PRO_COLS)
    pr["score_general"] = (pr["score_calidad"]*0.4 + pr["score_puntualidad"]*0.35 + pr["score_precio"]*0.25).round(2)
    pr.to_csv(OUT/"proveedores.csv", index=False)
    print(f"  proveedores.csv → {len(pr)} filas")


def gen_bodegas():
    pd.DataFrame(BODEGAS).to_csv(OUT/"bodegas.csv", index=False)


def gen_maestros():
    pd.DataFrame(PRODUCTOS, columns=PROD_COLS).to_csv(OUT/"productos.csv", index=False)
    print(f"  productos.csv → {len(PRODUCTOS)} filas")


def gen_paises_mensual(pedidos: pd.DataFrame, marketing: pd.DataFrame = None):
    ped_unicos = pedidos.drop_duplicates("pedido_id")
    rows = []
    for (mes, pais), g in ped_unicos.groupby(["mes","pais"]):
        ventas = g["total_cop"].sum()
        n_pedidos = g["pedido_id"].nunique()
        clientes_activos = g["cliente_id"].nunique()
        rows.append({
            "periodo": mes + "-01", "pais": pais,
            "ventas_cop": ventas, "pedidos": n_pedidos,
            "clientes_activos": clientes_activos,
            "ticket_promedio_cop": round(ventas / n_pedidos) if n_pedidos else 0,
        })
    df = pd.DataFrame(rows)
    df.to_csv(OUT/"paises_mensual.csv", index=False)
    print(f"  paises_mensual.csv → {len(df)} filas")


if __name__ == "__main__":
    print("Generando datos demo de Paranice...")
    gen_maestros()
    gen_bodegas()
    gen_proveedores()
    pedidos = gen_pedidos()
    gen_clientes(pedidos)
    gen_marketing(pedidos)
    gen_inventario()
    gen_produccion()
    gen_envios(pedidos)
    gen_paises_mensual(pedidos)
    print("✓ Listo — todos los CSVs generados en data/")
