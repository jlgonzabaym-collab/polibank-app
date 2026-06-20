from fastapi import APIRouter
from app.ai_core import clasificar_gasto
from app.finance_logic import (
    registrar_nuevo_ingreso,
    registrar_nuevo_egreso,
    obtener_datos_para_grafica
)

router = APIRouter()

# 1. Ruta que ya tenías para probar la IA a secas
@router.get("/categorizar")
def obtener_categoria(gasto: str):
    categoria_final = clasificar_gasto(gasto)
    return {"gasto": gasto, "categoria": categoria_final}

# 2. Ruta para meter ingresos de plata
@router.post("/ingresos")
def agregar_ingreso(monto: float):
    return registrar_nuevo_ingreso(monto)

# 3. LA RUTA CLAVE: Registra el gasto usando la IA y lo guarda en la calculadora
@router.post("/egresos")
def agregar_egreso(monto: float, texto_gasto: str):
    # Primero la IA hace su magia para saber qué es
    categoria_detectada = clasificar_gasto(texto_gasto)
    # Luego la lógica financiera lo mete al historial sumando en su categoría
    resultado = registrar_nuevo_egreso(monto, categoria_detectada)
    return resultado

# 4. Ruta que pide Flutter para dibujar los gráficos en el cel
@router.get("/grafica")
def obtener_resumen_grafica():
    return obtener_datos_para_grafica()