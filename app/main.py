from fastapi import FastAPI

from dotenv import load_dotenv
load_dotenv()

from backend.core.db import create_db_and_tables

app = FastAPI(title="GERESACO API", version="1.0.0")

@app.on_event("startup")
def on_startup():
    # Crea las tablas si no existen
    create_db_and_tables()

@app.get("/")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn

    # Ejecutar con: python -m app.main
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
