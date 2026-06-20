import streamlit as st
from app.database import registrar_usuario, login_usuario, guardar_movimiento, obtener_movimientos, obtener_videos_educativos
from datetime import datetime
import pandas as pd
import plotly.express as px
from app.ai_core import clasificar_gasto

# Configuración de la página de la app
st.set_page_config(page_title="Polibank Prototipo", page_icon="🚀", layout="centered")

st.title("🏦 Polibank - Prototipo ESPOL")
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

    # Cabecera de usuario y cerrar sesión
    col_user, col_logout = st.columns([4, 1])
    with col_user:
        st.write(f"👤 Conectado como: **{correo_user}**")
    with col_logout:
        if st.button("❌ Salir"):
            del st.session_state["usuario_conectado"]
            st.rerun()

    st.write("---")

    # --- MENÚ DE NAVEGACIÓN PRINCIPAL (BOTONES/OPCIONES) ---
    # Usamos st.radio o st.sidebar para simular los botones grandes de navegación limpia
    opcion_menu = st.sidebar.radio(
        "📱 Navegación Polibank",
        ["💰 Control de Ingresos y Gastos", "📚 Educación Financiera"]
    )

    # ==========================================
    # BOTÓN/OPCIÓN 1: INGRESOS Y GASTOS
    # ==========================================
    if opcion_menu == "💰 Control de Ingresos y Gastos":

        # TRAEMOS LOS MOVIMIENTOS REALES DESDE SUPABASE
        movimientos_db = obtener_movimientos(user_id)

        # Procesamos los datos reales para las métricas y gráficas
        total_ingresos = 0.0
        total_egresos = 0.0
        historial_tabla = []

        # Diccionario para agrupar ingresos y gastos por día
        datos_por_dia = {}

        for mov in movimientos_db:
            monto_num = float(mov["monto"])
            fecha_dt = datetime.strptime(mov["fecha"], "%Y-%m-%d")
            fecha_formateada = fecha_dt.strftime("%d-%b")  # Ejemplo: 20-Jun

            # Inicializamos el día en el diccionario si no existe
            if fecha_formateada not in datos_por_dia:
                datos_por_dia[fecha_formateada] = {"Ingresos": 0.0, "Egresos": 0.0}

            if mov["tipo"] == "Ingreso":
                total_ingresos += monto_num
                tipo_emoji = "💰 Ingreso"
                monto_texto = f"+${monto_num:.2f}"
                datos_por_dia[fecha_formateada]["Ingresos"] += monto_num
            else:
                total_egresos += monto_num
                tipo_emoji = "🛒 Gasto"
                monto_texto = f"-${monto_num:.2f}"
                datos_por_dia[fecha_formateada]["Egresos"] += monto_num

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

        # SECCIÓN 2: GRÁFICA COMPARATIVA DIARIA (INTERACTIVA POR DÍAS)
        st.subheader(" Comparativa Diaria: Ingresos vs Egresos")
        if len(datos_por_dia) > 0:
            filas_grafico = []
            for fecha, montos in datos_por_dia.items():
                filas_grafico.append({"Fecha": fecha, "Monto ($)": montos["Ingresos"], "Tipo": "Ingresos"})
                filas_grafico.append({"Fecha": fecha, "Monto ($)": montos["Egresos"], "Tipo": "Egresos"})

            df_grafico = pd.DataFrame(filas_grafico)

            fig = px.bar(
                df_grafico,
                x="Fecha",
                y="Monto ($)",
                color="Tipo",
                barmode="group",
                color_discrete_map={"Ingresos": "#0052cc", "Egresos": "#ff0000"},
                text_auto='.2f'
            )

            fig.update_layout(
                xaxis_title="Días",
                yaxis_title="Monto ($)",
                legend_title="Tipo",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aún no tienes movimientos guardados en tu cuenta. ¡Agrega uno abajo para activar el gráfico!")

        # SECCIÓN 3: HISTORIAL DE MOVIMIENTOS
        st.subheader(" Historial de Movimientos")
        if len(historial_tabla) > 0:
            df_tabla = pd.DataFrame(historial_tabla)
            st.dataframe(df_tabla, use_container_width=True, hide_index=True)
        else:
            st.write("No hay transacciones registradas.")

        st.write("---")

        # SECCIÓN 4: ACCIONES (FORMULARIOS CON SELECTOR DE FECHA DINÁMICO)
        st.header("📥 Registrar Movimientos")
        tab1, tab2 = st.tabs(["💰 Registrar Ingreso", "🛒 Registrar Gasto con IA"])

        with tab1:
            with st.form("form_ingreso", clear_on_submit=True):
                monto_ingreso = st.number_input("Monto del Ingreso ($)", min_value=0.0, step=10.0)
                fecha_ingreso = st.date_input("Fecha del Ingreso", value=datetime.now())
                bot_ingreso = st.form_submit_button("Guardar Ingreso")

                if bot_ingreso and monto_ingreso > 0:
                    fecha_ingreso_db = fecha_ingreso.strftime("%Y-%m-%d")
                    exito, msg = guardar_movimiento(user_id, "Ingreso", "Ingreso manual de dinero", monto_ingreso,
                                                    "INGRESOS", fecha_ingreso_db)
                    if exito:
                        st.success(f"¡Ingreso de ${monto_ingreso} guardado para el {fecha_ingreso_db}!")
                        st.rerun()
                    else:
                        st.error(msg)

        with tab2:
            with st.form("form_gasto", clear_on_submit=True):
                monto_gasto = st.number_input("Monto del Gasto ($)", min_value=0.0, step=1.0)
                texto_gasto = st.text_input("¿En qué gastaste?", placeholder="Ej: un almuerzo en el comedor de la FCSH")
                fecha_gasto = st.date_input("Fecha del Gasto", value=datetime.now())
                bot_gasto = st.form_submit_button("Procesar Gasto con IA")

                if bot_gasto and monto_gasto > 0 and texto_gasto:
                    with st.spinner("La IA de Polibank está clasificando tu gasto..."):
                        fecha_gasto_db = fecha_gasto.strftime("%Y-%m-%d")
                        categoria_ia = clasificar_gasto(texto_gasto)
                        exito, msg = guardar_movimiento(user_id, "Gasto", texto_gasto, monto_gasto,
                                                        categoria_ia.upper(), fecha_gasto_db)
                    if exito:
                        st.success(f"Gasto guardado para el {fecha_gasto_db}. Categoría IA: **{categoria_ia.upper()}**")
                        st.rerun()
                    else:
                        st.error(msg)

    # BOTÓN/OPCIÓN 2: EDUCACIÓN FINANCIERA
    elif opcion_menu == "📚 Educación Financiera":
        st.header("📚 Academia Polibank")
        st.write("Aprende a manejar tu dinero como un profesional con nuestros videos cortos.")

        # Botón interno para ir al TikTok de la app
        st.subheader("📱 ¡Síguenos en nuestra comunidad!")
        st.link_button("🎵 Ir al TikTok de Polibank", "https://www.tiktok.com/@polibank_?lang=es-419")

        st.write("---")
        st.subheader("📺 Videos Recomendados")

        # Llamamos a los videos reales que pusiste en Supabase
        videos_db = obtener_videos_educativos()

        if len(videos_db) > 0:
            columnas = st.columns(len(videos_db))
            for i, video in enumerate(videos_db):
                with columnas[i]:
                    st.markdown(f"**{video['titulo']}**")
                    st.video(video['url_youtube'])
        else:
            st.info("El administrador aún no ha subido videos informativos. ¡Vuelve pronto!")