from fastapi import APIRouter
from datetime import date, timedelta
from app.ai_core import clasificar_gasto
from app.database import (
    guardar_movimiento,
    obtener_movimientos,
    obtener_videos_educativos
)

router = APIRouter()


# 1. Ruta de prueba para la IA
@router.get("/categorizar")
def obtener_categoria(gasto: str):
    categoria_final = clasificar_gasto(gasto)
    return {"gasto": gasto, "categoria": categoria_final}


# 2. Registrar ingreso (ahora con fuente/concepto y guardando en Supabase)
@router.post("/ingresos")
def agregar_ingreso(usuario_id: int, monto: float, fuente: str = "Ingreso manual", fecha: date = None):
    fecha_real = fecha or date.today()
    exito, msg = guardar_movimiento(
        usuario_id=usuario_id,
        tipo="Ingreso",
        detalle=fuente,
        monto=monto,
        categoria="INGRESOS",
        fecha=str(fecha_real)
    )
    return {"status": "ok" if exito else "error", "mensaje": msg}


# 3. Registrar egreso con clasificación IA, guardando en Supabase
@router.post("/egresos")
def agregar_egreso(usuario_id: int, monto: float, texto_gasto: str, fecha: date = None):
    fecha_real = fecha or date.today()
    categoria_detectada = clasificar_gasto(texto_gasto)
    exito, msg = guardar_movimiento(
        usuario_id=usuario_id,
        tipo="Gasto",
        detalle=texto_gasto,
        monto=monto,
        categoria=categoria_detectada.upper(),
        fecha=str(fecha_real)
    )
    return {
        "status": "ok" if exito else "error",
        "mensaje": msg,
        "categoria_ia": categoria_detectada
    }


# 4. Resumen/gráfica para Flutter: ahora con rango de fechas opcional
@router.get("/grafica")
def obtener_resumen_grafica(
    usuario_id: int,
    desde: date = None,
    hasta: date = None
):
    hasta_real = hasta or date.today()
    desde_real = desde or (hasta_real - timedelta(days=29))  # últimos 30 días por defecto

    movimientos = obtener_movimientos(usuario_id)

    ingresos_por_dia = {}
    egresos_por_dia = {}
    totales_categoria = {"comida": 0.0, "transporte": 0.0, "estudios": 0.0, "diversion": 0.0, "otros": 0.0}
    total_ingresos = 0.0
    total_egresos = 0.0

    for mov in movimientos:
        fecha_mov = date.fromisoformat(mov["fecha"])
        if not (desde_real <= fecha_mov <= hasta_real):
            continue

        monto = float(mov["monto"])
        clave = mov["fecha"]

        if mov["tipo"] == "Ingreso":
            total_ingresos += monto
            ingresos_por_dia[clave] = ingresos_por_dia.get(clave, 0.0) + monto
        else:
            total_egresos += monto
            egresos_por_dia[clave] = egresos_por_dia.get(clave, 0.0) + monto
            cat = mov.get("categoria", "otros").lower()
            if cat in totales_categoria:
                totales_categoria[cat] += monto
            else:
                totales_categoria["otros"] += monto

    return {
        "desde": str(desde_real),
        "hasta": str(hasta_real),
        "total_ingresos": total_ingresos,
        "total_egresos": total_egresos,
        "balance": total_ingresos - total_egresos,
        "ingresos_por_dia": ingresos_por_dia,
        "egresos_por_dia": egresos_por_dia,
        "gastos_por_categoria": totales_categoria
    }


# 5. Videos educativos
@router.get("/videos")
def listar_videos():
    return obtener_videos_educativos()