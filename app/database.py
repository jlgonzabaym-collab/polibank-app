import bcrypt
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

# ESTO SOLUCIONA EL ERROR PGRST125: Limpiamos espacios y la barra diagonal '/' del final si existe
url_limpia = SUPABASE_URL.strip().rstrip('/')
key_limpia = SUPABASE_KEY.strip()

# Conexión segura a Supabase usando las rutas limpias
supabase: Client = create_client(url_limpia, key_limpia)


# 1. FUNCIÓN PARA REGISTRAR UN USUARIO NUEVO
def registrar_usuario(correo, password):
    # Encriptamos la contraseña para que esté segura en la base de datos
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        # Insertamos los datos en la tabla usando de una vez el estándar .from_()
        data = supabase.from_("usuarios").insert({
            "correo": correo.lower().strip(),
            "password_hash": hashed_pw
        }).execute()
        return True, "¡Usuario registrado con éxito! Ya puedes iniciar sesión."
    except Exception as e:
        return False, "El correo ya se encuentra registrado."


# 2. FUNCIÓN PARA INICIAR SESIÓN
def login_usuario(correo, password):
    try:
        # Buscamos al usuario por su correo
        respuesta = supabase.from_("usuarios").select("*").eq("correo", correo.lower().strip()).execute()
        usuarios = respuesta.data

        if usuarios:
            usuario = usuarios[0]
            # Verificamos si la contraseña coincide con el hash encriptado
            if bcrypt.checkpw(password.encode('utf-8'), usuario["password_hash"].encode('utf-8')):
                return True, usuario  # Login exitoso

        return False, "Correo o contraseña incorrectos."
    except Exception as e:
        return False, f"Error al conectar con la base de datos: {str(e)}"


# 3. FUNCIÓN PARA REGISTRAR UN MOVIMIENTO REAL EN SUPABASE
def guardar_movimiento(usuario_id, tipo, detalle, monto, categoria, fecha):
    try:
        # Usamos los nombres exactos de tus columnas en Supabase
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


# 4. FUNCIÓN PARA OBTENER LOS MOVIMIENTOS REALES DE UN USUARIO
def obtener_movimientos(usuario_id):
    try:
        # Quitamos el .order() por ahora para descartar errores de formato de fecha
        respuesta = supabase.from_("movimientos").select("*").eq("usuario_id", usuario_id).execute()
        return respuesta.data
    except Exception as e:
        print(f"Error al obtener movimientos: {str(e)}")
        return []


def obtener_videos_educativos():
    """Trae la lista de videos subidos por el administrador desde Supabase"""
    # Forzamos a Python a buscar la variable 'supabase' que está arriba en el archivo
    global supabase

    try:
        # Cambiamos .table() por .from_() que es más estable en esta versión de la librería
        respuesta = supabase.from_("videos").select("*").order("id").execute()
        return respuesta.data
    except Exception as e:
        print(f"Error al cargar videos: {e}")
        return []