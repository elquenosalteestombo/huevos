from pymongo import MongoClient
from pymongo.collection import Collection
from typing import Dict, Any, List

class MongoDB:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
            cls._instance.client = MongoClient("mongodb://localhost:27017/")
            cls._instance.db = cls._instance.client["avicola_llano_grande"]
        return cls._instance
    
    def get_collection(self, collection_name: str) -> Collection:
        return self.db[collection_name]
    
    # Egg inventory operations
    def get_all_eggs(self) -> List[Dict[str, Any]]:
        return list(self.get_collection("eggs").find({}, {"_id": 0}))
    
    def get_egg(self, egg_type: str, egg_size: str) -> Dict[str, Any]:
        return self.get_collection("eggs").find_one(
            {"type": egg_type, "size": egg_size},
            {"_id": 0}
        )
    
    def upsert_egg(self, egg_data: Dict[str, Any]) -> bool:
        result = self.get_collection("eggs").update_one(
            {"type": egg_data["type"], "size": egg_data["size"]},
            {"$set": egg_data},
            upsert=True
        )
        return result.acknowledged
    
    def update_egg_stock(self, egg_type: str, egg_size: str, quantity: int) -> bool:
        result = self.get_collection("eggs").update_one(
            {"type": egg_type, "size": egg_size},
            {"$inc": {"stock": quantity}}
        )
        return result.acknowledged and result.modified_count > 0
    
    # Customer operations
    def create_customer(self, customer_data: Dict[str, Any]) -> str:
        result = self.get_collection("customers").insert_one(customer_data)
        return str(result.inserted_id)
    
    def get_customer(self, document_number: str) -> Dict[str, Any]:
        return self.get_collection("customers").find_one(
            {"document_number": document_number},
            {"_id": 0}
        )
    
    # Sales operations
    def create_sale(self, sale_data: Dict[str, Any]) -> str:
        result = self.get_collection("sales").insert_one(sale_data)
        return str(result.inserted_id)
    
    def get_sale(self, sale_id: str) -> Dict[str, Any]:
        return self.get_collection("sales").find_one(
            {"id": sale_id},
            {"_id": 0}
        )