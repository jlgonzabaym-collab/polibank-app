"""
asistente_flotante.py
Renderiza el chat flotante de la tortuga IA accesible desde cualquier pantalla.
Llamar render_asistente_flotante(user_id, movimientos, gami_estado) desde app_visual.py
"""
import streamlit as st
from app.ai_core import asistente_general

CSS_FLOTANTE = """
<style>
/* Botón flotante */
.flotante-btn {
  position: fixed; bottom: 24px; right: 20px; z-index: 9999;
  width: 60px; height: 60px; border-radius: 50%;
  background: linear-gradient(135deg, #1B8A4C, #27AE60);
  box-shadow: 0 4px 16px rgba(27,138,76,0.45);
  display: flex; align-items: center; justify-content: center;
  font-size: 28px; cursor: pointer; border: none;
  animation: pulso-btn 2.5s ease-in-out infinite;
  transition: transform .15s;
}
.flotante-btn:hover { transform: scale(1.1); }
@keyframes pulso-btn {
  0%,100% { box-shadow: 0 4px 16px rgba(27,138,76,.45); }
  50%      { box-shadow: 0 4px 24px rgba(27,138,76,.7); }
}

/* Panel del chat */
.chat-panel {
  background: white; border-radius: 20px 20px 0 0;
  box-shadow: 0 -4px 24px rgba(0,0,0,.15);
  padding: 0; overflow: hidden;
}
.chat-header {
  background: linear-gradient(135deg, #1B8A4C, #27AE60);
  padding: 14px 18px; color: white;
  display: flex; align-items: center; gap: 10px;
}
.chat-avatar { font-size: 28px; }
.chat-nombre { font-weight: 800; font-size: 15px; }
.chat-sub    { font-size: 11px; opacity: .8; }
.chat-msgs   { padding: 14px; max-height: 320px; overflow-y: auto; }
.msg-wrap    { display: flex; margin-bottom: 10px; }
.msg-wrap.user { justify-content: flex-end; }
.msg-burbuja {
  max-width: 78%; padding: 10px 14px; border-radius: 16px;
  font-size: 13px; line-height: 1.5;
}
.msg-burbuja.bot  { background: #f0faf4; color: #1a1a1a; border-bottom-left-radius: 4px; }
.msg-burbuja.user { background: #1B8A4C; color: white; border-bottom-right-radius: 4px; }
.msg-typing { background: #f0faf4; padding: 10px 14px; border-radius: 16px; display: inline-block; }
.typing-dot {
  display: inline-block; width: 7px; height: 7px; border-radius: 50%;
  background: #1B8A4C; margin: 0 2px;
  animation: typing 1.2s ease-in-out infinite;
}
.typing-dot:nth-child(2) { animation-delay: .2s; }
.typing-dot:nth-child(3) { animation-delay: .4s; }
@keyframes typing { 0%,60%,100%{transform:translateY(0)} 30%{transform:translateY(-6px)} }
</style>
"""

SUGERENCIAS = [
    "¿En qué estoy gastando más?",
    "¿Cómo puedo ahorrar más?",
    "¿Cómo está mi saldo?",
    "Dame un consejo financiero",
]


def render_asistente_flotante(user_id: int, movimientos: list, gami_estado: dict):
    st.markdown(CSS_FLOTANTE, unsafe_allow_html=True)

    # Inicializar estado del chat
    if "chat_abierto"   not in st.session_state: st.session_state["chat_abierto"]   = False
    if "chat_historial" not in st.session_state: st.session_state["chat_historial"] = []
    if "chat_input_key" not in st.session_state: st.session_state["chat_input_key"] = 0

    # Botón flotante
    col_esp, col_btn = st.columns([6, 1])
    with col_btn:
        etiqueta = "✕" if st.session_state["chat_abierto"] else "🐢"
        if st.button(etiqueta, key="btn_flotante",
                     help="Asistente Polito",
                     use_container_width=True):
            st.session_state["chat_abierto"] = not st.session_state["chat_abierto"]
            st.rerun()

    # Panel del chat
    if st.session_state["chat_abierto"]:
        st.markdown("""
        <div class="chat-panel">
          <div class="chat-header">
            <div class="chat-avatar">🐢</div>
            <div>
              <div class="chat-nombre">Polito IA</div>
              <div class="chat-sub">Tu asistente financiero personal</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Mensaje de bienvenida
        if not st.session_state["chat_historial"]:
            st.session_state["chat_historial"].append({
                "rol": "asistente",
                "texto": "¡Hola! Soy Polito, tu asistente financiero. Puedo ayudarte a entender tus gastos, darte consejos personalizados o responder cualquier duda de finanzas. ¿En qué te ayudo?"
            })

        # Mostrar mensajes
        st.markdown('<div class="chat-msgs">', unsafe_allow_html=True)
        for msg in st.session_state["chat_historial"]:
            cls = "user" if msg["rol"] == "usuario" else "bot"
            align = "user" if msg["rol"] == "usuario" else ""
            st.markdown(f"""
            <div class="msg-wrap {align}">
              <div class="msg-burbuja {cls}">{msg['texto']}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Sugerencias rápidas (solo si el chat está vacío)
        if len(st.session_state["chat_historial"]) <= 1:
            st.markdown("**Preguntas rápidas:**")
            cols = st.columns(2)
            for i, sug in enumerate(SUGERENCIAS):
                with cols[i % 2]:
                    if st.button(sug, key=f"sug_{i}", use_container_width=True):
                        _enviar_mensaje(sug, movimientos, gami_estado)

        # Input del usuario
        col_inp, col_send = st.columns([5, 1])
        with col_inp:
            user_input = st.text_input(
                "Escribe tu pregunta...",
                key=f"chat_input_{st.session_state['chat_input_key']}",
                label_visibility="collapsed",
                placeholder="¿En qué te ayudo?"
            )
        with col_send:
            if st.button("➤", key="send_btn", use_container_width=True):
                if user_input and user_input.strip():
                    _enviar_mensaje(user_input.strip(), movimientos, gami_estado)

        # Botón limpiar chat
        if len(st.session_state["chat_historial"]) > 1:
            if st.button("🗑️ Limpiar chat", key="limpiar_chat"):
                st.session_state["chat_historial"] = []
                st.session_state["chat_input_key"] += 1
                st.rerun()


def _enviar_mensaje(texto: str, movimientos: list, gami_estado: dict):
    # Agregar mensaje del usuario
    st.session_state["chat_historial"].append({"rol": "usuario", "texto": texto})

    # Obtener respuesta de la IA
    with st.spinner("🐢 Pensando..."):
        respuesta = asistente_general(
            pregunta=texto,
            movimientos=movimientos,
            historial_chat=st.session_state["chat_historial"],
            gami_estado=gami_estado
        )

    # Agregar respuesta
    st.session_state["chat_historial"].append({"rol": "asistente", "texto": respuesta})
    st.session_state["chat_input_key"] += 1
    st.rerun()