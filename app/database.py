import bcrypt
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

supabase: Client = create_client(SUPABASE_URL.strip().rstrip('/'), SUPABASE_KEY.strip())

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
        return False, f"Error al conectar: {str(e)}"

def guardar_movimiento(usuario_id, tipo, detalle, monto, categoria, fecha, factura_url=None):
    try:
        fila = {
            "usuario_id": usuario_id,
            "tipo":       tipo,
            "detalle":    detalle,
            "monto":      float(monto),
            "categoria":  categoria,
            "fecha":      str(fecha)
        }
        if factura_url:
            fila["factura_url"] = factura_url
        supabase.from_("movimientos").insert(fila).execute()
        return True, "Movimiento guardado."
    except Exception as e:
        return False, f"Error al guardar: {str(e)}"

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
        print(f"Error: {str(e)}")
        return []

def obtener_videos_educativos():
    try:
        return supabase.from_("videos").select("*").order("id").execute().data
    except Exception as e:
        print(f"Error: {e}")
        return []

def eliminar_movimiento(movimiento_id):
    try:
        supabase.from_("movimientos").delete().eq("id", movimiento_id).execute()
        return True, "Eliminado."
    except Exception as e:
        return False, str(e)