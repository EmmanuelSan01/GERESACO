from fastapi import FastAPI
from dotenv import load_dotenv
import os
import sys
import logging
import threading
import time
from contextlib import asynccontextmanager

# Configure logging FIRST
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Ajustar sys.path para que siempre encuentre backend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.core.db import create_db_and_tables
from backend.routes.users.UsersRoutes import router as users_router
from backend.routes.rooms.RoomsRoutes import router as rooms_router
from backend.routes.reservations.ReservationsRoutes import router as reservations_router
from backend.routes.auth.AuthRoutes import router as auth_router

from backend.models.users.UsersModel import User
from backend.models.rooms.RoomsModel import Room
from backend.models.reservations.ReservationsModel import Reservation

def start_console_interface_thread():
    """Start console interface in a separate thread after a delay"""
    def delayed_start():
        # Wait for the server to start
        time.sleep(3)
        
        # Check if we're running in development mode
        if os.getenv("ENABLE_CONSOLE_INTERFACE", "true").lower() == "true":
            try:
                from app.utils.console_interface import start_console_interface
                logger.info("🖥️  Iniciando interfaz de consola...")
                start_console_interface()
            except ImportError as e:
                logger.error(f"Error importing console interface: {e}")
            except Exception as e:
                logger.error(f"Error starting console interface: {e}")
    
    # Start console interface in a separate thread
    console_thread = threading.Thread(target=delayed_start, daemon=True)
    console_thread.start()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Application startup complete. Creating database and tables...")
    create_db_and_tables()
    
    # Start console interface if enabled
    if os.getenv("ENABLE_CONSOLE_INTERFACE", "true").lower() == "true":
        start_console_interface_thread()
    
    yield
    logger.info("🛑 Application shutdown.")

app = FastAPI(
    title="GERESACO API",
    version="1.0.0",
    lifespan=lifespan
)

# Incluir rutas
app.include_router(users_router)
app.include_router(rooms_router)
app.include_router(reservations_router)
app.include_router(auth_router)

@app.get("/")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    
    # Print startup message
    print("🚀 Iniciando GERESACO...")
    print("📡 API disponible en: http://localhost:8000")
    print("📚 Documentación en: http://localhost:8000/docs")
    print("🖥️  Interfaz de consola se iniciará automáticamente...")
    print("-" * 50)
    
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)