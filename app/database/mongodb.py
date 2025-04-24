import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from typing import Dict, Any, List
from bson import ObjectId 

# Carga las variables del archivo .env
load_dotenv()

class MongoDB:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
            uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
            cls._instance.client = MongoClient(uri)
            cls._instance.db = cls._instance.client["avicola_llano_grande"]
        return cls._instance

    def get_collection(self, collection_name: str) -> Collection:
        return self.db[collection_name]



    # -------------------------------
    # Operaciones de inventario de huevos
    # -------------------------------

    def get_all_eggs(self) -> List[Dict[str, Any]]:
        return list(self.get_collection("eggs").find({}, {"_id": 0}))

    def upsert_egg(self, egg_data: Dict[str, Any]) -> bool:
        result = self.get_collection("eggs").update_one(
            {"type": egg_data["type"], "size": egg_data["size"]},
            {"$set": egg_data},
            upsert=True,
        )
        return result.acknowledged

    def delete_egg(self, egg_type: str, egg_size: str) -> bool:
        result = self.get_collection("eggs").delete_one({"type": egg_type, "size": egg_size})
        return result.deleted_count > 0

    def get_egg_inventory_by_type(self, egg_type: str) -> List[Dict[str, Any]]:
        return list(self.get_collection("eggs").find({"type": egg_type}, {"_id": 0}))

    def get_egg_stock_by_size(self, size: str) -> List[Dict[str, Any]]:
        return list(self.get_collection("eggs").find({"size": size}, {"_id": 0}))

    def get_egg_stock_by_type_and_size(self, egg_type: str, size: str) -> List[Dict[str, Any]]:
        return list(self.get_collection("eggs").find({"type": egg_type, "size": size}, {"_id": 0}))

    def get_total_egg_stock(self) -> int:
        total_stock = 0
        eggs = self.get_all_eggs()
        for egg in eggs:
            total_stock += egg.get("stock", 0)
        return total_stock

    # -------------------------------
    # Operaciones de clientes
    # -------------------------------

    def create_customer(self, customer_data: Dict[str, Any]) -> str:
        result = self.get_collection("customers").insert_one(customer_data)
        return str(result.inserted_id)

    def get_customer(self, document_number: str) -> Dict[str, Any]:
        return self.get_collection("customers").find_one({"document_number": document_number}, {"_id": 0})

    def update_customer(self, document_number: str, updated_data: Dict[str, Any]) -> bool:
        result = self.get_collection("customers").update_one(
            {"document_number": document_number}, {"$set": updated_data}
        )
        return result.modified_count > 0

    def delete_customer(self, document_number: str) -> bool:
        result = self.get_collection("customers").delete_one({"document_number": document_number})
        return result.deleted_count > 0

    # -------------------------------
    # Operaciones de ventas
    # -------------------------------

    def create_sale(self, sale_data: Dict[str, Any]) -> str:
        result = self.get_collection("sales").insert_one(sale_data)
        return str(result.inserted_id)

    def get_sales_by_customer(self, customer_document: str) -> List[Dict[str, Any]]:
        return list(self.get_collection("sales").find({"customer_document": customer_document}, {"_id": 0}))

    def get_all_sales(self) -> List[Dict[str, Any]]:
        return list(self.get_collection("sales").find({}, {"_id": 0}))

    def delete_sale(self, sale_id: str) -> bool:
        try:
            # Busca por el campo "id" en lugar de "_id"
            result = self.get_collection("sales").delete_one({"id": sale_id})
            return result.deleted_count > 0
        except Exception as e:
            # Maneja errores si el ID no es válido
            print(f"Error al eliminar la venta: {e}")
            return False

    def calculate_total_sales(self) -> float:
        total = 0.0
        sales = self.get_collection("sales").find({}, {"total": 1})
        for sale in sales:
            total += sale.get("total", 0)
        return total



