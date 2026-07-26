import streamlit as st
import base64
from pathlib import Path
from app.database import (
    registrar_usuario, login_usuario,
    guardar_movimiento, obtener_movimientos,
    obtener_videos_educativos, eliminar_movimiento,
    obtener_gastos_recurrentes, agregar_gasto_recurrente, eliminar_gasto_recurrente
)
from app.gamificacion import registrar_accion, obtener_estado, BADGES
from datetime import datetime, date
from zoneinfo import ZoneInfo
import pandas as pd
import plotly.express as px
from app.ai_core import clasificar_gasto, asistente_general
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY
import uuid
from academia_ui import render_academia
from leaderboard import render_leaderboard, sumar_xp_semanal
from streamlit_cookies_manager import EncryptedCookieManager

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
st.set_page_config(page_title="Polibank", page_icon="🐢", layout="centered")

# ── Sesión persistente: guarda el login en una cookie cifrada del
# navegador para que no haya que volver a loguearse en cada visita.
cookies = EncryptedCookieManager(
    prefix="polibank_",
    password="polibank_cookie_secret_2026",  # cambia esto por algo propio si quieres
)
if not cookies.ready():
    st.stop()

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
  h1, h2, h3, .metric-value, .progreso-stat-val {{ font-family: 'Sora', sans-serif; }}

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
  .metric-card, .progreso-card, .badge-card, .sidebar-gami, [class*="st-key-movcard_"] {{
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

  /* Botón "+" de gastos recurrentes: mismo estilo que el stepper de monto */
  [data-testid="stPopover"] > div > button {{
    background-color: #F1F4F1 !important;
    color: {COLOR_TINTA} !important;
    border: none !important;
    box-shadow: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    min-height: 2.7rem;
  }}

  /* Subidor de archivos */
  [data-testid="stFileUploaderDropzone"] {{
    background-color: #F1F4F1 !important;
    border-radius: 14px !important;
    border: 1.5px dashed #C7D2C9 !important;
    pointer-events: auto !important;
    position: relative;
    z-index: 1;
  }}
  [data-testid="stFileUploaderDropzone"] * {{
    color: {COLOR_TINTA} !important;
    pointer-events: auto !important;
  }}
  [data-testid="stFileUploaderDropzoneInstructions"] svg {{ fill: {COLOR_TINTA} !important; }}
  [data-testid="stFileUploaderDropzone"] input[type="file"] {{
    opacity: 0;
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    cursor: pointer;
  }}
  [data-testid="stBaseButton-secondary"] {{
    pointer-events: auto !important;
  }}

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
  .stTabs [data-baseweb="tab"] {{ padding: 10px 2px; background: transparent; font-weight: 600; }}
  .stTabs [data-baseweb="tab"] p {{ color: #6B7A70 !important; }}
  .stTabs [aria-selected="true"] p {{ color: {COLOR_VERDE} !important; }}

  /* Filas del historial de movimientos */
  [class*="st-key-movcard_"] {{ padding: 14px 16px !important; margin-bottom: 10px; }}
  [class*="st-key-movcard_"] [data-testid="stVerticalBlockBorderWrapper"] {{ padding: 0 !important; }}
  .mov-detalle {{ font-size: 0.92rem; color: {COLOR_TINTA}; font-weight: 600; }}
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
  /* Tarjeta única de progreso: escena de racha arriba + stats abajo,
     reemplaza las 3 tarjetas separadas (la del medio quedaba vacía/fea). */
  .progreso-card {{
    background: #FFFFFF;
    border-radius: 20px;
    border: 1px solid #EDF1EE !important;
    box-shadow: 0 6px 20px rgba(20,40,30,0.04) !important;
    overflow: hidden;
    margin-bottom: 20px;
  }}
  .progreso-escena {{ position: relative; overflow: hidden; aspect-ratio: 340 / 150; }}
  .racha-arbol-bg {{ position: absolute; inset: 0; }}
  .racha-arbol-bg svg {{ width: 100%; height: 100%; display: block; }}
  .racha-arbol-dormant {{ filter: grayscale(80%) brightness(0.94); }}
  .racha-arbol-anim {{ transform-origin: 66px 92px; animation: racha-sway 6s ease-in-out infinite alternate; }}
  @keyframes racha-sway {{ 0% {{ transform: rotate(-1.3deg); }} 100% {{ transform: rotate(1.3deg); }} }}
  .racha-badge {{
    position: absolute; top: 10px; right: 12px; z-index: 2;
    font-size: 1.9rem; font-weight: 800; line-height: 1.1; color: {COLOR_ROJO};
    text-shadow: 0 1px 4px rgba(255,255,255,0.6), 0 1px 8px rgba(255,255,255,0.4);
  }}
  .racha-caption {{
    position: absolute; bottom: 10px; left: 14px; z-index: 2;
    font-size: 0.62rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.4px;
    color: #FFFFFF; text-shadow: 0 1px 3px rgba(10,30,20,0.35);
  }}
  .progreso-stats-row {{
    display: flex;
    align-items: center;
    padding: 16px 8px;
    border-top: 1px solid #EDF1EE;
  }}
  .progreso-stat {{ flex: 1; text-align: center; }}
  .progreso-stat-val {{ font-size: 1.6rem; font-weight: 800; line-height: 1.1; font-family: 'Sora', sans-serif; }}
  .progreso-stat-lbl {{ font-size: 0.62rem; color: #8B988F; font-weight: 700; text-transform: uppercase; margin-top: 6px; letter-spacing: 0.4px; }}
  .progreso-divider {{ width: 1px; align-self: stretch; background: #E7ECE8; margin: 2px 0; }}

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
    display: grid !important;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }}
  div[role="radiogroup"] label {{
    background: #FFFFFF;
    border: 1px solid #E7ECE8;
    border-radius: 100px;
    padding: 10px 10px;
    font-weight: 600;
    font-size: 0.82rem;
    line-height: 1.1;
    display: flex;
    align-items: center;
    justify-content: center;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    width: 100%;
    box-sizing: border-box;
    transition: all 0.15s ease;
  }}
  div[role="radiogroup"] label p {{
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin: 0;
  }}
  div[role="radiogroup"] label:has(input:checked) {{
    background: {COLOR_VERDE};
    border-color: {COLOR_VERDE};
  }}
  div[role="radiogroup"] label:has(input:checked) p {{
    color: #FFFFFF !important;
  }}
  div[role="radiogroup"] input {{ display: none; }}
  /* Oculta el círculo del radio — varios selectores porque la estructura
     interna de BaseWeb varía entre versiones de Streamlit */
  div[role="radiogroup"] label > div:first-child,
  div[role="radiogroup"] label svg,
  div[role="radiogroup"] [data-baseweb="radio"] > div:first-child {{
    display: none !important;
    width: 0 !important;
    height: 0 !important;
  }}

  /* Botón de eliminar en el historial: ícono compacto, no la píldora
     grande por defecto — se aplica a cualquier fila (delbtn_<id>) */
  [class*="st-key-delbtn_"] [data-testid="stButton"] button {{
    background: #FCEDEB !important;
    color: {COLOR_ROJO} !important;
    border-radius: 50% !important;
    width: 34px !important;
    height: 34px !important;
    min-height: 34px !important;
    padding: 0 !important;
    box-shadow: none !important;
    font-size: 0.85rem !important;
  }}

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

DIAS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES_ES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
            "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
ZONA_ECUADOR = ZoneInfo("America/Guayaquil")


def _saludo_contextual(nombre: str) -> dict:
    """El saludo cambia en 3 franjas; el fondo (día/noche) en 2, para
    mantenerlo simple y confiable. Usa siempre la hora de Ecuador, sin
    importar en qué servidor/huso horario esté corriendo la app."""
    hora = datetime.now(ZONA_ECUADOR).hour
    es_dia = 5 <= hora < 19
    if 5 <= hora < 12:
        saludo, icono = f"¡Buenos días, {nombre}!", "☀️"
    elif 12 <= hora < 19:
        saludo, icono = f"¡Buenas tardes, {nombre}!", "🌤️"
    else:
        saludo, icono = f"¡Buenas noches, {nombre}!", "🌙"

    if es_dia:
        return {
            "saludo": saludo, "icono": icono, "es_dia": True,
            "fondo": f"linear-gradient(160deg, #EAFBF1 0%, #C9F0DA 55%, {COLOR_VERDE_CLARO} 100%)",
            "astro": "radial-gradient(circle at 82% 20%, #FFE9A8 0%, #FFDD6E 30%, rgba(255,221,110,0) 65%)",
            "color_monte": COLOR_VERDE,
            "color_texto": COLOR_TINTA, "color_sub": "#3E5A4B",
        }
    else:
        return {
            "saludo": saludo, "icono": icono, "es_dia": False,
            "fondo": "linear-gradient(160deg, #0F5636 0%, #0A3D27 55%, #041712 100%)",
            "astro": (
                "radial-gradient(circle at 82% 20%, #F4F1DE 0%, #F4F1DE 22%, rgba(244,241,222,0) 45%),"
                "radial-gradient(1.5px 1.5px at 15% 25%, #fff 0, transparent 60%),"
                "radial-gradient(1.5px 1.5px at 35% 15%, #fff 0, transparent 60%),"
                "radial-gradient(1px 1px at 55% 35%, #fff 0, transparent 60%),"
                "radial-gradient(1.5px 1.5px at 25% 45%, #fff 0, transparent 60%),"
                "radial-gradient(1px 1px at 45% 22%, #fff 0, transparent 60%)"
            ),
            "color_monte": "#083C28",
            "color_texto": "#FFFFFF", "color_sub": "rgba(255,255,255,0.75)",
        }


def _svg_escena_racha(dias: int, viva: bool) -> str:
    """Mini-paisaje con un árbol que crece con la racha.

    - 0 días: solo tierra con una semilla recién plantada.
    - Crecimiento continuo (sin saltos bruscos) hasta ~30 días, con
      tronco, copa en capas (más volumen) y ramas.
    - Día 21+: brotes dorados en la copa, como premio visual.
    - Racha rota (viva=False): escena en tonos apagados y sin balanceo,
      para transmitir "está dormida, revívela".
    - El número de racha va como insignia flotante aparte (ver
      render_leaderboard / Mi Progreso), no dentro del dibujo.
    """
    COLOR_MARRON = "#8B5E34"
    g = min(dias / 30, 1.0)  # factor de crecimiento 0..1
    cx, base_y = 66, 92
    semilla = dias == 0

    defs = (
        '<defs>'
        '<linearGradient id="cieloRachaGrad" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="#EAFBF1" /><stop offset="100%" stop-color="#CFEEDD" /></linearGradient>'
        '<radialGradient id="solRachaGrad" cx="50%" cy="50%" r="50%">'
        '<stop offset="0%" stop-color="#FFEFAF" stop-opacity="0.85" /><stop offset="100%" stop-color="#FFEFAF" stop-opacity="0" /></radialGradient>'
        '</defs>'
    )
    cielo = '<rect x="0" y="0" width="160" height="110" fill="url(#cieloRachaGrad)" />'
    sol = '<circle cx="20" cy="22" r="28" fill="url(#solRachaGrad)" />'
    colina_fondo = f'<path d="M0,80 Q40,64 80,76 T160,72 L160,110 L0,110 Z" fill="{COLOR_VERDE_CLARO}" fill-opacity="0.32" />'
    suelo = f'<path d="M0,88 Q40,74 80,86 T160,82 L160,110 L0,110 Z" fill="{COLOR_VERDE}" fill-opacity="0.55" />'

    if semilla:
        planta = (
            f'<ellipse cx="{cx}" cy="{base_y-2}" rx="14" ry="4" fill="{COLOR_VERDE}" fill-opacity="0.3" />'
            f'<circle cx="{cx}" cy="{base_y-4}" r="3.4" fill="{COLOR_VERDE_CLARO}" />'
        )
    else:
        alto = 16 + 50 * g
        top_y = base_y - alto
        bw = 5 + 5 * g   # ancho del tronco en la base
        tw = 2 + 2 * g   # ancho del tronco arriba (afinado)
        tronco = (
            f'<path d="M {cx-bw/2:.1f} {base_y} L {cx-tw/2:.1f} {top_y:.1f} '
            f'L {cx+tw/2:.1f} {top_y:.1f} L {cx+bw/2:.1f} {base_y} Z" fill="{COLOR_MARRON}" />'
        )
        sombra = f'<ellipse cx="{cx}" cy="{base_y+3}" rx="{bw*1.5:.1f}" ry="2.6" fill="#0A2419" fill-opacity="0.12" />'

        ramas = ""
        if g > 0.3:
            fr = min((g - 0.3) / 0.7, 1.0)
            lr = 7 + 8 * fr
            y_rama = top_y + alto * 0.3
            ramas = (
                f'<path d="M {cx:.1f} {y_rama:.1f} q -{lr:.1f} -3 -{lr*1.2:.1f} -{lr*0.4:.1f}" fill="none" '
                f'stroke="{COLOR_MARRON}" stroke-width="{1.6+1.4*fr:.1f}" stroke-linecap="round" />'
                f'<path d="M {cx:.1f} {(y_rama-5):.1f} q {lr:.1f} -3 {lr*1.2:.1f} -{lr*0.4:.1f}" fill="none" '
                f'stroke="{COLOR_MARRON}" stroke-width="{1.6+1.4*fr:.1f}" stroke-linecap="round" />'
            )

        # Copa en capas: fondo más oscuro para dar cuerpo + luces más
        # claras arriba a la izquierda, simulando volumen con el sol.
        copa = ""
        if g > 0.04:
            r = 9 + 7 * g
            for dx, dy in [(-r*0.55, r*0.12), (r*0.55, r*0.12), (0, -r*0.4)]:
                copa += (
                    f'<ellipse cx="{cx+dx:.1f}" cy="{top_y+dy:.1f}" rx="{r*0.85:.1f}" ry="{r*0.72:.1f}" '
                    f'fill="{COLOR_VERDE}" />'
                )
            for dx, dy in [(-r*0.32, -r*0.28), (r*0.18, -r*0.42)]:
                copa += (
                    f'<ellipse cx="{cx+dx:.1f}" cy="{top_y+dy:.1f}" rx="{r*0.48:.1f}" ry="{r*0.4:.1f}" '
                    f'fill="{COLOR_VERDE_CLARO}" fill-opacity="0.85" />'
                )

        pasto = (
            f'<path d="M {cx-bw*1.8:.1f} {base_y} q 2 -6 4 0" fill="none" stroke="{COLOR_VERDE}" '
            f'stroke-width="1.6" stroke-linecap="round" />'
            f'<path d="M {cx+bw*1.6:.1f} {base_y} q -2 -7 3 -1" fill="none" stroke="{COLOR_VERDE}" '
            f'stroke-width="1.6" stroke-linecap="round" />'
        )

        flores = ""
        if dias >= 21:
            r = 9 + 7 * g
            for dx, dy in [(-r*0.4, -r*0.5), (r*0.35, -r*0.15), (-r*0.1, r*0.05)]:
                flores += f'<circle cx="{cx+dx:.1f}" cy="{top_y+dy:.1f}" r="1.7" fill="{COLOR_ORO}" />'

        planta = sombra + tronco + ramas + copa + flores + pasto

    clase_anim = "racha-arbol-anim" if (viva and not semilla) else ""
    clase_dormido = "" if viva else "racha-arbol-dormant"

    escena_svg = (
        '<svg viewBox="0 0 160 110" preserveAspectRatio="xMidYMax slice" xmlns="http://www.w3.org/2000/svg">'
        f'{defs}{cielo}{sol}{colina_fondo}{suelo}<g class="{clase_anim}">{planta}</g></svg>'
    )
    badge = f'<div class="racha-badge">🔥 {dias}</div>'
    caption = '<div class="racha-caption">Racha Actual</div>'
    return f'<div class="racha-arbol-bg {clase_dormido}">{escena_svg}</div>{badge}{caption}'


if "usuario_conectado" not in st.session_state:
    _cookie_id = cookies.get("usuario_id")
    _cookie_correo = cookies.get("usuario_correo")
    if st.session_state.get("sesion_recien_cerrada"):
        if not _cookie_id and not _cookie_correo:
            st.session_state["sesion_recien_cerrada"] = False
    elif _cookie_id and _cookie_correo:
        st.session_state["usuario_conectado"] = {"id": int(_cookie_id), "correo": _cookie_correo}

if "usuario_conectado" not in st.session_state:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
      {_logo_tag}
      <h1 style="margin:0;font-size:1.6rem;font-family:'Sora',sans-serif;">Polibank · ESPOL</h1>
    </div>
    """, unsafe_allow_html=True)

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
                    cookies["usuario_id"] = str(resultado["id"])
                    cookies["usuario_correo"] = resultado["correo"]
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


else:
    user_id = st.session_state["usuario_conectado"]["id"]
    correo_user = st.session_state["usuario_conectado"]["correo"]
    nombre_user = correo_user.split("@")[0].capitalize()

    ahora = datetime.now(ZONA_ECUADOR)
    ctx = _saludo_contextual(nombre_user)
    subtitulo = f"{DIAS_ES[ahora.weekday()]} {ahora.day} de {MESES_ES[ahora.month - 1]} · {ahora.strftime('%I:%M %p').lstrip('0')}"

    st.markdown(f"""
    <style>
    .st-key-saludo_dinamico {{
      position: relative;
      overflow: hidden;
      background: {ctx['fondo']} !important;
      border-radius: 24px;
      padding: 18px 16px 12px 16px;
      margin-bottom: 16px;
      border: none !important;
      box-shadow: 0 10px 26px rgba(15,92,59,0.18);
    }}
    .st-key-saludo_dinamico [data-testid="stButton"] button {{
      background: {"rgba(255,255,255,0.16)" if not ctx["es_dia"] else "rgba(255,255,255,0.55)"} !important;
      color: {ctx['color_texto']} !important;
      box-shadow: none !important;
      font-size: 0.76rem !important;
      padding: 6px 4px !important;
    }}

    .st-key-saludo_dinamico::before {{
      content: "";
      position: absolute; inset: 0;
      background-image: {ctx['astro']};
      background-repeat: no-repeat;
      z-index: 0;
      pointer-events: none;
    }}
    .st-key-saludo_dinamico::after {{
      content: "";
      position: absolute; left: -10%; right: -10%; bottom: -10px; height: 60px;
      background: {ctx['color_monte']};
      opacity: 0.5;
      clip-path: polygon(0% 100%, 0% 55%, 12% 35%, 25% 58%, 38% 25%, 52% 55%, 65% 38%, 78% 60%, 90% 42%, 100% 58%, 100% 100%);
      z-index: 0;
      pointer-events: none;
      animation: deriva 22s linear infinite alternate;
    }}
    @keyframes deriva {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-4%); }} }}
    </style>
    """, unsafe_allow_html=True)

    with st.container(key="saludo_dinamico"):
        st.markdown(f"""
        <div style="position:relative;z-index:1;display:flex;flex-direction:column;align-items:center;text-align:center;">
          <div style="background:#FFFFFF;border-radius:100px;padding:10px;box-shadow:0 4px 14px rgba(0,0,0,0.14);margin-bottom:10px;">
            {_logo_tag}
          </div>
          <div style="font-size:1.15rem;font-weight:800;color:{ctx['color_texto']};font-family:'Sora',sans-serif;">
            {ctx['saludo']} {ctx['icono']}
          </div>
          <div style="font-size:0.8rem;color:{ctx['color_sub']};margin-top:2px;">{subtitulo}</div>
        </div>
        """, unsafe_allow_html=True)

        _, col_salir = st.columns([5, 1])
        with col_salir:
            if st.button("Salir ✕", key="btn_salir_hero", use_container_width=True):
                del st.session_state["usuario_conectado"]
                if "usuario_id" in cookies:
                    del cookies["usuario_id"]
                if "usuario_correo" in cookies:
                    del cookies["usuario_correo"]
                cookies.save()
                st.session_state["sesion_recien_cerrada"] = True
                st.rerun()


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

    opcion_menu = st.radio(
        "📱 Menú Polibank",
        ["💰 Finanzas Personales", "🏆 Mi Progreso", "📚 Academia Financiera", "🐢 Asistente Polibank"],
        horizontal=True,
        label_visibility="collapsed",
    )
    st.divider()

    if "gami_notif" in st.session_state:
        notif = st.session_state.pop("gami_notif")
        for b in notif.get("badges_nuevos", []):
            info = BADGES.get(b, {})
            st.markdown(
                f'<div class="toast-nuevo">🏅 ¡Nuevo logro! {info.get("emoji", "")} '
                f'<strong>{info.get("nombre", "")}</strong> — {info.get("desc", "")}</div>',
                unsafe_allow_html=True
            )

    if opcion_menu == "💰 Finanzas Personales":

        movimientos_db = obtener_movimientos(user_id)

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
            cat = (mov.get("categoria") or "OTROS").upper()
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

        st.subheader("Resumen de tu Cuenta")
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
                        font=dict(size=11, color="#12241C"), bgcolor="rgba(0,0,0,0)",
                        title_text=""
                    ),
                    xaxis=dict(showgrid=False, linecolor="#E7ECE8",
                               tickfont=dict(size=10, color="#7A8A80"), title=""),
                    yaxis=dict(showgrid=True, gridcolor="#F0F4F1",
                               linecolor="#E7ECE8", tickfont=dict(size=10, color="#7A8A80"),
                               tickprefix="$", title="", fixedrange=True),
                    xaxis_fixedrange=False,
                    dragmode="pan",
                    bargap=0.12, bargroupgap=0.04,
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

        st.subheader("Registrar Movimiento")
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
                            sumar_xp_semanal(user_id, res_gami["xp_ganado"])
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
            col_lbl, col_add = st.columns([5, 1])
            with col_lbl:
                st.markdown(
                    '<div style="font-size:0.82rem;font-weight:600;color:#31333F;margin-top:8px;">¿En qué gastaste?</div>',
                    unsafe_allow_html=True
                )
            with col_add:
                with st.popover("➕"):
                    st.markdown("**Gastos recurrentes**")
                    recurrentes = obtener_gastos_recurrentes(user_id)
                    if recurrentes:
                        for r in recurrentes:
                            c1, c2 = st.columns([4, 1])
                            with c1:
                                if st.button(r["nombre"], key=f"rec_{r['id']}", use_container_width=True):
                                    st.session_state["texto_gas_input"] = r["nombre"]
                                    st.rerun()
                            with c2:
                                if st.button("🗑️", key=f"delrec_{r['id']}"):
                                    eliminar_gasto_recurrente(r["id"])
                                    st.rerun()
                    else:
                        st.caption("Aún no tienes gastos recurrentes guardados.")
                    st.divider()
                    nuevo_rec = st.text_input(
                        "Agregar nuevo", key="nuevo_recurrente_input",
                        placeholder="Ej: Almuerzo", label_visibility="collapsed"
                    )
                    if st.button("➕ Agregar a la lista", key="btn_add_recurrente", use_container_width=True):
                        if nuevo_rec.strip():
                            agregar_gasto_recurrente(user_id, nuevo_rec.strip())
                            st.rerun()

            with st.form("form_gasto", clear_on_submit=True):
                monto_gas = st.number_input("Monto ($)", min_value=0.01, step=1.0)
                texto_gas = st.text_input(
                    "¿En qué gastaste?",
                    key="texto_gas_input",
                    placeholder="Almuerzo comedor FCSH, bus Guayaquil…",
                    label_visibility="collapsed"
                )
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
                            sumar_xp_semanal(user_id, res_gami["xp_ganado"])
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

        st.subheader("🗒️ Historial de Movimientos")

        if historial_tabla:
            historial_tabla.sort(key=lambda x: x["_fecha_dt"], reverse=True)

            col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
            with col_f1:
                filtro_tipo = st.selectbox("Tipo", ["Todos", "💵 Ingreso", "🛒 Gasto"], key="filtro_tipo")
            with col_f2:
                fecha_desde = st.date_input("Desde", value=None, key="fecha_desde")
            with col_f3:
                fecha_hasta = st.date_input("Hasta", value=None, key="fecha_hasta")

            lista = historial_tabla.copy()
            if filtro_tipo != "Todos":
                lista = [m for m in lista if m["Tipo"] == filtro_tipo]
            if fecha_desde:
                lista = [m for m in lista if m["_fecha_dt"].date() >= fecha_desde]
            if fecha_hasta:
                lista = [m for m in lista if m["_fecha_dt"].date() <= fecha_hasta]

            st.caption(f"Mostrando {min(len(lista), 8)} de {len(lista)} transacciones")


            def render_mov(mov):
                es_ingreso = mov["Tipo"] == "💵 Ingreso"
                color_m = COLOR_VERDE if es_ingreso else COLOR_ROJO
                tiene_factura = bool(mov.get("_factura_url"))
                icono_factura = " 📎" if tiene_factura else ""

                with st.container(key=f"movcard_{mov['_id']}"):
                    col_info, col_del = st.columns([11, 1], vertical_alignment="center")
                    with col_info:
                        st.markdown(
                            f'<div style="display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap;">'
                            f'<span style="font-size:0.78rem;color:#999;">{mov["Fecha"]}</span>'
                            f'{badge_cat(mov["Categoría"])}'
                            f'</div>'
                            f'<div style="display:flex;align-items:center;justify-content:space-between;gap:8px;margin-top:6px;">'
                            f'<span class="mov-detalle" style="margin-top:0;">{mov["Detalle"]}{icono_factura}</span>'
                            f'<span class="mov-monto" style="color:{color_m};white-space:nowrap;">{mov["Monto ($)"]}</span>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    with col_del:
                        with st.container(key=f"delbtn_{mov['_id']}"):
                            if mov.get("_id") and st.button("🗑️", key=f"del_{mov['_id']}"):
                                ok, _ = eliminar_movimiento(mov["_id"])
                                if ok:
                                    st.rerun()

                    if tiene_factura:
                        url = mov["_factura_url"]
                        with st.expander("📎 Ver factura adjunta"):
                            if url.lower().endswith(".pdf"):
                                st.markdown(
                                    f'<a href="{url}" target="_blank" style="font-weight:600;color:{COLOR_VERDE};">'
                                    f'📄 Abrir PDF en nueva pestaña</a>',
                                    unsafe_allow_html=True
                                )
                            else:
                                st.image(url, use_container_width=True)
                                st.markdown(
                                    f'<a href="{url}" target="_blank" style="font-size:0.8rem;color:#888;">Ver en tamaño completo ↗</a>',
                                    unsafe_allow_html=True
                                )


            for mov in lista[:8]:
                render_mov(mov)

            if len(lista) > 8:
                with st.expander(f"Ver {len(lista) - 8} transacciones más…"):
                    for mov in lista[8:]:
                        render_mov(mov)
        else:
            st.info("No hay transacciones registradas aún.")


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
        <div class="progreso-card">
          <div class="progreso-escena">
            {_svg_escena_racha(gami['racha_actual'], gami['racha_viva'])}
          </div>
          <div class="progreso-stats-row">
            <div class="progreso-stat">
              <div class="progreso-stat-val" style="color:{COLOR_ORO};">⭐ {gami['xp_total']}</div>
              <div class="progreso-stat-lbl">XP Total</div>
            </div>
            <div class="progreso-divider"></div>
            <div class="progreso-stat">
              <div class="progreso-stat-val" style="color:{COLOR_AZUL};">🏅 {len(gami['badges'])}/{len(BADGES)}</div>
              <div class="progreso-stat-lbl">Logros</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if not gami["racha_viva"] and gami["racha_actual"] == 0:
            st.info("💡 Registra un ingreso o gasto hoy para iniciar tu racha.")
        elif gami["racha_viva"]:
            st.markdown('<div class="tip-box">🌱 ¡Sigue sumando días y tu árbol seguirá creciendo! Vuelve mañana para no perder la racha.</div>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ Tu racha se rompió. ¡Registra un movimiento hoy para reiniciarla!")

        if gami["racha_maxima"] > 0:
            st.caption(f"🏆 Tu récord personal: **{gami['racha_maxima']} días** seguidos")

        tab_ranking, tab_logros = st.tabs(["🏆 Ranking Semanal", "🏅 Mis Logros"])

        with tab_logros:
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
| 📚 Completar un curso | +25 XP |
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

        with tab_ranking:
            render_leaderboard(user_id)


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

        if "chat_historial" not in st.session_state:
            st.session_state["chat_historial"] = []
        if "chat_input_key" not in st.session_state:
            st.session_state["chat_input_key"] = 0

        if not st.session_state["chat_historial"]:
            st.session_state["chat_historial"].append({
                "rol": "asistente",
                "texto": "¡Hola! 🐢 Soy Polibank, tu asistente personal. Puedo ayudarte con tus finanzas, responder preguntas, darte consejos personalizados o simplemente conversar. ¿En qué te ayudo hoy?"
            })

        for msg in st.session_state["chat_historial"]:
            if msg["rol"] == "usuario":
                with st.chat_message("user"):
                    st.write(msg["texto"])
            else:
                with st.chat_message("assistant", avatar="🐢"):
                    st.write(msg["texto"])

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

        if len(st.session_state["chat_historial"]) > 1:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            col_esp, col_btn = st.columns([3, 1])
            with col_btn:
                if st.button("🗑️ Limpiar", key="limpiar_chat", use_container_width=True):
                    st.session_state["chat_historial"] = []
                    st.session_state["chat_input_key"] += 1
                    st.rerun()

    elif opcion_menu == "📚 Academia Financiera":

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

        render_academia(user_id, registrar_accion)