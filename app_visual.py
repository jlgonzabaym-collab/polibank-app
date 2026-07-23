import streamlit as st
from app.database import (
    registrar_usuario, login_usuario,
    guardar_movimiento, obtener_movimientos,
    obtener_videos_educativos, eliminar_movimiento
)
from app.gamificacion import registrar_accion, obtener_estado, BADGES
from datetime import datetime, date
import pandas as pd
import plotly.express as px
from app.ai_core import clasificar_gasto
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY
import uuid
import json
from streamlit_cookies_manager import EncryptedCookieManager
from academia_ui import render_academia

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
st.set_page_config(page_title="Polibank", page_icon="🐢", layout="centered")

COLOR_VERDE       = "#1B8A4C"
COLOR_VERDE_CLARO = "#27AE60"
COLOR_ROJO        = "#E74C3C"
COLOR_AZUL        = "#2E86AB"
COLOR_ORO         = "#F39C12"

supabase_client = create_client(SUPABASE_URL.strip().rstrip('/'), SUPABASE_KEY.strip())

# ── COOKIES para mantener sesión al refrescar
cookies = EncryptedCookieManager(prefix="polibank_", password="polibank_espol_2024_secret")
if not cookies.ready():
    st.stop()

st.markdown(f"""
<style>
  .block-container {{ padding-top: 1.5rem; }}
  .metric-card {{
    background: white; border-radius: 12px; padding: 18px 16px;
    text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    border-left: 4px solid {COLOR_VERDE};
  }}
  .metric-card.rojo {{ border-left-color: {COLOR_ROJO}; }}
  .metric-card.azul {{ border-left-color: {COLOR_AZUL}; }}
  .metric-label {{ font-size:0.78rem; color:#666; font-weight:600; text-transform:uppercase; letter-spacing:.5px; margin-bottom:4px; }}
  .metric-value {{ font-size:1.6rem; font-weight:800; color:#1a1a1a; }}
  .metric-value.verde {{ color:{COLOR_VERDE}; }}
  .metric-value.rojo  {{ color:{COLOR_ROJO};  }}
  .metric-value.azul  {{ color:{COLOR_AZUL};  }}
  .badge-cat {{ display:inline-block; padding:2px 10px; border-radius:20px; font-size:0.72rem; font-weight:700; }}
  .badge-comida     {{ background:#FFF3CD; color:#856404; }}
  .badge-transporte {{ background:#D1ECF1; color:#0C5460; }}
  .badge-estudios   {{ background:#D4EDDA; color:#155724; }}
  .badge-diversion  {{ background:#F8D7DA; color:#721C24; }}
  .badge-otros      {{ background:#E2E3E5; color:#383D41; }}
  .badge-ingresos   {{ background:#D4EDDA; color:#155724; }}
  .alerta-negativo {{
    background:#FFF3CD; border-left:4px solid #FFC107; border-radius:8px;
    padding:12px 16px; margin:12px 0; font-weight:600; color:#856404;
  }}
  .tip-box {{
    background:#EAF6EE; border-left:4px solid {COLOR_VERDE}; border-radius:8px;
    padding:12px 16px; margin:10px 0; font-size:0.88rem; color:#1a5c34;
  }}
  .mov-row {{
    background: white; border-radius: 10px; padding: 12px 16px;
    margin-bottom: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.07);
    border-left: 3px solid #e8e8e8;
  }}
  .mov-row.ingreso {{ border-left-color: {COLOR_VERDE}; }}
  .mov-row.gasto   {{ border-left-color: {COLOR_ROJO}; }}
  .mov-detalle  {{ font-size:0.88rem; color:#555; }}
  .mov-monto    {{ font-size:1.05rem; font-weight:800; }}
  /* GAMIFICACIÓN */
  .gami-hero {{
    background: linear-gradient(135deg, #1B8A4C, #27AE60);
    border-radius: 16px; padding: 24px; color: white; margin-bottom: 20px;
  }}
  .gami-stat-grid {{
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px;
  }}
  .gami-stat {{
    background: white; border-radius: 10px; padding: 14px;
    text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  }}
  .gami-stat-val {{ font-size: 1.9rem; font-weight: 800; line-height: 1.1; }}
  .gami-stat-lbl {{ font-size: 0.72rem; color: #888; font-weight: 600; text-transform: uppercase; margin-top: 4px; }}
  .xp-bar-wrap {{
    background: rgba(255,255,255,0.25); border-radius: 20px; height: 10px;
    margin: 10px 0 6px; overflow: hidden;
  }}
  .xp-bar-fill {{ height: 10px; border-radius: 20px; background: white; }}
  .nivel-pill {{
    display: inline-block; background: rgba(255,255,255,0.2); border-radius: 20px;
    padding: 3px 14px; font-size: 0.8rem; font-weight: 700; margin-left: 10px;
  }}
  .badge-grid {{
    display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 12px; margin-top: 12px;
  }}
  .badge-card {{
    background: white; border-radius: 12px; padding: 14px 10px;
    text-align: center; border: 2px solid #e8e8e8;
  }}
  .badge-card.desbloqueado {{ border-color: {COLOR_VERDE}; background: #f0faf4; }}
  .badge-card.bloqueado    {{ opacity: 0.4; }}
  .badge-emoji  {{ font-size: 2rem; margin-bottom: 6px; }}
  .badge-nombre {{ font-size: 0.78rem; font-weight: 700; color: #333; }}
  .badge-desc   {{ font-size: 0.66rem; color: #888; margin-top: 3px; }}
  .toast-nuevo {{
    background: {COLOR_VERDE}; color: white; border-radius: 10px;
    padding: 12px 18px; margin: 6px 0; font-weight: 700; font-size: 0.95rem;
  }}
  .sidebar-gami {{
    background:#f0faf4; border-radius:10px; padding:12px; text-align:center;
    margin-bottom:16px; border: 1px solid #c3e6cb;
  }}
</style>
""", unsafe_allow_html=True)

EMOJI_CAT = {
    "COMIDA":"🍽️", "TRANSPORTE":"🚌", "ESTUDIOS":"📚",
    "DIVERSION":"🎮", "OTROS":"📦", "INGRESOS":"💵"
}

def badge_cat(categoria: str) -> str:
    cat = categoria.upper()
    return f'<span class="badge-cat badge-{cat.lower()}">{EMOJI_CAT.get(cat,"📦")} {cat}</span>'

def subir_factura(archivo, usuario_id: int, mov_descripcion: str) -> str | None:
    """Sube una imagen al bucket 'facturas' de Supabase Storage y devuelve la URL pública."""
    try:
        extension = archivo.name.split(".")[-1].lower()
        nombre_archivo = f"{usuario_id}/{uuid.uuid4()}.{extension}"
        contenido = archivo.read()
        supabase_client.storage.from_("facturas").upload(
            path=nombre_archivo,
            file=contenido,
            file_options={"content-type": archivo.type}
        )
        url_publica = supabase_client.storage.from_("facturas").get_public_url(nombre_archivo)
        return url_publica
    except Exception as e:
        print(f"Error subiendo factura: {e}")
        return None


# ─────────────────────────────────────────────
# CABECERA
# ─────────────────────────────────────────────
col_logo, col_titulo = st.columns([1, 5], vertical_alignment="center")
with col_logo:
    st.image("logo_polibank.png", width=110)
with col_titulo:
    st.title("Polibank · ESPOL")

# ── Restaurar sesión desde cookie si existe
if "usuario_conectado" not in st.session_state:
    cookie_usuario = cookies.get("usuario")
    if cookie_usuario:
        try:
            st.session_state["usuario_conectado"] = json.loads(cookie_usuario)
        except Exception:
            pass

# ═══════════════════════════════════════════════
# BLOQUE A: LOGIN / REGISTRO
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
                    cookies["usuario"] = json.dumps(resultado)
                    cookies.save()
                    registrar_accion(resultado["id"], "login")
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
                    st.success(mensaje) if exito else st.error(mensaje)
            else:
                st.warning("Completa todos los campos.")


# ═══════════════════════════════════════════════
# BLOQUE B: APP PRINCIPAL
# ═══════════════════════════════════════════════
else:
    user_id     = st.session_state["usuario_conectado"]["id"]
    correo_user = st.session_state["usuario_conectado"]["correo"]

    col_user, col_logout = st.columns([4, 1])
    with col_user:
        st.caption(f"👤 {correo_user}")
    with col_logout:
        if st.button("Salir ❌", use_container_width=True):
            del st.session_state["usuario_conectado"]
            cookies["usuario"] = ""
            cookies.save()
            st.rerun()

    st.divider()

    # Mini widget sidebar
    gami = obtener_estado(user_id)
    racha_emoji = "🔥" if gami["racha_viva"] else "💤"
    st.sidebar.markdown(f"""
    <div class="sidebar-gami">
      <div style="font-size:0.7rem;color:#555;font-weight:700;text-transform:uppercase;letter-spacing:.5px;">Tu progreso</div>
      <div style="font-size:1.6rem;font-weight:800;color:#1B8A4C;margin:4px 0;">{racha_emoji} {gami['racha_actual']} días</div>
      <div style="font-size:0.75rem;color:#888;">⭐ {gami['xp_total']} XP · Nivel {gami['nivel']} {gami['nivel_nombre']}</div>
    </div>
    """, unsafe_allow_html=True)

    opcion_menu = st.sidebar.radio(
        "📱 Menú Polibank",
        ["💰 Finanzas Personales", "🏆 Mi Progreso", "📚 Academia Financiera"]
    )

    # Notificación de badges nuevos
    if "gami_notif" in st.session_state:
        notif = st.session_state.pop("gami_notif")
        for b in notif.get("badges_nuevos", []):
            info = BADGES.get(b, {})
            st.markdown(
                f'<div class="toast-nuevo">🏅 ¡Nuevo logro! {info.get("emoji","")} '
                f'<strong>{info.get("nombre","")}</strong> — {info.get("desc","")}</div>',
                unsafe_allow_html=True
            )


    # ══════════════════════════════════════════
    # SECCIÓN 1: FINANZAS PERSONALES
    # ══════════════════════════════════════════
    if opcion_menu == "💰 Finanzas Personales":

        movimientos_db = obtener_movimientos(user_id)

        # Calcular totales
        total_ingresos = 0.0
        total_egresos  = 0.0
        historial_tabla = []
        datos_por_dia   = {}
        cat_totales     = {"COMIDA":0.0,"TRANSPORTE":0.0,"ESTUDIOS":0.0,"DIVERSION":0.0,"OTROS":0.0}

        for mov in movimientos_db:
            monto_num   = float(mov["monto"])
            fecha_dt    = datetime.strptime(mov["fecha"], "%Y-%m-%d")
            fecha_label = fecha_dt.strftime("%d-%b")
            if fecha_label not in datos_por_dia:
                datos_por_dia[fecha_label] = {"Ingresos":0.0,"Egresos":0.0,"_orden":fecha_dt}
            cat = mov.get("categoria","OTROS").upper()
            if mov["tipo"] == "Ingreso":
                total_ingresos += monto_num
                datos_por_dia[fecha_label]["Ingresos"] += monto_num
                tipo_label = "💵 Ingreso"; monto_texto = f"+${monto_num:.2f}"
            else:
                total_egresos += monto_num
                datos_por_dia[fecha_label]["Egresos"] += monto_num
                tipo_label = "🛒 Gasto"; monto_texto = f"-${monto_num:.2f}"
                cat_totales[cat if cat in cat_totales else "OTROS"] += monto_num
            historial_tabla.append({
                "Fecha": fecha_label, "Tipo": tipo_label, "Detalle": mov["detalle"],
                "Categoría": cat, "Monto ($)": monto_texto,
                "_id": mov.get("id"), "_fecha_dt": fecha_dt,
                "_monto_num": monto_num, "_fecha_raw": mov["fecha"],
                "_factura_url": mov.get("factura_url")
            })

        balance = total_ingresos - total_egresos

        # ── MÉTRICAS
        st.subheader("📊 Resumen de tu Cuenta")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Ingresos</div><div class="metric-value verde">${total_ingresos:,.2f}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card rojo"><div class="metric-label">Gastos</div><div class="metric-value rojo">${total_egresos:,.2f}</div></div>', unsafe_allow_html=True)
        with c3:
            color_bal = "verde" if balance >= 0 else "rojo"
            st.markdown(f'<div class="metric-card azul"><div class="metric-label">Saldo</div><div class="metric-value {color_bal}">${balance:,.2f}</div></div>', unsafe_allow_html=True)

        if balance < 0:
            st.markdown('<div class="alerta-negativo">⚠️ Tu saldo está en negativo. Revisa tus gastos.</div>', unsafe_allow_html=True)

        if total_ingresos > 0 and total_egresos > 0:
            pct = ((total_ingresos - total_egresos) / total_ingresos) * 100
            if pct >= 20:   tip = f"🎉 Estás ahorrando el {pct:.0f}% de tus ingresos. ¡Excelente!"
            elif pct > 0:   tip = f"💡 Ahorras el {pct:.0f}%. La meta recomendada es el 20%."
            else:           tip = "📉 Gastas más de lo que ganas. Identifica gastos no esenciales."
            st.markdown(f'<div class="tip-box">{tip}</div>', unsafe_allow_html=True)

        st.write("")

        # ── GRÁFICAS
        if datos_por_dia:
            tab_barras, tab_categorias, tab_linea = st.tabs(
                ["📊 Ingresos vs Gastos", "📊 Gastos por Categoría", "📈 Saldo Acumulado"]
            )
            dias_ord = sorted(datos_por_dia.items(), key=lambda x: x[1]["_orden"])

            with tab_barras:
                filas = []
                for fl, m in dias_ord:
                    filas += [{"Fecha":fl,"Monto ($)":m["Ingresos"],"Tipo":"Ingresos"},
                               {"Fecha":fl,"Monto ($)":m["Egresos"],"Tipo":"Egresos"}]
                fig = px.bar(pd.DataFrame(filas), x="Fecha", y="Monto ($)", color="Tipo",
                             barmode="group", text_auto='.2f',
                             color_discrete_map={"Ingresos":COLOR_VERDE_CLARO,"Egresos":COLOR_ROJO})
                fig.update_layout(height=360, plot_bgcolor="white")
                st.plotly_chart(fig, use_container_width=True)

            with tab_categorias:
                # Barras horizontales por categoría
                cat_f = {k:v for k,v in cat_totales.items() if v > 0}
                if cat_f:
                    df_cat = pd.DataFrame([
                        {"Categoría": f"{EMOJI_CAT.get(k,'📦')} {k}", "Monto ($)": v}
                        for k, v in sorted(cat_f.items(), key=lambda x: x[1], reverse=True)
                    ])
                    fig_cat = px.bar(
                        df_cat, x="Monto ($)", y="Categoría", orientation="h",
                        text_auto='.2f',
                        color="Monto ($)",
                        color_continuous_scale=["#27AE60","#F39C12","#E74C3C"]
                    )
                    fig_cat.update_layout(
                        height=320, plot_bgcolor="white",
                        showlegend=False, coloraxis_showscale=False,
                        yaxis={"categoryorder":"total ascending"}
                    )
                    fig_cat.update_traces(textposition="outside")
                    st.plotly_chart(fig_cat, use_container_width=True)
                    cat_max = max(cat_f, key=cat_f.get)
                    st.markdown(f'<div class="tip-box">💡 Mayor gasto: <strong>{cat_max}</strong> (${cat_f[cat_max]:,.2f})</div>', unsafe_allow_html=True)
                else:
                    st.info("Aún no hay gastos para mostrar.")

            with tab_linea:
                saldo_acum = 0.0; puntos = []
                for fl, m in dias_ord:
                    saldo_acum += m["Ingresos"] - m["Egresos"]
                    puntos.append({"Fecha":fl,"Saldo ($)":saldo_acum})
                fig3 = px.line(pd.DataFrame(puntos), x="Fecha", y="Saldo ($)", markers=True,
                               color_discrete_sequence=[COLOR_AZUL])
                fig3.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5)
                fig3.update_layout(height=340, plot_bgcolor="white")
                st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("⬇️ Aún no tienes movimientos. ¡Agrega uno abajo!")

        st.divider()

        # ══════════════════════════════════════════
        # REGISTRAR MOVIMIENTOS (ahora arriba del historial)
        # ══════════════════════════════════════════
        st.subheader("➕ Registrar Movimiento")
        tab_ing, tab_gas = st.tabs(["💵 Ingreso", "🛒 Gasto con IA"])

        with tab_ing:
            with st.form("form_ingreso", clear_on_submit=True):
                monto_ing  = st.number_input("Monto ($)", min_value=0.01, step=10.0)
                fuente_ing = st.text_input("Fuente", placeholder="Beca ESPOL, Trabajo, Mesada…")
                fecha_ing  = st.date_input("Fecha", value=date.today())
                factura_ing = st.file_uploader(
                    "📎 Adjuntar factura (opcional)",
                    type=["jpg","jpeg","png","pdf"],
                    key="factura_ing"
                )
                if st.form_submit_button("💾 Guardar Ingreso", use_container_width=True):
                    if monto_ing > 0:
                        # Subir factura si hay
                        url_factura = None
                        if factura_ing:
                            with st.spinner("Subiendo factura…"):
                                url_factura = subir_factura(factura_ing, user_id, fuente_ing)

                        exito, msg = guardar_movimiento(
                            user_id, "Ingreso",
                            fuente_ing.strip() or "Ingreso manual",
                            monto_ing, "INGRESOS",
                            fecha_ing.strftime("%Y-%m-%d"),
                            factura_url=url_factura
                        )
                        if exito:
                            res_gami = registrar_accion(user_id, "ingreso", {
                                "_saldo_positivo": (total_ingresos + monto_ing - total_egresos) > 0
                            })
                            st.session_state["gami_notif"] = res_gami
                            msg_ok = f"✅ Ingreso de ${monto_ing:.2f} guardado · +{res_gami['xp_ganado']} XP ⭐"
                            if url_factura:
                                msg_ok += " · 📎 Factura guardada"
                            st.success(msg_ok)
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("El monto debe ser mayor a $0.")

        with tab_gas:
            with st.form("form_gasto", clear_on_submit=True):
                monto_gas  = st.number_input("Monto ($)", min_value=0.01, step=1.0)
                texto_gas  = st.text_input("¿En qué gastaste?", placeholder="Almuerzo comedor FCSH, bus Guayaquil…")
                fecha_gas  = st.date_input("Fecha", value=date.today())
                factura_gas = st.file_uploader(
                    "📎 Adjuntar factura (opcional)",
                    type=["jpg","jpeg","png","pdf"],
                    key="factura_gas"
                )
                if st.form_submit_button("🤖 Clasificar con IA y Guardar", use_container_width=True):
                    if monto_gas > 0 and texto_gas.strip():
                        with st.spinner("Clasificando con IA…"):
                            cat_ia = clasificar_gasto(texto_gas)

                        url_factura = None
                        if factura_gas:
                            with st.spinner("Subiendo factura…"):
                                url_factura = subir_factura(factura_gas, user_id, texto_gas)

                        exito, msg = guardar_movimiento(
                            user_id, "Gasto", texto_gas,
                            monto_gas, cat_ia.upper(),
                            fecha_gas.strftime("%Y-%m-%d"),
                            factura_url=url_factura
                        )
                        if exito:
                            res_gami = registrar_accion(user_id, "gasto")
                            st.session_state["gami_notif"] = res_gami
                            msg_ok = (
                                f"✅ Gasto guardado · Categoría: **{cat_ia.upper()}** "
                                f"{EMOJI_CAT.get(cat_ia.upper(),'📦')} · +{res_gami['xp_ganado']} XP ⭐"
                            )
                            if url_factura:
                                msg_ok += " · 📎 Factura guardada"
                            st.success(msg_ok)
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("Completa el monto y la descripción.")

        st.divider()

        # ══════════════════════════════════════════
        # HISTORIAL COMPACTO CON BÚSQUEDA POR FECHA
        # ══════════════════════════════════════════
        st.subheader("🗒️ Historial de Movimientos")

        if historial_tabla:
            historial_tabla.sort(key=lambda x: x["_fecha_dt"], reverse=True)

            # Filtros en una fila
            col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
            with col_f1:
                filtro_tipo = st.selectbox("Tipo", ["Todos","💵 Ingreso","🛒 Gasto"], key="filtro_tipo")
            with col_f2:
                fecha_desde = st.date_input("Desde", value=None, key="fecha_desde")
            with col_f3:
                fecha_hasta = st.date_input("Hasta", value=None, key="fecha_hasta")

            # Aplicar filtros
            lista = historial_tabla.copy()
            if filtro_tipo != "Todos":
                lista = [m for m in lista if m["Tipo"] == filtro_tipo]
            if fecha_desde:
                lista = [m for m in lista if m["_fecha_dt"].date() >= fecha_desde]
            if fecha_hasta:
                lista = [m for m in lista if m["_fecha_dt"].date() <= fecha_hasta]

            st.caption(f"Mostrando {min(len(lista), 8)} de {len(lista)} transacciones")

            # Mostrar máximo 8 filas, el resto con expander
            def render_mov(mov):
                es_ingreso  = mov["Tipo"] == "💵 Ingreso"
                color_m     = COLOR_VERDE if es_ingreso else COLOR_ROJO
                clase       = "ingreso" if es_ingreso else "gasto"
                tiene_factura = bool(mov.get("_factura_url"))
                icono_factura = " 📎" if tiene_factura else ""

                # Fila principal: info + botón eliminar
                col_info, col_del = st.columns([11, 1])
                with col_info:
                    st.markdown(
                        f'<div class="mov-row {clase}">'
                        f'<span style="font-size:0.78rem;color:#999;">{mov["Fecha"]}</span> '
                        f'{badge_cat(mov["Categoría"])} '
                        f'<span class="mov-detalle">{mov["Detalle"]}{icono_factura}</span>'
                        f'<span class="mov-monto" style="color:{color_m};float:right;">{mov["Monto ($)"]}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                with col_del:
                    st.write("")
                    if mov.get("_id") and st.button("🗑️", key=f"del_{mov['_id']}"):
                        ok, _ = eliminar_movimiento(mov["_id"])
                        if ok:
                            st.rerun()

                # Panel de factura expandible debajo de la fila
                if tiene_factura:
                    url = mov["_factura_url"]
                    with st.expander("📎 Ver factura adjunta"):
                        # Detectar si es PDF o imagen por la URL
                        if url.lower().endswith(".pdf"):
                            st.markdown(
                                f'<a href="{url}" target="_blank" style="font-weight:600;color:{COLOR_VERDE};">'
                                f'📄 Abrir PDF en nueva pestaña</a>',
                                unsafe_allow_html=True
                            )
                        else:
                            # Mostrar imagen directamente
                            st.image(url, use_container_width=True)
                            st.markdown(
                                f'<a href="{url}" target="_blank" style="font-size:0.8rem;color:#888;">Ver en tamaño completo ↗</a>',
                                unsafe_allow_html=True
                            )

            # Primeros 8 visibles
            for mov in lista[:8]:
                render_mov(mov)

            # El resto dentro de un expander
            if len(lista) > 8:
                with st.expander(f"Ver {len(lista) - 8} transacciones más…"):
                    for mov in lista[8:]:
                        render_mov(mov)
        else:
            st.info("No hay transacciones registradas aún.")


    # ══════════════════════════════════════════
    # SECCIÓN 2: MI PROGRESO
    # ══════════════════════════════════════════
    elif opcion_menu == "🏆 Mi Progreso":

        gami = obtener_estado(user_id)
        racha_emoji = "🔥" if gami["racha_viva"] else "💤"

        st.markdown(f"""
        <div class="gami-hero">
          <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;flex-wrap:wrap;">
            <span style="font-size:2.8rem;">{racha_emoji}</span>
            <div>
              <div style="font-size:0.9rem;font-weight:500;opacity:.8;">Racha actual</div>
              <div style="font-size:2.6rem;font-weight:800;line-height:1;">{gami['racha_actual']} días</div>
            </div>
            <span class="nivel-pill">Nivel {gami['nivel']} · {gami['nivel_nombre']}</span>
          </div>
          <div style="font-size:0.82rem;opacity:.8;margin-bottom:6px;">
            Progreso al siguiente nivel — {gami['xp_total']} / {gami['xp_siguiente']} XP
          </div>
          <div class="xp-bar-wrap">
            <div class="xp-bar-fill" style="width:{gami['progreso_pct']}%;"></div>
          </div>
          <div style="font-size:0.75rem;opacity:.65;">{gami['progreso_pct']}% completado</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="gami-stat-grid">
          <div class="gami-stat">
            <div class="gami-stat-val" style="color:{COLOR_ORO};">⭐ {gami['xp_total']}</div>
            <div class="gami-stat-lbl">XP Total</div>
          </div>
          <div class="gami-stat">
            <div class="gami-stat-val" style="color:{COLOR_ROJO};">🔥 {gami['racha_actual']}</div>
            <div class="gami-stat-lbl">Racha Actual</div>
          </div>
          <div class="gami-stat">
            <div class="gami-stat-val" style="color:{COLOR_AZUL};">🏅 {len(gami['badges'])}/{len(BADGES)}</div>
            <div class="gami-stat-lbl">Logros</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if not gami["racha_viva"] and gami["racha_actual"] == 0:
            st.info("💡 Registra un ingreso o gasto hoy para iniciar tu racha.")
        elif gami["racha_viva"]:
            st.markdown('<div class="tip-box">🔥 ¡Tu racha sigue viva! Vuelve mañana para seguir sumando días.</div>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ Tu racha se rompió. ¡Registra un movimiento hoy para reiniciarla!")

        if gami["racha_maxima"] > 0:
            st.caption(f"🏆 Tu récord personal: **{gami['racha_maxima']} días** seguidos")

        st.divider()

        st.subheader("⭐ ¿Cómo ganar XP?")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("""
| Acción | XP |
|--------|-----|
| 🛒 Registrar un gasto | +10 XP |
| 💵 Registrar un ingreso | +5 XP |
| 🎬 Visitar la Academia | +15 XP |
| 🔐 Hacer login | +2 XP |
            """)
        with col_b:
            st.markdown("""
| Nivel | XP Requerido |
|-------|-------------|
| 1 · Principiante | 0 XP |
| 2 · Estudiante | 100 XP |
| 3 · Analista | 500 XP |
| 4 · Experto | 1000 XP |
            """)

        st.divider()

        st.subheader("🏅 Colección de Logros")
        badges_usuario = gami["badges"] or []
        cards_html = '<div class="badge-grid">'
        for clave, info in BADGES.items():
            desbloqueado = clave in badges_usuario
            clase = "badge-card desbloqueado" if desbloqueado else "badge-card bloqueado"
            icono = info["emoji"] if desbloqueado else "🔒"
            cards_html += f"""
            <div class="{clase}">
              <div class="badge-emoji">{icono}</div>
              <div class="badge-nombre">{info['nombre']}</div>
              <div class="badge-desc">{info['desc']}</div>
            </div>"""
        cards_html += '</div>'
        st.markdown(cards_html, unsafe_allow_html=True)


    # ══════════════════════════════════════════
    # SECCIÓN 3: ACADEMIA FINANCIERA
    # ══════════════════════════════════════════
    elif opcion_menu == "📚 Academia Financiera":

        # Banner TikTok
        st.markdown("""
        <div style="background:linear-gradient(135deg,#010101,#69C9D0);
                    border-radius:12px;padding:16px 20px;text-align:center;margin-bottom:16px;">
          <div style="color:white;font-size:1rem;font-weight:700;margin-bottom:4px;">
            \U0001f4f1 \u00a1S\u00edguenos en TikTok para contenido nuevo cada semana!
          </div>
          <div style="color:#ddd;font-size:0.82rem;">@polibank_ \u00b7 Tips de finanzas para universitarios</div>
        </div>
        """, unsafe_allow_html=True)
        col_tik, _, _ = st.columns([1, 1, 1])
        with col_tik:
            st.link_button("\U0001f3b5 Ir al TikTok de Polibank",
                           "https://www.tiktok.com/@polibank_?lang=es-419",
                           use_container_width=True)
        st.divider()

        # Sistema de lecciones estilo Duolingo
        render_academia(user_id, registrar_accion)