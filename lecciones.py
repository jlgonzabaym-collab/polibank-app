"""
lecciones.py — Sistema de aprendizaje estilo Duolingo para Polibank
Cada lección tiene: portada → contenido + imagen → quiz → resultado + XP
"""

# ─────────────────────────────────────────────────────────────
# CONTENIDO DE TODAS LAS LECCIONES
# ─────────────────────────────────────────────────────────────
LECCIONES = [

    # ══════════════ NIVEL 1 ══════════════
    {
        "id": 1, "nivel": 1, "nivel_nombre": "Básico",
        "titulo": "¿Qué es un presupuesto?",
        "emoji": "📋",
        "duracion": "3 min",
        "descripcion": "Aprende a planificar tus gastos antes de gastar.",
        "imagen_url": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=600&q=80",
        "secciones": [
            {
                "tipo": "texto",
                "titulo": "¿Qué es un presupuesto?",
                "contenido": "Un **presupuesto** es un plan que te dice cuánto dinero tienes y en qué lo vas a gastar **antes de gastarlo**. Es como un mapa para tu dinero.",
                "emoji": "🗺️"
            },
            {
                "tipo": "ejemplo",
                "titulo": "Ejemplo real",
                "contenido": "Imagina que recibes $200 de mesada al mes. Sin presupuesto probablemente gastas todo sin darte cuenta. Con presupuesto decides: $80 comida, $40 transporte, $30 diversión, $50 ahorro. ¡Listo!",
                "emoji": "💡"
            },
            {
                "tipo": "dato",
                "titulo": "¿Sabías que...?",
                "contenido": "El 78% de las personas que no tienen presupuesto gastan más de lo que ganan. Tener un presupuesto puede reducir tu estrés financiero hasta en un 40%.",
                "emoji": "📊"
            },
        ],
        "quiz": [
            {
                "pregunta": "¿Para qué sirve un presupuesto?",
                "opciones": ["Para gastar más dinero", "Para planificar tus gastos antes de gastarlos", "Para pedir préstamos", "Para invertir en bolsa"],
                "respuesta": 1,
                "explicacion": "Un presupuesto es un plan previo que te dice en qué gastarás tu dinero antes de hacerlo."
            },
            {
                "pregunta": "Si recibes $300 al mes, ¿cuál sería un buen primer paso?",
                "opciones": ["Gastarlo todo en lo que necesites", "Dividirlo en categorías antes de gastar", "Guardarlo bajo el colchón", "Dárselo a tus padres"],
                "respuesta": 1,
                "explicacion": "Dividir el dinero en categorías (comida, transporte, ahorro) es la base de un presupuesto."
            },
            {
                "pregunta": "¿Cuándo debes hacer tu presupuesto?",
                "opciones": ["Cuando ya gastaste todo", "Al final del mes", "Antes de recibir o gastar el dinero", "Solo cuando tienes deudas"],
                "respuesta": 2,
                "explicacion": "El presupuesto se hace ANTES de gastar, no después."
            },
        ]
    },

    {
        "id": 2, "nivel": 1, "nivel_nombre": "Básico",
        "titulo": "La Regla 50/30/20",
        "emoji": "🥧",
        "duracion": "3 min",
        "descripcion": "La fórmula más simple para organizar tu dinero.",
        "imagen_url": "https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=600&q=80",
        "secciones": [
            {
                "tipo": "texto",
                "titulo": "La regla más famosa de las finanzas",
                "contenido": "La regla **50/30/20** divide tus ingresos en tres partes: el **50%** para necesidades, el **30%** para gustos y el **20%** para ahorrar. Simple, práctica y funciona para cualquier nivel de ingresos.",
                "emoji": "📐"
            },
            {
                "tipo": "ejemplo",
                "titulo": "Aplicado a tu vida universitaria",
                "contenido": "Si ganas o recibes **$400 al mes**:\n\n• **$200 (50%)** → Necesidades: comida, transporte, arriendo\n• **$120 (30%)** → Gustos: salidas, ropa, entretenimiento\n• **$80 (20%)** → Ahorro: fondo de emergencia, metas",
                "emoji": "🎓"
            },
            {
                "tipo": "dato",
                "titulo": "¿Qué pasa si no puedes ahorrar el 20%?",
                "contenido": "Empieza por el **1%** y auméntalo cada mes. Ahorrar $4 al mes es infinitamente mejor que no ahorrar nada. La clave es el hábito, no la cantidad.",
                "emoji": "🌱"
            },
        ],
        "quiz": [
            {
                "pregunta": "En la regla 50/30/20, ¿qué representa el 20%?",
                "opciones": ["Comida y transporte", "Diversión y gustos", "Ahorro", "Deudas"],
                "respuesta": 2,
                "explicacion": "El 20% siempre va al ahorro. Es el porcentaje más importante para tu futuro."
            },
            {
                "pregunta": "Si recibes $500 al mes, ¿cuánto deberías ahorrar según la regla 50/30/20?",
                "opciones": ["$50", "$100", "$150", "$250"],
                "respuesta": 1,
                "explicacion": "El 20% de $500 = $100. Ese es el ahorro recomendado."
            },
            {
                "pregunta": "¿Qué entra en el 50% de necesidades?",
                "opciones": ["Netflix y salidas", "Comida, transporte y arriendo", "Ropa de marca y gadgets", "Viajes y vacaciones"],
                "respuesta": 1,
                "explicacion": "Las necesidades son gastos esenciales: alimentación, transporte básico, vivienda."
            },
        ]
    },

    {
        "id": 3, "nivel": 1, "nivel_nombre": "Básico",
        "titulo": "Fondo de Emergencia",
        "emoji": "🛡️",
        "duracion": "3 min",
        "descripcion": "Tu red de seguridad financiera.",
        "imagen_url": "https://images.unsplash.com/photo-1633158829585-23ba8f7c8caf?w=600&q=80",
        "secciones": [
            {
                "tipo": "texto",
                "titulo": "¿Qué es un fondo de emergencia?",
                "contenido": "Es dinero guardado específicamente para **imprevistos**: se daña tu laptop, te enfermas, pierdes tu trabajo. No es para vacaciones ni ropa. Es tu escudo financiero.",
                "emoji": "🛡️"
            },
            {
                "tipo": "ejemplo",
                "titulo": "¿Cuánto necesitas?",
                "contenido": "Los expertos recomiendan tener entre **3 y 6 meses** de tus gastos guardados. Si gastas $300 al mes, tu fondo de emergencia ideal es entre **$900 y $1,800**.\n\nSi eso parece mucho, empieza con una meta de **$100** y ve subiendo.",
                "emoji": "🎯"
            },
            {
                "tipo": "dato",
                "titulo": "Error común",
                "contenido": "Mucha gente usa su tarjeta de crédito para emergencias. Eso convierte un problema en dos: el imprevisto más una deuda con intereses. Un fondo de emergencia te evita exactamente eso.",
                "emoji": "⚠️"
            },
        ],
        "quiz": [
            {
                "pregunta": "¿Para qué sirve un fondo de emergencia?",
                "opciones": ["Para comprar lo que quieras", "Para cubrir imprevistos sin endeudarte", "Para invertir en acciones", "Para pagar vacaciones"],
                "respuesta": 1,
                "explicacion": "El fondo de emergencia es exclusivo para imprevistos reales, no para gastos planeados."
            },
            {
                "pregunta": "¿Cuántos meses de gastos se recomienda tener en el fondo?",
                "opciones": ["1 mes", "2 meses", "Entre 3 y 6 meses", "12 meses"],
                "respuesta": 2,
                "explicacion": "3 a 6 meses de gastos es el estándar recomendado por expertos financieros."
            },
            {
                "pregunta": "¿Dónde NO deberías guardar tu fondo de emergencia?",
                "opciones": ["Cuenta de ahorros", "Invertido en criptomonedas", "Cuenta corriente", "Efectivo en un lugar seguro"],
                "respuesta": 1,
                "explicacion": "Las criptomonedas son muy volátiles. Tu fondo de emergencia necesita estar disponible y estable."
            },
        ]
    },

    # ══════════════ NIVEL 2 ══════════════
    {
        "id": 4, "nivel": 2, "nivel_nombre": "Intermedio",
        "titulo": "Interés Simple vs Compuesto",
        "emoji": "📈",
        "duracion": "4 min",
        "descripcion": "Entiende cómo crece (o decrece) tu dinero con el tiempo.",
        "imagen_url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=600&q=80",
        "secciones": [
            {
                "tipo": "texto",
                "titulo": "Interés Simple",
                "contenido": "El **interés simple** se calcula siempre sobre el capital original. Si depositas **$1,000** al 10% anual:\n\n• Año 1: $100 de interés → Total: $1,100\n• Año 2: $100 de interés → Total: $1,200\n• Año 3: $100 de interés → Total: $1,300\n\nSiempre ganas lo mismo.",
                "emoji": "➕"
            },
            {
                "tipo": "ejemplo",
                "titulo": "Interés Compuesto — La magia",
                "contenido": "El **interés compuesto** se calcula sobre el capital más los intereses acumulados. Con los mismos $1,000 al 10%:\n\n• Año 1: $100 → Total: $1,100\n• Año 2: $110 → Total: $1,210\n• Año 3: $121 → Total: $1,331\n\n¡Cada año ganas MÁS que el anterior!",
                "emoji": "🚀"
            },
            {
                "tipo": "dato",
                "titulo": "La Regla del 72",
                "contenido": "Divide **72** entre la tasa de interés anual y obtienes los años que tarda en duplicarse tu dinero.\n\n• Al 6% anual: 72 ÷ 6 = **12 años** para duplicarse\n• Al 12% anual: 72 ÷ 12 = **6 años** para duplicarse\n\nEmpezar joven es tu mayor ventaja.",
                "emoji": "✨"
            },
        ],
        "quiz": [
            {
                "pregunta": "¿En qué se diferencia el interés compuesto del simple?",
                "opciones": [
                    "No hay diferencia",
                    "El compuesto genera interés sobre el capital más los intereses acumulados",
                    "El simple genera más dinero",
                    "El compuesto solo aplica a préstamos"
                ],
                "respuesta": 1,
                "explicacion": "El interés compuesto crece exponencialmente porque genera interés sobre interés."
            },
            {
                "pregunta": "Según la Regla del 72, ¿en cuántos años se duplica $500 al 9% anual?",
                "opciones": ["5 años", "8 años", "10 años", "12 años"],
                "respuesta": 1,
                "explicacion": "72 ÷ 9 = 8 años. En 8 años, tus $500 se convierten en $1,000."
            },
            {
                "pregunta": "¿Por qué es importante empezar a ahorrar/invertir joven?",
                "opciones": [
                    "Porque los jóvenes tienen más suerte",
                    "Porque el interés compuesto necesita tiempo para crecer significativamente",
                    "Porque los bancos dan mejores tasas a jóvenes",
                    "No importa la edad"
                ],
                "respuesta": 1,
                "explicacion": "El tiempo es el ingrediente más poderoso del interés compuesto. Cada año que esperas cuesta más que el anterior."
            },
        ]
    },

    {
        "id": 5, "nivel": 2, "nivel_nombre": "Intermedio",
        "titulo": "Deuda Buena vs Deuda Mala",
        "emoji": "💳",
        "duracion": "3 min",
        "descripcion": "No toda deuda es igual. Aprende a diferenciarlas.",
        "imagen_url": "https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=600&q=80",
        "secciones": [
            {
                "tipo": "texto",
                "titulo": "Deuda Buena",
                "contenido": "Una **deuda buena** te ayuda a generar más valor del que cuesta. Ejemplos:\n\n• **Crédito educativo**: tu carrera puede generarte ingresos por décadas\n• **Préstamo para un negocio**: si el negocio gana más de lo que pagas en intereses\n• **Hipoteca**: pagas por algo que se valoriza con el tiempo",
                "emoji": "✅"
            },
            {
                "tipo": "ejemplo",
                "titulo": "Deuda Mala",
                "contenido": "Una **deuda mala** financia consumo que pierde valor inmediatamente:\n\n• **Tarjeta de crédito para ropa o salidas**: pagas intereses del 30-60% anual por algo que ya consumiste\n• **Crédito para celular de lujo**: el celular pierde valor, la deuda sigue\n• **Préstamos de 'gota a gota'**: tasas de interés ilegalmente altas",
                "emoji": "❌"
            },
            {
                "tipo": "dato",
                "titulo": "El costo real de la tarjeta de crédito",
                "contenido": "Si compras algo de **$500** con tarjeta y solo pagas el mínimo cada mes:\n\n• Con interés del 40% anual puedes terminar pagando **$1,200+**\n• Puede tomarte más de **3 años** en liquidarlo\n\nSiempre paga el saldo completo al final del mes.",
                "emoji": "💡"
            },
        ],
        "quiz": [
            {
                "pregunta": "¿Cuál es un ejemplo de deuda BUENA?",
                "opciones": [
                    "Tarjeta de crédito para salir a comer",
                    "Crédito educativo para tu carrera",
                    "Préstamo para comprar ropa de marca",
                    "Deuda para un viaje de vacaciones"
                ],
                "respuesta": 1,
                "explicacion": "Un crédito educativo invierte en tu capacidad de generar ingresos futuros."
            },
            {
                "pregunta": "¿Qué hace que una deuda sea 'mala'?",
                "opciones": [
                    "Que tenga intereses bajos",
                    "Que financie activos que se valorizan",
                    "Que financie consumo que pierde valor y tenga intereses altos",
                    "Que sea a largo plazo"
                ],
                "respuesta": 2,
                "explicacion": "La deuda mala financia cosas que pierden valor (ropa, salidas) y cobra intereses altos."
            },
            {
                "pregunta": "¿Cuál es la mejor práctica con la tarjeta de crédito?",
                "opciones": [
                    "Pagar solo el mínimo cada mes",
                    "Usarla para todo y no preocuparse",
                    "Pagar el saldo completo al final de cada mes",
                    "Tener varias tarjetas a la vez"
                ],
                "respuesta": 2,
                "explicacion": "Pagar el saldo completo evita los intereses. La tarjeta es útil si la controlas tú, no ella a ti."
            },
        ]
    },

    {
        "id": 6, "nivel": 2, "nivel_nombre": "Intermedio",
        "titulo": "Cómo Empezar a Invertir",
        "emoji": "🌱",
        "duracion": "4 min",
        "descripcion": "Invierte desde cero, sin necesitar mucho dinero.",
        "imagen_url": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=600&q=80",
        "secciones": [
            {
                "tipo": "texto",
                "titulo": "¿Qué es invertir?",
                "contenido": "Invertir es poner tu dinero a trabajar para que **genere más dinero**. No necesitas ser rico para empezar — muchas plataformas permiten invertir desde **$1**.\n\nLa diferencia entre ahorrar e invertir: el ahorro preserva tu dinero, la inversión lo hace crecer.",
                "emoji": "💰"
            },
            {
                "tipo": "ejemplo",
                "titulo": "Opciones para universitarios",
                "contenido": "**Bajo riesgo:**\n• Cuenta de ahorro con interés\n• Certificados de depósito (CDPs)\n\n**Riesgo medio:**\n• Fondos mutuos (pool de inversiones)\n• ETFs (fondos que replican el mercado)\n\n**Alto riesgo:**\n• Acciones individuales\n• Criptomonedas\n\nEmpieza por lo de bajo riesgo mientras aprendes.",
                "emoji": "📊"
            },
            {
                "tipo": "dato",
                "titulo": "El error más común",
                "contenido": "Esperar a tener 'suficiente' dinero para invertir. Si inviertes **$20 al mes** desde los 20 años al 8% anual, a los 65 tendrás más de **$100,000**.\n\nSi esperas hasta los 30 para empezar con los mismos $20, tendrás solo **$45,000**.\n\n¡10 años de diferencia = más del doble de dinero!",
                "emoji": "⏰"
            },
        ],
        "quiz": [
            {
                "pregunta": "¿Cuál es la diferencia entre ahorrar e invertir?",
                "opciones": [
                    "No hay diferencia",
                    "El ahorro preserva el dinero, la inversión lo hace crecer",
                    "Invertir es más seguro que ahorrar",
                    "Solo los ricos pueden invertir"
                ],
                "respuesta": 1,
                "explicacion": "Ahorrar protege tu dinero de gastos. Invertir lo expone a un riesgo calculado para que crezca."
            },
            {
                "pregunta": "¿Cuál de estas opciones tiene MENOR riesgo?",
                "opciones": [
                    "Criptomonedas",
                    "Acciones individuales",
                    "Certificados de depósito (CDPs)",
                    "Startups"
                ],
                "respuesta": 2,
                "explicacion": "Los CDPs tienen rendimiento fijo y garantizado. Son ideales para empezar."
            },
            {
                "pregunta": "¿Por qué es importante empezar a invertir joven aunque sea poco?",
                "opciones": [
                    "Los jóvenes pagan menos impuestos",
                    "El interés compuesto multiplica más el dinero con más tiempo",
                    "Es más fácil abrir cuentas siendo joven",
                    "Los mercados suben más cuando eres joven"
                ],
                "respuesta": 1,
                "explicacion": "El tiempo es el factor más importante en la inversión. Más tiempo = más interés compuesto acumulado."
            },
        ]
    },

    # ══════════════ NIVEL 3 ══════════════
    {
        "id": 7, "nivel": 3, "nivel_nombre": "Avanzado",
        "titulo": "ETFs y Fondos Indexados",
        "emoji": "📦",
        "duracion": "4 min",
        "descripcion": "La forma más inteligente y simple de invertir a largo plazo.",
        "imagen_url": "https://images.unsplash.com/photo-1642790551116-18e4f4da1fb4?w=600&q=80",
        "secciones": [
            {
                "tipo": "texto",
                "titulo": "¿Qué es un ETF?",
                "contenido": "Un **ETF (Exchange Traded Fund)** es como una canasta que contiene muchas acciones a la vez. En lugar de comprar acciones de una sola empresa, compras una pequeña parte de cientos de empresas.\n\nEjemplo: el ETF **S&P 500** incluye las 500 empresas más grandes de EE.UU. Con $10 puedes tener una fracción de Apple, Google, Amazon y otras 497 empresas.",
                "emoji": "🧺"
            },
            {
                "tipo": "ejemplo",
                "titulo": "¿Por qué son mejores que acciones individuales?",
                "contenido": "**Diversificación automática**: si una empresa cae, las otras te protegen.\n\n**Comisiones bajas**: los ETFs cobran 0.03% - 0.20% anual vs 1-2% de fondos activos.\n\n**Rendimiento histórico**: el S&P 500 ha dado en promedio **10% anual** en los últimos 100 años, incluyendo crisis y pandemias.",
                "emoji": "🏆"
            },
            {
                "tipo": "dato",
                "titulo": "Warren Buffett lo recomienda",
                "contenido": "Warren Buffett, uno de los inversores más exitosos del mundo, ha dicho múltiples veces que para la mayoría de personas la mejor inversión es un **fondo indexado de bajo costo**.\n\nSi el mejor inversor del mundo lo recomienda para gente normal, algo de bueno tendrá.",
                "emoji": "💎"
            },
        ],
        "quiz": [
            {
                "pregunta": "¿Qué es un ETF?",
                "opciones": [
                    "Una cuenta bancaria especial",
                    "Un fondo que agrupa muchas acciones en una sola inversión",
                    "Un tipo de criptomoneda",
                    "Un préstamo bancario"
                ],
                "respuesta": 1,
                "explicacion": "Un ETF es una canasta de acciones que te da diversificación automática con una sola compra."
            },
            {
                "pregunta": "¿Cuál es una ventaja clave de los ETFs sobre acciones individuales?",
                "opciones": [
                    "Siempre suben de precio",
                    "Son garantizados por el gobierno",
                    "Diversifican el riesgo automáticamente",
                    "No tienen ningún riesgo"
                ],
                "respuesta": 2,
                "explicacion": "Al tener muchas acciones, si una empresa cae mucho, el impacto en tu inversión total es menor."
            },
            {
                "pregunta": "¿Qué rendimiento promedio anual ha dado históricamente el S&P 500?",
                "opciones": ["2%", "5%", "10%", "25%"],
                "respuesta": 2,
                "explicacion": "El S&P 500 ha rentado aproximadamente 10% anual en promedio durante los últimos 100 años."
            },
        ]
    },

    {
        "id": 8, "nivel": 3, "nivel_nombre": "Avanzado",
        "titulo": "Planificación Financiera a Largo Plazo",
        "emoji": "🏁",
        "duracion": "4 min",
        "descripcion": "Diseña tu futuro financiero desde hoy.",
        "imagen_url": "https://images.unsplash.com/photo-1434626881859-194d67b2b86f?w=600&q=80",
        "secciones": [
            {
                "tipo": "texto",
                "titulo": "Las 4 metas financieras de vida",
                "contenido": "Los expertos identifican 4 grandes metas que todos deberíamos planificar:\n\n1. **Fondo de emergencia** (3-6 meses de gastos)\n2. **Pagar deudas de alto interés**\n3. **Jubilación** (sí, desde los 20 años)\n4. **Metas específicas** (casa, negocio, viaje)",
                "emoji": "🎯"
            },
            {
                "tipo": "ejemplo",
                "titulo": "El orden importa",
                "contenido": "**Paso 1:** Fondo de emergencia → nunca te endeudes por un imprevisto\n**Paso 2:** Elimina deudas de tarjeta → 30-60% de interés es imposible de superar invirtiendo\n**Paso 3:** Contribuye a jubilación → aunque sea el 5% de tus ingresos\n**Paso 4:** Invierte para metas → con lo que sobre después de los 3 pasos anteriores",
                "emoji": "📋"
            },
            {
                "tipo": "dato",
                "titulo": "El poder de los pequeños hábitos",
                "contenido": "No necesitas ganar mucho para tener buena salud financiera. Necesitas:\n\n✅ Gastar menos de lo que ganas\n✅ Ahorrar algo cada mes, aunque sea poco\n✅ Evitar deudas de consumo\n✅ Invertir con paciencia y consistencia\n\nEsos 4 hábitos, aplicados por años, construyen libertad financiera.",
                "emoji": "🌟"
            },
        ],
        "quiz": [
            {
                "pregunta": "¿Cuál debería ser la PRIMERA meta financiera según los expertos?",
                "opciones": [
                    "Invertir en bolsa",
                    "Comprar una casa",
                    "Construir un fondo de emergencia",
                    "Pagar la jubilación"
                ],
                "respuesta": 2,
                "explicacion": "Sin fondo de emergencia, cualquier imprevisto puede arruinar todo tu progreso financiero."
            },
            {
                "pregunta": "¿Por qué conviene pagar deudas de tarjeta ANTES de invertir?",
                "opciones": [
                    "Porque los bancos lo exigen",
                    "Porque la deuda cobra 30-60% de interés, más de lo que cualquier inversión rinde",
                    "Porque las inversiones son ilegales con deudas",
                    "No conviene, es mejor invertir primero"
                ],
                "respuesta": 1,
                "explicacion": "Es matemáticamente imposible que una inversión normal supere el 40-60% que cobra una tarjeta de crédito."
            },
            {
                "pregunta": "¿Cuál de estos hábitos es más importante para la salud financiera?",
                "opciones": [
                    "Ganar mucho dinero",
                    "Tener trabajo estable",
                    "Gastar menos de lo que ganas consistentemente",
                    "Vivir con los padres"
                ],
                "respuesta": 2,
                "explicacion": "Gastar menos de lo que ganas es la base de toda salud financiera, sin importar cuánto ganes."
            },
        ]
    },
]

# ─────────────────────────────────────────────────────────────
# FUNCIONES DE PROGRESO (Supabase)
# ─────────────────────────────────────────────────────────────
from config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client

supabase = create_client(SUPABASE_URL.strip().rstrip('/'), SUPABASE_KEY.strip())


def obtener_progreso(usuario_id: int) -> dict:
    """Devuelve dict {leccion_id: 'completada'|'en_progreso'} del usuario."""
    try:
        res = supabase.from_("progreso_lecciones").select("*").eq("usuario_id", usuario_id).execute()
        return {r["leccion_id"]: r["estado"] for r in (res.data or [])}
    except Exception as e:
        print(f"Error obteniendo progreso: {e}")
        return {}


def marcar_leccion_completada(usuario_id: int, leccion_id: int):
    """Marca una lección como completada en Supabase."""
    try:
        existente = supabase.from_("progreso_lecciones").select("id")\
            .eq("usuario_id", usuario_id).eq("leccion_id", leccion_id).execute()
        if existente.data:
            supabase.from_("progreso_lecciones").update({"estado": "completada"})\
                .eq("usuario_id", usuario_id).eq("leccion_id", leccion_id).execute()
        else:
            supabase.from_("progreso_lecciones").insert({
                "usuario_id": usuario_id,
                "leccion_id": leccion_id,
                "estado": "completada"
            }).execute()
    except Exception as e:
        print(f"Error guardando progreso: {e}")