from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
from controllers.google_connect.google_drive_connection_routes.utils.files_drive_utils import json_serializable_documents, verificar_validez_valores
from database import get_client
from datetime import datetime
client = get_client()

singles_values_bp = Blueprint('single_values_routes', __name__, url_prefix="")

@singles_values_bp.route('/single_values', methods=['GET'])
def single_values():
	# Selecciona la base de datos KPI_PRAPS
	# Uso de la función
    db = client["Data_Loss"]
    collection = db["single_values"]
    
    #return all the documents in the collection
    documents = list(collection.find())
    try:
        documents = list(collection.find())
        result = json_serializable_documents(documents)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': f'Error al obtener el documento: {str(e)}'}), 500
    
@singles_values_bp.route('/single_values_by_name', methods=['GET'])
def single_values_by_name():
	# Selecciona la base de datos KPI_PRAPS
	# Uso de la función
    nombre = request.args.get('nombre')
    db = client["Data_Loss"]
    collection = db["single_values"]
    
    #return all the documents in the collection
    try:
        documents = list(collection.find({'nombre': nombre}))
        result = json_serializable_documents(documents)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': f'Error al obtener el documento: {str(e)}'}), 500
    
@singles_values_bp.route('/single_values_update', methods=['PUT'])
def update_field():
    db = client["Data_Loss"]
    collection = db["single_values"]
    id = request.args.get('id')
    try:
            updates = request.json
            
            # Verificar si el documento existe
            result = collection.find_one({"_id": ObjectId(id)})
            if not result:
                return jsonify({'error': 'Documento no encontrado'}), 404
            
            # Actualizar los campos en el documento
            for key, value in updates.items():
                result[key] = value
            
            # Validar el documento actualizado
            if result:
                # Aplicar las actualizaciones al documento en la base de datos
                collection.update_one({"_id": ObjectId(id)}, {"$set": updates})
                return jsonify({'message': 'Documento actualizado correctamente'}), 200
            else:
                return jsonify({'error': 'El documento actualizado no es válido'}), 400
    except Exception as e:
        return jsonify({'error': f'Error al actualizar el documento: {str(e)}'}), 500
@singles_values_bp.route('/insert_single_values', methods=['POST'])
def insert_single_values():
    db = client["Data_Loss"]
    collection = db["single_values"]
    try:
            new_document = request.json

            result = collection.insert_one(new_document)
            if result.inserted_id:
                return jsonify({'message': 'Documento insertado correctamente', 'id': str(result.inserted_id)}), 201
            else:
                return jsonify({'error': 'Error al insertar el documento'}), 500

    except Exception as e:
        return jsonify({'error': f'Error al insertar el documento: {str(e)}'}), 500
    
@singles_values_bp.route('/check_values', methods=['GET'])
def check_values():
    db = client["Data_Loss"]
    collection = db["single_values"]
    try:
        valores_por_vencer, valores_vencidos = verificar_validez_valores(collection)
        return jsonify({
            'valores_por_vencer': valores_por_vencer,
            'valores_vencidos': valores_vencidos
        }), 200
    except Exception as e:
        return jsonify({'error': f'Error al verificar los valores: {str(e)}'}), 500

@singles_values_bp.route('/single_values_update_new', methods=['PUT'])
def update_field_new():
    db = client["Data_Loss"]
    collection = db["single_values"]
    id = request.args.get('id')
    
    try:
        updates = request.json
        result = collection.find_one({"_id": ObjectId(id)})

        if not result:
            return jsonify({'error': 'Documento no encontrado'}), 404

        # Extraer la fecha y el valor nuevos de la solicitud
        new_value = updates.get("Value")
        new_date = updates.get("Fecha")
        
        # Crear una entrada de versión solo si new_value y new_date no son None
        if new_value is not None or new_date is not None:
            version_entry = {
                "Value": new_value,
                "Fecha": new_date,
                "updated_at": datetime.now().isoformat()
            }
            
            # Asegurarse de que la lista de versiones exista
            if "versions" not in result:
                result["versions"] = []
            result["versions"].append(version_entry)
        
        # Actualizar el documento con los nuevos datos
        collection.update_one({"_id": ObjectId(id)}, {"$set": updates})
        
        return jsonify({'message': 'Documento actualizado correctamente'}), 200
    except Exception as e:
        return jsonify({'error': f'Error al actualizar el documento: {str(e)}'}), 500
