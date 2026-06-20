import streamlit as st
from datetime import datetime
import pandas as pd
import plotly.express as px
from app.ai_core import clasificar_gasto
from app.finance_logic import registrar_nuevo_ingreso, registrar_nuevo_egreso, obtener_datos_para_grafica

# Configuración de la página de la app
st.set_page_config(page_title="Polibank Prototipo", page_icon="🚀", layout="centered")

st.title("🏦 Polibank - Prototipo Interactivo")
st.write("Prueba cómo funciona la IA y las gráficas financieras en tiempo real.")

# SECCIÓN 1: BALANCE GENERAL
st.header("📊 Resumen de tu Cuenta")
datos = obtener_datos_para_grafica()

col1, col2, col3 = st.columns(3)
col1.metric("Total Ingresos", f"${datos['total_ingresos']:.2f}")
col2.metric("Total Gastos", f"${datos['total_egresos']:.2f}")
col3.metric("Saldo Disponible (Saldo)", f"${datos['balance']:.2f}")

# SECCIÓN 2: GRÁFICA COMPARATIVA DIARIA
st.subheader("📊 Comparativa de Hoy: Ingresos vs Egresos")

# Obtenemos la fecha de hoy formateada (Ej: "19-Jun-2026")
fecha_hoy = datetime.now().strftime("%d-%b")

# Creamos la estructura de datos para el gráfico de barras comparativo
data_grafico = {
    "Fecha": [fecha_hoy, fecha_hoy],
    "Monto ($)": [datos["total_ingresos"], datos["total_egresos"]],
    "Tipo": ["Ingresos", "Egresos"]
}

df = pd.DataFrame(data_grafico)

# Si hay movimientos, dibujamos el gráfico interactivo
if datos["total_ingresos"] > 0 or datos["total_egresos"] > 0:
    # Creamos un gráfico usando posiciones numéricas para controlar la cercanía exacta
    fig = px.bar(
        df,
        x=[-0.12, 0.12],  # Esto fuerza a que la barra azul se mueva a la izquierda y la roja a la derecha
        y="Monto ($)",
        color="Tipo",
        color_discrete_map={"Ingresos": "#0052cc", "Egresos": "#ff0000"}
    )

    # Ajustamos el grosor para que se toquen perfectamente en el centro
    fig.update_traces(width=0.24)

    fig.update_layout(
        bargap=0.0,
        # Forzamos a que en el centro de las barras aparezca la fecha de hoy
        xaxis=dict(
            tickvals=[0],
            ticktext=[fecha_hoy],
            range=[-1, 1]  # Centra el gráfico para que no se mueva
        ),
        xaxis_title=None,
        width=500,
        height=400
    )
    st.plotly_chart(fig)
else:
    st.info("Aún no hay movimientos registrados hoy. ¡Agrega un monto abajo para activar el gráfico!")

# SECCIÓN 3: ACCIONES (FORMULARIOS)
st.header("📥 Registrar Movimientos")

tab1, tab2 = st.tabs(["💰 Registrar Ingreso", "🛒 Registrar Gasto con IA"])

with tab1:
    with st.form("form_ingreso", clear_on_submit=True):
        monto_ingreso = st.number_input("Monto del Ingreso ($)", min_value=0.0, step=10.0)
        bot_ingreso = st.form_submit_button("Guardar Ingreso")
        if bot_ingreso and monto_ingreso > 0:
            registrar_nuevo_ingreso(monto_ingreso)
            st.success(f"¡Ingreso de ${monto_ingreso} registrado con éxito!")
            st.rerun()

with tab2:
    with st.form("form_gasto", clear_on_submit=True):
        monto_gasto = st.number_input("Monto del Gasto ($)", min_value=0.0, step=1.0)
        texto_gasto = st.text_input("¿En qué gastaste?", placeholder="Ej: un almuerzo en el comedor de la fch")
        bot_gasto = st.form_submit_button("Procesar Gasto con IA")

        if bot_gasto and monto_gasto > 0 and texto_gasto:
            with st.spinner("La IA de Polibank está clasificando tu gasto..."):
                categoria_ia = clasificar_gasto(texto_gasto)
                registrar_nuevo_egreso(monto_gasto, categoria_ia)
            st.success(f"Gasto guardado. La IA lo clasificó en: **{categoria_ia.upper()}**")
            st.rerun()