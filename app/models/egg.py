from pydantic import BaseModel
from enum import Enum
from typing import Optional

class EggType(str, Enum):
    RED = "red"
    WHITE = "white"

class EggSize(str, Enum):
    A = "A"
    AA = "AA"
    B = "B"
    EXTRA = "EXTRA"

class Egg(BaseModel):
    type: EggType
    size: EggSize
    stock: int = 0  # Current quantity in stock
    
    def get_price_per_unit(self) -> float:
        # Price per egg based on type and size
        price_table = {
            (EggType.RED, EggSize.A): 400 / 30,      # Price per egg (400 per cubeta of 30)
            (EggType.RED, EggSize.AA): 450 / 30,
            (EggType.RED, EggSize.B): 380 / 30,
            (EggType.RED, EggSize.EXTRA): 500 / 30,
            (EggType.WHITE, EggSize.A): 380 / 30,
            (EggType.WHITE, EggSize.AA): 420 / 30,
            (EggType.WHITE, EggSize.B): 370 / 30,
            (EggType.WHITE, EggSize.EXTRA): 480 / 30,
        }
        return price_table[(self.type, self.size)]

    def get_price_per_cubeta(self) -> float:
        # Price per cubeta (30 eggs)
        return self.get_price_per_unit() * 30
    
    def get_price_per_dozen(self) -> float:
        # Price per dozen (12 eggs)
        return self.get_price_per_unit() * 12