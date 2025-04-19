from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import enum
from datetime import datetime

# PostgreSQL connection
DATABASE_URL = "postgresql://username:password@localhost/avicola_llano_grande"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# PostgreSQL models (if you decide to use them alongside MongoDB)
class EggTypeEnum(enum.Enum):
    RED = "red"
    WHITE = "white"

class EggSizeEnum(enum.Enum):
    A = "A"
    AA = "AA"
    B = "B"
    EXTRA = "EXTRA"

class EggInventory(Base):
    __tablename__ = "egg_inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    egg_type = Column(Enum(EggTypeEnum), nullable=False)
    egg_size = Column(Enum(EggSizeEnum), nullable=False)
    stock = Column(Integer, default=0)
    
    def __init__(self, egg_type, egg_size, stock=0):
        self.egg_type = egg_type
        self.egg_size = egg_size
        self.stock = stock

class CustomerTypeEnum(enum.Enum):
    NATURAL = "natural"
    JURIDICAL = "juridical"

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    document_type = Column(String, nullable=False)  # CC or NIT
    document_number = Column(String, nullable=False, unique=True)
    customer_type = Column(Enum(CustomerTypeEnum), nullable=False)
    contact_phone = Column(String)
    email = Column(String)
    
    sales = relationship("Sale", back_populates="customer")

class SaleUnitTypeEnum(enum.Enum):
    CUBETA = "cubeta"
    DOZEN = "dozen"

class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    date = Column(DateTime, default=datetime.now)
    subtotal = Column(Float, nullable=False)
    iva = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    
    customer = relationship("Customer", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale")

class SaleItem(Base):
    __tablename__ = "sale_items"
    
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"))
    egg_type = Column(Enum(EggTypeEnum), nullable=False)
    egg_size = Column(Enum(EggSizeEnum), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_type = Column(Enum(SaleUnitTypeEnum), nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    
    sale = relationship("Sale", back_populates="items")

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)