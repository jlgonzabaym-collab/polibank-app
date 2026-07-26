"""
academia_ui.py — Academia estilo Canvas con cursos, videos y quiz
"""
import streamlit as st
from config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client

supabase = create_client(SUPABASE_URL.strip().rstrip('/'), SUPABASE_KEY.strip())

COLOR_VERDE = "#1B8A4C"
COLOR_ROJO  = "#E74C3C"
COLOR_AZUL  = "#2E86AB"
COLOR_ORO   = "#F39C12"

CSS = f"""
<style>
.academia-header {{
  background: linear-gradient(135deg, {COLOR_VERDE}, #27AE60);
  border-radius: 16px; padding: 20px 24px; color: white; margin-bottom: 20px;
}}
.academia-header h2 {{ font-size: 1.3rem; font-weight: 800; margin-bottom: 4px; }}
.academia-header p  {{ font-size: 0.85rem; opacity: .85; }}

.stats-row {{
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px;
}}
.stat-card {{
  background: white; border-radius: 12px; padding: 14px;
  text-align: center; border: 0.5px solid #e8e8e8;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}}
.stat-val {{ font-size: 1.6rem; font-weight: 800; color: #1a1a1a; }}
.stat-lbl {{ font-size: 0.7rem; color: #888; font-weight: 600;
             text-transform: uppercase; letter-spacing: .5px; margin-top: 2px; }}

.cat-titulo {{
  font-size: 0.78rem; font-weight: 700; color: #666;
  text-transform: uppercase; letter-spacing: .5px;
  margin: 20px 0 10px; padding-bottom: 6px;
  border-bottom: 2px solid #f0f0f0;
}}

.cursos-grid {{
  display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 14px;
  margin-bottom: 8px;
}}

.curso-card {{
  background: white; border-radius: 14px; overflow: hidden;
  border: 0.5px solid #e8e8e8; box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  cursor: pointer; transition: transform .15s, box-shadow .15s;
}}
.curso-card:hover {{ transform: translateY(-3px); box-shadow: 0 6px 16px rgba(0,0,0,0.12); }}

.curso-card img.curso-img {{
  width: 100% !important;
  max-width: 100% !important;
  height: 100px !important;
  object-fit: cover !important;
  object-position: center !important;
  display: block !important;
  margin: 0 !important;
  padding: 0 !important;
}}
.curso-img-placeholder {{
  width: 100%; height: 100px; display: flex; align-items: center;
  justify-content: center; font-size: 2.5rem;
}}

.curso-body {{ padding: 12px; }}
.curso-titulo {{ font-size: 0.85rem; font-weight: 700; color: #222;
                 margin-bottom: 4px; line-height: 1.3; }}
.curso-desc  {{ font-size: 0.75rem; color: #777; margin-bottom: 8px;
                line-height: 1.4; }}
.curso-meta  {{ font-size: 0.7rem; color: #aaa; margin-bottom: 8px; }}

.prog-wrap {{ background: #f0f0f0; border-radius: 4px; height: 5px;
              overflow: hidden; margin-bottom: 4px; }}
.prog-fill {{ height: 5px; border-radius: 4px; background: {COLOR_VERDE}; }}
.prog-lbl  {{ font-size: 0.68rem; color: #aaa; }}

.curso-footer {{
  padding: 8px 12px; border-top: 0.5px solid #f0f0f0;
  display: flex; align-items: center; justify-content: space-between;
}}
.xp-pill {{
  font-size: 0.68rem; font-weight: 700;
  background: #e8f5e9; color: #1b5e20;
  padding: 2px 8px; border-radius: 20px;
}}
.badge-comp {{ background: #e8f5e9; color: #1b5e20; }}
.badge-nuevo {{ background: #e3f2fd; color: #0d47a1; }}
.badge-prog  {{ background: #fff8e1; color: #e65100; }}

.curso-btn-label {{
  font-size: 0.7rem; font-weight: 700; color: {COLOR_VERDE};
}}

.video-wrap {{
  border-radius: 12px; overflow: hidden; margin-bottom: 16px;
}}

.quiz-card {{
  background: white; border-radius: 14px; padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,.08); margin-bottom: 12px;
}}
.q-num  {{ font-size: 0.7rem; color: #aaa; font-weight: 700; margin-bottom: 6px; }}
.q-txt  {{ font-size: 1rem; font-weight: 800; color: #222; margin-bottom: 16px; }}
.q-expl {{ border-radius: 8px; padding: 10px 14px; margin-top: 6px;
           font-size: 0.82rem; line-height: 1.5; }}
.q-expl.ok  {{ background: #d4edda; color: #155724; }}
.q-expl.mal {{ background: #f8d7da; color: #721c24; }}

.quiz-dots {{ display: flex; gap: 6px; margin-bottom: 16px; }}
.qdot {{ flex: 1; height: 6px; border-radius: 3px; background: #e0e0e0; }}
.qdot.done   {{ background: {COLOR_VERDE}; }}
.qdot.active {{ background: {COLOR_AZUL}; }}

.res-hero {{
  background: linear-gradient(135deg, {COLOR_VERDE}, #27AE60);
  border-radius: 16px; padding: 28px; text-align: center;
  color: white; margin-bottom: 16px;
}}
.res-emo  {{ font-size: 3rem; margin-bottom: 8px; }}
.res-tit  {{ font-size: 1.4rem; font-weight: 800; margin-bottom: 4px; }}
.res-sub  {{ opacity: .85; font-size: .9rem; }}

.search-wrap {{
  background: white; border-radius: 10px; border: 0.5px solid #e0e0e0;
  padding: 8px 14px; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;
}}
</style>
"""

# ── Funciones de base de datos ──────────────────────────────

def obtener_cursos():
    try:
        return supabase.from_("cursos").select("*").order("categoria").order("id").execute().data or []
    except Exception as e:
        print(f"Error cursos: {e}"); return []

def obtener_preguntas(curso_id: int):
    try:
        return supabase.from_("preguntas_quiz").select("*").eq("curso_id", curso_id).execute().data or []
    except Exception as e:
        print(f"Error preguntas: {e}"); return []

def obtener_progreso_cursos(usuario_id: int):
    try:
        res = supabase.from_("progreso_cursos").select("*").eq("usuario_id", usuario_id).execute()
        return {r["curso_id"]: r["completado"] for r in (res.data or [])}
    except Exception as e:
        print(f"Error progreso: {e}"); return {}

def marcar_curso_completado(usuario_id: int, curso_id: int):
    try:
        existente = supabase.from_("progreso_cursos").select("id")\
            .eq("usuario_id", usuario_id).eq("curso_id", curso_id).execute()
        if existente.data:
            supabase.from_("progreso_cursos").update({"completado": True})\
                .eq("usuario_id", usuario_id).eq("curso_id", curso_id).execute()
        else:
            supabase.from_("progreso_cursos").insert({
                "usuario_id": usuario_id, "curso_id": curso_id, "completado": True
            }).execute()
    except Exception as e:
        print(f"Error marcando completado: {e}")


# ── Render principal ─────────────────────────────────────────

def render_academia(user_id: int, registrar_accion_fn):
    st.markdown(CSS, unsafe_allow_html=True)

    # Estado de navegación
    for k, v in [("curso_activo", None), ("curso_fase", "video"),
                 ("quiz_idx", 0), ("quiz_resp", {}), ("busqueda", "")]:
        if k not in st.session_state:
            st.session_state[k] = v

    cursos   = obtener_cursos()
    progreso = obtener_progreso_cursos(user_id)

    if st.session_state["curso_activo"] is None:
        _render_catalogo(cursos, progreso, user_id)
    else:
        curso = next((c for c in cursos if c["id"] == st.session_state["curso_activo"]), None)
        if not curso:
            st.session_state["curso_activo"] = None; st.rerun(); return

        fase = st.session_state["curso_fase"]
        if fase == "video":
            _render_video(curso, progreso)
        elif fase == "quiz":
            _render_quiz(curso, user_id, progreso, registrar_accion_fn)
        elif fase == "resultado":
            _render_resultado(curso, user_id, registrar_accion_fn)


def _render_catalogo(cursos, progreso, user_id):
    total     = len(cursos)
    comp      = sum(1 for c in cursos if progreso.get(c["id"]))
    xp_total  = comp * 25

    st.markdown(f"""
    <div class="academia-header">
      <h2>📚 Academia Polibank</h2>
      <p>Aprende finanzas a tu ritmo · {comp}/{total} cursos completados · {xp_total} XP ganados</p>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    en_progreso = sum(1 for c in cursos if not progreso.get(c["id"]) and c["id"] in progreso)
    st.markdown(f"""
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-val">{total}</div>
        <div class="stat-lbl">Cursos disponibles</div>
      </div>
      <div class="stat-card">
        <div class="stat-val" style="color:{COLOR_VERDE}">{comp}</div>
        <div class="stat-lbl">Completados</div>
      </div>
      <div class="stat-card">
        <div class="stat-val" style="color:{COLOR_ORO}">{xp_total} XP</div>
        <div class="stat-lbl">XP ganados</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Buscador
    busqueda = st.text_input("🔍 Buscar curso...", key="busqueda_input",
                              placeholder="Ej: interés, presupuesto, inversión...")

    # Agrupar por categoría
    categorias = {}
    for curso in cursos:
        if busqueda and busqueda.lower() not in curso["titulo"].lower() \
                    and busqueda.lower() not in curso.get("descripcion","").lower():
            continue
        cat = curso["categoria"]
        if cat not in categorias:
            categorias[cat] = []
        categorias[cat].append(curso)

    if not categorias:
        st.info("No se encontraron cursos con esa búsqueda.")
        return

    for cat, lista in categorias.items():
        st.markdown(f'<div class="cat-titulo">{cat}</div>', unsafe_allow_html=True)

        cols = st.columns(min(len(lista), 3))
        for i, curso in enumerate(lista):
            es_comp = progreso.get(curso["id"], False)
            with cols[i % 3]:
                _render_card(curso, es_comp)


def _render_card(curso, es_comp):
    img_url = curso.get("imagen_url", "")
    emoji   = curso.get("emoji", "📚")

    # Imagen o placeholder
    if img_url:
        st.markdown(f"""
        <div class="curso-card">
          <img src="{img_url}" class="curso-img" alt="{curso['titulo']}"/>
        """, unsafe_allow_html=True)
    else:
        color_bg = "#e8f5e9" if es_comp else "#e3f2fd"
        st.markdown(f"""
        <div class="curso-card">
          <div class="curso-img-placeholder" style="background:{color_bg}">{emoji}</div>
        """, unsafe_allow_html=True)

    # Badge
    if es_comp:
        badge = '<span style="background:#e8f5e9;color:#1b5e20;font-size:.65rem;font-weight:700;padding:2px 8px;border-radius:20px;">✅ Completado</span>'
    else:
        badge = '<span style="background:#e3f2fd;color:#0d47a1;font-size:.65rem;font-weight:700;padding:2px 8px;border-radius:20px;">▶ Disponible</span>'

    prog_pct = 100 if es_comp else 0
    btn_lbl  = "Repasar" if es_comp else "Empezar curso"

    st.markdown(f"""
      <div class="curso-body">
        <div class="curso-titulo">{curso['titulo']}</div>
        <div class="curso-desc">{curso.get('descripcion','')[:80]}...</div>
        {badge}
        <div class="prog-wrap" style="margin-top:8px">
          <div class="prog-fill" style="width:{prog_pct}%"></div>
        </div>
      </div>
      <div class="curso-footer">
        <span class="xp-pill">+{curso.get('xp',25)} XP</span>
        <span class="curso-btn-label">{btn_lbl} →</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button(btn_lbl, key=f"curso_{curso['id']}", use_container_width=True):
        st.session_state["curso_activo"] = curso["id"]
        st.session_state["curso_fase"]   = "video"
        st.session_state["quiz_idx"]     = 0
        st.session_state["quiz_resp"]    = {}
        st.rerun()


def _render_video(curso, progreso):
    if st.button("← Volver a los cursos", key="volver_cat"):
        st.session_state["curso_activo"] = None; st.rerun()

    # Header del curso
    es_comp = progreso.get(curso["id"], False)
    st.markdown(f"""
    <div style="background:white;border-radius:14px;padding:16px;
                border:0.5px solid #e8e8e8;margin-bottom:16px;">
      <div style="font-size:1.1rem;font-weight:800;color:#222;margin-bottom:4px;">
        {curso.get('emoji','📚')} {curso['titulo']}
      </div>
      <div style="font-size:0.82rem;color:#888;margin-bottom:8px;">
        {curso['categoria']} · +{curso.get('xp',25)} XP al completar
      </div>
      <div style="font-size:0.88rem;color:#555;line-height:1.5;">
        {curso.get('descripcion','')}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Video
    st.subheader("📺 Video del curso")
    st.video(curso["url_video"])

    st.write("")

    if es_comp:
        st.success("✅ Ya completaste este curso.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 Repasar el quiz", key="repasar_quiz", use_container_width=True):
                st.session_state["curso_fase"] = "quiz"
                st.session_state["quiz_idx"]   = 0
                st.session_state["quiz_resp"]  = {}
                st.rerun()
        with c2:
            if st.button("← Volver a cursos", key="volver_comp", use_container_width=True):
                st.session_state["curso_activo"] = None; st.rerun()
    else:
        if st.button("¡Listo! Hacer el quiz →", key="ir_quiz",
                     use_container_width=True, type="primary"):
            st.session_state["curso_fase"] = "quiz"
            st.session_state["quiz_idx"]   = 0
            st.session_state["quiz_resp"]  = {}
            st.rerun()


def _render_quiz(curso, user_id, progreso, registrar_accion_fn):
    if st.button("← Volver al video", key="volver_video"):
        st.session_state["curso_fase"] = "video"; st.rerun()

    preguntas = obtener_preguntas(curso["id"])
    if not preguntas:
        st.warning("Este curso aún no tiene preguntas de quiz.")
        return

    total_p = len(preguntas)
    idx     = st.session_state.get("quiz_idx", 0)
    resp    = st.session_state.get("quiz_resp", {})

    if idx >= total_p:
        st.session_state["curso_fase"] = "resultado"; st.rerun(); return

    st.markdown(f"### 🧠 Quiz — {curso['titulo']}")

    # Barra de progreso
    dots = "".join([
        f'<div class="qdot {"done" if i < idx else "active" if i == idx else ""}"></div>'
        for i in range(total_p)
    ])
    st.markdown(f'<div class="quiz-dots">{dots}</div>', unsafe_allow_html=True)

    preg    = preguntas[idx]
    ya_resp = idx in resp

    st.markdown(f"""
    <div class="quiz-card">
      <div class="q-num">Pregunta {idx+1} de {total_p}</div>
      <div class="q-txt">{preg['pregunta']}</div>
    </div>
    """, unsafe_allow_html=True)

    opciones = {
        "a": preg["opcion_a"], "b": preg["opcion_b"],
        "c": preg["opcion_c"], "d": preg["opcion_d"]
    }

    for letra, texto in opciones.items():
        if ya_resp:
            es_c = letra == preg["respuesta"]
            es_e = resp[idx] == letra
            color = "#d4edda" if es_c else "#f8d7da" if es_e else "white"
            borde = COLOR_VERDE if es_c else COLOR_ROJO if es_e else "#e0e0e0"
            st.markdown(
                f'<div style="padding:10px 14px;margin-bottom:8px;border-radius:10px;'
                f'border:2px solid {borde};background:{color};font-size:.88rem;">'
                f'{texto}</div>',
                unsafe_allow_html=True
            )
        else:
            if st.button(texto, key=f"op_{idx}_{letra}", use_container_width=True):
                resp[idx] = letra
                st.session_state["quiz_resp"] = resp; st.rerun()

    if ya_resp:
        es_ok = resp[idx] == preg["respuesta"]
        cls   = "q-expl ok" if es_ok else "q-expl mal"
        icono = "✅" if es_ok else "❌"
        st.markdown(
            f'<div class="{cls}">{icono} {preg.get("explicacion","")}</div>',
            unsafe_allow_html=True
        )
        st.write("")
        label = "Siguiente →" if idx < total_p - 1 else "Ver resultado 🏆"
        if st.button(label, key="sig_preg", use_container_width=True, type="primary"):
            st.session_state["quiz_idx"] = idx + 1; st.rerun()


def _render_resultado(curso, user_id, registrar_accion_fn):
    preguntas = obtener_preguntas(curso["id"])
    resp      = st.session_state.get("quiz_resp", {})
    correctas = sum(1 for i, p in enumerate(preguntas)
                    if resp.get(i) == p["respuesta"])
    total     = len(preguntas)
    aprobo    = correctas >= max(1, round(total * 0.6))

    if aprobo:
        marcar_curso_completado(user_id, curso["id"])
        registrar_accion_fn(user_id, "leccion", {})
        emo = "🏆" if correctas == total else "🎉"
        tit = "¡Perfecto!" if correctas == total else "¡Curso completado!"
        st.markdown(f"""
        <div class="res-hero">
          <div class="res-emo">{emo}</div>
          <div class="res-tit">{tit}</div>
          <div class="res-sub">{correctas}/{total} correctas · +{curso.get('xp',25)} XP ganados ⭐</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background:#fff3cd;border-radius:14px;padding:24px;
                    text-align:center;margin-bottom:16px;">
          <div style="font-size:2.5rem;">😅</div>
          <div style="font-size:1.15rem;font-weight:800;color:#856404;margin:8px 0;">¡Casi!</div>
          <div style="color:#856404;font-size:.88rem;">
            {correctas}/{total} correctas. Necesitas al menos {max(1, round(total*0.6))} para aprobar.
          </div>
        </div>
        """, unsafe_allow_html=True)

    # Revisión de respuestas
    st.markdown("#### 📋 Revisión")
    for i, preg in enumerate(preguntas):
        es_ok = resp.get(i) == preg["respuesta"]
        with st.expander(f"{'✅' if es_ok else '❌'} Pregunta {i+1}: {preg['pregunta'][:50]}..."):
            resp_u = resp.get(i)
            opciones = {"a": preg["opcion_a"], "b": preg["opcion_b"],
                        "c": preg["opcion_c"], "d": preg["opcion_d"]}
            if not es_ok and resp_u:
                st.markdown(f"Tu respuesta: ~~{opciones.get(resp_u, '')}~~")
            st.markdown(f"✅ Correcta: **{opciones.get(preg['respuesta'], '')}**")
            cls = "q-expl ok" if es_ok else "q-expl mal"
            st.markdown(
                f'<div class="{cls}">💡 {preg.get("explicacion","")}</div>',
                unsafe_allow_html=True
            )

    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        if not aprobo:
            if st.button("🔄 Reintentar", key="reintentar", use_container_width=True):
                st.session_state["curso_fase"] = "quiz"
                st.session_state["quiz_idx"]   = 0
                st.session_state["quiz_resp"]  = {}; st.rerun()
    with c2:
        if st.button("← Volver a cursos", key="volver_final", use_container_width=True):
            st.session_state["curso_activo"] = None; st.rerun()