from flask import Blueprint, jsonify, request
from controllers.google_connect.google_drive_connection_routes.utils.files_drive_utils import get_latest_version_documents, json_serializable_documents
from controllers.google_connect.google_drive_connection_routes.utils.json_utils import validar_json, corregir_y_validar_json
from bson import ObjectId
from database import get_client

client = get_client()

metas_sanitarias_18_bp = Blueprint('metas_sanitarias_18_routes', __name__, url_prefix="")

@metas_sanitarias_18_bp.route('/Kpi_Metas_18_Values', methods=['GET'])
def Kpi_Metas_18_Values():
	# Selecciona la base de datos KPI_PRAPS
		# Uso de la función
	latest_documents = get_latest_version_documents("KPI_METAS_SANITARIAS_18", "Metas_Sanitarias_18",False)
	if latest_documents:
		# Convierte los ObjectId en cadenas para que los documentos sean JSON serializables
		latest_documents = json_serializable_documents(latest_documents)
     
		print("Documentos de la versión más reciente:")
		#for document in latest_documents:
		#	print(document)
		return jsonify(latest_documents), 200
	else:
		print("No se encontraron documentos.")
		return jsonify({'error': 'No se encontraron documentos.'}), 404
@metas_sanitarias_18_bp.route('/insert_clave_referencia_metas_18', methods=['POST'])
def insert_clave_referencia_Metas_18():
    db = client["Clave_referencia"]
    collection = db["Metas_Sanitarias_18"]
    nueva_clave_referencia = request.json

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
        valido, mensaje_error, documento_corregido = corregir_y_validar_json(request.json)
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
        
@metas_sanitarias_18_bp.route('/update_clave_referencia_metas_18', methods=['PUT'])
def update_clave_referencia_Metas_18():
    id = request.args.get('id')
    updates = request.json
    db = client["Clave_referencia"]
    collection = db["Metas_Sanitarias_18"]
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
            collection.update_one({"_id": ObjectId(id)}, {"$set": result})
            return jsonify({'message': 'Clave-referencia actualizada correctamente'}), 200
        else:
            return jsonify({'error': 'El documento actualizado no es válido'}), 400

    except Exception as e:
        return jsonify({'error': f'Error al actualizar la clave-referencia: {str(e)}'}), 500