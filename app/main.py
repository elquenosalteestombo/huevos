from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.routes import inventory, sales
import os

# Crear la aplicación FastAPI
app = FastAPI(
    title="Avícola Llano Grande SAS",
    description="Sistema de gestión de inventario y ventas para una granja avícola",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP
    allow_headers=["*"],  # Permitir todos los encabezados
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Incluir routers
app.include_router(inventory.router)
app.include_router(sales.router)

# Configuración de plantillas
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Renderiza la página principal"""
    return templates.TemplateResponse(
        "base.html", 
        {"request": request, "title": "Avícola Llano Grande SAS"}
    )

# Crear directorios necesarios
os.makedirs("app/invoices", exist_ok=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8010, reload=True)