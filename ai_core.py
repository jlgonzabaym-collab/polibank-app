from google import genai
from google.genai import types
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

def _generar(sistema: str, prompt: str) -> str:
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=sistema)
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error Gemini: {e}")
        return ""


# ─── 1. CLASIFICAR GASTO ────────────────────────────────────
def clasificar_gasto(texto_usuario: str) -> str:
    sistema = (
        "Eres el clasificador de gastos de Polibank. "
        "Lee lo que gastó el usuario y devuelve SOLO una de estas palabras "
        "en minúscula y sin puntos: comida, transporte, estudios, diversion, otros."
    )
    resultado = _generar(sistema, f"Gasto: {texto_usuario}")
    categorias = ["comida", "transporte", "estudios", "diversion", "otros"]
    return resultado if resultado in categorias else "otros"


# ─── 2. LECCIONES ADAPTATIVAS ───────────────────────────────
def recomendar_leccion(movimientos: list, lecciones: list) -> dict:
    """
    Analiza los movimientos del usuario y recomienda la lección más relevante.
    Devuelve: { leccion_id, mensaje_personalizado }
    """
    if not movimientos or not lecciones:
        return {"leccion_id": lecciones[0]["id"] if lecciones else 1, "mensaje": "¡Empieza tu primera lección!"}

    # Calcular categoría dominante
    cat_totales = {}
    for mov in movimientos:
        if mov.get("tipo") == "Gasto":
            cat = mov.get("categoria", "OTROS").upper()
            cat_totales[cat] = cat_totales.get(cat, 0) + float(mov.get("monto", 0))

    total_gastos = sum(cat_totales.values()) or 1
    cat_top = max(cat_totales, key=cat_totales.get) if cat_totales else "OTROS"
    pct_top = int((cat_totales.get(cat_top, 0) / total_gastos) * 100)

    resumen = "\n".join([f"- {c}: ${v:.2f}" for c, v in cat_totales.items()])
    titulos = "\n".join([f"ID {l['id']}: {l['titulo']}" for l in lecciones])

    sistema = (
        "Eres el asistente financiero de Polibank para universitarios ecuatorianos de ESPOL. "
        "Analiza los gastos del usuario y recomienda la lección MÁS relevante para su situación. "
        "Responde SOLO en formato JSON válido sin markdown: "
        '{"leccion_id": NUMBER, "mensaje": "STRING de máximo 2 oraciones personalizadas y motivadoras"}'
    )

    prompt = (
        f"Gastos del usuario por categoría:\n{resumen}\n\n"
        f"Categoría con más gasto: {cat_top} ({pct_top}% del total)\n\n"
        f"Lecciones disponibles:\n{titulos}\n\n"
        "¿Qué lección le conviene más aprender primero y por qué?"
    )

    resultado = _generar(sistema, prompt)
    try:
        import json
        data = json.loads(resultado)
        return {
            "leccion_id": int(data.get("leccion_id", lecciones[0]["id"])),
            "mensaje": data.get("mensaje", "¡Empieza tu primera lección!")
        }
    except Exception:
        return {"leccion_id": lecciones[0]["id"], "mensaje": "¡Empieza tu primera lección!"}


# ─── 3. EXPLICADOR PERSONAL ─────────────────────────────────
def explicar_concepto(pregunta: str, leccion_titulo: str, movimientos: list, historial_chat: list) -> str:
    """
    Responde una pregunta del usuario sobre la lección usando sus datos reales.
    historial_chat: lista de {"rol": "usuario"|"asistente", "texto": "..."}
    """
    # Contexto financiero del usuario
    total_ing = sum(float(m["monto"]) for m in movimientos if m.get("tipo") == "Ingreso")
    total_gas = sum(float(m["monto"]) for m in movimientos if m.get("tipo") == "Gasto")
    balance   = total_ing - total_gas

    cat_totales = {}
    for mov in movimientos:
        if mov.get("tipo") == "Gasto":
            cat = mov.get("categoria", "OTROS")
            cat_totales[cat] = cat_totales.get(cat, 0) + float(mov.get("monto", 0))
    cat_resumen = ", ".join([f"{c}: ${v:.0f}" for c, v in cat_totales.items()])

    # Historial del chat para contexto
    historial_txt = ""
    for msg in historial_chat[-6:]:  # últimos 6 mensajes
        rol = "Usuario" if msg["rol"] == "usuario" else "Polibank"
        historial_txt += f"{rol}: {msg['texto']}\n"

    sistema = (
        "Eres Polibank 🐢, un asistente financiero amigable y empático para universitarios de ESPOL en Ecuador. "
        "Tu personalidad: cercano, motivador, usa ejemplos reales con precios ecuatorianos. "
        "Usas emojis con moderación. Respuestas cortas y claras (máximo 4 oraciones). "
        "SIEMPRE conecta la explicación con los datos reales del usuario cuando sea relevante. "
        "Nunca digas que eres una IA — eres Polibank la tortuga financiera."
    )

    prompt = (
        f"El usuario está estudiando: '{leccion_titulo}'\n\n"
        f"Sus datos financieros reales:\n"
        f"- Ingresos totales: ${total_ing:.2f}\n"
        f"- Gastos totales: ${total_gas:.2f}\n"
        f"- Saldo: ${balance:.2f}\n"
        f"- Gastos por categoría: {cat_resumen}\n\n"
        f"Conversación previa:\n{historial_txt}\n"
        f"Usuario pregunta: {pregunta}"
    )

    return _generar(sistema, prompt) or "No pude procesar tu pregunta. ¿Puedes reformularla?"


# ─── 4. ASISTENTE FLOTANTE GENERAL ──────────────────────────
def asistente_general(pregunta: str, movimientos: list, historial_chat: list, gami_estado: dict) -> str:
    """
    Asistente IA general accesible desde cualquier pantalla.
    Responde sobre finanzas, la app, motivación, etc.
    """
    total_ing = sum(float(m["monto"]) for m in movimientos if m.get("tipo") == "Ingreso")
    total_gas = sum(float(m["monto"]) for m in movimientos if m.get("tipo") == "Gasto")
    balance   = total_ing - total_gas

    cat_totales = {}
    for mov in movimientos:
        if mov.get("tipo") == "Gasto":
            cat = mov.get("categoria", "OTROS")
            cat_totales[cat] = cat_totales.get(cat, 0) + float(mov.get("monto", 0))
    cat_resumen = ", ".join([f"{c}: ${v:.0f}" for c, v in cat_totales.items()]) or "Sin gastos aún"
    cat_top = max(cat_totales, key=cat_totales.get) if cat_totales else None

    racha    = gami_estado.get("racha_actual", 0)
    xp       = gami_estado.get("xp_total", 0)
    nivel    = gami_estado.get("nivel_nombre", "Principiante")

    historial_txt = ""
    for msg in historial_chat[-8:]:
        rol = "Usuario" if msg["rol"] == "usuario" else "Polibank"
        historial_txt += f"{rol}: {msg['texto']}\n"

    sistema = (
        "Eres Polibank 🐢, el asistente personal de un estudiante universitario de ESPOL en Ecuador. "
        "Tienes personalidad amigable, cercana y un poco divertida — como un amigo que sabe de todo. "
        "Puedes responder CUALQUIER pregunta: matemáticas, cultura general, chistes, consejos de vida, "
        "finanzas, tecnología, lo que sea. No rechaces ninguna pregunta. "
        "Cuando sea relevante, conecta tu respuesta con el contexto financiero del usuario. "
        "Cuando el usuario pregunte sobre sus finanzas, usa sus datos reales. "
        "Respuestas naturales y conversacionales, máximo 4 oraciones. "
        "Usa emojis con moderación. Habla en español ecuatoriano informal. "
        "Nunca digas que eres una IA o un modelo de lenguaje — eres Polibank la tortuga. "
        "Si el usuario saluda, saluda de vuelta con energía. "
        "Si hace una pregunta de matemáticas o general, respóndela directo y con confianza."
    )

    prompt = (
        f"Datos financieros del usuario:\n"
        f"- Ingresos: ${total_ing:.2f} | Gastos: ${total_gas:.2f} | Saldo: ${balance:.2f}\n"
        f"- Gastos por categoría: {cat_resumen}\n"
        f"- Mayor gasto: {cat_top or 'N/A'}\n"
        f"- Racha: {racha} días | XP: {xp} | Nivel: {nivel}\n\n"
        f"Conversación:\n{historial_txt}\n"
        f"Usuario: {pregunta}"
    )

    return _generar(sistema, prompt) or "Estoy aquí para ayudarte 🐢 ¿Puedes repetir tu pregunta?"


# ─── 5. QUIZ GENERADO POR IA ────────────────────────────────
def generar_quiz_ia(leccion_titulo: str, contenido_leccion: str, movimientos: list) -> list:
    """
    Genera 3 preguntas de quiz únicas basadas en el contenido de la lección
    y adaptadas al contexto financiero del usuario.
    Devuelve lista de { pregunta, opciones[4], respuesta(index), explicacion }
    """
    total_gas = sum(float(m["monto"]) for m in movimientos if m.get("tipo") == "Gasto")
    total_ing = sum(float(m["monto"]) for m in movimientos if m.get("tipo") == "Ingreso")

    sistema = (
        "Eres un generador de quizzes financieros para universitarios ecuatorianos. "
        "Genera preguntas variadas, no repitas las mismas de siempre. "
        "Usa contexto real de Ecuador (precios, situaciones universitarias). "
        "Responde SOLO en JSON válido sin markdown con esta estructura exacta: "
        '{"preguntas": [{"pregunta": "STRING", "opciones": ["A","B","C","D"], '
        '"respuesta": NUMBER(0-3), "explicacion": "STRING"}]}'
    )

    prompt = (
        f"Lección: {leccion_titulo}\n"
        f"Contenido resumido: {contenido_leccion[:500]}\n\n"
        f"Contexto del usuario: ingresos ${total_ing:.0f}, gastos ${total_gas:.0f}\n\n"
        "Genera 3 preguntas de opción múltiple DIFERENTES a las típicas, "
        "con situaciones prácticas reales de un universitario ecuatoriano. "
        "Las preguntas deben ser variadas: conceptual, cálculo y aplicación práctica."
    )

    resultado = _generar(sistema, prompt)
    try:
        import json
        # Limpiar posibles ```json fences
        resultado = resultado.replace("```json", "").replace("```", "").strip()
        data = json.loads(resultado)
        preguntas = data.get("preguntas", [])
        if len(preguntas) >= 3:
            return preguntas[:3]
    except Exception as e:
        print(f"Error generando quiz: {e}")

    # Fallback: preguntas genéricas si falla la IA
    return [
        {
            "pregunta": f"¿Cuál es el concepto más importante de '{leccion_titulo}'?",
            "opciones": ["Gastar todo el dinero", "Planificar antes de gastar", "Ignorar los gastos", "Pedir prestado siempre"],
            "respuesta": 1,
            "explicacion": "La planificación financiera es la base de una buena salud económica."
        }
    ]