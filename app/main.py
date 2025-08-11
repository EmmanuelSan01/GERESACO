from fastapi import FastAPI
from dotenv import load_dotenv
import os
import sys

# Cargar variables de entorno
load_dotenv()

# Ajustar sys.path para que siempre encuentre backend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.core.db import create_db_and_tables
from backend.routes.users.UsersRoutes import router as users_router

# Crear app
app = FastAPI(title="GERESACO API", version="1.0.0")

# Incluir rutas
app.include_router(users_router)

@app.on_event("startup")
def on_startup():
    # Crear tablas si no existen
    create_db_and_tables()

@app.get("/")
def health_check():
    return {"status": "ok"}

# Mostrar rutas cargadas para depuración
@app.on_event("startup")
def show_routes():
    print("Rutas cargadas:", [route.path for route in app.routes])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)