from pydantic import BaseModel
from enum import Enum

class CustomerType(str, Enum):
    NATURAL = "natural"  # Individual person
    JURIDICAL = "juridical"  # Business/organization

class Customer(BaseModel):
    name: str
    document_type: str  # "CC" for natural persons, "NIT" for juridical
    document_number: str
    customer_type: CustomerType
    
    
