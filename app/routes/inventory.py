from fastapi import APIRouter, HTTPException, Body, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, List
from app.models.egg import EggType, EggSize
from app.database.mongodb import MongoDB

router = APIRouter(tags=["inventory"])
templates = Jinja2Templates(directory="app/templates")
db = MongoDB()

@router.get("/inventory", response_class=HTMLResponse)
async def inventory_page(request: Request):
    """Renderiza la página de gestión de inventario"""
    return templates.TemplateResponse("inventory.html", {"request": request})

@router.get("/api/inventory", response_model=List[Dict])
async def get_inventory():
    """Obtiene todos los huevos en el inventario"""
    eggs = db.get_all_eggs()
    if not eggs:
        raise HTTPException(status_code=404, detail="No hay huevos en el inventario")
    return eggs

@router.post("/api/inventory/add")
async def add_eggs(
    egg_type: EggType = Body(...),
    egg_size: EggSize = Body(...),
    quantity: int = Body(...)
):
    """Agrega huevos al inventario"""
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser positiva")
    
    egg_data = {
        "type": egg_type,
        "size": egg_size,
        "stock": quantity
    }
    success = db.upsert_egg(egg_data)
    if not success:
        raise HTTPException(status_code=500, detail="Error al agregar huevos al inventario")
    
    return {"message": f"Se agregaron {quantity} huevos {egg_type} {egg_size} al inventario"}

@router.put("/api/inventory/update")
async def update_egg_inventory(
    egg_type: EggType = Body(...),
    egg_size: EggSize = Body(...),
    new_stock: int = Body(...)
):
    """Actualiza el stock de huevos en el inventario"""
    if new_stock < 0:
        raise HTTPException(status_code=400, detail="El stock no puede ser negativo")
    
    egg_data = {
        "type": egg_type,
        "size": egg_size,
        "stock": new_stock
    }
    success = db.upsert_egg(egg_data)
    if not success:
        raise HTTPException(status_code=500, detail="Error al actualizar el inventario")
    
    return {"message": f"El stock de huevos {egg_type} {egg_size} se actualizó a {new_stock}"}