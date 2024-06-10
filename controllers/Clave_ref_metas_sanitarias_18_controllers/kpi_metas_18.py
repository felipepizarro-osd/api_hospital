from flask import Blueprint, jsonify, request
from controllers.google_connect.google_drive_connection_routes.utils.files_drive_utils import get_latest_version_documents, json_serializable_documents
from controllers.google_connect.google_drive_connection_routes.utils.json_utils import validar_json, corregir_y_validar_json
from bson import ObjectId
from controllers.google_connect.google_drive_connection_routes.utils.json_utils import get_kpi_historical_data, get_Metas_historical_data
from database import get_client
from pymongo.errors import PyMongoError

client = get_client()

kpi_metas_sanitarias_18_bp = Blueprint('kpi_metas_sanitarias_18_routes', __name__, url_prefix="")

@kpi_metas_sanitarias_18_bp.route('/Kpi_Metas_18_Values', methods=['GET'])
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

@kpi_metas_sanitarias_18_bp.route('/get_kpi_historical_data_metas_18', methods=['GET'])
def get_kpi_historical_data_route():
    database_name = 'KPI_METAS_SANITARIAS_18'
    collection_prefix = "Metas_Sanitarias_18"
    kpi_name = request.args.get('kpi_name')

    if not kpi_name:
        return jsonify({'error': 'Faltan parámetros necesarios: database_name, collection_prefix, kpi_name'}), 400

    try:
        historical_data = get_kpi_historical_data(database_name, collection_prefix, kpi_name)
        return jsonify(historical_data), 200
    except Exception as e:
        return jsonify({'error': f'Error al obtener los datos históricos: {str(e)}'}), 500
    
@kpi_metas_sanitarias_18_bp.route('/kpi_metas_general_18', methods=['GET'])
def kpi_praps_general():
    latest_documents = get_latest_version_documents("GENERAL", "GENERAL_PROGRAMS_METAS_18",False)
    #return the latest documents registers
    if latest_documents:
        latest_documents = json_serializable_documents(latest_documents)
        return jsonify(latest_documents), 200
    else:
        print("No se encontraron documentos.")
        return jsonify({'error': 'No se encontraron documentos.'}), 404
     
@kpi_metas_sanitarias_18_bp.route('/get_general_historical_data_metas_18', methods=['GET'])
def get_general_historical_data_route():
    database_name = 'GENERAL'
    collection_prefix = "GENERAL_PROGRAMS_METAS_18"

    try:
        historical_data = get_Metas_historical_data(database_name, collection_prefix, "Metas Sanitarias Ley 18")
        return jsonify(historical_data), 200
    except Exception as e:
        return jsonify({'error': f'Error al obtener los datos históricos: {str(e)}'}), 500
    
@kpi_metas_sanitarias_18_bp.route('/kpi_metas_PROPS_18', methods=['GET'])
def get_PROPS():

    collection = get_latest_version_documents("KPI_GOALS", "PROPS_KPI_METAS_18",True)
    try:
        # Obtener todos los documentos de Praps Primario
        documents = json_serializable_documents(list(collection.find()))
        return jsonify(documents), 200
    except PyMongoError as e:
        return jsonify({'error': f'Error al obtener los documentos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error inesperado: {str(e)}'}), 500

@kpi_metas_sanitarias_18_bp.route('/kpi_metas_objetivos_18', methods=['GET'])
def get_metas_objetivos():
	collection = get_latest_version_documents("KPI_GOALS", "METAS_Y_OBJETIVOS_METAS_18",True)
	try:
		# Obtener todos los documentos de Praps Primario
		documents = json_serializable_documents(list(collection.find()))
		return jsonify(documents), 200
	except PyMongoError as e:
		return jsonify({'error': f'Error al obtener los documentos: {str(e)}'}), 500
	except Exception as e:
		return jsonify({'error': f'Error inesperado: {str(e)}'}), 500

@kpi_metas_sanitarias_18_bp.route('/get_kpi_by_id_metas_18', methods=['GET'])
def get_kpi_by_id():
    id = request.args.get('id')
    collection = get_latest_version_documents("KPI_GOALS", "PROPS_KPI_METAS_18", True)
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