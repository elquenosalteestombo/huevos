from pymongo import MongoClient
from pymongo.collection import Collection
from typing import Dict, Any, List


class MongoDB:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
            cls._instance.client = MongoClient(
                "mongodb+srv://kamilo:kamilo@cluster0.zd6ncoj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
            )
            cls._instance.db = cls._instance.client["avicola_llano_grande"]
        return cls._instance

    def get_collection(self, collection_name: str) -> Collection:
        """Obtiene una colección de la base de datos."""
        return self.db[collection_name]

    # Operaciones de inventario de huevos
    def get_all_eggs(self) -> List[Dict[str, Any]]:
        """Obtiene todos los huevos del inventario."""
        return list(self.get_collection("eggs").find({}, {"_id": 0}))

    def upsert_egg(self, egg_data: Dict[str, Any]) -> bool:
        """Inserta o actualiza un huevo en el inventario."""
        result = self.get_collection("eggs").update_one(
            {"type": egg_data["type"], "size": egg_data["size"]},
            {"$set": egg_data},
            upsert=True,
        )
        return result.acknowledged

    def delete_egg(self, egg_type: str, egg_size: str) -> bool:
        """Elimina un huevo del inventario."""
        result = self.get_collection("eggs").delete_one({"type": egg_type, "size": egg_size})
        return result.deleted_count > 0

    # Operaciones de clientes
    def create_customer(self, customer_data: Dict[str, Any]) -> str:
        """Crea un nuevo cliente."""
        result = self.get_collection("customers").insert_one(customer_data)
        return str(result.inserted_id)

    def get_customer(self, document_number: str) -> Dict[str, Any]:
        """Obtiene un cliente por su número de documento."""
        return self.get_collection("customers").find_one({"document_number": document_number}, {"_id": 0})

    def update_customer(self, document_number: str, updated_data: Dict[str, Any]) -> bool:
        """Actualiza la información de un cliente."""
        result = self.get_collection("customers").update_one(
            {"document_number": document_number}, {"$set": updated_data}
        )
        return result.modified_count > 0

    def delete_customer(self, document_number: str) -> bool:
        """Elimina un cliente."""
        result = self.get_collection("customers").delete_one({"document_number": document_number})
        return result.deleted_count > 0

    # Operaciones de ventas
    def create_sale(self, sale_data: Dict[str, Any]) -> str:
        """Crea una nueva venta."""
        result = self.get_collection("sales").insert_one(sale_data)
        return str(result.inserted_id)

    def get_sales_by_customer(self, customer_document: str) -> List[Dict[str, Any]]:
        """Obtiene todas las ventas de un cliente."""
        return list(self.get_collection("sales").find({"customer_document": customer_document}, {"_id": 0}))

    def get_all_sales(self) -> List[Dict[str, Any]]:
        """Obtiene todas las ventas."""
        return list(self.get_collection("sales").find({}, {"_id": 0}))

    def delete_sale(self, sale_id: str) -> bool:
        """Elimina una venta."""
        result = self.get_collection("sales").delete_one({"_id": sale_id})
        return result.deleted_count > 0

    # Funciones adicionales
    def calculate_total_sales(self) -> float:
        """Calcula el total de todas las ventas."""
        total = 0.0
        sales = self.get_collection("sales").find({}, {"total": 1})
        for sale in sales:
            total += sale.get("total", 0)
        return total

    def get_total_egg_stock(self) -> int:
        """Calcula el stock total de huevos."""
        total_stock = 0
        eggs = self.get_all_eggs()
        for egg in eggs:
            total_stock += egg.get("stock", 0)
        return total_stock

    def get_egg_inventory_by_type(self, egg_type: str) -> List[Dict[str, Any]]:
        """Obtiene el inventario de huevos por tipo."""
        return list(self.get_collection("eggs").find({"type": egg_type}, {"_id": 0}))

    def get_egg_stock_by_size(self, size: str) -> List[Dict[str, Any]]:
        """Obtiene el inventario de huevos por tamaño."""
        return list(self.get_collection("eggs").find({"size": size}, {"_id": 0}))

    def get_egg_stock_by_type_and_size(self, egg_type: str, size: str) -> List[Dict[str, Any]]:
        """Obtiene el inventario de huevos por tipo y tamaño."""
        return list(self.get_collection("eggs").find({"type": egg_type, "size": size}, {"_id": 0}))


# Ejemplo de uso
if __name__ == "__main__":
    db_mongo = MongoDB()

    # Crear un nuevo cliente
    customer_data = {
        "name": "Jane Doe",
        "document_type": "CC",
        "document_number": "987654321",
        "contact_phone": "123456789",
        "email": "jane.doe@example.com",
    }
    customer_id = db_mongo.create_customer(customer_data)
    print(f"Cliente creado con ID: {customer_id}")

    # Crear un nuevo huevo
    egg_data = {"type": "red", "size": "A", "stock": 50}
    db_mongo.upsert_egg(egg_data)

    # Obtener todos los huevos
    eggs = db_mongo.get_all_eggs()
    print(f"Huevos en inventario: {eggs}")

    # Crear una nueva venta
    sale_data = {
        "customer_document": "987654321",
        "items": [{"egg_type": "red", "egg_size": "A", "quantity": 2, "unit_price": 12.0}],
        "subtotal": 24.0,
        "iva": 1.2,
        "total": 25.2,
    }
    sale_id = db_mongo.create_sale(sale_data)
    print(f"Venta creada con ID: {sale_id}")

    # Obtener todas las ventas
    sales = db_mongo.get_all_sales()
    print(f"Ventas registradas: {sales}")