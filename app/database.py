import streamlit as st
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