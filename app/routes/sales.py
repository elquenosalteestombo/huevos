from fastapi import APIRouter, HTTPException, Body, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Dict
from app.models.customer import CustomerType
from app.models.egg import EggType, EggSize
from app.models.sale import SaleItem
from app.database.mongodb import MongoDB

router = APIRouter(tags=["sales"])
db = MongoDB()
templates = Jinja2Templates(directory="app/templates")

@router.get("/sales", response_class=HTMLResponse)
async def sales_page(request: Request):
    """Renderiza la página de gestión de ventas"""
    return templates.TemplateResponse("sales.html", {"request": request})

@router.post("/api/customers")
async def create_customer(customer_data: Dict):
    """Crea un nuevo cliente"""
    existing_customer = db.get_collection("customers").find_one({"document_number": customer_data["document_number"]})
    if existing_customer:
        raise HTTPException(status_code=400, detail="El cliente ya existe")
    
    customer_id = db.create_customer(customer_data)
    return {"message": "Cliente creado exitosamente", "customer_id": customer_id}

@router.get("/api/customers/{document_number}")
async def get_customer(document_number: str):
    """Obtiene un cliente por su número de documento"""
    customer = db.get_collection("customers").find_one({"document_number": document_number}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return customer

@router.post("/api/sales")
async def create_sale(
    customer_document: str = Body(...),
    items: List[Dict] = Body(...)
):
    """Registra una nueva venta"""
    customer = db.get_collection("customers").find_one({"document_number": customer_document})
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    sale_items = []
    subtotal = 0.0

    for item in items:
        egg_type = item["egg_type"]
        egg_size = item["egg_size"]
        quantity = item["quantity"]
        unit_type = item["unit_type"]

        # Validar stock
        egg = db.get_collection("eggs").find_one({"type": egg_type, "size": egg_size})
        if not egg or egg["stock"] < quantity:
            raise HTTPException(
                status_code=400,
                detail=f"No hay suficiente stock para {egg_type} {egg_size}"
            )

        # Actualizar stock
        db.get_collection("eggs").update_one(
            {"type": egg_type, "size": egg_size},
            {"$inc": {"stock": -quantity}}
        )

        # Calcular subtotal
        unit_price = 30 if unit_type == "cubeta" else 12
        subtotal += unit_price * quantity

        sale_items.append(SaleItem(
            egg_type=egg_type,
            egg_size=egg_size,
            quantity=quantity,
            unit_type=unit_type,
            unit_price=unit_price
        ).dict())

    # Calcular IVA y total
    iva = subtotal * 0.05
    total = subtotal + iva

    # Guardar la venta en la base de datos
    sale_data = {
        "customer_id": customer["_id"],
        "customer_name": customer["name"],
        "items": sale_items,
        "subtotal": subtotal,
        "iva": iva,
        "total": total
    }
    sale_id = db.create_sale(sale_data)

    return {"message": "Venta registrada exitosamente", "sale_id": sale_id}

@router.get("/api/sales/customer/{customer_document}")
async def get_sales_by_customer(customer_document: str):
    """Obtiene todas las ventas de un cliente"""
    sales = db.get_sales_by_customer(customer_document)
    if not sales:
        raise HTTPException(status_code=404, detail="No se encontraron ventas para este cliente")
    return sales

@router.get("/api/sales")
async def get_all_sales():
    """Obtiene todas las ventas"""
    sales = db.get_all_sales()
    if not sales:
        raise HTTPException(status_code=404, detail="No se encontraron ventas")
    return sales

@router.delete("/api/sales/{sale_id}")
async def delete_sale(sale_id: str):
    """Elimina una venta"""
    success = db.delete_sale(sale_id)
    if not success:
        raise HTTPException(status_code=404, detail="La venta no existe")
    return {"message": "Venta eliminada exitosamente"}