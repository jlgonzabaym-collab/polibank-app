import bcrypt
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

url_limpia = SUPABASE_URL.strip().rstrip('/')
key_limpia = SUPABASE_KEY.strip()

supabase: Client = create_client(url_limpia, key_limpia)


# 1. REGISTRAR USUARIO
def registrar_usuario(correo, password):
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        supabase.from_("usuarios").insert({
            "correo": correo.lower().strip(),
            "password_hash": hashed_pw
        }).execute()
        return True, "¡Usuario registrado con éxito! Ya puedes iniciar sesión."
    except Exception:
        return False, "El correo ya se encuentra registrado."


# 2. INICIAR SESIÓN
def login_usuario(correo, password):
    try:
        respuesta = supabase.from_("usuarios").select("*").eq("correo", correo.lower().strip()).execute()
        usuarios = respuesta.data
        if usuarios:
            usuario = usuarios[0]
            if bcrypt.checkpw(password.encode('utf-8'), usuario["password_hash"].encode('utf-8')):
                return True, usuario
        return False, "Correo o contraseña incorrectos."
    except Exception as e:
        return False, f"Error al conectar con la base de datos: {str(e)}"


# 3. GUARDAR MOVIMIENTO
def guardar_movimiento(usuario_id, tipo, detalle, monto, categoria, fecha):
    try:
        supabase.from_("movimientos").insert({
            "usuario_id": usuario_id,
            "tipo": tipo,
            "detalle": detalle,
            "monto": float(monto),
            "categoria": categoria,
            "fecha": str(fecha)
        }).execute()
        return True, "Movimiento guardado con éxito."
    except Exception as e:
        return False, f"Error al guardar movimiento: {str(e)}"


# 4. OBTENER MOVIMIENTOS (ordenados por fecha descendente)
def obtener_movimientos(usuario_id):
    try:
        respuesta = (
            supabase.from_("movimientos")
            .select("*")
            .eq("usuario_id", usuario_id)
            .order("fecha", desc=True)
            .execute()
        )
        return respuesta.data
    except Exception as e:
        print(f"Error al obtener movimientos: {str(e)}")
        return []


# 5. OBTENER VIDEOS EDUCATIVOS
def obtener_videos_educativos():
    try:
        respuesta = supabase.from_("videos").select("*").order("id").execute()
        return respuesta.data
    except Exception as e:
        print(f"Error al cargar videos: {e}")
        return []


# 6. ELIMINAR MOVIMIENTO POR ID
def eliminar_movimiento(movimiento_id):
    try:
        supabase.from_("movimientos").delete().eq("id", movimiento_id).execute()
        return True, "Movimiento eliminado."
    except Exception as e:
        return False, f"Error al eliminar: {str(e)}"