from pymongo import MongoClient
from pymongo.collection import Collection
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Dict, Any, List

# Configuración de SQLAlchemy
Base = declarative_base()
engine = create_engine('sqlite:///example.db')
Session = sessionmaker(bind=engine)

# Modelo de SQLAlchemy para Clientes
class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    document_type = Column(String)
    document_number = Column(String, unique=True)
    contact_phone = Column(String)
    email = Column(String)

Base.metadata.create_all(engine)

# Clase para MongoDB
class MongoDB:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
            cls._instance.client = MongoClient("mongodb+srv://apoxelados22:jorgeandres22@cluster0.p5okp3y.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
            cls._instance.db = cls._instance.client["avicola_llano_grande"]
        return cls._instance
    
    def get_collection(self, collection_name: str) -> Collection:
        return self.db[collection_name]
    
    # Operaciones de inventario de huevos
    def get_all_eggs(self) -> List[Dict[str, Any]]:
        return list(self.get_collection("eggs").find({}, {"_id": 0}))
    
    def upsert_egg(self, egg_data: Dict[str, Any]) -> bool:
        result = self.get_collection("eggs").update_one(
            {"type": egg_data["type"], "size": egg_data["size"]},
            {"$set": egg_data},
            upsert=True
        )
        return result.acknowledged
    
    # Operaciones de clientes
    def create_customer(self, customer_data: Dict[str, Any]) -> str:
        result = self.get_collection("customers").insert_one(customer_data)
        return str(result.inserted_id)
    
    # Operaciones de ventas
    def create_sale(self, sale_data: Dict[str, Any]) -> str:
        result = self.get_collection("sales").insert_one(sale_data)
        return str(result.inserted_id)

# Ejemplo de uso
if __name__ == "__main__":
    # Inicializar MongoDB
    db_mongo = MongoDB()

    # Crear un nuevo cliente en SQLAlchemy
    new_customer = Customer(name="Jane Doe", document_type="CC", document_number="987654321", contact_phone="123456789", email="jane.doe@example.com")
    session = Session()
    session.add(new_customer)
    session.commit()
    print(f"Cliente creado con ID: {new_customer.id}")

    # Crear un nuevo cliente en MongoDB
    mongo_customer_data = {
        "name": "Jane Doe",
        "document_type": "CC",
        "document_number": "987654321",
        "contact_phone": "123456789",
        "email": "jane.doe@example.com"
    }
    mongo_customer_id = db_mongo.create_customer(mongo_customer_data)
    print(f"Cliente creado en MongoDB con ID: {mongo_customer_id}")

    # Crear un nuevo huevo
    egg_data = {
        "type": "red",
        "size": "A",
        "stock": 50
    }
    db_mongo.upsert_egg(egg_data)

    # Obtener todos los huevos
    eggs = db_mongo.get_all_eggs()
    print(f"Huevos en inventario: {eggs}")

    # Crear una nueva venta
    sale_data = {
        "customer_id": mongo_customer_id,
        "subtotal": 100.0,
        "iva": 5.0,
        "total": 105.0,
        "items": []
    }
    sale_id = db_mongo.create_sale(sale_data)
    print(f"Venta creada con ID: {sale_id}")

    # Mostrar todos los clientes en MongoDB
    all_customers = db_mongo.get_collection("customers").find({}, {"_id": 0})
    print("Clientes en MongoDB:")
    for customer in all_customers:
        print(customer)

    # Mostrar todas las ventas en MongoDB
    all_sales = db_mongo.get_collection("sales").find({}, {"_id": 0})
    print("Ventas en MongoDB:")
    for sale in all_sales:
        print(sale)

    # Mostrar todos los huevos en MongoDB
    all_eggs = db_mongo.get_all_eggs()
    print("Huevos en MongoDB:")
    for egg in all_eggs:
        print(egg)

    # Función para eliminar un cliente
    def delete_customer(customer_id: str) -> bool:
        result = db_mongo.get_collection("customers").delete_one({"document_number": customer_id})
        return result.deleted_count > 0

    # Ejemplo de eliminación de un cliente
    if delete_customer("987654321"):
        print("Cliente eliminado exitosamente.")
    else:
        print("No se pudo eliminar el cliente.")

    # Función para actualizar un huevo
    def update_egg(egg_data: Dict[str, Any]) -> bool:
        return db_mongo.upsert_egg(egg_data)

    # Ejemplo de actualización de un huevo
    updated_egg_data = {
        "type": "red",
        "size": "A",
        "stock": 60  # Actualizando el stock
    }
    if update_egg(updated_egg_data):
        print("Huevo actualizado exitosamente.")
    else:
        print("No se pudo actualizar el huevo.")

    # Función para obtener una venta por ID
    def get_sale_by_id(sale_id: str) -> Dict[str, Any]:
        return db_mongo.get_collection("sales").find_one({"_id": sale_id}, {"_id": 0})

    # Ejemplo de obtención de una venta
    sale_info = get_sale_by_id(sale_id)
    if sale_info:
        print("Detalles de la venta:", sale_info)
    else:
        print("Venta no encontrada.")

    # Función para obtener un cliente por ID
    def get_customer_by_id(customer_id: str) -> Dict[str, Any]:
        return db_mongo.get_collection("customers").find_one({"document_number": customer_id}, {"_id": 0})

    # Ejemplo de obtención de un cliente
    customer_info = get_customer_by_id("987654321")
    if customer_info:
        print("Detalles del cliente:", customer_info)
    else:
        print("Cliente no encontrado.")

    # Función para listar todas las ventas de un cliente
    def get_sales_by_customer(customer_id: str) -> List[Dict[str, Any]]:
        return list(db_mongo.get_collection("sales").find({"customer_id": customer_id}, {"_id": 0}))

    # Ejemplo de obtención de ventas por cliente
    customer_sales = get_sales_by_customer(mongo_customer_id)
    print(f"Ventas del cliente {mongo_customer_id}:")
    for sale in customer_sales:
        print(sale)

    # Función para calcular el total de ventas
    def calculate_total_sales() -> float:
        total = 0.0
        all_sales = db_mongo.get_collection("sales").find({}, {"total": 1})
        for sale in all_sales:
            total += sale.get("total", 0)
        return total

    # Ejemplo de cálculo del total de ventas
    total_sales = calculate_total_sales()
    print(f"Total de ventas: {total_sales}")

    # Función para obtener el inventario de huevos
    def get_egg_inventory() -> List[Dict[str, Any]]:
        return db_mongo.get_all_eggs()

    # Ejemplo de obtención del inventario de huevos
    egg_inventory = get_egg_inventory()
    print("Inventario de huevos:")
    for egg in egg_inventory:
        print(egg)

    # Función para eliminar un huevo
    def delete_egg(egg_data: Dict[str, Any]) -> bool:
        result = db_mongo.get_collection("eggs").delete_one({"type": egg_data["type"], "size": egg_data["size"]})
        return result.deleted_count > 0

    # Ejemplo de eliminación de un huevo
    if delete_egg({"type": "red", "size": "A"}):
        print("Huevo eliminado exitosamente.")
    else:
        print("No se pudo eliminar el huevo.")

    # Función para listar todos los clientes
    def list_all_customers() -> List[Dict[str, Any]]:
        return list(db_mongo.get_collection("customers").find({}, {"_id": 0}))

    # Ejemplo de listado de todos los clientes
    all_customers = list_all_customers()
    print("Lista de todos los clientes:")
    for customer in all_customers:
        print(customer)

    # Función para contar el número de clientes
    def count_customers() -> int:
        return db_mongo.get_collection("customers").count_documents({})

    # Ejemplo de conteo de clientes
    total_customers = count_customers()
    print(f"Número total de clientes: {total_customers}")

    # Función para contar el número de ventas
    def count_sales() -> int:
        return db_mongo.get_collection("sales").count_documents({})

    # Ejemplo de conteo de ventas
    total_sales_count = count_sales()
    print(f"Número total de ventas: {total_sales_count}")

    # Función para obtener el stock total de huevos
    def get_total_egg_stock() -> int:
        total_stock = 0
        all_eggs = db_mongo.get_all_eggs()
        for egg in all_eggs:
            total_stock += egg.get("stock", 0)
        return total_stock

    # Ejemplo de obtención del stock total de huevos
    total_egg_stock = get_total_egg_stock()
    print(f"Stock total de huevos: {total_egg_stock}")

    # Función para obtener detalles de una venta por ID
    def get_sale_details(sale_id: str) -> Dict[str, Any]:
        return db_mongo.get_collection("sales").find_one({"_id": sale_id}, {"_id": 0})

    # Ejemplo de obtención de detalles de una venta
    sale_details = get_sale_details(sale_id)
    if sale_details:
        print("Detalles de la venta:", sale_details)
    else:
        print("Detalles de la venta no encontrados.")

    # Función para obtener detalles de un cliente por ID
    def get_customer_details(customer_id: str) -> Dict[str, Any]:
        return db_mongo.get_collection("customers").find_one({"document_number": customer_id}, {"_id": 0})

    # Ejemplo de obtención de detalles de un cliente
    customer_details = get_customer_details("987654321")
    if customer_details:
        print("Detalles del cliente:", customer_details)
    else:
        print("Detalles del cliente no encontrados.")

    # Función para listar todas las ventas
    def list_all_sales() -> List[Dict[str, Any]]:
        return list(db_mongo.get_collection("sales").find({}, {"_id": 0}))

    # Ejemplo de listado de todas las ventas
    all_sales_list = list_all_sales()
    print("Lista de todas las ventas:")
    for sale in all_sales_list:
        print(sale)

    # Función para calcular el promedio de ventas
    def calculate_average_sales() -> float:
        total = calculate_total_sales()
        total_count = count_sales()
        return total / total_count if total_count > 0 else 0.0

    # Ejemplo de cálculo del promedio de ventas
    average_sales = calculate_average_sales()
    print(f"Promedio de ventas: {average_sales}")

    # Función para obtener el inventario de huevos por tipo
    def get_egg_inventory_by_type(egg_type: str) -> List[Dict[str, Any]]:
        return list(db_mongo.get_collection("eggs").find({"type": egg_type}, {"_id": 0}))

    # Ejemplo de obtención del inventario de huevos por tipo
    red_egg_inventory = get_egg_inventory_by_type("red")
    print("Inventario de huevos rojos:")
    for egg in red_egg_inventory:
        print(egg)

    # Función para actualizar la información de un cliente
    def update_customer(customer_id: str, updated_data: Dict[str, Any]) -> bool:
        result = db_mongo.get_collection("customers").update_one({"document_number": customer_id}, {"$set": updated_data})
        return result.modified_count > 0

    # Ejemplo de actualización de un cliente
    updated_customer_data = {
        "contact_phone": "987654321",
        "email": "jane.new@example.com"
    }
    if update_customer("987654321", updated_customer_data):
        print("Cliente actualizado exitosamente.")
    else:
        print("No se pudo actualizar el cliente.")

    # Función para eliminar una venta
    def delete_sale(sale_id: str) -> bool:
        result = db_mongo.get_collection("sales").delete_one({"_id": sale_id})
        return result.deleted_count > 0

    # Ejemplo de eliminación de una venta
    if delete_sale(sale_id):
        print("Venta eliminada exitosamente.")
    else:
        print("No se pudo eliminar la venta.")

    # Función para obtener el total de ventas por cliente
    def get_total_sales_by_customer(customer_id: str) -> float:
        total = 0.0
        sales = get_sales_by_customer(customer_id)
        for sale in sales:
            total += sale.get("total", 0)
        return total

    # Ejemplo de obtención del total de ventas por cliente
    total_sales_for_customer = get_total_sales_by_customer(mongo_customer_id)
    print(f"Total de ventas para el cliente {mongo_customer_id}: {total_sales_for_customer}")

    # Función para listar todos los huevos por tipo
    def list_eggs_by_type(egg_type: str) -> List[Dict[str, Any]]:
        return db_mongo.get_collection("eggs").find({"type": egg_type}, {"_id": 0})

    # Ejemplo de listado de huevos por tipo
    eggs_of_type_red = list_eggs_by_type("red")
    print("Huevos de tipo rojo:")
    for egg in eggs_of_type_red:
        print(egg)

    # Función para contar el stock de un tipo específico de huevo
    def count_stock_by_egg_type(egg_type: str) -> int:
        eggs = list_eggs_by_type(egg_type)
        return sum(egg.get("stock", 0) for egg in eggs)

    # Ejemplo de conteo de stock de huevos rojos
    red_egg_stock_count = count_stock_by_egg_type("red")
    print(f"Stock total de huevos rojos: {red_egg_stock_count}")

    # Función para obtener el promedio de stock de huevos
    def calculate_average_egg_stock() -> float:
        total_stock = get_total_egg_stock()
        total_types = len(db_mongo.get_all_eggs())
        return total_stock / total_types if total_types > 0 else 0.0

    # Ejemplo de cálculo del promedio de stock de huevos
    average_egg_stock = calculate_average_egg_stock()
    print(f"Promedio de stock de huevos: {average_egg_stock}")

    # Función para obtener el historial de ventas
    def get_sales_history() -> List[Dict[str, Any]]:
        return list(db_mongo.get_collection("sales").find({}, {"_id": 0}))

    # Ejemplo de obtención del historial de ventas
    sales_history = get_sales_history()
    print("Historial de ventas:")
    for sale in sales_history:
        print(sale)

    # Función para obtener el total de clientes
    def get_total_customers() -> int:
        return count_customers()

    # Ejemplo de obtención del total de clientes
    total_customers_count = get_total_customers()
    print(f"Número total de clientes: {total_customers_count}")

    # Función para obtener el total de ventas
    def get_total_sales_count() -> int:
        return count_sales()

    # Ejemplo de obtención del total de ventas
    total_sales_count = get_total_sales_count()
    print(f"Número total de ventas: {total_sales_count}")

    # Función para obtener el stock de huevos por tamaño
    def get_egg_stock_by_size(size: str) -> List[Dict[str, Any]]:
        return list(db_mongo.get_collection("eggs").find({"size": size}, {"_id": 0}))

    # Ejemplo de obtención del stock de huevos por tamaño
    egg_stock_size_a = get_egg_stock_by_size("A")
    print("Stock de huevos tamaño A:")
    for egg in egg_stock_size_a:
        print(egg)

    # Función para obtener el stock de huevos por tipo y tamaño
    def get_egg_stock_by_type_and_size(egg_type: str, size: str) -> List[Dict[str, Any]]:
        return list(db_mongo.get_collection("eggs").find({"type": egg_type, "size": size}, {"_id": 0}))

    # Ejemplo de obtención del stock de huevos rojos tamaño A
    red_egg_stock_size_a = get_egg_stock_by_type_and_size("red", "A")
    print("Stock de huevos rojos tamaño A:")
    for egg in red_egg_stock_size_a:
        print(egg)

    # Función para obtener el total de ventas por tipo de huevo
    def get_total_sales_by_egg_type(egg_type: str) -> float:
        total = 0.0
        sales = db_mongo.get_collection("sales").find({}, {"items": 1})
        for sale in sales:
            for item in sale.get("items", []):
                if item.get("type") == egg_type:
                    total += sale.get("total", 0)
        return total
