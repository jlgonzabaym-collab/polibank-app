import streamlit as st
from datetime import datetime
import pandas as pd
import plotly.express as px
from app.database import registrar_usuario, login_usuario, guardar_movimiento, obtener_movimientos
from app.ai_core import clasificar_gasto

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

# --- SI EL USUARIO YA INICIÓ SESIÓN, ENTRA A TU APP REAL ---
else:
    # Capturamos los datos del usuario conectado
    user_id = st.session_state["usuario_conectado"]["id"]
    correo_user = st.session_state["usuario_conectado"]["correo"]

    col_user, col_logout = st.columns([4, 1])
    with col_user:
        st.write(f"👤 Conectado como: **{correo_user}**")
    with col_logout:
        if st.button("❌ Salir"):
            del st.session_state["usuario_conectado"]
            st.rerun()

    # TRAEMOS LOS MOVIMIENTOS REALES DESDE SUPABASE
    movimientos_db = obtener_movimientos(user_id)

    # Procesamos los datos reales para las métricas y gráficas
    total_ingresos = 0.0
    total_egresos = 0.0
    historial_tabla = []

    for mov in movimientos_db:
        monto_num = float(mov["monto"])
        # Formateamos la fecha que viene de la BD (YYYY-MM-DD) a algo más amigable
        fecha_dt = datetime.strptime(mov["fecha"], "%Y-%m-%d")
        fecha_formateada = fecha_dt.strftime("%d-%b")

        if mov["tipo"] == "Ingreso":
            total_ingresos += monto_num
            tipo_emoji = "💰 Ingreso"
            monto_texto = f"+${monto_num:.2f}"
        else:
            total_egresos += monto_num
            tipo_emoji = "🛒 Gasto"
            monto_texto = f"-${monto_num:.2f}"

        historial_tabla.append({
            "Fecha": fecha_formateada,
            "Tipo": tipo_emoji,
            "Detalle": mov["detalle"],
            "Categoría": mov["categoria"].upper(),
            "Monto ($)": monto_texto
        })

    balance = total_ingresos - total_egresos

    # SECCIÓN 1: BALANCE GENERAL
    st.header("📊 Resumen de tu Cuenta")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Ingresos", f"${total_ingresos:.2f}")
    col2.metric("Total Gastos", f"${total_egresos:.2f}")
    col3.metric("Saldo Disponible", f"${balance:.2f}")

    # SECCIÓN 2: GRÁFICA COMPARATIVA DIARIA
    st.subheader("📊 Comparativa Total: Ingresos vs Egresos")
    fecha_hoy = datetime.now().strftime("%d-%b")

    if total_ingresos > 0 or total_egresos > 0:
        data_grafico = {
            "Monto ($)": [total_ingresos, total_egresos],
            "Tipo": ["Ingresos", "Egresos"]
        }
        df = pd.DataFrame(data_grafico)
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
                ticktext=["Histórico"],
                range=[-1, 1]
            ),
            xaxis_title=None,
            width=500,
            height=400
        )
        st.plotly_chart(fig)
    else:
        st.info("Aún no tienes movimientos guardados en tu cuenta. ¡Agrega uno abajo para activar el gráfico!")

    # SECCIÓN 3: HISTORIAL DE MOVIMIENTOS REALES
    st.header("📜 Historial de Actividad (Base de Datos)")
    if len(historial_tabla) > 0:
        df_historial = pd.DataFrame(historial_tabla)
        st.dataframe(df_historial, use_container_width=True, hide_index=True)
    else:
        st.info("No hay transacciones registradas en tu cuenta permanente.")

        # SECCIÓN 4: ACCIONES (TUS FORMULARIOS + SECCIÓN EDUCATIVA)
        st.header("📥 Explora Polibank")

        # Añadimos la tercera pestaña para la Escuela Financiera
        tab1, tab2, tab3 = st.tabs(["💰 Registrar Ingreso", "🛒 Registrar Gasto con IA", "📚 Escuela Financiera"])

        fecha_actual_db = datetime.now().strftime("%Y-%m-%d")

        with tab1:
            with st.form("form_ingreso", clear_on_submit=True):
                monto_ingreso = st.number_input("Monto del Ingreso ($)", min_value=0.0, step=10.0)
                bot_ingreso = st.form_submit_button("Guardar Ingreso")
                if bot_ingreso and monto_ingreso > 0:
                    exito, msg = guardar_movimiento(user_id, "Ingreso", "Ingreso manual de dinero", monto_ingreso,
                                                    "INGRESOS", fecha_actual_db)
                    if exito:
                        st.success(f"¡Ingreso de ${monto_ingreso} guardado en la nube!")
                        st.rerun()
                    else:
                        st.error(msg)

        with tab2:
            with st.form("form_gasto", clear_on_submit=True):
                monto_gasto = st.number_input("Monto del Gasto ($)", min_value=0.0, step=1.0)
                texto_gasto = st.text_input("¿En qué gastaste?", placeholder="Ej: un almuerzo en el comedor de la FCSH")
                bot_gasto = st.form_submit_button("Procesar Gasto con IA")

                if bot_gasto and monto_gasto > 0 and texto_gasto:
                    with st.spinner("La IA de Polibank está clasificando tu gasto..."):
                        categoria_ia = clasificar_gasto(texto_gasto)
                        exito, msg = guardar_movimiento(user_id, "Gasto", texto_gasto, monto_gasto,
                                                        categoria_ia.upper(), fecha_actual_db)
                    if exito:
                        st.success(f"Gasto guardado en la nube. Categoría IA: **{categoria_ia.upper()}**")
                        st.rerun()
                    else:
                        st.error(msg)

        # --- NUEVA PESTAÑA: EDUCACIÓN FINANCIERA ---
        with tab3:
            st.subheader("🎓 Polibank Academy")
            st.write("Aprende a dominar tus finanzas con estos tutoriales rápidos de YouTube:")

            # Creamos dos columnas para mostrar dos videos bonitos de prueba
            col_vid1, col_vid2 = st.columns(2)

            with col_vid1:
                st.markdown("**💡 El método del ahorro inteligente**")
                # Puedes cambiar este link de YouTube por el tuyo después
                st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

            with col_vid2:
                st.markdown("**📈 ¿Qué es el Interés Compuesto?**")
                # Puedes cambiar este link de YouTube por el tuyo después
                st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

            st.markdown("---")
            st.write("📱 **¡Disfruta de más contenido interactivo en nuestra comunidad!**")

            # Botón dinámico que abre tu TikTok en una pestaña nueva
            # Recuerda cambiar 'https://www.tiktok.com/@tu_cuenta' por el link real de tu proyecto
            st.link_button("🚀 Visitar nuestro TikTok Oficial", "https://www.tiktok.com/", use_container_width=True)