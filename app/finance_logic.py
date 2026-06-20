from datetime import datetime

# Listas temporales en memoria para simular la base de datos
historial_ingresos = []
historial_egresos = []  # Cada egreso tendrá: {"monto": X, "categoria": Y}
historial_general = []  # NUEVO: Guardará el detalle de todo para la tabla visual


def registrar_nuevo_ingreso(monto: float):
    # Guarda el ingreso en nuestra lista
    historial_ingresos.append(monto)

    # NUEVO: Guardamos el registro en el historial general
    historial_general.append({
        "Fecha": datetime.now().strftime("%d-%b %H:%M"),
        "Tipo": "💰 Ingreso",
        "Detalle": "Ingreso manual de dinero",
        "Categoría": "INGRESOS",
        "Monto ($)": f"+${monto:.2f}"
    })

    return {"status": "Ingreso guardado", "monto": monto}


def registrar_nuevo_egreso(monto: float, categoria: str, texto: str = "Gasto registrado"):
    # Pasamos a minúsculas y quitamos espacios extras
    cat_limpia = categoria.lower().strip()

    # Quitamos cualquier tilde rara que pueda mandar la IA (incluyendo la ú de estudios)
    cat_limpia = cat_limpia.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")

    # Guarda el egreso con la categoría limpia
    egreso = {"monto": monto, "categoria": cat_limpia}
    historial_egresos.append(egreso)

    # NUEVO: Guardamos el registro con la descripción de la IA en el historial general
    historial_general.append({
        "Fecha": datetime.now().strftime("%d-%b %H:%M"),
        "Tipo": "🛒 Gasto",
        "Detalle": texto,
        "Categoría": cat_limpia.upper(),
        "Monto ($)": f"-${monto:.2f}"
    })

    return {"status": "Egreso guardado", "monto": monto, "categoria": cat_limpia}


def obtener_datos_para_grafica():
    # Sumamos todos los ingresos acumulados
    total_ingresos = sum(historial_ingresos)

    # Preparamos un diccionario con las categorías fijas en 0
    totales_por_categoria = {
        "comida": 0.0,
        "transporte": 0.0,
        "estudios": 0.0,
        "diversion": 0.0,
        "otros": 0.0
    }

    # Recorremos los egresos y los vamos sumando en su categoría correspondiente
    for egreso in historial_egresos:
        cat = egreso["categoria"]
        if cat in totales_por_categoria:
            totales_por_categoria[cat] += egreso["monto"]
        else:
            totales_por_categoria["otros"] += egreso["monto"]

    # Calculamos el total general de gastos
    total_egresos = sum(totales_por_categoria.values())

    # Calculamos el balance neto (lo que le queda disponible)
    balance_neto = total_ingresos - total_egresos

    # Le devolvemos todo ordenadito a la app para que dibuje la gráfica
    return {
        "total_ingresos": total_ingresos,
        "total_egresos": total_egresos,
        "balance": balance_neto,
        "detalles_grafica": totales_por_categoria
    }