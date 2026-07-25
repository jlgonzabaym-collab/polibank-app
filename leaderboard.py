"""
leaderboard.py — Tabla de clasificación semanal de Polibank
"""
import streamlit as st
from datetime import date, timedelta
from config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client

supabase = create_client(SUPABASE_URL.strip().rstrip('/'), SUPABASE_KEY.strip())

COLOR_VERDE = "#1B8A4C"


def _lunes_semana_actual() -> date:
    hoy = date.today()
    return hoy - timedelta(days=hoy.weekday())


def _dias_restantes() -> int:
    lunes = _lunes_semana_actual()
    proximo_lunes = lunes + timedelta(days=7)
    return (proximo_lunes - date.today()).days


def sumar_xp_semanal(usuario_id: int, xp: int):
    """Suma XP al contador semanal del usuario."""
    try:
        semana = str(_lunes_semana_actual())
        existente = supabase.from_("xp_semanal").select("*")\
            .eq("usuario_id", usuario_id).eq("semana", semana).execute()
        if existente.data:
            nuevo_xp = existente.data[0]["xp_semana"] + xp
            supabase.from_("xp_semanal").update({"xp_semana": nuevo_xp})\
                .eq("usuario_id", usuario_id).eq("semana", semana).execute()
        else:
            supabase.from_("xp_semanal").insert({
                "usuario_id": usuario_id,
                "semana": semana,
                "xp_semana": xp
            }).execute()
    except Exception as e:
        print(f"Error sumando XP semanal: {e}")


def obtener_ranking(limite: int = 10) -> list:
    """Obtiene el top N de usuarios de la semana actual."""
    try:
        semana = str(_lunes_semana_actual())
        res = supabase.from_("xp_semanal").select(
            "xp_semana, usuario_id, usuarios(correo)"
        ).eq("semana", semana)\
         .order("xp_semana", desc=True)\
         .limit(limite).execute()
        ranking = []
        for i, r in enumerate(res.data or []):
            correo = r.get("usuarios", {}).get("correo", "usuario")
            nombre = correo.split("@")[0][:12]
            ranking.append({
                "pos":       i + 1,
                "usuario_id": r["usuario_id"],
                "nombre":    nombre,
                "xp":        r["xp_semana"],
            })
        return ranking
    except Exception as e:
        print(f"Error obteniendo ranking: {e}")
        return []


def obtener_posicion_usuario(usuario_id: int) -> dict:
    """Obtiene posición y XP semanal del usuario actual."""
    try:
        semana = str(_lunes_semana_actual())
        res = supabase.from_("xp_semanal").select("xp_semana")\
            .eq("usuario_id", usuario_id).eq("semana", semana).execute()
        xp_usuario = res.data[0]["xp_semana"] if res.data else 0

        # Contar cuántos tienen más XP
        conteo = supabase.from_("xp_semanal").select("usuario_id", count="exact")\
            .eq("semana", semana).gt("xp_semana", xp_usuario).execute()
        posicion = (conteo.count or 0) + 1

        # XP del usuario anterior para saber cuánto le falta
        anterior = supabase.from_("xp_semanal").select("xp_semana")\
            .eq("semana", semana).gt("xp_semana", xp_usuario)\
            .order("xp_semana").limit(1).execute()
        xp_siguiente = anterior.data[0]["xp_semana"] if anterior.data else None

        return {
            "posicion":     posicion,
            "xp_semana":    xp_usuario,
            "xp_siguiente": xp_siguiente,
            "faltan":       (xp_siguiente - xp_usuario) if xp_siguiente else 0
        }
    except Exception as e:
        print(f"Error posición: {e}")
        return {"posicion": 0, "xp_semana": 0, "xp_siguiente": None, "faltan": 0}


CSS_LB = f"""
<style>
.lb-header {{
  background: linear-gradient(135deg, #1B5E20, #2E7D32);
  border-radius: 16px; padding: 16px 20px; color: white; margin-bottom: 20px;
}}
.lb-title {{ font-size: 1.05rem; font-weight: 800; margin-bottom: 2px; }}
.lb-sub   {{ font-size: 0.78rem; opacity: .8; margin-bottom: 10px; }}
.lb-header-row {{ display: flex; align-items: center; justify-content: space-between; }}
.reset-badge {{
  background: rgba(255,255,255,.15); border: 1px solid rgba(255,255,255,.25);
  border-radius: 20px; padding: 4px 10px; font-size: 0.72rem; font-weight: 700;
}}
.lb-top3 {{
  display: grid; grid-template-columns: 1fr 1.12fr 1fr;
  gap: 8px; margin-bottom: 16px;
}}
.podio-card {{
  border-radius: 14px; padding: 14px 10px; text-align: center;
  border: 0.5px solid #e0e0e0;
}}
.podio-card.p1 {{
  background: linear-gradient(160deg, #FFF8E1, #FFF3CD);
  border: 1.5px solid #F9A825; position: relative; overflow: hidden;
}}
.podio-card.p2 {{ background: linear-gradient(160deg, #F5F5F5, #ECEFF1); border-color: #90A4AE; }}
.podio-card.p3 {{ background: linear-gradient(160deg, #FBE9E7, #FFF3E0); border-color: #FFAB91; }}
.shimmer {{
  position: absolute; inset: 0; pointer-events: none;
  background: linear-gradient(105deg, transparent 40%, rgba(255,255,255,.4) 50%, transparent 60%);
  background-size: 200% 100%;
  animation: shimmer 2.5s linear infinite;
}}
@keyframes shimmer {{ 0%{{background-position:200% 0}} 100%{{background-position:-200% 0}} }}
.corona {{
  font-size: 1.6rem; display: block; margin-bottom: 2px;
  animation: bounce 1.8s ease-in-out infinite;
}}
@keyframes bounce {{
  0%,100%{{transform:translateY(0) rotate(-5deg)}} 50%{{transform:translateY(-5px) rotate(5deg)}}
}}
.podio-pos  {{ font-size: 0.7rem; font-weight: 700; color: #888; margin-bottom: 3px; }}
.podio-med  {{ font-size: 1.3rem; margin-bottom: 3px; }}
.podio-name {{ font-size: 0.8rem; font-weight: 700; color: #222; margin-bottom: 2px; }}
.podio-xp   {{ font-size: 0.75rem; color: #666; }}
.podio-xp strong {{ color: #111; font-weight: 800; }}

.capsula {{
  border-radius: 12px; padding: 10px 14px;
  border: 0.5px solid #e8e8e8; background: white;
  display: flex; align-items: center; gap: 12px; margin-bottom: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,.05);
}}
.capsula.yo {{
  border: 1.5px solid {COLOR_VERDE}; background: #f0fdf4;
}}
.cap-pos {{ font-size: 0.82rem; font-weight: 700; color: #aaa; min-width: 20px; text-align: center; }}
.cap-avatar {{
  width: 34px; height: 34px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.82rem; font-weight: 700; flex-shrink: 0;
}}
.cap-info {{ flex: 1; }}
.cap-name  {{ font-size: 0.85rem; font-weight: 700; color: #222; }}
.cap-nivel {{ font-size: 0.7rem; color: #888; }}
.cap-xp-val {{ font-size: 0.92rem; font-weight: 800; color: #111; text-align: right; }}
.cap-xp-lbl {{ font-size: 0.65rem; color: #aaa; text-align: right; }}
.badge-yo {{
  font-size: 0.62rem; font-weight: 700;
  background: #d1fae5; color: #065f46;
  border-radius: 20px; padding: 1px 7px;
  border: 1px solid #6ee7b7; margin-left: 5px;
}}
.mi-pos-box {{
  border-radius: 12px; padding: 12px 16px;
  border: 1.5px solid {COLOR_VERDE};
  background: linear-gradient(135deg, #f0fdf4, #dcfce7);
  display: flex; align-items: center; justify-content: space-between;
  margin-top: 4px;
}}
.mi-pos-num {{ font-size: 1.5rem; font-weight: 800; color: #065f46; }}
.mi-pos-txt {{ font-size: 0.85rem; font-weight: 700; color: #065f46; }}
.mi-pos-sub {{ font-size: 0.75rem; color: #16a34a; margin-top: 2px; }}
.vacio-box {{
  text-align: center; padding: 28px 16px;
  background: #f8fffe; border-radius: 14px;
  border: 1px dashed #c3e6cb; margin-bottom: 16px;
}}
</style>
"""

COLORES_AVATAR = [
    ("#EDE9FE", "#6D28D9"), ("#FEF3C7", "#D97706"),
    ("#FCE7F3", "#BE185D"), ("#DBEAFE", "#1D4ED8"),
    ("#FFF7ED", "#C2410C"), ("#F0FDF4", "#15803D"),
    ("#F5F3FF", "#7C3AED"), ("#FFF1F2", "#BE123C"),
]


def render_leaderboard(usuario_id: int):
    st.markdown(CSS_LB, unsafe_allow_html=True)

    dias = _dias_restantes()
    semana_str = _lunes_semana_actual().strftime("%d de %B")
    ranking    = obtener_ranking(10)
    mi_pos     = obtener_posicion_usuario(usuario_id)

    # Header
    st.markdown(f"""
    <div class="lb-header">
      <div class="lb-header-row">
        <div>
          <div class="lb-title">🏆 Clasificación Semanal</div>
          <div class="lb-sub">Semana del {semana_str} · Se reinicia cada lunes</div>
        </div>
        <div class="reset-badge">⏱ {dias} día{'s' if dias != 1 else ''} restante{'s' if dias != 1 else ''}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if not ranking:
        st.markdown("""
        <div class="vacio-box">
          <div style="font-size:2rem;margin-bottom:8px;">🏁</div>
          <div style="font-weight:800;color:#1B8A4C;font-size:1rem;margin-bottom:4px;">
            ¡Sé el primero esta semana!
          </div>
          <div style="font-size:0.82rem;color:#555;">
            Registra movimientos, completa cursos y gana XP para aparecer en el ranking.
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── TOP 3 PODIO
    top3 = ranking[:3]
    orden_podio = [1, 0, 2] if len(top3) >= 3 else list(range(len(top3)))
    medallas    = ["🥈", "🥇", "🥉"]
    clases      = ["p2", "p1", "p3"]
    posiciones  = ["2° lugar", "1° lugar", "3° lugar"]

    html_podio = '<div class="lb-top3">'
    for idx in orden_podio:
        if idx >= len(top3): continue
        u   = top3[idx]
        cls = clases[idx]
        med = medallas[idx]
        pos = posiciones[idx]
        es_lider = idx == 0
        shimmer  = '<div class="shimmer"></div>' if es_lider else ""
        corona   = '<span class="corona">👑</span>' if es_lider else f'<div class="podio-med">{med}</div>'
        es_yo    = u["usuario_id"] == usuario_id
        nombre   = u["nombre"] + (" (tú)" if es_yo else "")

        html_podio += f"""
        <div class="podio-card {cls}">
          {shimmer}
          {corona}
          <div class="podio-pos">{pos}</div>
          <div class="podio-name">{nombre}</div>
          <div class="podio-xp"><strong>{u['xp']}</strong> XP</div>
        </div>"""
    html_podio += "</div>"
    st.markdown(html_podio, unsafe_allow_html=True)

    # ── LISTA DESDE PUESTO 4
    resto = ranking[3:]
    if resto:
        for u in resto:
            es_yo   = u["usuario_id"] == usuario_id
            cls_cap = "capsula yo" if es_yo else "capsula"
            iniciales = u["nombre"][:2].upper()
            color_bg, color_txt = COLORES_AVATAR[(u["pos"] - 4) % len(COLORES_AVATAR)]
            badge_yo = '<span class="badge-yo">Tú</span>' if es_yo else ""

            st.markdown(f"""
            <div class="{cls_cap}">
              <div class="cap-pos">{u['pos']}</div>
              <div class="cap-avatar" style="background:{color_bg};color:{color_txt};">{iniciales}</div>
              <div class="cap-info">
                <div class="cap-name">{u['nombre']}{badge_yo}</div>
                <div class="cap-nivel">⭐ {u['xp']} XP esta semana</div>
              </div>
              <div>
                <div class="cap-xp-val">{u['xp']} XP</div>
                <div class="cap-xp-lbl">esta semana</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ── MI POSICIÓN (si no está en el top 10)
    en_ranking = any(u["usuario_id"] == usuario_id for u in ranking)
    if not en_ranking and mi_pos["xp_semana"] > 0:
        st.markdown(f"""
        <div class="mi-pos-box">
          <div>
            <div class="mi-pos-txt">Tu posición esta semana</div>
            <div class="mi-pos-sub">
              {'Te faltan ' + str(mi_pos['faltan']) + ' XP para subir' if mi_pos['faltan'] > 0 else '¡Gana XP para aparecer en el ranking!'}
            </div>
          </div>
          <div class="mi-pos-num">#{mi_pos['posicion']}</div>
        </div>
        """, unsafe_allow_html=True)
    elif not en_ranking:
        st.markdown(f"""
        <div class="mi-pos-box">
          <div>
            <div class="mi-pos-txt">Aún no tienes XP esta semana</div>
            <div class="mi-pos-sub">Registra un movimiento o completa un curso para entrar al ranking</div>
          </div>
          <div class="mi-pos-num">—</div>
        </div>
        """, unsafe_allow_html=True)