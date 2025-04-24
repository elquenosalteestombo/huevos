from fastapi import APIRouter, HTTPException, Body, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List
from datetime import datetime
from app.database.mongodb import MongoDB
from app.models.customer import Customer, CustomerType
from app.models.egg import Egg, EggType, EggSize
from app.models.sale import Sale, SaleItem, SaleUnitType
from bson import ObjectId

router = APIRouter(tags=["sales"])
db = MongoDB()
templates = Jinja2Templates(directory="app/templates")

@router.get("/sales", response_class=HTMLResponse)
async def sales_page(request: Request):
    """Renderiza la página de gestión de ventas"""
    return templates.TemplateResponse("sales.html", {"request": request})

@router.post("/api/customers", response_model=Customer)
async def create_customer(customer: Customer):
    """Crea un nuevo cliente"""
    existing_customer = db.get_customer(customer.document_number)
    if existing_customer:
        raise HTTPException(status_code=400, detail="El cliente ya existe")
    
    customer_id = db.create_customer(customer.dict())
    return Customer(**db.get_customer(customer.document_number))

@router.get("/api/customers/{document_number}", response_model=Customer)
async def get_customer(document_number: str):
    """Obtiene un cliente por su número de documento"""
    customer = db.get_customer(document_number)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return Customer(**customer)

@router.post("/api/sales", response_model=Sale)
async def create_sale(sale_data: dict = Body(...)):
    """Registra una nueva venta"""
    # Validar datos básicos
    if "customer_document" not in sale_data or "items" not in sale_data:
        raise HTTPException(
            status_code=400,
            detail="Faltan campos requeridos: customer_document, items"
        )
    
    # Obtener información del cliente
    customer = db.get_customer(sale_data["customer_document"])
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    customer_model = Customer(**customer)
    
    # Procesar items de venta
    sale_items = []
    subtotal = 0.0
    
    for item in sale_data["items"]:
        # Validar campos del item
        required_fields = ["egg_type", "egg_size", "quantity", "unit_type"]
        if not all(field in item for field in required_fields):
            raise HTTPException(
                status_code=400,
                detail="Cada item debe tener: egg_type, egg_size, quantity y unit_type"
            )
        
        # Verificar stock disponible
        eggs = db.get_egg_stock_by_type_and_size(item["egg_type"], item["egg_size"])
        if not eggs:
            raise HTTPException(
                status_code=400,
                detail=f"No hay huevos tipo {item['egg_type']} tamaño {item['egg_size']} en inventario"
            )
        
        egg_model = Egg(**eggs[0])
        quantity = item["quantity"]
        unit_type = SaleUnitType(item["unit_type"])
        
        # Calcular cantidad total de huevos
        eggs_needed = quantity * (30 if unit_type == SaleUnitType.CUBETA else 12)
        if egg_model.stock < eggs_needed:
            raise HTTPException(
                status_code=400,
                detail=f"No hay suficiente stock para {quantity} {unit_type.value} de {item['egg_type']} {item['egg_size']}"
            )
        
        # Calcular precios
        if unit_type == SaleUnitType.CUBETA:
            unit_price = egg_model.get_price_per_cubeta()
        else:
            unit_price = egg_model.get_price_per_dozen()
        
        item_subtotal = unit_price * quantity
        subtotal += item_subtotal
        
        # Crear item de venta
        sale_item = SaleItem(
            egg_type=item["egg_type"],
            egg_size=item["egg_size"],
            quantity=quantity,
            unit_type=unit_type,
            unit_price=unit_price,
            subtotal=item_subtotal
        )
        sale_items.append(sale_item)
        
        # Actualizar stock
        updated_stock = egg_model.stock - eggs_needed
        db.upsert_egg({
            "type": item["egg_type"],
            "size": item["egg_size"],
            "stock": updated_stock
        })
    
    # Calcular totales
    iva = subtotal * 0.05  # 5% de IVA
    total = subtotal + iva
    
    # Crear registro de venta
    sale = Sale(
        customer_id="",  # Se asignará al guardar
        customer_name=customer_model.name,
        customer_document=customer_model.document_number,
        items=sale_items,
        subtotal=subtotal,
        iva=iva,
        total=total
    )
    
    # Guardar en MongoDB
    sale_dict = sale.dict()
    sale_id = db.create_sale(sale_dict)
    sale_dict["id"] = sale_id
    
    return Sale(**sale_dict)

@router.get("/api/sales/customer/{customer_document}", response_model=List[Sale])
async def get_customer_sales(customer_document: str):
    """Obtiene todas las ventas de un cliente"""
    sales = db.get_sales_by_customer(customer_document)
    if not sales:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron ventas para este cliente"
        )
    return [Sale(**sale) for sale in sales]

@router.get("/api/sales", response_model=List[Sale])
async def get_all_sales():
    """Obtiene todas las ventas"""
    sales = db.get_all_sales()
    if not sales:
        raise HTTPException(status_code=404, detail="No se encontraron ventas")
    return [Sale(**sale) for sale in sales]

@router.delete("/api/sales/{sale_id}")
async def delete_sale(sale_id: str):
    try:
        # Pasa el ID como string directamente al método delete_sale
        result = db.delete_sale(sale_id)
        if not result:
            raise HTTPException(status_code=404, detail="Venta no encontrada")
        return {"message": "Venta eliminada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al eliminar la venta: {str(e)}")


@router.delete("/api/customers/{document_number}", status_code=204)
async def delete_customer(document_number: str):
    """Elimina un cliente por su número de documento"""
    # Verificar si el cliente tiene ventas asociadas
    sales = db.get_sales_by_customer(document_number)
    if sales:
        raise HTTPException(status_code=400, detail="No se puede eliminar el cliente porque tiene ventas asociadas")

    result = db.delete_customer(document_number)
    if not result:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return {"message": "Cliente eliminado exitosamente"}


    






