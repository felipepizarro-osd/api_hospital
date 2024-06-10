from flask import Blueprint, jsonify, request
from bson import ObjectId
from pymongo.errors import PyMongoError
import json
from controllers.google_connect.google_drive_connection_routes.utils.files_drive_utils import get_latest_version_documents, json_serializable_documents
from urllib.parse import unquote
from controllers.google_connect.google_drive_connection_routes.utils.json_utils import validar_json, corregir_y_validar_json, calculate_program_compliance, procesar_single_values, insertar_kpi_en_mongodb, get_kpi_historical_data, get_praps_historical_data
from controllers.google_connect.google_drive_connection_routes.utils.props_metas_praps import procesar_PROPS_PRAPS, procesar_METAS_PRAPS

from database import get_client

praps_routes_bp = Blueprint('praps_routes', __name__, url_prefix="")

client = get_client()
@praps_routes_bp.route('/insert_clave_referencia', methods=['POST'])
def insert_clave_referencia_praps():
    db = client["Clave_referencia"]
    collection = db["Praps_Primario"]
    db_single_values = client["Data_Loss"]
    collection_single_values = db_single_values["single_values"]
    
    # Obtener el JSON del cuerpo de la solicitud
    json_data = request.get_json()  # Usar get_json() para asegurarse de que se deserialice correctamente
    
    if isinstance(json_data, str):
        json_data = json.loads(json_data)  # Deserializar si aún es un string
    
    print(f"JSON DATA: {json_data}")

    # Procesar el JSON para identificar datos faltantes
    datos_faltantes = procesar_single_values([json_data])
    
    # Insertar datos faltantes en la colección single_values
    if datos_faltantes:
        collection_single_values.insert_many(datos_faltantes)
    
    nueva_clave_referencia = json_data  # Usar json_data que ya hemos deserializado

    if validar_json(nueva_clave_referencia):
        try:
            resultado = collection.insert_one(nueva_clave_referencia)
            if resultado.inserted_id:
                return jsonify({'message': 'Clave-referencia insertada correctamente'}), 201
            else:
                return jsonify({'error': 'Error al insertar la clave-referencia'}), 500
        except Exception as e:
            return jsonify({'error': f'Error al insertar la clave-referencia: {str(e)}'}), 500
    else:
        valido, mensaje_error, documento_corregido = corregir_y_validar_json(nueva_clave_referencia)
        if valido:
            try:
                resultado = collection.insert_one(documento_corregido)
                if resultado.inserted_id:
                    return jsonify({'message': 'Clave-referencia insertada correctamente'}), 201
                else:
                    return jsonify({'error': 'Error al insertar la clave-referencia'}), 500
            except Exception as e:
                return jsonify({'error': f'Error al insertar la clave-referencia: {str(e)}'}), 500
        else:
            return jsonify({'error': mensaje_error, 'documento_corregido': documento_corregido}), 400

        
@praps_routes_bp.route('/update_clave_referencia_praps', methods=['PUT'])
def update_clave_referencia_praps():
    id = request.args.get('id')
    updates = request.json
    db = client["Clave_referencia"]
    collection = db["Praps_Primario"]
    try:
        # Busca el documento por ID
        result = collection.find_one({"_id": ObjectId(id)})
        if not result:
            return jsonify({'error': 'Clave-referencia no encontrada'}), 404
        
        # Aplica las actualizaciones al documento
        for key, value in updates.items():
            result[key] = value
        
        # Valida el documento actualizado
        if validar_json(result):
            # Actualiza el documento en la base de datos
            update_result = collection.update_one({"_id": ObjectId(id)}, {"$set": result})
            # Genera la respuesta en función del resultado de la actualización
            if update_result.matched_count == 0:
                return jsonify({'message': 'No se encontraron documentos que coincidan con el filtro.'}), 404
            elif update_result.modified_count == 0:
                return jsonify({'message': 'El documento ya tiene los valores especificados.'}), 200
            else:
                return jsonify({
                    'message': 'Documento actualizado exitosamente.',
                    'matched_count': update_result.matched_count,
                    'modified_count': update_result.modified_count
                }), 200
        else:
            return jsonify({'error': 'El documento actualizado no es válido'}), 400

    except PyMongoError as e:
        return jsonify({'error': f'Error al actualizar el documento: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error inesperado: {str(e)}'}), 500
@praps_routes_bp.route('/update_clave_referencia_PRAPS', methods=['PUT'])
def update_clave_referencia_PRAPS():
    id = request.args.get('id')
    updates = request.json
    db = client["Clave_referencia"]
    collection = db["Praps_Primario"]
    
    try:
        # Busca el documento por ID
        result = collection.find_one({"_id": ObjectId(id)})
        if not result:
            return jsonify({'error': 'Clave-referencia no encontrada'}), 404

        # Aplica las actualizaciones específicas al `denominator` y `numerator` dentro de `formula`
        if "formula" in result:
            formula = result["formula"]
            for formula_item in formula:
                if "denominator" in updates:
                    update_nested_fields(formula_item["denominator"], updates["denominator"])
                if "numerator" in updates:
                    update_nested_fields(formula_item["numerator"], updates["numerator"])

        # Aplica otras actualizaciones al documento
        for key, value in updates.items():
            if key != "denominator" and key != "numerator":
                result[key] = value

        # Valida el documento actualizado
        if validar_json(result):
            # Actualiza el documento en la base de datos
            update_result = collection.update_one({"_id": ObjectId(id)}, {"$set": result})
            # Genera la respuesta en función del resultado de la actualización
            if update_result.matched_count == 0:
                return jsonify({'message': 'No se encontraron documentos que coincidan con el filtro.'}), 404
            elif update_result.modified_count == 0:
                return jsonify({'message': 'El documento ya tiene los valores especificados.'}), 200
            else:
                return jsonify({
                    'message': 'Documento actualizado exitosamente.',
                    'matched_count': update_result.matched_count,
                    'modified_count': update_result.modified_count
                }), 200
        else:
            return jsonify({'error': 'El documento actualizado no es válido'}), 400

    except PyMongoError as e:
        return jsonify({'error': f'Error al actualizar el documento: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error inesperado: {str(e)}'}), 500
@praps_routes_bp.route('/delete_clave_referencia_praps', methods=['DELETE'])
def delete_clave_referencia_praps():
    id = request.args.get('id')
    db = client["Clave_referencia"]
    collection = db["Praps_Primario"]
    try:
        # Elimina el documento por ID
        delete_result = collection.delete_one({"_id": ObjectId(id)})
        # Genera la respuesta en función del resultado de la eliminación
        if delete_result.deleted_count == 0:
            return jsonify({'message': 'No se encontraron documentos que coincidan con el filtro.'}), 404
        else:
            return jsonify({
                'message': 'Documento eliminado exitosamente.',
                'deleted_count': delete_result.deleted_count
            }), 200
    except PyMongoError as e:
        return jsonify({'error': f'Error al eliminar el documento: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error inesperado: {str(e)}'}), 500

@praps_routes_bp.route('/assing_metas', methods=['POST'])
def assing_metas():
    db = client["Clave_referencia"]
    collection = db["Praps_Primario"]
    try:
        # Obtener todos los documentos de Praps Primario
        documents = list(collection.find())

        # Procesar los documentos para asignar metas
        kpi_documentos = procesar_PROPS_PRAPS(documents)
        metas_praps = procesar_METAS_PRAPS(documents)
        # Insertar los documentos procesados en la colección de KPI
        if insertar_kpi_en_mongodb(kpi_documentos,"PROPS_KPI_PRAPS") and insertar_kpi_en_mongodb(metas_praps,"METAS_Y_OBJETIVOS_PRAPS"):
            return jsonify({'message': 'Metas asignadas correctamente'}), 200
        else:
            return jsonify({'error': 'Error al asignar metas'}), 500

    except PyMongoError as e:
        return jsonify({'error': f'Error al procesar los documentos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error inesperado: {str(e)}'}), 500
@praps_routes_bp.route('/get_kpi_historical_data_praps', methods=['GET'])
def get_kpi_historical_data_route():
    database_name = 'KPI_PRAPS'
    collection_prefix = "Praps"
    kpi_name = request.args.get('kpi_name')

    if not kpi_name:
        return jsonify({'error': 'Faltan parámetros necesarios: database_name, collection_prefix, kpi_name'}), 400

    try:
        historical_data = get_kpi_historical_data(database_name, collection_prefix, kpi_name)
        return jsonify(historical_data), 200
    except Exception as e:
        return jsonify({'error': f'Error al obtener los datos históricos: {str(e)}'}), 500
    
@praps_routes_bp.route('/get_general_historical_data_praps', methods=['GET'])
def get_general_historical_data_route():
    database_name = 'GENERAL'
    collection_prefix = "GENERAL_PROGRAMS_PRAPS"

    try:
        historical_data = get_praps_historical_data(database_name, collection_prefix)
        return jsonify(historical_data), 200
    except Exception as e:
        return jsonify({'error': f'Error al obtener los datos históricos: {str(e)}'}), 500
@praps_routes_bp.route('/get_PROPS', methods=['GET'])
def get_PROPS():
    db = client["KPI_GOALS"]
    collection = db["PROPS_KPI_PRAPS"]
    try:
        # Obtener todos los documentos de Praps Primario
        documents = json_serializable_documents(list(collection.find()))
        return jsonify(documents), 200
    except PyMongoError as e:
        return jsonify({'error': f'Error al obtener los documentos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error inesperado: {str(e)}'}), 500

@praps_routes_bp.route('/get_kpi_by_id', methods=['GET'])
def get_kpi_by_id():
    id = request.args.get('id')
    collection = get_latest_version_documents("KPI_GOALS", "PROPS_KPI_PRAPS", True)
    try:
        document = collection.find_one({"_id": ObjectId(id)})
        print(document)
        if document:
            result = json_serializable_documents(document)
            return jsonify(result), 200
        else:
            return jsonify({'error': 'Documento no encontrado'}), 404
    except PyMongoError as e:
        return jsonify({'error': f'Error al obtener el KPI: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error inesperado: {str(e)}'}), 500
    
def update_nested_fields(nested_list, updates_list):
    for update in updates_list:
        name_to_update = update.get("Name")
        if not name_to_update:
            return jsonify({'error': 'Se requiere el campo "Name" para actualizar.'}), 400
        for item in nested_list:
            if item.get("Name") == name_to_update:
                for key, value in update.items():
                    if key != "Name":
                        item[key] = value
