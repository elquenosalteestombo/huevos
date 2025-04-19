from fastapi import APIRouter, HTTPException, Body, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, List
from app.models.egg import Egg, EggType, EggSize
from app.models.customer import Customer, CustomerType
from app.models.sale import Sale, SaleItem, SaleUnitType
from app.database.mongodb import MongoDB
from app.utils.invoice import generate_invoice
from datetime import datetime
import os
import uuid

router = APIRouter(tags=["sales"])
templates = Jinja2Templates(directory="app/templates")
db = MongoDB()

@router.get("/sales", response_class=HTMLResponse)
async def sales_page(request: Request):
    """Render the sales page"""
    eggs = db.get_all_eggs()
    return templates.TemplateResponse(
        "sales.html", 
        {"request": request, "eggs": eggs}
    )

@router.post("/api/customers")
async def create_customer(customer: Customer):
    """Create a new customer"""
    existing = db.get_customer(customer.document_number)
    if existing:
        return {"id": existing.get("id"), "message": "Customer already exists"}
    
    customer_dict = customer.dict()
    customer_dict["id"] = str(uuid.uuid4())
    customer_id = db.create_customer(customer_dict)
    
    return {"id": customer_dict["id"], "message": "Customer created successfully"}

@router.get("/api/customers/{document_number}")
async def get_customer(document_number: str):
    """Get customer by document number"""
    customer = db.get_customer(document_number)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.post("/api/sales")
async def create_sale(
    customer_document: str = Body(...),
    items: List[Dict] = Body(...)
):
    """Create a new sale with validation rules"""
    customer = db.get_customer(customer_document)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    sale_items = []
    subtotal = 0.0
    
    for item in items:
        egg_type = item["egg_type"]
        egg_size = item["egg_size"]
        quantity = item["quantity"]
        unit_type = item["unit_type"]
        
        if customer["customer_type"] == CustomerType.JURIDICAL and unit_type != SaleUnitType.CUBETA:
            raise HTTPException(
                status_code=400, 
                detail="Juridical customers can only purchase by cubeta"
            )
        
        egg = db.get_egg(egg_type, egg_size)
        if not egg:
            raise HTTPException(status_code=404, detail=f"Egg type {egg_type} {egg_size} not found")
        
        eggs_per_unit = 30 if unit_type == SaleUnitType.CUBETA else 12
        total_eggs = quantity * eggs_per_unit
        
        if egg["stock"] < total_eggs:
            raise HTTPException(
                status_code=400, 
                detail=f"Not enough stock for {egg_type} {egg_size} eggs. Available: {egg['stock']}, Requested: {total_eggs}"
            )
        
        egg_model = Egg(type=egg_type, size=egg_size, stock=egg["stock"])
        unit_price = egg_model.get_price_per_cubeta() if unit_type == SaleUnitType.CUBETA else egg_model.get_price_per_dozen()
        item_subtotal = unit_price * quantity
        
        sale_items.append(SaleItem(
            egg_type=egg_type,
            egg_size=egg_size,
            quantity=quantity,
            unit_type=unit_type,
            unit_price=unit_price,
            subtotal=item_subtotal
        ).dict())
        
        subtotal += item_subtotal
        db.update_egg_stock(egg_type, egg_size, -total_eggs)
    
    iva = subtotal * 0.05
    total = subtotal + iva
    
    sale = Sale(
        customer_id=customer["id"],
        customer_name=customer["name"],
        customer_document=customer["document_number"],
        items=sale_items,
        subtotal=subtotal,
        iva=iva,
        total=total
    )
    
    sale_id = db.create_sale(sale.dict())
    invoice_path = generate_invoice(sale.dict())
    
    return {
        "sale_id": sale.id,
        "invoice_path": invoice_path,
        "message": "Sale completed successfully"
    }

@router.get("/api/sales/{sale_id}")
async def get_sale(sale_id: str):
    """Get sale by ID"""
    sale = db.get_sale(sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale

@router.get("/api/invoices/{sale_id}")
async def get_invoice(sale_id: str):
    """Download the invoice for a sale"""
    sale = db.get_sale(sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    invoice_filename = f"invoice_{sale_id}.txt"
    invoice_path = os.path.join("invoices", invoice_filename)
    
    if not os.path.exists(invoice_path):
        invoice_path = generate_invoice(sale)
    
    return FileResponse(
        path=invoice_path,
        filename=invoice_filename,
        media_type="text/plain"
    )