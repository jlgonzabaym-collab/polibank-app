import streamlit as st
import base64
from pathlib import Path
from app.database import (
    registrar_usuario, login_usuario,
    guardar_movimiento, obtener_movimientos,
    obtener_videos_educativos, eliminar_movimiento
)
from app.gamificacion import registrar_accion, obtener_estado, BADGES
from datetime import datetime, date
import pandas as pd
import plotly.express as px
from app.ai_core import clasificar_gasto, asistente_general
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY
import uuid
from academia_ui import render_academia

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
st.set_page_config(page_title="Polibank", page_icon="🐢", layout="centered")

COLOR_VERDE = "#0F5C3B"        # Verde oscuro del logo (faceta izquierda)
COLOR_VERDE_CLARO = "#2FAE60"  # Verde brillante del logo (faceta derecha) — ingresos
COLOR_MENTA = "#A6E8C8"        # Verde menta del logo (base) — acento de marca
COLOR_ROJO = "#E5533D"         # Gastos / alertas
COLOR_AZUL = "#2E6F9E"         # Neutral / informativo
COLOR_ORO = "#E8A722"          # XP / logros
COLOR_TINTA = "#12241C"        # Texto principal, con matiz verdoso sutil
COLOR_FONDO = "#F5FBF7"        # Fondo de app, menta muy claro (del logo)

supabase_client = create_client(SUPABASE_URL.strip().rstrip('/'), SUPABASE_KEY.strip())

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;500;600;700;800&display=swap');

  /* Se oculta solo el toolbar (botón "Deploy", menú de tres puntos) —
     NO el header completo, para no romper accesos nativos de Streamlit. */
  [data-testid="stToolbar"] {{visibility: hidden;}}
  #MainMenu {{visibility: hidden;}}
  footer {{visibility: hidden;}}

  html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; color: {COLOR_TINTA}; }}
  h1, h2, h3, .metric-value, .gami-stat-val {{ font-family: 'Sora', sans-serif; }}

  /* Blindaje contra el modo oscuro del navegador: sin esto, Streamlit
     puede pintar títulos y texto en blanco sobre nuestro fondo claro. */
  [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{ background: {COLOR_FONDO} !important; }}
  h1, h2, h3, h4, p, span, label, .stMarkdown, [data-testid="stMarkdownContainer"] {{ color: {COLOR_TINTA} !important; }}
  [data-testid="stCaptionContainer"] {{ color: #6B7A70 !important; }}

  .stApp {{ background: {COLOR_FONDO}; }}

  /* Raya indicadora de la pestaña activa (elemento aparte del texto) */
  [data-baseweb="tab-highlight"] {{ background-color: {COLOR_VERDE} !important; }}

  /* Márgenes limpios para aprovechar la pantalla del celular al máximo */
  .block-container {{ padding: 1.25rem 1rem 3rem 1rem !important; max-width: 100%; }}

  /* Tarjetas: sin bordes agresivos, redondeadas y sombras súper suaves */
  .metric-card, .mov-row, .gami-stat, .badge-card, .sidebar-gami {{
    background: #FFFFFF;
    border-radius: 20px;
    border: 1px solid #EDF1EE !important;
    box-shadow: 0 6px 20px rgba(20,40,30,0.04) !important;
  }}

  /* Métricas (Dashboard): Saldo imponente y claro */
  .metric-card {{ padding: 20px 16px; text-align: center; margin-bottom: 12px; }}
  .metric-label {{ font-size: 0.68rem; color: #7A8A80; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 6px; }}
  .metric-value {{ font-size: 1.9rem; font-weight: 800; letter-spacing: -0.5px; line-height: 1.1; }}
  .metric-value.verde {{ color: {COLOR_VERDE}; }}
  .metric-value.rojo  {{ color: {COLOR_ROJO};  }}
  .metric-value.azul  {{ color: {COLOR_TINTA}; }} /* saldo neutro: oscuro para dar seriedad */

  /* Inputs refinados (estilo iOS) — se apunta a data-baseweb porque las
     clases .stTextInput/.stNumberInput cambian entre versiones de Streamlit,
     mientras que data-baseweb es de la librería interna y es mucho más estable. */
  [data-baseweb="input"], [data-baseweb="select"] > div, [data-baseweb="datepicker"] input {{
    border-radius: 14px !important;
    background-color: #F1F4F1 !important;
    border: 1.5px solid transparent !important;
    box-shadow: none !important;
  }}
  [data-baseweb="input"] input, [data-baseweb="select"] input,
  [data-baseweb="datepicker"] input, [data-baseweb="input"] textarea {{
    background-color: transparent !important;
    color: {COLOR_TINTA} !important;
  }}
  [data-baseweb="input"]:focus-within, [data-baseweb="select"] > div:focus-within {{
    border-color: {COLOR_VERDE} !important;
    background-color: #FFFFFF !important;
  }}
  [data-baseweb="select"] svg, [data-baseweb="datepicker"] svg {{ fill: {COLOR_TINTA} !important; }}

  /* Botones +/- del number_input y menú desplegable del selectbox */
  [data-testid="stNumberInputStepUp"], [data-testid="stNumberInputStepDown"] {{
    background-color: #F1F4F1 !important;
    color: {COLOR_TINTA} !important;
  }}
  [data-baseweb="popover"] [data-baseweb="menu"] {{
    background-color: #FFFFFF !important;
  }}
  [data-baseweb="menu"] li {{ color: {COLOR_TINTA} !important; }}

  /* Subidor de archivos */
  [data-testid="stFileUploaderDropzone"] {{
    background-color: #F1F4F1 !important;
    border-radius: 14px !important;
    border: 1.5px dashed #C7D2C9 !important;
  }}
  [data-testid="stFileUploaderDropzone"] * {{ color: {COLOR_TINTA} !important; }}
  [data-testid="stFileUploaderDropzoneInstructions"] svg {{ fill: {COLOR_TINTA} !important; }}

  /* Botones — varios selectores porque el testid cambió de nombre entre versiones */
  .stButton>button, [data-testid^="stBaseButton"], [data-testid="stFormSubmitButton"]>button {{
    background-color: {COLOR_VERDE} !important;
    color: #FFFFFF !important;
    border-radius: 100px !important;
    font-weight: 700;
    font-size: 0.95rem;
    padding: 12px 22px;
    border: none !important;
    box-shadow: 0 6px 16px rgba(15,92,59,0.15);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
  }}
  .stButton>button p, [data-testid^="stBaseButton"] p, [data-testid="stFormSubmitButton"] p {{ color: #FFFFFF !important; }}
  .stButton>button:active, [data-testid^="stBaseButton"]:active {{ transform: scale(0.96); box-shadow: none; }}
  .stButton>button:focus-visible, [data-testid^="stBaseButton"]:focus-visible {{ outline: 2px solid {COLOR_VERDE}; outline-offset: 2px; }}

  /* Pestañas (Tabs) más sutiles y elegantes */
  .stTabs [data-baseweb="tab-list"] {{ gap: 20px; border-bottom: 1px solid #E7ECE8; }}
  .stTabs [data-baseweb="tab"] {{ padding: 10px 2px; background: transparent; font-weight: 600; color: #6B7A70; }}
  .stTabs [aria-selected="true"] {{ color: {COLOR_VERDE} !important; }}

  /* Filas del historial de movimientos */
  .mov-row {{ padding: 14px 16px; margin-bottom: 10px; display: flex; flex-direction: column; }}
  .mov-detalle {{ font-size: 0.92rem; color: {COLOR_TINTA}; font-weight: 600; margin-top: 6px; }}
  .mov-monto {{ font-size: 1.1rem; font-weight: 800; }}

  /* Etiquetas de categorías pulidas (píldoras de colores pastel) */
  .badge-cat {{ display:inline-block; padding:5px 12px; border-radius:100px; font-size:0.66rem; font-weight:800; letter-spacing: 0.4px; }}
  .badge-comida     {{ background:#FFF1EF; color:#C43D2A; }}
  .badge-transporte {{ background:#EEF3FC; color:{COLOR_AZUL}; }}
  .badge-estudios   {{ background:{COLOR_MENTA}33; color:{COLOR_VERDE}; }}
  .badge-diversion  {{ background:#FFF6E4; color:#B9790A; }}
  .badge-otros      {{ background:#F1F3F1; color:#5F6E64; }}
  .badge-ingresos   {{ background:{COLOR_MENTA}33; color:{COLOR_VERDE}; }}

  /* Alertas y Tips informativos */
  .alerta-negativo {{ background:#FFF3E9; border-radius:14px; padding:14px 18px; font-weight:600; color:#9A5B10; font-size: 0.88rem; }}
  .tip-box {{ background:{COLOR_MENTA}33; border-radius:14px; padding:14px 18px; margin:14px 0; font-size:0.88rem; color:{COLOR_VERDE}; font-weight: 600; }}

  /* Sección de Gamificación (Hero Banner) */
  .gami-hero {{
    background: linear-gradient(135deg, {COLOR_VERDE}, #0A3D27);
    border-radius: 24px;
    padding: 28px 22px;
    color: white;
    margin-bottom: 20px;
    box-shadow: 0 12px 28px rgba(15,92,59,0.22);
    border-top: 3px solid {COLOR_MENTA};
  }}
  .gami-stat-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px; }}
  .gami-stat {{ background: transparent; box-shadow: none !important; border: 1px solid #E7ECE8 !important; padding: 14px 8px; text-align: center; }}
  .gami-stat-val {{ font-size: 1.7rem; font-weight: 800; line-height: 1.1; }}
  .gami-stat-lbl {{ font-size: 0.62rem; color: #8B988F; font-weight: 700; text-transform: uppercase; margin-top: 6px; letter-spacing: 0.4px; }}

  /* Píldora de nivel — antes sin padding/tipografía, quedaba invisible */
  .nivel-pill {{
    display: inline-block;
    background: rgba(255,255,255,0.16);
    backdrop-filter: blur(4px);
    padding: 6px 14px;
    border-radius: 100px;
    font-size: 0.72rem;
    font-weight: 700;
    margin-left: auto;
  }}

  /* Barra de progreso de XP — antes no existía en el CSS, no se veía */
  .xp-bar-wrap {{
    width: 100%;
    height: 8px;
    background: rgba(166,232,200,0.25);
    border-radius: 100px;
    overflow: hidden;
    margin: 6px 0;
  }}
  .xp-bar-fill {{
    height: 100%;
    background: {COLOR_ORO};
    border-radius: 100px;
    transition: width 0.4s ease;
  }}

  /* Logros/Badges */
  .badge-card {{ padding: 20px 12px; background: #F8FAF8; border: 1px solid #EDF1EE !important; border-radius: 20px; text-align: center; }}
  .badge-card.desbloqueado {{ background: #FFFFFF; box-shadow: 0 8px 20px rgba(20,40,30,0.05) !important; }}
  .badge-card.bloqueado {{ opacity: 0.55; }}

  /* Grilla de logros — antes no existía, las tarjetas quedaban apiladas sin orden */
  .badge-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }}
  .badge-emoji {{ font-size: 1.8rem; margin-bottom: 6px; }}
  .badge-nombre {{ font-size: 0.82rem; font-weight: 700; color: {COLOR_TINTA}; margin-bottom: 4px; }}
  .badge-desc {{ font-size: 0.72rem; color: #7A8A80; line-height: 1.3; }}

  /* Notificaciones elegantes (Toasts) */
  .toast-nuevo {{
    background: {COLOR_TINTA};
    color: white;
    border-radius: 100px;
    padding: 12px 20px;
    font-weight: 600;
    font-size: 0.86rem;
    text-align: center;
    box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    margin-bottom: 10px;
  }}

  /* Menú principal horizontal (antes en el sidebar) — estilo de pastillas */
  div[role="radiogroup"] {{
    gap: 8px;
    flex-wrap: wrap;
  }}
  div[role="radiogroup"] label {{
    background: #FFFFFF;
    border: 1px solid #E7ECE8;
    border-radius: 100px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 0.85rem;
    transition: all 0.15s ease;
  }}
  div[role="radiogroup"] label:has(input:checked) {{
    background: {COLOR_VERDE};
    border-color: {COLOR_VERDE};
  }}
  div[role="radiogroup"] label:has(input:checked) p {{
    color: #FFFFFF !important;
  }}
  div[role="radiogroup"] input {{ display: none; }}
  div[role="radiogroup"] > label > div:first-child {{ display: none; }} /* oculta el círculo del radio */

  .sidebar-gami {{ padding: 14px 18px; }}
</style>
""", unsafe_allow_html=True)

EMOJI_CAT = {
    "COMIDA": "🍽️", "TRANSPORTE": "🚌", "ESTUDIOS": "📚",
    "DIVERSION": "🎮", "OTROS": "📦", "INGRESOS": "💵"
}


def badge_cat(categoria: str) -> str:
    cat = categoria.upper()
    return f'<span class="badge-cat badge-{cat.lower()}">{EMOJI_CAT.get(cat, "📦")} {cat}</span>'


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
def _logo_en_base64(ruta: str) -> str | None:
    """Lee el logo del disco y lo devuelve codificado para incrustarlo
    directo en el HTML — así el tamaño del logo no depende de columnas
    de Streamlit, que se estiran distinto según el ancho de pantalla."""
    try:
        datos = Path(ruta).read_bytes()
        return base64.b64encode(datos).decode()
    except Exception:
        return None


_logo_b64 = _logo_en_base64("logo_polibank.png")
_logo_tag = (
    f'<img src="data:image/png;base64,{_logo_b64}" style="height:48px;width:auto;display:block;">'
    if _logo_b64 else "🐢"
)

st.markdown(f"""
<div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
  {_logo_tag}
  <h1 style="margin:0;font-size:1.6rem;font-family:'Sora',sans-serif;">Polibank · ESPOL</h1>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# BLOQUE A: LOGIN / REGISTRO
# ═══════════════════════════════════════════════
if "usuario_conectado" not in st.session_state:
    tab_login, tab_registro = st.tabs(["🔒 Iniciar Sesión", "📝 Crear Cuenta"])

    with tab_login:
        st.subheader("Bienvenido de vuelta 👋")
        correo_login = st.text_input("Correo Electrónico", key="login_correo")
        pass_login = st.text_input("Contraseña", type="password", key="login_pass")
        if st.button("Ingresar", key="btn_login_submit", use_container_width=True):
            if correo_login and pass_login:
                exito, resultado = login_usuario(correo_login, pass_login)
                if exito:
                    st.session_state["usuario_conectado"] = resultado
                    registrar_accion(resultado["id"], "login")
                    st.rerun()
                else:
                    st.error(resultado)
            else:
                st.warning("Completa todos los campos.")

    with tab_registro:
        st.subheader("Crea tu cuenta gratis 🐢")
        correo_reg = st.text_input("Correo Electrónico", key="reg_correo")
        pass_reg = st.text_input("Contraseña (mínimo 6 caracteres)", type="password", key="reg_pass")
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
    user_id = st.session_state["usuario_conectado"]["id"]
    correo_user = st.session_state["usuario_conectado"]["correo"]

    col_user, col_logout = st.columns([4, 1])
    with col_user:
        st.caption(f"👤 {correo_user}")
    with col_logout:
        if st.button("Salir ❌", use_container_width=True):
            del st.session_state["usuario_conectado"]
            st.rerun()

    st.divider()

    # Widget de racha — arriba del menú, siempre visible en el contenido principal
    gami = obtener_estado(user_id)
    racha_emoji = "🔥" if gami["racha_viva"] else "💤"
    st.markdown(f"""
    <div class="sidebar-gami" style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;">
      <div>
        <div style="font-size:0.68rem;color:#7A8A80;font-weight:700;text-transform:uppercase;letter-spacing:.5px;">Tu progreso</div>
        <div style="font-size:1.4rem;font-weight:800;color:{COLOR_VERDE};margin:2px 0;">{racha_emoji} {gami['racha_actual']} días</div>
      </div>
      <div style="font-size:0.78rem;color:#7A8A80;text-align:right;">⭐ {gami['xp_total']} XP<br>Nivel {gami['nivel']} · {gami['nivel_nombre']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Menú principal — como pestañas horizontales en el contenido principal,
    # en vez de en el sidebar. Así el menú siempre está a la vista, sin
    # depender de un botón para abrir/cerrar un panel lateral.
    opcion_menu = st.radio(
        "📱 Menú Polibank",
        ["💰 Finanzas Personales", "🏆 Mi Progreso", "📚 Academia Financiera", "🐢 Asistente Polibank"],
        horizontal=True,
        label_visibility="collapsed",
    )
    st.divider()

    # Notificación de badges nuevos
    if "gami_notif" in st.session_state:
        notif = st.session_state.pop("gami_notif")
        for b in notif.get("badges_nuevos", []):
            info = BADGES.get(b, {})
            st.markdown(
                f'<div class="toast-nuevo">🏅 ¡Nuevo logro! {info.get("emoji", "")} '
                f'<strong>{info.get("nombre", "")}</strong> — {info.get("desc", "")}</div>',
                unsafe_allow_html=True
            )

    # ══════════════════════════════════════════
    # SECCIÓN 1: FINANZAS PERSONALES
    # ══════════════════════════════════════════
    if opcion_menu == "💰 Finanzas Personales":

        movimientos_db = obtener_movimientos(user_id)

        # Calcular totales
        total_ingresos = 0.0
        total_egresos = 0.0
        historial_tabla = []
        datos_por_dia = {}
        cat_totales = {"COMIDA": 0.0, "TRANSPORTE": 0.0, "ESTUDIOS": 0.0, "DIVERSION": 0.0, "OTROS": 0.0}

        for mov in movimientos_db:
            monto_num = float(mov["monto"])
            fecha_dt = datetime.strptime(mov["fecha"], "%Y-%m-%d")
            fecha_label = fecha_dt.strftime("%d-%b")
            if fecha_label not in datos_por_dia:
                datos_por_dia[fecha_label] = {"Ingresos": 0.0, "Egresos": 0.0, "_orden": fecha_dt}
            cat = mov.get("categoria", "OTROS").upper()
            if mov["tipo"] == "Ingreso":
                total_ingresos += monto_num
                datos_por_dia[fecha_label]["Ingresos"] += monto_num
                tipo_label = "💵 Ingreso";
                monto_texto = f"+${monto_num:.2f}"
            else:
                total_egresos += monto_num
                datos_por_dia[fecha_label]["Egresos"] += monto_num
                tipo_label = "🛒 Gasto";
                monto_texto = f"-${monto_num:.2f}"
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
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Ingresos</div><div class="metric-value verde">${total_ingresos:,.2f}</div></div>',
                unsafe_allow_html=True)
        with c2:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Gastos</div><div class="metric-value rojo">${total_egresos:,.2f}</div></div>',
                unsafe_allow_html=True)
        with c3:
            color_bal = "verde" if balance >= 0 else "rojo"
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Saldo</div><div class="metric-value {color_bal}">${balance:,.2f}</div></div>',
                unsafe_allow_html=True)

        if balance < 0:
            st.markdown('<div class="alerta-negativo">⚠️ Tu saldo está en negativo. Revisa tus gastos.</div>',
                        unsafe_allow_html=True)

        if total_ingresos > 0 and total_egresos > 0:
            pct = ((total_ingresos - total_egresos) / total_ingresos) * 100
            if pct >= 20:
                tip = f"🎉 Estás ahorrando el {pct:.0f}% de tus ingresos. ¡Excelente!"
            elif pct > 0:
                tip = f"💡 Ahorras el {pct:.0f}%. La meta recomendada es el 20%."
            else:
                tip = "📉 Gastas más de lo que ganas. Identifica gastos no esenciales."
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
                    filas += [{"Fecha": fl, "Monto ($)": m["Ingresos"], "Tipo": "Ingresos"},
                              {"Fecha": fl, "Monto ($)": m["Egresos"], "Tipo": "Egresos"}]
                fig = px.bar(pd.DataFrame(filas), x="Fecha", y="Monto ($)", color="Tipo",
                             barmode="group",
                             color_discrete_map={"Ingresos": COLOR_VERDE_CLARO, "Egresos": COLOR_ROJO})
                fig.update_traces(
                    texttemplate="$%{y:,.0f}", textposition="outside",
                    textfont=dict(size=9, color="#12241C"),
                    marker_line_width=0,
                    selector=dict(type="bar")
                )
                fig.update_layout(
                    height=320,
                    plot_bgcolor="white", paper_bgcolor="white",
                    font=dict(family="Inter, sans-serif", color="#12241C", size=11),
                    margin=dict(l=8, r=8, t=36, b=8),
                    legend=dict(
                        orientation="h", yanchor="bottom", y=1.02,
                        xanchor="right", x=1,
                        font=dict(size=11), bgcolor="rgba(0,0,0,0)",
                        title_text=""
                    ),
                    xaxis=dict(showgrid=False, linecolor="#E7ECE8",
                               tickfont=dict(size=10, color="#7A8A80"), title=""),
                    yaxis=dict(showgrid=True, gridcolor="#F0F4F1",
                               linecolor="#E7ECE8", tickfont=dict(size=10, color="#7A8A80"),
                               tickprefix="$", title="", fixedrange=True),
                    xaxis_fixedrange=False,
                    dragmode="pan",
                    bargap=0.25, bargroupgap=0.1,
                    modebar_remove=["zoom","pan","select","lasso2d","zoomIn2d",
                                    "zoomOut2d","autoScale2d","resetScale2d",
                                    "toImage","sendDataToCloud"],
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "scrollZoom": False, "doubleClick": False, "staticPlot": False})

            with tab_categorias:
                cat_f = {k: v for k, v in cat_totales.items() if v > 0}
                if cat_f:
                    df_cat = pd.DataFrame([
                        {"Categoría": f"{EMOJI_CAT.get(k, '📦')} {k}", "Monto ($)": v}
                        for k, v in sorted(cat_f.items(), key=lambda x: x[1])
                    ])
                    fig_cat = px.bar(
                        df_cat, x="Monto ($)", y="Categoría", orientation="h",
                        color="Monto ($)",
                        color_continuous_scale=["#2FAE60", "#E8A722", "#E5533D"]
                    )
                    fig_cat.update_traces(
                        texttemplate="$%{x:,.0f}", textposition="outside",
                        textfont=dict(size=9, color="#12241C"),
                        marker_line_width=0,
                    )
                    fig_cat.update_layout(
                        height=max(200, len(cat_f) * 52),
                        plot_bgcolor="white", paper_bgcolor="white",
                        font=dict(family="Inter, sans-serif", color="#12241C", size=11),
                        margin=dict(l=8, r=48, t=8, b=8),
                        showlegend=False, coloraxis_showscale=False,
                        xaxis=dict(showgrid=True, gridcolor="#F0F4F1",
                                   linecolor="#E7ECE8", tickfont=dict(size=10, color="#7A8A80"),
                                   tickprefix="$", title=""),
                        yaxis=dict(showgrid=False, linecolor="#E7ECE8",
                                   tickfont=dict(size=11, color="#12241C"),
                                   title="", categoryorder="total ascending",
                                   fixedrange=True),
                        xaxis_fixedrange=True,
                        dragmode=False,
                        modebar_remove=["zoom","pan","select","lasso2d","zoomIn2d",
                                        "zoomOut2d","autoScale2d","resetScale2d",
                                        "toImage","sendDataToCloud"],
                    )
                    st.plotly_chart(fig_cat, use_container_width=True, config={"displayModeBar": False, "scrollZoom": False, "doubleClick": False, "staticPlot": False})
                    cat_max = max(cat_f, key=cat_f.get)
                    st.markdown(
                        f'<div class="tip-box">💡 Mayor gasto: <strong>{cat_max}</strong> (${cat_f[cat_max]:,.2f})</div>',
                        unsafe_allow_html=True)
                else:
                    st.info("Aún no hay gastos para mostrar.")

            with tab_linea:
                saldo_acum = 0.0
                puntos = []
                for fl, m in dias_ord:
                    saldo_acum += m["Ingresos"] - m["Egresos"]
                    puntos.append({"Fecha": fl, "Saldo ($)": saldo_acum})
                fig3 = px.line(pd.DataFrame(puntos), x="Fecha", y="Saldo ($)",
                               markers=True,
                               color_discrete_sequence=["#0F5C3B"])
                fig3.update_traces(
                    line=dict(width=2.5),
                    marker=dict(size=7, color="white", line=dict(color="#0F5C3B", width=2.5)),
                    fill="tozeroy",
                    fillcolor="rgba(47,174,96,0.08)",
                )
                fig3.add_hline(y=0, line_dash="dot", line_color="#E5533D",
                               line_width=1.5, opacity=0.6)
                fig3.update_layout(
                    height=300,
                    plot_bgcolor="white", paper_bgcolor="white",
                    font=dict(family="Inter, sans-serif", color="#12241C", size=11),
                    margin=dict(l=8, r=8, t=8, b=8),
                    xaxis=dict(showgrid=False, linecolor="#E7ECE8",
                               tickfont=dict(size=10, color="#7A8A80"), title=""),
                    yaxis=dict(showgrid=True, gridcolor="#F0F4F1",
                               linecolor="#E7ECE8", tickfont=dict(size=10, color="#7A8A80"),
                               tickprefix="$", title="", fixedrange=True),
                    xaxis_fixedrange=False,
                    dragmode="pan",
                    modebar_remove=["zoom","pan","select","lasso2d","zoomIn2d",
                                    "zoomOut2d","autoScale2d","resetScale2d",
                                    "toImage","sendDataToCloud"],
                )
                st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False, "scrollZoom": False, "doubleClick": False, "staticPlot": False})
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
                monto_ing = st.number_input("Monto ($)", min_value=0.01, step=10.0)
                fuente_ing = st.text_input("Fuente", placeholder="Beca ESPOL, Trabajo, Mesada…")
                fecha_ing = st.date_input("Fecha", value=date.today())
                factura_ing = st.file_uploader(
                    "📎 Adjuntar factura (opcional)",
                    type=["jpg", "jpeg", "png", "pdf"],
                    key="factura_ing"
                )
                if st.form_submit_button("💾 Guardar Ingreso", use_container_width=True):
                    if monto_ing > 0:
                        # Subir factura si hay
                        url_factura = None
                        if factura_ing:
                            with st.spinner("Subiendo factura…"):
                                url_factura = subir_factura(factura_ing, user_id, fuente_ing)
                            if not url_factura:
                                st.warning("⚠️ No se pudo subir la factura; el ingreso se guardará sin ella.")

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
                monto_gas = st.number_input("Monto ($)", min_value=0.01, step=1.0)
                texto_gas = st.text_input("¿En qué gastaste?", placeholder="Almuerzo comedor FCSH, bus Guayaquil…")
                fecha_gas = st.date_input("Fecha", value=date.today())
                factura_gas = st.file_uploader(
                    "📎 Adjuntar factura (opcional)",
                    type=["jpg", "jpeg", "png", "pdf"],
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
                            if not url_factura:
                                st.warning("⚠️ No se pudo subir la factura; el gasto se guardará sin ella.")

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
                                f"{EMOJI_CAT.get(cat_ia.upper(), '📦')} · +{res_gami['xp_ganado']} XP ⭐"
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
                filtro_tipo = st.selectbox("Tipo", ["Todos", "💵 Ingreso", "🛒 Gasto"], key="filtro_tipo")
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
                es_ingreso = mov["Tipo"] == "💵 Ingreso"
                color_m = COLOR_VERDE if es_ingreso else COLOR_ROJO
                clase = "ingreso" if es_ingreso else "gasto"
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

        # 'gami' ya se cargó arriba para el widget del sidebar — reutilizarlo
        # evita una segunda consulta idéntica a la base de datos en cada carga.
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
            st.markdown('<div class="tip-box">🔥 ¡Tu racha sigue viva! Vuelve mañana para seguir sumando días.</div>',
                        unsafe_allow_html=True)
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

    # ══════════════════════════════════════════
    # SECCIÓN 4: ASISTENTE POLIBANK
    # ══════════════════════════════════════════
    elif opcion_menu == "🐢 Asistente Polibank":

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,{COLOR_VERDE},{COLOR_VERDE_CLARO});
                    border-radius:16px;padding:20px 24px;color:white;margin-bottom:20px;">
          <div style="display:flex;align-items:center;gap:12px;">
            <span style="font-size:2.5rem;">🐢</span>
            <div>
              <div style="font-size:1.1rem;font-weight:800;">Asistente Polibank</div>
              <div style="font-size:0.82rem;opacity:.85;">Tu amigo financiero personal · Siempre disponible</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Inicializar historial
        if "chat_historial" not in st.session_state:
            st.session_state["chat_historial"] = []
        if "chat_input_key" not in st.session_state:
            st.session_state["chat_input_key"] = 0

        # Mensaje de bienvenida
        if not st.session_state["chat_historial"]:
            st.session_state["chat_historial"].append({
                "rol": "asistente",
                "texto": "¡Hola! 🐢 Soy Polibank, tu asistente personal. Puedo ayudarte con tus finanzas, responder preguntas, darte consejos personalizados o simplemente conversar. ¿En qué te ayudo hoy?"
            })

        # Mostrar mensajes
        for msg in st.session_state["chat_historial"]:
            if msg["rol"] == "usuario":
                with st.chat_message("user"):
                    st.write(msg["texto"])
            else:
                with st.chat_message("assistant", avatar="🐢"):
                    st.write(msg["texto"])

        # Sugerencias rápidas
        if len(st.session_state["chat_historial"]) <= 1:
            st.markdown("**Preguntas frecuentes:**")
            sugs = [
                "¿En qué estoy gastando más?",
                "¿Cómo puedo ahorrar más?",
                "¿Cuál es mi saldo actual?",
                "Dame un consejo financiero",
            ]
            cols = st.columns(2)
            for i, sug in enumerate(sugs):
                with cols[i % 2]:
                    if st.button(sug, key=f"sug_{i}", use_container_width=True):
                        st.session_state["chat_historial"].append({"rol": "usuario", "texto": sug})
                        movs = obtener_movimientos(user_id)
                        with st.spinner("🐢 Pensando..."):
                            respuesta = asistente_general(
                                pregunta=sug,
                                movimientos=movs,
                                historial_chat=st.session_state["chat_historial"],
                                gami_estado=gami
                            )
                        st.session_state["chat_historial"].append({"rol": "asistente", "texto": respuesta})
                        st.session_state["chat_input_key"] += 1
                        st.rerun()

        # Input del usuario
        user_input = st.chat_input("Escribe tu mensaje...", key=f"chat_{st.session_state['chat_input_key']}")
        if user_input and user_input.strip():
            st.session_state["chat_historial"].append({"rol": "usuario", "texto": user_input.strip()})
            movs = obtener_movimientos(user_id)
            with st.spinner("🐢 Pensando..."):
                respuesta = asistente_general(
                    pregunta=user_input.strip(),
                    movimientos=movs,
                    historial_chat=st.session_state["chat_historial"],
                    gami_estado=gami
                )
            st.session_state["chat_historial"].append({"rol": "asistente", "texto": respuesta})
            st.session_state["chat_input_key"] += 1
            st.rerun()

        # Botón limpiar — discreto, debajo del input
        if len(st.session_state["chat_historial"]) > 1:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            col_esp, col_btn = st.columns([3, 1])
            with col_btn:
                if st.button("🗑️ Limpiar", key="limpiar_chat", use_container_width=True):
                    st.session_state["chat_historial"] = []
                    st.session_state["chat_input_key"] += 1
                    st.rerun()

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
        _, col_tik, _ = st.columns([1, 2, 1])
        with col_tik:
            st.link_button("\U0001f3b5 Ir al TikTok de Polibank",
                           "https://www.tiktok.com/@polibank_?lang=es-419",
                           use_container_width=True)
        st.divider()

        # Sistema de lecciones estilo Duolingo
        render_academia(user_id, registrar_accion)