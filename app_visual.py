import streamlit as st
from app.database import (
    registrar_usuario, login_usuario,
    guardar_movimiento, obtener_movimientos,
    obtener_videos_educativos, eliminar_movimiento
)
from datetime import datetime, date
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from app.ai_core import clasificar_gasto

# ─────────────────────────────────────────────
# CONFIGURACIÓN GENERAL
# ─────────────────────────────────────────────
st.set_page_config(page_title="Polibank", page_icon="🐢", layout="centered")

# Colores de marca
COLOR_VERDE      = "#1B8A4C"
COLOR_VERDE_CLARO = "#27AE60"
COLOR_ROJO       = "#E74C3C"
COLOR_AZUL       = "#2E86AB"
COLOR_FONDO      = "#F4F6F9"

# CSS global: tarjetas, badges de categoría, tabla más limpia
st.markdown(f"""
<style>
  .block-container {{ padding-top: 1.5rem; }}

  /* Tarjeta métrica */
  .metric-card {{
    background: white;
    border-radius: 12px;
    padding: 18px 16px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    border-left: 4px solid {COLOR_VERDE};
  }}
  .metric-card.rojo  {{ border-left-color: {COLOR_ROJO}; }}
  .metric-card.azul  {{ border-left-color: {COLOR_AZUL}; }}
  .metric-label {{ font-size: 0.78rem; color: #666; font-weight: 600; text-transform: uppercase; letter-spacing: .5px; margin-bottom: 4px; }}
  .metric-value {{ font-size: 1.6rem; font-weight: 800; color: #1a1a1a; }}
  .metric-value.verde {{ color: {COLOR_VERDE}; }}
  .metric-value.rojo  {{ color: {COLOR_ROJO};  }}
  .metric-value.azul  {{ color: {COLOR_AZUL};  }}

  /* Badge de categoría */
  .badge {{
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: .3px;
  }}
  .badge-comida     {{ background:#FFF3CD; color:#856404; }}
  .badge-transporte {{ background:#D1ECF1; color:#0C5460; }}
  .badge-estudios   {{ background:#D4EDDA; color:#155724; }}
  .badge-diversion  {{ background:#F8D7DA; color:#721C24; }}
  .badge-otros      {{ background:#E2E3E5; color:#383D41; }}
  .badge-ingresos   {{ background:#D4EDDA; color:#155724; }}

  /* Aviso de saldo negativo */
  .alerta-negativo {{
    background: #FFF3CD; border-left: 4px solid #FFC107;
    border-radius: 8px; padding: 12px 16px; margin: 12px 0;
    font-weight: 600; color: #856404;
  }}

  /* Tip financiero */
  .tip-box {{
    background: #EAF6EE; border-left: 4px solid {COLOR_VERDE};
    border-radius: 8px; padding: 12px 16px; margin: 10px 0;
    font-size: 0.88rem; color: #1a5c34;
  }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPER: badge de categoría
# ─────────────────────────────────────────────
EMOJI_CAT = {
    "COMIDA": "🍽️", "TRANSPORTE": "🚌", "ESTUDIOS": "📚",
    "DIVERSION": "🎮", "OTROS": "📦", "INGRESOS": "💵",
    "DIVERSION": "🎮"
}

def badge(categoria: str) -> str:
    cat = categoria.upper()
    cls = f"badge-{cat.lower()}"
    emoji = EMOJI_CAT.get(cat, "📦")
    return f'<span class="badge {cls}">{emoji} {cat}</span>'


# ─────────────────────────────────────────────
# CABECERA SIEMPRE VISIBLE
# ─────────────────────────────────────────────
col_logo, col_titulo = st.columns([1, 5], vertical_alignment="center")
with col_logo:
    st.image("logo_polibank.png", width=110)
with col_titulo:
    st.title("Polibank · ESPOL")


# ═══════════════════════════════════════════════
# BLOQUE A: PANTALLA DE LOGIN / REGISTRO
# ═══════════════════════════════════════════════
if "usuario_conectado" not in st.session_state:

    tab_login, tab_registro = st.tabs(["🔒 Iniciar Sesión", "📝 Crear Cuenta"])

    with tab_login:
        st.subheader("Bienvenido de vuelta 👋")
        correo_login = st.text_input("Correo Electrónico", key="login_correo")
        pass_login   = st.text_input("Contraseña", type="password", key="login_pass")
        if st.button("Ingresar", key="btn_login_submit", use_container_width=True):
            if correo_login and pass_login:
                exito, resultado = login_usuario(correo_login, pass_login)
                if exito:
                    st.session_state["usuario_conectado"] = resultado
                    st.rerun()
                else:
                    st.error(resultado)
            else:
                st.warning("Completa todos los campos.")

    with tab_registro:
        st.subheader("Crea tu cuenta gratis 🐢")
        correo_reg = st.text_input("Correo Electrónico", key="reg_correo")
        pass_reg   = st.text_input("Contraseña (mínimo 6 caracteres)", type="password", key="reg_pass")
        if st.button("Registrarse", key="btn_reg_submit", use_container_width=True):
            if correo_reg and pass_reg:
                if len(pass_reg) < 6:
                    st.warning("La contraseña debe tener al menos 6 caracteres.")
                else:
                    exito, mensaje = registrar_usuario(correo_reg, pass_reg)
                    if exito:
                        st.success(mensaje)
                    else:
                        st.error(mensaje)
            else:
                st.warning("Completa todos los campos.")


# ═══════════════════════════════════════════════
# BLOQUE B: APP PRINCIPAL (usuario autenticado)
# ═══════════════════════════════════════════════
else:
    user_id     = st.session_state["usuario_conectado"]["id"]
    correo_user = st.session_state["usuario_conectado"]["correo"]

    # Barra superior
    col_user, col_logout = st.columns([4, 1])
    with col_user:
        st.caption(f"👤 {correo_user}")
    with col_logout:
        if st.button("Salir ❌", use_container_width=True):
            del st.session_state["usuario_conectado"]
            st.rerun()

    st.divider()

    # Menú lateral
    opcion_menu = st.sidebar.radio(
        "📱 Menú Polibank",
        ["💰 Finanzas Personales", "📚 Academia Financiera"]
    )

    # ══════════════════════════════════════════
    # SECCIÓN 1: FINANZAS PERSONALES
    # ══════════════════════════════════════════
    if opcion_menu == "💰 Finanzas Personales":

        movimientos_db = obtener_movimientos(user_id)

        # ── Calcular totales y series
        total_ingresos = 0.0
        total_egresos  = 0.0
        historial_tabla = []
        datos_por_dia   = {}
        cat_totales     = {"COMIDA": 0.0, "TRANSPORTE": 0.0, "ESTUDIOS": 0.0, "DIVERSION": 0.0, "OTROS": 0.0}

        for mov in movimientos_db:
            monto_num   = float(mov["monto"])
            fecha_dt    = datetime.strptime(mov["fecha"], "%Y-%m-%d")
            fecha_label = fecha_dt.strftime("%d-%b")

            if fecha_label not in datos_por_dia:
                datos_por_dia[fecha_label] = {"Ingresos": 0.0, "Egresos": 0.0, "_orden": fecha_dt}

            cat = mov.get("categoria", "OTROS").upper()

            if mov["tipo"] == "Ingreso":
                total_ingresos += monto_num
                datos_por_dia[fecha_label]["Ingresos"] += monto_num
                tipo_label  = "💵 Ingreso"
                monto_texto = f"+${monto_num:.2f}"
            else:
                total_egresos += monto_num
                datos_por_dia[fecha_label]["Egresos"] += monto_num
                tipo_label  = "🛒 Gasto"
                monto_texto = f"-${monto_num:.2f}"
                key_cat = cat if cat in cat_totales else "OTROS"
                cat_totales[key_cat] += monto_num

            historial_tabla.append({
                "Fecha":     fecha_label,
                "Tipo":      tipo_label,
                "Detalle":   mov["detalle"],
                "Categoría": cat,
                "Monto ($)": monto_texto,
                "_id":       mov.get("id"),
                "_fecha_dt": fecha_dt
            })

        balance = total_ingresos - total_egresos

        # ── MÉTRICAS (tarjetas custom)
        st.subheader("📊 Resumen de tu Cuenta")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-label">Total Ingresos</div>
              <div class="metric-value verde">${total_ingresos:,.2f}</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-card rojo">
              <div class="metric-label">Total Gastos</div>
              <div class="metric-value rojo">${total_egresos:,.2f}</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            color_bal = "verde" if balance >= 0 else "rojo"
            st.markdown(f"""
            <div class="metric-card azul">
              <div class="metric-label">Saldo Disponible</div>
              <div class="metric-value {color_bal}">${balance:,.2f}</div>
            </div>""", unsafe_allow_html=True)

        # Alerta si el saldo es negativo
        if balance < 0:
            st.markdown(f"""
            <div class="alerta-negativo">
              ⚠️ Tu saldo está en negativo (${balance:,.2f}). Revisa tus gastos y considera reducir la categoría
              con mayor consumo.
            </div>""", unsafe_allow_html=True)

        # Tip financiero dinámico
        if total_egresos > 0 and total_ingresos > 0:
            pct_ahorro = ((total_ingresos - total_egresos) / total_ingresos) * 100
            if pct_ahorro >= 20:
                tip = f"🎉 ¡Excelente! Estás ahorrando el {pct_ahorro:.0f}% de tus ingresos. ¡Sigue así!"
            elif pct_ahorro > 0:
                tip = f"💡 Estás ahorrando el {pct_ahorro:.0f}% de tus ingresos. La meta recomendada es el 20%."
            else:
                tip = "📉 Estás gastando más de lo que ganas. Intenta identificar gastos no esenciales."
            st.markdown(f'<div class="tip-box">{tip}</div>', unsafe_allow_html=True)

        st.write("")

        # ── GRÁFICAS (tabs para no apilar)
        if len(datos_por_dia) > 0:
            tab_barras, tab_pie, tab_linea = st.tabs(
                ["📊 Ingresos vs Gastos", "🥧 Gastos por Categoría", "📈 Tendencia de Saldo"]
            )

            # Ordenamos el diccionario por fecha real
            dias_ordenados = sorted(datos_por_dia.items(), key=lambda x: x[1]["_orden"])

            with tab_barras:
                filas = []
                for fecha_lbl, montos in dias_ordenados:
                    filas.append({"Fecha": fecha_lbl, "Monto ($)": montos["Ingresos"], "Tipo": "Ingresos"})
                    filas.append({"Fecha": fecha_lbl, "Monto ($)": montos["Egresos"],  "Tipo": "Egresos"})
                df_bar = pd.DataFrame(filas)
                fig_bar = px.bar(
                    df_bar, x="Fecha", y="Monto ($)", color="Tipo", barmode="group",
                    color_discrete_map={"Ingresos": COLOR_VERDE_CLARO, "Egresos": COLOR_ROJO},
                    text_auto='.2f'
                )
                fig_bar.update_layout(height=380, xaxis_title="Día", yaxis_title="Monto ($)",
                                      legend_title="Tipo", plot_bgcolor="white")
                st.plotly_chart(fig_bar, use_container_width=True)

            with tab_pie:
                # Solo categorías con gasto > 0
                cat_filtradas = {k: v for k, v in cat_totales.items() if v > 0}
                if cat_filtradas:
                    fig_pie = px.pie(
                        values=list(cat_filtradas.values()),
                        names=list(cat_filtradas.keys()),
                        color_discrete_sequence=px.colors.qualitative.Set2,
                        hole=0.38
                    )
                    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                    fig_pie.update_layout(height=360, showlegend=True)
                    st.plotly_chart(fig_pie, use_container_width=True)

                    # Categoría con mayor gasto
                    cat_max = max(cat_filtradas, key=cat_filtradas.get)
                    st.markdown(
                        f'<div class="tip-box">💡 Tu mayor gasto es en <strong>{cat_max}</strong> '
                        f'(${cat_filtradas[cat_max]:,.2f}). ¿Puedes reducirlo?</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.info("Aún no hay gastos para mostrar por categoría.")

            with tab_linea:
                # Línea de saldo acumulado día a día
                saldo_acum = 0.0
                puntos = []
                for fecha_lbl, montos in dias_ordenados:
                    saldo_acum += montos["Ingresos"] - montos["Egresos"]
                    puntos.append({"Fecha": fecha_lbl, "Saldo ($)": saldo_acum})
                df_linea = pd.DataFrame(puntos)
                fig_linea = px.line(
                    df_linea, x="Fecha", y="Saldo ($)",
                    markers=True,
                    color_discrete_sequence=[COLOR_AZUL]
                )
                fig_linea.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5)
                fig_linea.update_layout(height=360, plot_bgcolor="white",
                                        xaxis_title="Día", yaxis_title="Saldo acumulado ($)")
                st.plotly_chart(fig_linea, use_container_width=True)
        else:
            st.info("⬇️ Aún no tienes movimientos. ¡Agrega uno abajo para activar las gráficas!")

        st.divider()

        # ── HISTORIAL DE MOVIMIENTOS
        st.subheader("🗒️ Historial de Movimientos")

        if historial_tabla:
            # Ordenar por fecha más reciente primero
            historial_tabla.sort(key=lambda x: x["_fecha_dt"], reverse=True)

            # Filtro por tipo
            filtro = st.selectbox("Filtrar por tipo:", ["Todos", "💵 Ingreso", "🛒 Gasto"], key="filtro_hist")
            lista_filtrada = [m for m in historial_tabla if filtro == "Todos" or m["Tipo"] == filtro]

            if lista_filtrada:
                for mov in lista_filtrada:
                    col_info, col_del = st.columns([10, 1])
                    with col_info:
                        es_ingreso = mov["Tipo"] == "💵 Ingreso"
                        color_monto = COLOR_VERDE if es_ingreso else COLOR_ROJO
                        st.markdown(
                            f"**{mov['Fecha']}** · {badge(mov['Categoría'])} "
                            f"&nbsp;{mov['Detalle']}&nbsp; "
                            f"<span style='color:{color_monto}; font-weight:800'>{mov['Monto ($)']}</span>",
                            unsafe_allow_html=True
                        )
                    with col_del:
                        if mov.get("_id") and st.button("🗑️", key=f"del_{mov['_id']}", help="Eliminar"):
                            ok, _ = eliminar_movimiento(mov["_id"])
                            if ok:
                                st.rerun()
            else:
                st.write("No hay movimientos con ese filtro.")
        else:
            st.write("No hay transacciones registradas aún.")

        st.divider()

        # ── REGISTRAR MOVIMIENTOS
        st.subheader("➕ Registrar Movimiento")
        tab_ing, tab_gas = st.tabs(["💵 Registrar Ingreso", "🛒 Registrar Gasto con IA"])

        with tab_ing:
            with st.form("form_ingreso", clear_on_submit=True):
                monto_ingreso  = st.number_input("Monto ($)", min_value=0.01, step=10.0)
                fuente_ingreso = st.text_input(
                    "Fuente del ingreso",
                    placeholder="Ej: Beca ESPOL, Trabajo freelance, Mesada mensual…"
                )
                fecha_ingreso  = st.date_input("Fecha", value=date.today())
                if st.form_submit_button("💾 Guardar Ingreso", use_container_width=True):
                    if monto_ingreso > 0:
                        detalle = fuente_ingreso.strip() or "Ingreso manual"
                        exito, msg = guardar_movimiento(
                            user_id, "Ingreso", detalle,
                            monto_ingreso, "INGRESOS",
                            fecha_ingreso.strftime("%Y-%m-%d")
                        )
                        if exito:
                            st.success(f"✅ Ingreso de ${monto_ingreso:.2f} guardado correctamente.")
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("El monto debe ser mayor a $0.")

        with tab_gas:
            with st.form("form_gasto", clear_on_submit=True):
                monto_gasto = st.number_input("Monto ($)", min_value=0.01, step=1.0)
                texto_gasto = st.text_input(
                    "¿En qué gastaste?",
                    placeholder="Ej: Almuerzo en el comedor FCSH, Bus de Guayaquil a Samborondón…"
                )
                fecha_gasto = st.date_input("Fecha", value=date.today())
                if st.form_submit_button("🤖 Clasificar con IA y Guardar", use_container_width=True):
                    if monto_gasto > 0 and texto_gasto.strip():
                        with st.spinner("La IA de Polibank está clasificando tu gasto…"):
                            categoria_ia = clasificar_gasto(texto_gasto)
                            exito, msg   = guardar_movimiento(
                                user_id, "Gasto", texto_gasto,
                                monto_gasto, categoria_ia.upper(),
                                fecha_gasto.strftime("%Y-%m-%d")
                            )
                        if exito:
                            st.success(
                                f"✅ Gasto guardado · Categoría detectada: **{categoria_ia.upper()}** "
                                f"{EMOJI_CAT.get(categoria_ia.upper(), '📦')}"
                            )
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("Completa el monto y la descripción del gasto.")

    # ══════════════════════════════════════════
    # SECCIÓN 2: ACADEMIA FINANCIERA
    # ══════════════════════════════════════════
    elif opcion_menu == "📚 Academia Financiera":

        st.header("📚 Academia Polibank")
        st.write("Aprende a manejar tu dinero como un profesional con videos cortos y prácticos.")

        # CTA a TikTok
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#010101,#69C9D0);
                    border-radius:12px; padding:20px; text-align:center; margin-bottom:20px;">
          <div style="color:white; font-size:1.1rem; font-weight:700; margin-bottom:8px;">
            📱 ¡Síguenos en TikTok para contenido nuevo cada semana!
          </div>
          <div style="color:#ddd; font-size:0.85rem;">@polibank_ · Tips de finanzas para universitarios</div>
        </div>
        """, unsafe_allow_html=True)

        col_tik, _, _ = st.columns([1, 1, 1])
        with col_tik:
            st.link_button(
                "🎵 Ir al TikTok de Polibank",
                "https://www.tiktok.com/@polibank_?lang=es-419",
                use_container_width=True
            )

        st.divider()

        # Videos
        st.subheader("📺 Videos Recomendados")
        videos_db = obtener_videos_educativos()

        if videos_db:
            # Máximo 2 columnas para que no se rompan en pantallas pequeñas
            for i in range(0, len(videos_db), 2):
                cols = st.columns(min(2, len(videos_db) - i))
                for j, col in enumerate(cols):
                    if i + j < len(videos_db):
                        video = videos_db[i + j]
                        with col:
                            st.markdown(f"**{video['titulo']}**")
                            st.video(video['url_youtube'])
                st.write("")
        else:
            st.info("📭 Aún no hay videos publicados. ¡Vuelve pronto!")

        st.divider()

        # Glosario básico de conceptos financieros
        st.subheader("📖 Conceptos Clave")
        conceptos = {
            "💰 Presupuesto": "Plan para distribuir tus ingresos en gastos, ahorro e inversión antes de gastar.",
            "📈 Interés compuesto": "Ganar interés sobre tus intereses. Einstein lo llamó 'la octava maravilla del mundo'.",
            "🛡️ Fondo de emergencia": "Ahorro equivalente a 3–6 meses de gastos para imprevistos.",
            "📊 Regla 50/30/20": "50% necesidades · 30% gustos · 20% ahorro. Un modelo simple para empezar.",
            "🏦 Inversión": "Poner tu dinero a trabajar para ti: acciones, fondos mutuos, ETFs, etc.",
            "💳 Deuda buena vs mala": "Deuda buena genera valor (estudios, negocio). Deuda mala financia consumo que pierde valor.",
        }
        for titulo, descripcion in conceptos.items():
            with st.expander(titulo):
                st.write(descripcion)