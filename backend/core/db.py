import os
from typing import Generator
import logging
from urllib.parse import urlparse

from sqlmodel import SQLModel, Session, create_engine, text
import pymysql

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Crear un manejador para la consola
handler = logging.StreamHandler()

# Definir un formateador personalizado que excluya el nombre del logger
formatter = logging.Formatter('%(levelname)s: %(message)s')
handler.setFormatter(formatter)

# Limpiar manejadores previos y agregar el nuevo
logger.handlers.clear()
logger.addHandler(handler)

def get_database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set. "
            "Example (MySQL): mysql+pymysql://user:password@host:3306/database_name"
        )
    return url

def create_database_if_not_exists() -> None:
    """Create the database if it doesn't exist"""
    database_url = get_database_url()
    
    # Parse the URL to extract components
    parsed = urlparse(database_url)
    database_name = parsed.path[1:]  # Remove the leading '/'
    
    if not database_name:
        raise RuntimeError("No database name found in DATABASE_URL")
    
    # Create connection URL without database name
    server_url = f"{parsed.scheme}://{parsed.netloc}"
    if parsed.username and parsed.password:
        server_url = f"{parsed.scheme}://{parsed.username}:{parsed.password}@{parsed.hostname}"
        if parsed.port:
            server_url += f":{parsed.port}"
    
    logger.info(f"\tChecking if database '{database_name}' exists...")
    
    try:
        # Create engine without specifying database
        temp_engine = create_engine(server_url, echo=False)
        
        with Session(temp_engine) as session:
            # Check if database exists
            result = session.exec(
                text(f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{database_name}'")
            ).fetchone()
            
            if not result:
                logger.info(f"\tDatabase '{database_name}' does not exist. Creating...")
                session.exec(text(f"CREATE DATABASE {database_name} DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_0900_ai_ci"))
                session.commit()
                logger.info(f"\tDatabase '{database_name}' created successfully!")
            else:
                logger.info(f"\tDatabase '{database_name}' already exists.")
        
        temp_engine.dispose()
        
    except Exception as e:
        logger.error(f"\tError creating database: {e}")
        raise RuntimeError(f"\tFailed to create database '{database_name}': {e}")

# Create a synchronous engine (recommended for SQLModel by default)
engine = None

def get_engine():
    global engine
    if engine is None:
        engine = create_engine(get_database_url(), echo=False)
    return engine

def create_db_and_tables() -> None:
    """Create database and tables"""
    try:
        # First, ensure database exists
        create_database_if_not_exists()
        
        # Now create tables
        logger.info("\tCreating tables...")
        
        # Imports intentionally inside the function to avoid circular imports.
        from backend.models.users.UsersModel import User
        from backend.models.rooms.RoomsModel import Room
        from backend.models.reservations.ReservationsModel import Reservation

        SQLModel.metadata.create_all(get_engine())
        logger.info("\tTables created successfully!")
        
    except Exception as e:
        logger.error(f"\tError in create_db_and_tables: {e}")
        raise

def get_session() -> Generator[Session, None, None]:
    with Session(get_engine()) as session:
        yield session