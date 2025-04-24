from fastapi import APIRouter, HTTPException, Body, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List
from app.database.mongodb import MongoDB
from app.models.egg import Egg, EggType, EggSize

router = APIRouter(tags=["inventory"])
db = MongoDB()
templates = Jinja2Templates(directory="app/templates")

@router.get("/inventory", response_class=HTMLResponse)
async def inventory_page(request: Request):
    """Renderiza la página de gestión de inventario"""
    return templates.TemplateResponse("inventory.html", {"request": request})


@router.get("/api/inventory", response_model=List[Egg])
async def get_inventory():
    """Obtiene todos los huevos en el inventario"""
    inventory = db.get_all_eggs()
    return [Egg(**egg) for egg in inventory]  # incluso si inventory es []


@router.post("/api/inventory", response_model=Egg)
async def add_or_update_egg(egg: Egg):
    """Añade o actualiza un huevo en el inventario"""
    egg_data = egg.dict()
    success = db.upsert_egg(egg_data)
    if not success:
        raise HTTPException(status_code=500, detail="Error al actualizar el inventario")
    
    return Egg(**egg_data)

@router.delete("/api/inventory/{egg_type}/{size}")
async def remove_egg(egg_type: EggType, size: EggSize):
    """Elimina un huevo del inventario"""
    success = db.delete_egg(egg_type.value, size.value)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró huevo tipo {egg_type} tamaño {size}"
        )
    return {"message": "Huevo eliminado exitosamente"}

@router.get("/api/inventory/price/{egg_type}/{size}")
async def get_egg_prices(egg_type: EggType, size: EggSize):
    """Obtiene los precios de un tipo y tamaño de huevo"""
    eggs = db.get_egg_stock_by_type_and_size(egg_type.value, size.value)
    if not eggs:
        raise HTTPException(
            status_code=404,
            detail=f"No hay huevos tipo {egg_type} tamaño {size} en el inventario"
        )
    
    egg_model = Egg(**eggs[0])
    return {
        "unit_price": egg_model.get_price_per_unit(),
        "dozen_price": egg_model.get_price_per_dozen(),
        "cubeta_price": egg_model.get_price_per_cubeta()
    }
@router.get("/api/inventory/{egg_type}/{egg_size}")
async def get_stock(egg_type: EggType, egg_size: EggSize):
    """Obtiene el stock disponible para un tipo y tamaño de huevo"""
    stock = db.get_egg_stock_by_type_and_size(egg_type, egg_size)
    if stock is None:
        raise HTTPException(status_code=404, detail="Stock no encontrado")
    return {"stock": stock}