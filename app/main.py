from fastapi import FastAPI
from dotenv import load_dotenv
import os
import sys
import logging
from contextlib import asynccontextmanager

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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

from backend.models.users.UsersModel import User
from backend.models.rooms.RoomsModel import Room
from backend.models.reservations.ReservationsModel import Reservation

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("\tApplication startup complete. Creating database and tables...")
    create_db_and_tables()
    yield
    logger.info("\tApplication shutdown.")

app = FastAPI(
    title="GERESACO API",
    version="1.0.0",
    lifespan=lifespan
)

# Incluir rutas
app.include_router(users_router)
app.include_router(rooms_router)
app.include_router(reservations_router)

@app.get("/")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)