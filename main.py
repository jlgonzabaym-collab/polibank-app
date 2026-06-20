import uvicorn
from fastapi import FastAPI
from app.routes import router

# Inicializamos la aplicación de FastAPI
app = FastAPI(
    title="Polibank API",
    description="Backend para la categorización de gastos con IA",
    version="1.0.0"
)

# Conectamos las rutas que creamos en app/routes.py
app.include_router(router)

# Ruta de bienvenida para verificar que el servidor esté vivo
@app.get("/")
def inicio():
    return {"mensaje": "Servidor de Polibank corriendo perfecto 🚀"}

# Esto arranca el servidor usando uvicorn en el puerto 8000
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)