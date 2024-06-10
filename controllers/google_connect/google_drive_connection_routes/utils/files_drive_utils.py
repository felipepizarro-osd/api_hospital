from dotenv import load_dotenv
from pymongo import MongoClient
import re
from datetime import datetime , timedelta
from bson import ObjectId
from database import get_client

load_dotenv()


client = get_client()

def get_latest_version_documents(database_name, collection_prefix, collec):
    print(f'Buscando documentos de la versión más reciente en la base de datos "{database_name}" con prefijo de colección "{collection_prefix}"...')
    # Selecciona la base de datos especificada
    db = client[database_name]

    # Define el patrón para encontrar las colecciones
    collection_pattern = re.compile(rf'^{collection_prefix}_(\d{{4}}-\d{{2}}-\d{{2}})_v(\d+)$')

    # Encuentra las colecciones que coinciden con el patrón
    matching_collections = db.list_collection_names(filter={'name': {'$regex': collection_pattern}})

    # Inicializa variables para la fecha y versión más recientes
    latest_date = None
    latest_version = None
    latest_documents = None

    # Itera sobre las colecciones encontradas
    for collection_name in matching_collections:
        match = collection_pattern.match(collection_name)
        if match:
            # Extrae la fecha y la versión de la coincidencia
            collection_date = datetime.strptime(match.group(1), '%Y-%m-%d')
            collection_version = int(match.group(2))
            
            # Si es la versión más reciente hasta ahora, guarda los documentos
            if latest_date is None or collection_date > latest_date or (collection_date == latest_date and collection_version > latest_version):
                latest_date = collection_date
                latest_version = collection_version
                latest_collection = db[collection_name]
                latest_documents = list(latest_collection.find())
    if collec:
        return latest_collection
    else:
        return latest_documents
def json_serializable_documents(documents):
    """
    Convierte los ObjectId en cadenas para que los documentos sean JSON serializables.
    Maneja tanto una lista de documentos como un solo documento.
    """
    if isinstance(documents, dict):
        # Si documents es un solo documento (dict)
        for key, value in documents.items():
            if isinstance(value, ObjectId):
                documents[key] = str(value)
    elif isinstance(documents, list):
        # Si documents es una lista de documentos
        for doc in documents:
            for key, value in doc.items():
                if isinstance(value, ObjectId):
                    doc[key] = str(value)
    return documents


def verificar_validez_valores(collection):
    current_date = datetime.now().strftime('%Y-%m-%d')
    current_date_obj = datetime.strptime(current_date, '%Y-%m-%d').date()
    valores_por_vencer = []
    valores_vencidos = []

    documentos = collection.find()
    for doc in documentos:
        fecha_vencimiento_str = doc.get("Fecha")
        
        if fecha_vencimiento_str:
            try:
                fecha_vencimiento = datetime.strptime(fecha_vencimiento_str, "%Y-%m-%d").date()
                if fecha_vencimiento < current_date_obj:
                    valores_vencidos.append(doc)
                elif (fecha_vencimiento - current_date_obj) <= timedelta(days=7):  # Por vencer en 7 días
                    valores_por_vencer.append(doc)
            except ValueError:
                # Maneja fechas que no están en el formato esperado
                print(f"Fecha en formato incorrecto en documento: {doc['_id']}")
                continue
        else:
            # Si no hay fecha de vencimiento, se puede decidir qué hacer
            print(f"Documento sin fecha de vencimiento: {doc['_id']}")
            continue
    
    return valores_por_vencer, valores_vencidos