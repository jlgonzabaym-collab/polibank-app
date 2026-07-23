"""
academia_ui.py — Sistema de aprendizaje estilo Duolingo con mapa en zigzag
"""
import streamlit as st
from app.lecciones import LECCIONES, obtener_progreso, marcar_leccion_completada

COLOR_VERDE  = "#1B8A4C"
COLOR_AZUL   = "#2E86AB"
COLOR_ORO    = "#F39C12"
COLOR_ROJO   = "#E74C3C"
COLOR_MORADO = "#8E44AD"

COLORES_NIVEL = {1: "#27AE60", 2: "#2E86AB", 3: "#8E44AD"}
NOMBRES_NIVEL = {1: "Básico", 2: "Intermedio", 3: "Avanzado"}

AVATARES_POR_XP = [
    (0,   "🥚",  "Huevo"),
    (25,  "🐣",  "Pollito"),
    (75,  "🐥",  "Polluelo"),
    (125, "🦊",  "Zorro"),
    (175, "🦁",  "León"),
    (50,  "🦅",  "Águila"),   # nivel 6
    (225, "🌟",  "Estrella"),
    (999, "👑",  "Maestro"),
]

CSS = f"""
<style>
/* ── Mapa zigzag ── */
.mapa-header {{
  background: linear-gradient(135deg, {COLOR_VERDE}, #27AE60);
  border-radius: 16px; padding: 20px 24px; color: white; margin-bottom: 8px;
}}
.mapa-header-titulo {{ font-size: 1.2rem; font-weight: 800; margin-bottom: 2px; }}
.mapa-header-sub {{ font-size: 0.82rem; opacity: .8; margin-bottom: 12px; }}
.xp-bar-wrap {{
  background: rgba(255,255,255,.25); border-radius: 20px; height: 8px;
  margin: 8px 0 4px; overflow: hidden;
}}
.xp-bar-fill {{ height: 8px; border-radius: 20px; background: white; }}
.xp-bar-label {{ font-size: 0.72rem; opacity: .75; }}

/* ── Personaje flotante ── */
.personaje-box {{
  text-align: center; padding: 12px 0 4px;
}}
.personaje-avatar {{
  font-size: 2.4rem; display: block;
  animation: float 2.8s ease-in-out infinite;
}}
@keyframes float {{
  0%,100% {{ transform: translateY(0); }}
  50%      {{ transform: translateY(-6px); }}
}}
.personaje-nombre {{
  font-size: 0.75rem; font-weight: 700; color: #888;
  text-transform: uppercase; letter-spacing: .5px; margin-top: 4px;
}}

/* ── Nivel separador ── */
.nivel-sep {{
  display: flex; align-items: center; gap: 10px;
  margin: 18px 0 4px;
  font-size: 0.8rem; font-weight: 700; color: #666;
}}
.nivel-pill-sep {{
  padding: 3px 12px; border-radius: 20px; font-size: 0.72rem;
  font-weight: 700; color: white;
}}

/* ── Nodo del mapa ── */
.zigzag-row {{
  display: flex; align-items: center;
  margin: 6px 0;
}}
.zigzag-row.derecha {{ justify-content: flex-end; }}
.zigzag-row.centro  {{ justify-content: center; }}
.zigzag-row.izquierda {{ justify-content: flex-start; }}

.nodo-btn {{
  width: 82px; height: 82px; border-radius: 50%;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  border: 3px solid #e0e0e0;
  background: white;
  cursor: pointer; transition: transform .15s;
  position: relative; text-align: center;
  box-shadow: 0 3px 10px rgba(0,0,0,0.10);
}}
.nodo-btn:hover {{ transform: scale(1.07); }}
.nodo-btn.completado {{
  background: #f0faf4; border-color: {COLOR_VERDE};
  box-shadow: 0 3px 10px rgba(27,138,76,.2);
}}
.nodo-btn.activo {{
  background: #e8f5fd; border-color: {COLOR_AZUL}; border-width: 3px;
  box-shadow: 0 3px 14px rgba(46,134,171,.25);
}}
.nodo-btn.bloqueado {{
  opacity: .38; cursor: not-allowed; background: #f8f8f8;
}}
.nodo-emoji {{ font-size: 1.6rem; line-height: 1; }}
.nodo-label {{
  font-size: 0.6rem; font-weight: 700; color: #666;
  margin-top: 3px; width: 70px; line-height: 1.2;
  text-align: center;
}}
.nodo-check {{
  position: absolute; top: -5px; right: -5px;
  width: 22px; height: 22px; border-radius: 50%;
  background: {COLOR_VERDE}; color: white;
  font-size: 12px; display: flex; align-items: center; justify-content: center;
  border: 2px solid white;
}}
.nodo-lock {{
  position: absolute; bottom: -5px; right: -5px;
  width: 20px; height: 20px; border-radius: 50%;
  background: #bbb; color: white;
  font-size: 10px; display: flex; align-items: center; justify-content: center;
  border: 2px solid white;
}}

/* ── Conector vertical ── */
.conector-v {{
  width: 3px; height: 28px; border-radius: 2px;
  background: #e0e0e0; margin: 0 auto;
}}
.conector-v.done {{ background: {COLOR_VERDE}; }}

/* ── Panel detalle ── */
.detalle-card {{
  background: white; border-radius: 14px;
  border: 2px solid {COLOR_VERDE};
  padding: 18px; margin: 12px 0;
  box-shadow: 0 4px 16px rgba(27,138,76,.12);
}}
.detalle-top {{
  display: flex; align-items: center; gap: 12px; margin-bottom: 10px;
}}
.detalle-big-emoji {{ font-size: 2.2rem; }}
.detalle-titulo {{ font-size: 1rem; font-weight: 800; color: #222; }}
.detalle-meta {{ font-size: 0.75rem; color: #888; margin-top: 2px; }}
.detalle-desc {{ font-size: 0.85rem; color: #555; margin-bottom: 14px; line-height: 1.5; }}
.detalle-xp {{
  display: inline-block; background: #FFF3CD; color: #856404;
  border-radius: 20px; padding: 3px 12px; font-size: 0.75rem; font-weight: 700;
  margin-bottom: 14px;
}}
.detalle-xp.verde {{ background: #d4edda; color: #155724; }}

/* ── Botones ── */
.btn-iniciar {{
  display: block; width: 100%;
  background: {COLOR_VERDE}; color: white; border: none;
  border-radius: 10px; padding: 12px; font-size: 0.92rem;
  font-weight: 700; cursor: pointer; text-align: center;
  box-shadow: 0 3px 10px rgba(27,138,76,.25);
}}
.btn-repasar {{
  display: block; width: 100%;
  background: white; color: {COLOR_VERDE};
  border: 2px solid {COLOR_VERDE};
  border-radius: 10px; padding: 10px; font-size: 0.88rem;
  font-weight: 700; cursor: pointer; text-align: center;
}}

/* ── Contenido lección ── */
.lec-hero {{
  border-radius: 14px; overflow: hidden; margin-bottom: 16px; position: relative;
}}
.lec-hero img {{ width: 100%; height: 180px; object-fit: cover; display: block; }}
.lec-hero-overlay {{
  position: absolute; bottom: 0; left: 0; right: 0;
  background: linear-gradient(transparent, rgba(0,0,0,.65));
  padding: 20px 16px 14px; color: white;
}}
.lec-overlay-nivel {{ font-size: 0.72rem; opacity: .8; margin-bottom: 2px; }}
.lec-overlay-titulo {{ font-size: 1.15rem; font-weight: 800; }}

.sec-card {{
  border-radius: 12px; padding: 16px; margin-bottom: 12px;
  border-left: 4px solid {COLOR_VERDE};
  background: #f8fffe;
}}
.sec-card.ejemplo {{ border-left-color: {COLOR_AZUL}; background: #f0f8ff; }}
.sec-card.dato    {{ border-left-color: {COLOR_ORO};  background: #fffbf0; }}
.sec-tipo {{ font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: .5px; color: #999; margin-bottom: 4px; }}
.sec-titulo {{ font-size: 0.95rem; font-weight: 800; color: #222; margin-bottom: 8px; }}
.sec-cuerpo {{ font-size: 0.85rem; color: #444; line-height: 1.6; }}

/* ── Quiz ── */
.quiz-prog {{
  display: flex; gap: 6px; margin-bottom: 16px;
}}
.quiz-prog-dot {{
  flex: 1; height: 6px; border-radius: 3px; background: #e0e0e0;
}}
.quiz-prog-dot.done {{ background: {COLOR_VERDE}; }}
.quiz-prog-dot.activo {{ background: {COLOR_AZUL}; }}

.quiz-card {{
  background: white; border-radius: 14px; padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,.08); margin-bottom: 12px;
}}
.quiz-num {{ font-size: 0.7rem; color: #aaa; font-weight: 700; margin-bottom: 6px; }}
.quiz-pregunta {{ font-size: 1rem; font-weight: 800; color: #222; margin-bottom: 16px; }}
.quiz-opcion {{
  display: block; width: 100%; text-align: left;
  padding: 10px 14px; margin-bottom: 8px;
  border-radius: 10px; border: 2px solid #e0e0e0;
  background: white; cursor: pointer; font-size: 0.88rem;
  transition: all .15s; font-family: inherit;
}}
.quiz-opcion:hover {{ border-color: {COLOR_AZUL}; background: #f0f8ff; }}
.quiz-opcion.correcta {{ border-color: {COLOR_VERDE}; background: #f0faf4; color: #155724; font-weight: 700; }}
.quiz-opcion.incorrecta {{ border-color: {COLOR_ROJO}; background: #fdf2f2; color: #721c24; }}
.quiz-expl {{
  border-radius: 8px; padding: 10px 14px; margin-top: 6px;
  font-size: 0.82rem; line-height: 1.5;
}}
.quiz-expl.ok {{ background: #d4edda; color: #155724; }}
.quiz-expl.mal {{ background: #f8d7da; color: #721c24; }}

/* ── Resultado ── */
.resultado-hero {{
  background: linear-gradient(135deg, {COLOR_VERDE}, #27AE60);
  border-radius: 16px; padding: 28px; text-align: center; color: white; margin-bottom: 16px;
}}
.resultado-emoji {{ font-size: 3rem; margin-bottom: 8px; }}
.resultado-titulo {{ font-size: 1.4rem; font-weight: 800; margin-bottom: 4px; }}
.resultado-sub {{ opacity: .85; font-size: 0.9rem; }}
.resultado-xp {{ font-size: 1.1rem; font-weight: 800; margin-top: 12px; }}

.revision-item {{ margin-bottom: 14px; }}
.rev-pregunta {{ font-size: 0.85rem; font-weight: 700; color: #333; margin-bottom: 6px; }}
.rev-resp {{ font-size: 0.82rem; margin-bottom: 4px; color: #555; }}
</style>
"""


def render_academia(user_id: int, registrar_accion_fn):
    st.markdown(CSS, unsafe_allow_html=True)
    registrar_accion_fn(user_id, "video", {"_visito_academia": True})

    if "lec_vista"       not in st.session_state: st.session_state["lec_vista"]       = None
    if "lec_fase"        not in st.session_state: st.session_state["lec_fase"]         = "contenido"
    if "quiz_resp"       not in st.session_state: st.session_state["quiz_resp"]         = {}
    if "quiz_idx"        not in st.session_state: st.session_state["quiz_idx"]          = 0
    if "quiz_mostrar"    not in st.session_state: st.session_state["quiz_mostrar"]      = False
    if "nodo_selec"      not in st.session_state: st.session_state["nodo_selec"]        = None

    progreso = obtener_progreso(user_id)
    total_comp = sum(1 for v in progreso.values() if v == "completada")
    xp_total   = total_comp * 25

    if st.session_state["lec_vista"] is None:
        _render_mapa(user_id, progreso, xp_total)
    else:
        lec = next((l for l in LECCIONES if l["id"] == st.session_state["lec_vista"]), None)
        if lec is None:
            st.session_state["lec_vista"] = None
            st.rerun()
            return
        fase = st.session_state["lec_fase"]
        if fase   == "contenido": _render_contenido(lec)
        elif fase == "quiz":      _render_quiz(lec, progreso)
        elif fase == "resultado": _render_resultado(lec, user_id, progreso, registrar_accion_fn)


def _avatar_info(xp):
    avatar, nombre = "🥚", "Principiante"
    if xp >= 225: avatar, nombre = "👑", "Maestro"
    elif xp >= 175: avatar, nombre = "🌟", "Estrella"
    elif xp >= 125: avatar, nombre = "🦅", "Águila"
    elif xp >= 75:  avatar, nombre = "🦁", "León"
    elif xp >= 50:  avatar, nombre = "🦊", "Zorro"
    elif xp >= 25:  avatar, nombre = "🐥", "Polluelo"
    elif xp >= 1:   avatar, nombre = "🐣", "Pollito"
    return avatar, nombre


def _render_mapa(user_id, progreso, xp_total):
    total_lec  = len(LECCIONES)
    total_comp = sum(1 for v in progreso.values() if v == "completada")
    pct        = int((total_comp / total_lec) * 100)
    avatar, nombre_avatar = _avatar_info(xp_total)

    # ── Header
    st.markdown(f"""
    <div class="mapa-header">
      <div class="mapa-header-titulo">📚 Academia Polibank</div>
      <div class="mapa-header-sub">Completa lecciones para desbloquear el siguiente nivel</div>
      <div style="font-size:.78rem;opacity:.8;">{total_comp}/{total_lec} lecciones · {xp_total} XP</div>
      <div class="xp-bar-wrap"><div class="xp-bar-fill" style="width:{pct}%"></div></div>
      <div class="xp-bar-label">{pct}% completado</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Personaje
    st.markdown(f"""
    <div class="personaje-box">
      <span class="personaje-avatar">{avatar}</span>
      <div class="personaje-nombre">{nombre_avatar} · {xp_total} XP</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Zigzag por nivel
    POSICIONES = ["izquierda", "centro", "derecha"]  # patrón zigzag
    nodo_selec = st.session_state.get("nodo_selec")

    for nivel_num in [1, 2, 3]:
        lecs_nivel  = [l for l in LECCIONES if l["nivel"] == nivel_num]
        color_nivel = COLORES_NIVEL[nivel_num]
        comp_nivel  = sum(1 for l in lecs_nivel if progreso.get(l["id"]) == "completada")

        st.markdown(f"""
        <div class="nivel-sep">
          <span class="nivel-pill-sep" style="background:{color_nivel}">Nivel {nivel_num}</span>
          {NOMBRES_NIVEL[nivel_num]}
          <span style="margin-left:auto;font-size:.72rem;color:#bbb">{comp_nivel}/{len(lecs_nivel)}</span>
        </div>
        """, unsafe_allow_html=True)

        for i, lec in enumerate(lecs_nivel):
            es_comp  = progreso.get(lec["id"]) == "completada"
            desbloq  = lec["id"] == 1 or es_comp or progreso.get(lec["id"] - 1) == "completada"
            es_activo = nodo_selec == lec["id"]
            pos       = POSICIONES[i % 3]

            # Conector antes del nodo (excepto primero del nivel)
            if i > 0:
                prev_comp = progreso.get(lec["id"] - 1) == "completada"
                clase_conn = "conector-v done" if prev_comp else "conector-v"
                # Alinear conector con posición del nodo actual
                margen = {"izquierda": "0 auto 0 41px", "centro": "0 auto", "derecha": "0 41px 0 auto"}
                st.markdown(f'<div class="{clase_conn}" style="margin:{margen[pos]}"></div>', unsafe_allow_html=True)

            # Badge del nodo
            if es_comp:
                badge = '<div class="nodo-check">✓</div>'
            elif not desbloq:
                badge = '<div class="nodo-lock">🔒</div>'
            else:
                badge = ""

            clase_nodo = "nodo-btn" + (" completado" if es_comp else " activo" if es_activo else "" if desbloq else " bloqueado")

            alineacion = {"izquierda": "flex-start", "centro": "center", "derecha": "flex-end"}
            st.markdown(f"""
            <div style="display:flex;justify-content:{alineacion[pos]};margin:2px 0;">
              <div class="{clase_nodo}" style="{'outline: 3px solid ' + color_nivel + '; outline-offset: 3px;' if es_activo else ''}">
                <div class="nodo-emoji">{lec['emoji']}</div>
                <div class="nodo-label">{lec['titulo'][:20]}</div>
                {badge}
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Botón invisible encima del nodo para click
            if desbloq:
                col_l, col_c, col_r = st.columns([1, 1, 1])
                col_map = {"izquierda": col_l, "centro": col_c, "derecha": col_r}
                with col_map[pos]:
                    etiqueta = "✅ Ver" if es_comp else "▶ Iniciar"
                    if st.button(etiqueta, key=f"nodo_{lec['id']}", use_container_width=True):
                        nuevo = None if nodo_selec == lec["id"] else lec["id"]
                        st.session_state["nodo_selec"] = nuevo
                        st.rerun()

            # Panel detalle debajo del nodo seleccionado
            if es_activo:
                _render_detalle_inline(lec, es_comp, desbloq, progreso)

    # ── Divider y videos
    st.divider()
    _render_videos()


def _render_detalle_inline(lec, es_comp, desbloq, progreso):
    xp_txt = "✅ +25 XP ya ganados" if es_comp else "⭐ +25 XP al completar"
    clase_xp = "detalle-xp verde" if es_comp else "detalle-xp"

    st.markdown(f"""
    <div class="detalle-card">
      <div class="detalle-top">
        <div class="detalle-big-emoji">{lec['emoji']}</div>
        <div>
          <div class="detalle-titulo">{lec['titulo']}</div>
          <div class="detalle-meta">Nivel {lec['nivel']} · {NOMBRES_NIVEL[lec['nivel']]} · ⏱ {lec['duracion']}</div>
        </div>
      </div>
      <div class="detalle-desc">{lec['descripcion']}</div>
      <div class="{clase_xp}">{xp_txt}</div>
    </div>
    """, unsafe_allow_html=True)

    if es_comp:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Repasar", key=f"rep_{lec['id']}", use_container_width=True):
                st.session_state["lec_vista"]    = lec["id"]
                st.session_state["lec_fase"]     = "contenido"
                st.session_state["quiz_resp"]    = {}
                st.session_state["quiz_idx"]     = 0
                st.session_state["quiz_mostrar"] = False
                st.rerun()
        with col2:
            siguiente = next((l for l in LECCIONES if l["id"] == lec["id"] + 1), None)
            if siguiente and progreso.get(siguiente["id"]) != "completada":
                if st.button(f"▶ {siguiente['emoji']} Siguiente", key=f"sig_{lec['id']}", use_container_width=True):
                    st.session_state["lec_vista"]    = siguiente["id"]
                    st.session_state["lec_fase"]     = "contenido"
                    st.session_state["quiz_resp"]    = {}
                    st.session_state["quiz_idx"]     = 0
                    st.session_state["quiz_mostrar"] = False
                    st.rerun()
    else:
        if st.button(f"▶ Empezar lección", key=f"start_{lec['id']}", use_container_width=True, type="primary"):
            st.session_state["lec_vista"]    = lec["id"]
            st.session_state["lec_fase"]     = "contenido"
            st.session_state["quiz_resp"]    = {}
            st.session_state["quiz_idx"]     = 0
            st.session_state["quiz_mostrar"] = False
            st.rerun()


def _render_contenido(lec):
    if st.button("← Volver al mapa", key="volver_cont"):
        st.session_state["lec_vista"] = None
        st.rerun()

    # Hero
    st.markdown(f"""
    <div class="lec-hero">
      <img src="{lec['imagen_url']}" alt="{lec['titulo']}"/>
      <div class="lec-hero-overlay">
        <div class="lec-overlay-nivel">Nivel {lec['nivel']} · {NOMBRES_NIVEL[lec['nivel']]} · ⏱ {lec['duracion']}</div>
        <div class="lec-overlay-titulo">{lec['emoji']} {lec['titulo']}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    TIPO_CLASE  = {"texto": "", "ejemplo": "ejemplo", "dato": "dato"}
    TIPO_LABEL  = {"texto": "📖 Concepto", "ejemplo": "💡 Ejemplo", "dato": "📊 Dato clave"}

    for sec in lec["secciones"]:
        cls = TIPO_CLASE.get(sec["tipo"], "")
        lbl = TIPO_LABEL.get(sec["tipo"], "")
        st.markdown(f"""
        <div class="sec-card {cls}">
          <div class="sec-tipo">{lbl}</div>
          <div class="sec-titulo">{sec['emoji']} {sec['titulo']}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(sec["contenido"])
        st.write("")

    st.write("")
    if st.button("¡Listo! Ir al quiz →", key="ir_quiz", use_container_width=True, type="primary"):
        st.session_state["lec_fase"]     = "quiz"
        st.session_state["quiz_resp"]    = {}
        st.session_state["quiz_idx"]     = 0
        st.session_state["quiz_mostrar"] = False
        st.rerun()


def _render_quiz(lec, progreso):
    preguntas  = lec["quiz"]
    total_p    = len(preguntas)
    idx        = st.session_state.get("quiz_idx", 0)
    resp_dict  = st.session_state.get("quiz_resp", {})
    mostrar    = st.session_state.get("quiz_mostrar", False)

    if st.button("← Volver al contenido", key="volver_quiz"):
        st.session_state["lec_fase"] = "contenido"
        st.rerun()

    st.markdown(f"### 🧠 {lec['emoji']} Quiz")

    # Barra de progreso del quiz
    dots = ""
    for i in range(total_p):
        if i < idx:      cls = "done"
        elif i == idx:   cls = "activo"
        else:            cls = ""
        dots += f'<div class="quiz-prog-dot {cls}"></div>'
    st.markdown(f'<div class="quiz-prog">{dots}</div>', unsafe_allow_html=True)

    if idx >= total_p:
        # Todas respondidas → resultado
        st.session_state["lec_fase"] = "resultado"
        st.rerun()
        return

    pregunta = preguntas[idx]
    st.markdown(f"""
    <div class="quiz-card">
      <div class="quiz-num">Pregunta {idx+1} de {total_p}</div>
      <div class="quiz-pregunta">{pregunta['pregunta']}</div>
    </div>
    """, unsafe_allow_html=True)

    ya_resp = idx in resp_dict

    for j, opcion in enumerate(pregunta["opciones"]):
        es_correcta  = j == pregunta["respuesta"]
        resp_usuario = resp_dict.get(idx)
        es_elegida   = resp_usuario == j

        if ya_resp:
            if es_correcta:
                cls = "quiz-opcion correcta"
            elif es_elegida:
                cls = "quiz-opcion incorrecta"
            else:
                cls = "quiz-opcion"
            st.markdown(f'<button class="{cls}" disabled>{opcion}</button>', unsafe_allow_html=True)
        else:
            if st.button(opcion, key=f"op_{idx}_{j}", use_container_width=True):
                resp_dict[idx] = j
                st.session_state["quiz_resp"]    = resp_dict
                st.session_state["quiz_mostrar"] = True
                st.rerun()

    if ya_resp:
        es_ok = resp_dict[idx] == pregunta["respuesta"]
        cls   = "quiz-expl ok" if es_ok else "quiz-expl mal"
        icono = "✅" if es_ok else "❌"
        st.markdown(f'<div class="{cls}">{icono} {pregunta["explicacion"]}</div>', unsafe_allow_html=True)
        st.write("")

        label_sig = "Siguiente →" if idx < total_p - 1 else "Ver resultados 🏆"
        if st.button(label_sig, key="siguiente_preg", use_container_width=True, type="primary"):
            st.session_state["quiz_idx"]     = idx + 1
            st.session_state["quiz_mostrar"] = False
            st.rerun()


def _render_resultado(lec, user_id, progreso, registrar_accion_fn):
    resp_dict  = st.session_state.get("quiz_resp", {})
    preguntas  = lec["quiz"]
    correctas  = sum(1 for i, p in enumerate(preguntas) if resp_dict.get(i) == p["respuesta"])
    total      = len(preguntas)
    aprobo     = correctas >= 2

    if aprobo:
        if progreso.get(lec["id"]) != "completada":
            marcar_leccion_completada(user_id, lec["id"])
            registrar_accion_fn(user_id, "leccion", {})
        emoji_res = "🏆" if correctas == total else "🎉"
        titulo_res = "¡Perfecto!" if correctas == total else "¡Lección completada!"
        sub_res    = f"{correctas}/{total} correctas · +25 XP ganados ⭐"
        st.markdown(f"""
        <div class="resultado-hero">
          <div class="resultado-emoji">{emoji_res}</div>
          <div class="resultado-titulo">{titulo_res}</div>
          <div class="resultado-sub">{sub_res}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background:#fff3cd;border-radius:14px;padding:24px;text-align:center;margin-bottom:16px;">
          <div style="font-size:2.5rem;">😅</div>
          <div style="font-size:1.15rem;font-weight:800;color:#856404;margin:8px 0;">¡Casi!</div>
          <div style="color:#856404;font-size:.88rem;">{correctas}/{total} correctas. Necesitas al menos 2 para completar.</div>
        </div>
        """, unsafe_allow_html=True)

    # Revisión de respuestas
    st.markdown("#### 📋 Revisión")
    for i, preg in enumerate(preguntas):
        es_ok = resp_dict.get(i) == preg["respuesta"]
        icono = "✅" if es_ok else "❌"
        with st.expander(f"{icono} Pregunta {i+1}: {preg['pregunta'][:50]}…"):
            resp_u = resp_dict.get(i, -1)
            if not es_ok and resp_u >= 0:
                st.markdown(f"Tu respuesta: ~~{preg['opciones'][resp_u]}~~")
            st.markdown(f"✅ Correcta: **{preg['opciones'][preg['respuesta']]}**")
            cls  = "quiz-expl ok" if es_ok else "quiz-expl mal"
            st.markdown(f'<div class="{cls}">💡 {preg["explicacion"]}</div>', unsafe_allow_html=True)

    st.write("")
    col_a, col_b = st.columns(2)
    with col_a:
        if not aprobo:
            if st.button("🔄 Reintentar", key="reintentar", use_container_width=True):
                st.session_state["lec_fase"]     = "quiz"
                st.session_state["quiz_resp"]    = {}
                st.session_state["quiz_idx"]     = 0
                st.session_state["quiz_mostrar"] = False
                st.rerun()
        else:
            siguiente = next((l for l in LECCIONES if l["id"] == lec["id"] + 1), None)
            if siguiente:
                if st.button(f"▶ {siguiente['emoji']} Siguiente lección", key="sig_lec", use_container_width=True, type="primary"):
                    st.session_state["lec_vista"]    = siguiente["id"]
                    st.session_state["lec_fase"]     = "contenido"
                    st.session_state["quiz_resp"]    = {}
                    st.session_state["quiz_idx"]     = 0
                    st.session_state["quiz_mostrar"] = False
                    st.rerun()
    with col_b:
        if st.button("← Volver al mapa", key="volver_mapa_res", use_container_width=True):
            st.session_state["lec_vista"] = None
            st.session_state["nodo_selec"] = lec["id"]
            st.rerun()


def _render_videos():
    from app.database import obtener_videos_educativos
    st.subheader("🎬 Videos Recomendados")
    videos_db = obtener_videos_educativos()
    if videos_db:
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
        st.info("📭 Aún no hay videos publicados.")