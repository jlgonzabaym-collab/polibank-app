from app.database import registrar_usuario, login_usuario
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

# --- CONTROL DE SESIÓN ---
if "usuario_conectado" not in st.session_state:
    tab_login, tab_registro = st.tabs(["🔒 Iniciar Sesión", "📝 Crear Cuenta"])

    with tab_login:
        st.subheader("Ingresa a tu cuenta de Polibank")
        correo_login = st.text_input("Correo Electrónico", key="login_correo")
        pass_login = st.text_input("Contraseña", type="password", key="login_pass")
        if st.button("Ingresar", key="btn_login_submit"):
            if correo_login and pass_login:
                exito, resultado = login_usuario(correo_login, pass_login)
                if exito:
                    st.session_state["usuario_conectado"] = resultado
                    st.rerun()
                else:
                    st.error(resultado)
            else:
                st.warning("Llena todos los campos.")

    with tab_registro:
        st.subheader("Regístrate gratis")
        correo_reg = st.text_input("Correo Electrónico", key="reg_correo")
        pass_reg = st.text_input("Contraseña", type="password", key="reg_pass")
        if st.button("Registrarse", key="btn_reg_submit"):
            if correo_reg and pass_reg:
                exito, mensaje = registrar_usuario(correo_reg, pass_reg)
                if exito:
                    st.success(mensaje)
                else:
                    st.error(mensaje)
            else:
                st.warning("Llena todos los campos.")

# --- SI EL USUARIO YA INICIÓ SESIÓN, ENTRA A TU APP ---
else:
    # Botón para cerrar sesión arriba
    col_user, col_logout = st.columns([4, 1])
    with col_user:
        st.write(f"👤 Conectado como: **{st.session_state['usuario_conectado']['correo']}**")
    with col_logout:
        if st.button("❌ Salir"):
            del st.session_state["usuario_conectado"]
            st.rerun()

    # TRUCO INFALIBLE: Crear el historial en la memoria interna del navegador (Session State)
    if "historial_web" not in st.session_state:
        st.session_state["historial_web"] = []

    # SECCIÓN 1: BALANCE GENERAL
    st.header("📊 Resumen de tu Cuenta")
    datos = obtener_datos_para_grafica()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Ingresos", f"${datos['total_ingresos']:.2f}")
    col2.metric("Total Gastos", f"${datos['total_egresos']:.2f}")
    col3.metric("Saldo Disponible (Saldo)", f"${datos['balance']:.2f}")

    # SECCIÓN 2: GRÁFICA COMPARATIVA DIARIA
    st.subheader("📊 Comparativa de Hoy: Ingresos vs Egresos")

    fecha_hoy = datetime.now().strftime("%d-%b")

    data_grafico = {
        "Fecha": [fecha_hoy, fecha_hoy],
        "Monto ($)": [datos["total_ingresos"], datos["total_egresos"]],
        "Tipo": ["Ingresos", "Egresos"]
    }
    df = pd.DataFrame(data_grafico)

    if datos["total_ingresos"] > 0 or datos["total_egresos"] > 0:
        fig = px.bar(
            df,
            x=[-0.12, 0.12],
            y="Monto ($)",
            color="Tipo",
            color_discrete_map={"Ingresos": "#0052cc", "Egresos": "#ff0000"}
        )
        fig.update_traces(width=0.24)
        fig.update_layout(
            bargap=0.0,
            xaxis=dict(
                tickvals=[0],
                ticktext=[fecha_hoy],
                range=[-1, 1]
            ),
            xaxis_title=None,
            width=500,
            height=400
        )
        st.plotly_chart(fig)
    else:
        st.info("Aún no hay movimientos registrados hoy. ¡Agrega un monto abajo para activar el gráfico!")

    # SECCIÓN 3: HISTORIAL DE MOVIMIENTOS
    st.header("📜 Historial de Actividad")
    if len(st.session_state["historial_web"]) > 0:
        df_historial = pd.DataFrame(st.session_state["historial_web"])
        st.dataframe(df_historial, use_container_width=True, hide_index=True)
    else:
        st.info("No hay transacciones registradas en esta sesión.")

    # SECCIÓN 4: ACCIONES (TUS FORMULARIOS REGRESARON)
    st.header("📥 Registrar Movimientos")

    tab1, tab2 = st.tabs(["💰 Registrar Ingreso", "🛒 Registrar Gasto con IA"])

    with tab1:
        with st.form("form_ingreso", clear_on_submit=True):
            monto_ingreso = st.number_input("Monto del Ingreso ($)", min_value=0.0, step=10.0)
            bot_ingreso = st.form_submit_button("Guardar Ingreso")
            if bot_ingreso and monto_ingreso > 0:
                registrar_nuevo_ingreso(monto_ingreso)

                # Guardamos en la tabla interna de la web
                st.session_state["historial_web"].append({
                    "Fecha": datetime.now().strftime("%d-%b %H:%M"),
                    "Tipo": "💰 Ingreso",
                    "Detalle": "Ingreso manual de dinero",
                    "Categoría": "INGRESOS",
                    "Monto ($)": f"+${monto_ingreso:.2f}"
                })
                st.success(f"¡Ingreso de ${monto_ingreso} registrado con éxito!")
                st.rerun()

    with tab2:
        with st.form("form_gasto", clear_on_submit=True):
            monto_gasto = st.number_input("Monto del Gasto ($)", min_value=0.0, step=1.0)
            texto_gasto = st.text_input("¿En qué gastaste?", placeholder="Ej: un almuerzo en el comedor de la FCSH")
            bot_gasto = st.form_submit_button("Procesar Gasto con IA")

            if bot_gasto and monto_gasto > 0 and texto_gasto:
                with st.spinner("La IA de Polibank está clasificando tu gasto..."):
                    categoria_ia = clasificar_gasto(texto_gasto)
                    registrar_nuevo_egreso(monto_gasto, categoria_ia)

                    # Guardamos en la tabla interna de la web con el texto original
                    st.session_state["historial_web"].append({
                        "Fecha": datetime.now().strftime("%d-%b %H:%M"),
                        "Tipo": "🛒 Gasto",
                        "Detalle": texto_gasto,
                        "Categoría": categoria_ia.upper(),
                        "Monto ($)": f"-${monto_gasto:.2f}"
                    })
                st.success(f"Gasto guardado. La IA lo clasificó en: **{categoria_ia.upper()}**")
                st.rerun()

    # SECCIÓN 5: BOTÓN DE RESETEO
    st.markdown("---")
    if st.button("🗑️ Borrar todos los datos y reiniciar"):
        from app.finance_logic import historial_ingresos, historial_egresos

        historial_ingresos.clear()
        historial_egresos.clear()
        st.session_state["historial_web"].clear()  # Limpiamos el historial web
        st.success("¡Datos borrados por completo!")
        st.rerun()