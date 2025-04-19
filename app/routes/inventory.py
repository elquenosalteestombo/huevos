from fastapi import APIRouter, HTTPException, Body, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, List
from app.models.egg import Egg, EggType, EggSize
from app.database.mongodb import MongoDB

router = APIRouter(tags=["inventory"])
templates = Jinja2Templates(directory="app/templates")
db = MongoDB()

@router.get("/inventory", response_class=HTMLResponse)
async def inventory_page(request: Request):
    """Render the inventory management page"""
    eggs = db.get_all_eggs()
    return templates.TemplateResponse(
        "inventory.html", 
        {"request": request, "eggs": eggs}
    )

@router.get("/api/inventory", response_model=List[Dict])
async def get_inventory():
    """Get all eggs in inventory"""
    return db.get_all_eggs()

@router.get("/api/inventory/{egg_type}/{egg_size}")
async def get_egg_inventory(egg_type: EggType, egg_size: EggSize):
    """Get specific egg inventory by type and size"""
    egg = db.get_egg(egg_type, egg_size)
    if not egg:
        raise HTTPException(status_code=404, detail="Egg inventory not found")
    return egg

@router.post("/api/inventory/add")
async def add_eggs(
    egg_type: EggType = Body(...),
    egg_size: EggSize = Body(...),
    quantity: int = Body(...)
):
    """Add eggs to inventory"""
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    
    egg = db.get_egg(egg_type, egg_size)
    if egg:
        current_stock = egg.get("stock", 0)
        new_stock = current_stock + quantity
        success = db.update_egg_stock(egg_type, egg_size, quantity)
    else:
        egg_data = {
            "type": egg_type,
            "size": egg_size,
            "stock": quantity
        }
        success = db.upsert_egg(egg_data)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update inventory")
    
    return {"message": f"Added {quantity} {egg_type} {egg_size} eggs to inventory"}

@router.put("/api/inventory/update")
async def update_egg_inventory(
    egg_type: EggType = Body(...),
    egg_size: EggSize = Body(...),
    new_stock: int = Body(...)
):
    """Update egg inventory to a specific value"""
    if new_stock < 0:
        raise HTTPException(status_code=400, detail="Stock cannot be negative")
    
    egg_data = {
        "type": egg_type,
        "size": egg_size,
        "stock": new_stock
    }
    success = db.upsert_egg(egg_data)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update inventory")
    
    return {"message": f"Updated {egg_type} {egg_size} eggs stock to {new_stock}"}