from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import List, Optional
import uuid

class SaleUnitType(str, Enum):
    CUBETA = "cubeta"  # 30 eggs
    DOZEN = "dozen"  # 12 eggs

class SaleItem(BaseModel):
    egg_type: str
    egg_size: str
    quantity: int  # Number of units (cubeta or dozen)
    unit_type: SaleUnitType
    unit_price: float
    subtotal: float

class Sale(BaseModel):
    id: str = None
    customer_id: str
    customer_name: str
    customer_document: str
    items: List[SaleItem]
    date: datetime = None
    subtotal: float
    iva: float  # 5% tax
    total: float
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.date:
            self.date = datetime.now()