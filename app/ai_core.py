from google import genai
from google.genai import types
from config import GEMINI_API_KEY


def clasificar_gasto(texto_usuario: str) -> str:
    # Nos conectamos a Gemini con la clave que guardamos en config
    client = genai.Client(api_key=GEMINI_API_KEY)

    # Aquí le dejamos claro a la IA qué categorías queremos y que no meta floro
    instruccion = (
        "Eres el clasificador de gastos de Polibank. "
        "Lee lo que gastó el usuario y devuelve SOLO una de estas palabras "
        "en minúscula y sin puntos: comida, transporte, estudios, diversion, otros. "
        "Si no encaja en ninguna, pon: otros."
    )

    try:
        # Usamos el tipo de configuración correcto que pide la librería
        configuracion = types.GenerateContentConfig(
            system_instruction=instruccion
        )

        # Llamamos al modelo pasándole la configuración limpia
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Gasto: {texto_usuario}",
            config=configuracion
        )
        # Devolvemos el texto limpio sin espacios extras
        return response.text.strip()

    except Exception as e:
        print(f"Falló la conexión con Gemini: {e}")
        return "otros"

