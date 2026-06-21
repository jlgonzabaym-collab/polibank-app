from datetime import date, timedelta
from config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client, Client

supabase: Client = create_client(SUPABASE_URL.strip().rstrip('/'), SUPABASE_KEY.strip())

# ── Definición de todos los badges disponibles
BADGES = {
    "primer_movimiento": {"nombre": "Primer Paso",      "emoji": "👣", "desc": "Registraste tu primer movimiento"},
    "racha_3":           {"nombre": "En Llamas",         "emoji": "🔥", "desc": "3 días seguidos registrando"},
    "racha_7":           {"nombre": "Primera Semana",    "emoji": "🏅", "desc": "7 días seguidos registrando"},
    "racha_30":          {"nombre": "Mes Perfecto",      "emoji": "🏆", "desc": "30 días seguidos registrando"},
    "xp_100":            {"nombre": "Estudiante",        "emoji": "📘", "desc": "Llegaste a 100 XP"},
    "xp_500":            {"nombre": "Analista",          "emoji": "📊", "desc": "Llegaste a 500 XP"},
    "xp_1000":           {"nombre": "Experto",           "emoji": "💎", "desc": "Llegaste a 1000 XP"},
    "video_visto":       {"nombre": "Curioso Financiero","emoji": "🎬", "desc": "Visitaste la Academia"},
    "saldo_positivo":    {"nombre": "En Verde",          "emoji": "💚", "desc": "Mantuviste saldo positivo"},
}

XP_ACCIONES = {
    "ingreso":  5,
    "gasto":   10,
    "video":   15,
    "login":    2,
}


def _obtener_perfil(usuario_id: int) -> dict:
    try:
        res = supabase.from_("gamificacion").select("*").eq("usuario_id", usuario_id).execute()
        if res.data:
            return res.data[0]
    except Exception as e:
        print(f"Error obteniendo perfil: {e}")
    return None


def _crear_perfil(usuario_id: int) -> dict:
    perfil = {
        "usuario_id": usuario_id,
        "xp_total":        0,
        "racha_actual":    0,
        "racha_maxima":    0,
        "ultimo_registro": None,
        "badges":          []
    }
    try:
        supabase.from_("gamificacion").insert(perfil).execute()
    except Exception as e:
        print(f"Error creando perfil: {e}")
    return perfil


def _guardar_perfil(perfil: dict):
    try:
        supabase.from_("gamificacion").update({
            "xp_total":        perfil["xp_total"],
            "racha_actual":    perfil["racha_actual"],
            "racha_maxima":    perfil["racha_maxima"],
            "ultimo_registro": str(perfil["ultimo_registro"]) if perfil["ultimo_registro"] else None,
            "badges":          perfil["badges"]
        }).eq("usuario_id", perfil["usuario_id"]).execute()
    except Exception as e:
        print(f"Error guardando perfil: {e}")


def _verificar_badges(perfil: dict) -> list:
    """Devuelve lista de badges recién desbloqueados en esta acción."""
    nuevos = []
    badges_actuales = perfil.get("badges") or []

    def desbloquear(clave):
        if clave not in badges_actuales:
            badges_actuales.append(clave)
            nuevos.append(clave)

    xp    = perfil["xp_total"]
    racha = perfil["racha_actual"]
    movs  = perfil.get("_total_movimientos", 0)

    if movs >= 1:    desbloquear("primer_movimiento")
    if racha >= 3:   desbloquear("racha_3")
    if racha >= 7:   desbloquear("racha_7")
    if racha >= 30:  desbloquear("racha_30")
    if xp  >= 100:   desbloquear("xp_100")
    if xp  >= 500:   desbloquear("xp_500")
    if xp  >= 1000:  desbloquear("xp_1000")
    if perfil.get("_visito_academia"): desbloquear("video_visto")
    if perfil.get("_saldo_positivo"):  desbloquear("saldo_positivo")

    perfil["badges"] = badges_actuales
    return nuevos


def registrar_accion(usuario_id: int, accion: str, contexto: dict = None) -> dict:
    """
    Llama esto cada vez que el usuario hace algo relevante.
    accion: 'ingreso' | 'gasto' | 'video' | 'login'
    contexto: dict opcional con flags extra (_saldo_positivo, etc.)
    Devuelve: { xp_ganado, xp_total, racha_actual, racha_maxima, badges_nuevos }
    """
    perfil = _obtener_perfil(usuario_id)
    if not perfil:
        perfil = _crear_perfil(usuario_id)

    hoy         = date.today()
    xp_ganado   = XP_ACCIONES.get(accion, 0)
    ultimo_str  = perfil.get("ultimo_registro")
    ultimo_reg  = date.fromisoformat(str(ultimo_str)) if ultimo_str else None

    # ── Actualizar racha
    if accion in ("ingreso", "gasto"):
        if ultimo_reg is None or ultimo_reg < hoy:
            if ultimo_reg == hoy - timedelta(days=1):
                perfil["racha_actual"] = int(perfil["racha_actual"] or 0) + 1
            elif ultimo_reg == hoy:
                pass  # ya registró hoy, no suma racha de nuevo
            else:
                perfil["racha_actual"] = 1  # reset
            perfil["ultimo_registro"] = hoy
            perfil["racha_maxima"] = max(
                int(perfil.get("racha_maxima") or 0),
                int(perfil["racha_actual"])
            )

    # ── Sumar XP
    perfil["xp_total"] = int(perfil.get("xp_total") or 0) + xp_ganado

    # ── Contexto extra para badges
    if contexto:
        perfil.update(contexto)

    # Total de movimientos para badge "primer_movimiento"
    try:
        res = supabase.from_("movimientos").select("id", count="exact").eq("usuario_id", usuario_id).execute()
        perfil["_total_movimientos"] = res.count or 0
    except:
        perfil["_total_movimientos"] = 1

    # ── Verificar badges
    badges_nuevos = _verificar_badges(perfil)

    # ── Guardar
    _guardar_perfil(perfil)

    return {
        "xp_ganado":    xp_ganado,
        "xp_total":     perfil["xp_total"],
        "racha_actual": perfil["racha_actual"],
        "racha_maxima": perfil["racha_maxima"],
        "badges_nuevos": badges_nuevos,
        "todos_badges":  perfil["badges"]
    }


def obtener_estado(usuario_id: int) -> dict:
    """Lee el estado actual sin modificarlo (para mostrar en pantalla)."""
    perfil = _obtener_perfil(usuario_id)
    if not perfil:
        perfil = _crear_perfil(usuario_id)

    hoy        = date.today()
    ultimo_str = perfil.get("ultimo_registro")
    ultimo_reg = date.fromisoformat(str(ultimo_str)) if ultimo_str else None

    # ¿La racha sigue viva hoy?
    racha_viva = ultimo_reg in (hoy, hoy - timedelta(days=1)) if ultimo_reg else False
    racha_mostrar = int(perfil.get("racha_actual") or 0) if racha_viva else 0

    # Nivel según XP
    xp = int(perfil.get("xp_total") or 0)
    if xp < 100:
        nivel, nivel_nombre = 1, "Principiante"
    elif xp < 500:
        nivel, nivel_nombre = 2, "Estudiante"
    elif xp < 1000:
        nivel, nivel_nombre = 3, "Analista"
    else:
        nivel, nivel_nombre = 4, "Experto"

    # XP para el siguiente nivel
    limites = [0, 100, 500, 1000, 9999]
    xp_siguiente = limites[min(nivel, 4)]
    xp_anterior  = limites[nivel - 1]
    progreso_pct = int(((xp - xp_anterior) / max(xp_siguiente - xp_anterior, 1)) * 100) if nivel < 4 else 100

    return {
        "xp_total":      xp,
        "racha_actual":  racha_mostrar,
        "racha_maxima":  int(perfil.get("racha_maxima") or 0),
        "badges":        perfil.get("badges") or [],
        "nivel":         nivel,
        "nivel_nombre":  nivel_nombre,
        "progreso_pct":  progreso_pct,
        "xp_siguiente":  xp_siguiente,
        "racha_viva":    racha_viva,
    }