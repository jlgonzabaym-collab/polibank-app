from datetime import datetime, date, timedelta
from typing import Dict, List, Optional

# Listas temporales en memoria
historial_ingresos = []  # [{"monto": X, "fecha": date}]
historial_egresos = []   # [{"monto": X, "categoria": Y, "fecha": date}]
historial_general = []   # detalle para tabla visual


def _normalizar_fecha(fecha: Optional[date]) -> date:
    # Si no mandan fecha, usamos hoy
    return fecha or date.today()


def registrar_nuevo_ingreso(monto: float, fecha: Optional[date] = None):
    fecha_norm = _normalizar_fecha(fecha)

    historial_ingresos.append({
        "monto": monto,
        "fecha": fecha_norm
    })

    historial_general.append({
        "Fecha": fecha_norm.strftime("%d-%b %H:%M"),  # Nota: sin hora real
        "Tipo": "💰 Ingreso",
        "Detalle": "Ingreso manual de dinero",
        "Categoría": "INGRESOS",
        "Monto ($)": f"+${monto:.2f}"
    })

    return {"status": "Ingreso guardado", "monto": monto, "fecha": fecha_norm.isoformat()}


def registrar_nuevo_egreso(monto: float, categoria: str, texto: str = "Gasto registrado", fecha: Optional[date] = None):
    fecha_norm = _normalizar_fecha(fecha)

    cat_limpia = categoria.lower().strip()
    cat_limpia = (cat_limpia
                  .replace("á", "a").replace("é", "e").replace("í", "i")
                  .replace("ó", "o").replace("ú", "u"))

    historial_egresos.append({
        "monto": monto,
        "categoria": cat_limpia,
        "fecha": fecha_norm
    })

    historial_general.append({
        "Fecha": fecha_norm.strftime("%d-%b %H:%M"),
        "Tipo": "🛒 Gasto",
        "Detalle": texto,
        "Categoría": cat_limpia.upper(),
        "Monto ($)": f"-${monto:.2f}"
    })

    return {"status": "Egreso guardado", "monto": monto, "categoria": cat_limpia, "fecha": fecha_norm.isoformat()}


def _rango_fechas(desde: date, hasta: date) -> List[date]:
    if desde > hasta:
        raise ValueError("La fecha 'desde' no puede ser mayor que 'hasta'")
    dias = (hasta - desde).days
    return [desde + timedelta(days=i) for i in range(dias + 1)]


def obtener_datos_para_grafica(desde: date, hasta: date) -> Dict:
    fechas = _rango_fechas(desde, hasta)

    # Inicializamos series por día
    ingresos_por_dia = {d.isoformat(): 0.0 for d in fechas}
    egresos_por_dia = {d.isoformat(): 0.0 for d in fechas}

    # Totales por categoría (opcional si quieres por todo el rango)
    totales_por_categoria = {
        "comida": 0.0,
        "transporte": 0.0,
        "estudios": 0.0,
        "diversion": 0.0,
        "otros": 0.0
    }

    # Agregamos ingresos del rango
    for ing in historial_ingresos:
        f = ing["fecha"]
        if desde <= f <= hasta:
            ingresos_por_dia[f.isoformat()] += ing["monto"]

    # Agregamos egresos del rango y también totales por categoría
    for eg in historial_egresos:
        f = eg["fecha"]
        if desde <= f <= hasta:
            egresos_por_dia[f.isoformat()] += eg["monto"]

            cat = eg["categoria"]
            if cat in totales_por_categoria:
                totales_por_categoria[cat] += eg["monto"]
            else:
                totales_por_categoria["otros"] += eg["monto"]

    # Construimos balance por día
    labels = [d.isoformat() for d in fechas]
    series_ingresos = [ingresos_por_dia[l] for l in labels]
    series_egresos = [egresos_por_dia[l] for l in labels]
    series_neto = [i - e for i, e in zip(series_ingresos, series_egresos)]

    total_ingresos = sum(series_ingresos)
    total_egresos = sum(series_egresos)
    balance_neto = total_ingresos - total_egresos

    return {
        "labels_dias": labels,                # ✅ eje X real
        "ingresos_por_dia": series_ingresos, # serie
        "egresos_por_dia": series_egresos,   # serie
        "neto_por_dia": series_neto,         # serie
        "total_ingresos": total_ingresos,
        "total_egresos": total_egresos,
        "balance": balance_neto,
        "detalles_grafica": totales_por_categoria
    }