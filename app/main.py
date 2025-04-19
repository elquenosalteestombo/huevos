from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routes import inventory, sales
import os

# Create the FastAPI app
app = FastAPI(
    title="Avícola Llano Grande SAS",
    description="Sistema de gestión de inventario y ventas para una granja avícola",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(inventory.router)
app.include_router(sales.router)

# Templates
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Render the home page"""
    return templates.TemplateResponse(
        "base.html", 
        {"request": request, "title": "Avícola Llano Grande SAS"}
    )

# Create necessary directories
os.makedirs("invoices", exist_ok=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)