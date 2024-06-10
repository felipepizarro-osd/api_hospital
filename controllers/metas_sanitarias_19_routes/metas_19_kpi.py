from flask import Blueprint, jsonify, request
from controllers.google_connect.google_drive_connection_routes.utils.files_drive_utils import get_latest_version_documents, json_serializable_documents
from controllers.google_connect.google_drive_connection_routes.utils.json_utils import insertar_kpi_en_mongodb, get_kpi_historical_data, get_Metas_historical_data
from controllers.google_connect.google_drive_connection_routes.utils.metas_props_metas_19 import procesar_PROPS_metas_19, procesar_METAS_METAS19
from controllers.google_connect.google_drive_connection_routes.utils.metas_props_metas_18 import procesar_PROPS_metas_18, procesar_METAS_METAS18
from pymongo.errors import PyMongoError
from bson import ObjectId
from database import get_client

client = get_client()   

kpi_metas_sanitarias_19_bp = Blueprint('kpi_metas_sanitarias_19_routes', __name__, url_prefix="")
# This is the endpoint to get the values of the metas sanitarias 19
@kpi_metas_sanitarias_19_bp.route('/Kpi_Metas_19_Values', methods=['GET'])
def Kpi_Metas_19_Values():
	# Selecciona la base de datos KPI_PRAPS
		# Uso de la función
	latest_documents = get_latest_version_documents("KPI_METAS_SANITARIAS_19", "Metas_Sanitarias_19",False)
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

@kpi_metas_sanitarias_19_bp.route('/assing_metas_18_19', methods=['POST'])
def assing_metas_for_metas():
    db = client["Clave_referencia"]
    collection_19 = db["Metas_Sanitarias_19"]
    collection_18 = db["Metas_Sanitarias_18"]
    try:
        # Obtener todos los documentos de ambas colecciones
        documents_19 = list(collection_19.find())
        documents_18 = list(collection_18.find())

        # Procesar los documentos para asignar metas para Metas Sanitarias 19
        kpi_documentos_19 = procesar_PROPS_metas_19(documents_19)
        metas_praps_19 = procesar_METAS_METAS19(documents_19)

        # Procesar los documentos para asignar metas para Metas Sanitarias 18
        kpi_documentos_18 = procesar_PROPS_metas_18(documents_18)
        metas_praps_18 = procesar_METAS_METAS18(documents_18)

        # Insertar los documentos procesados en las colecciones de KPI
        inserted_19 = (insertar_kpi_en_mongodb(kpi_documentos_19, "PROPS_KPI_METAS_19") and 
                       insertar_kpi_en_mongodb(metas_praps_19, "METAS_Y_OBJETIVOS_METAS_19"))

        inserted_18 = (insertar_kpi_en_mongodb(kpi_documentos_18, "PROPS_KPI_METAS_18") and 
                       insertar_kpi_en_mongodb(metas_praps_18, "METAS_Y_OBJETIVOS_METAS_18"))

        if inserted_19 and inserted_18:
            return jsonify({'message': 'Metas asignadas correctamente'}), 200
        else:
            return jsonify({'error': 'Error al asignar metas'}), 500

    except PyMongoError as e:
        return jsonify({'error': f'Error al procesar los documentos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error inesperado: {str(e)}'}), 500
    
@kpi_metas_sanitarias_19_bp.route('/get_kpi_historical_data_metas_19', methods=['GET'])
def get_kpi_historical_data_route():
    database_name = 'KPI_METAS_SANITARIAS_19'
    collection_prefix = "Metas_Sanitarias_19"
    kpi_name = request.args.get('kpi_name')

    if not kpi_name:
        return jsonify({'error': 'Faltan parámetros necesarios: database_name, collection_prefix, kpi_name'}), 400

    try:
        historical_data = get_kpi_historical_data(database_name, collection_prefix, kpi_name)
        return jsonify(historical_data), 200
    except Exception as e:
        return jsonify({'error': f'Error al obtener los datos históricos: {str(e)}'}), 500

@kpi_metas_sanitarias_19_bp.route('/get_general_historical_data_metas_19', methods=['GET'])
def get_general_historical_data_route():
    database_name = 'GENERAL'
    collection_prefix = "GENERAL_PROGRAMS_METAS_19"

    try:
        historical_data = get_Metas_historical_data(database_name, collection_prefix, "Metas Sanitarias Ley 19")
        return jsonify(historical_data), 200
    except Exception as e:
        return jsonify({'error': f'Error al obtener los datos históricos: {str(e)}'}), 500
@kpi_metas_sanitarias_19_bp.route('/kpi_metas_general_19', methods=['GET'])
def kpi_praps_general():
    latest_documents = get_latest_version_documents("GENERAL", "GENERAL_PROGRAMS_METAS_19",False)
    #return the latest documents registers
    if latest_documents:
        latest_documents = json_serializable_documents(latest_documents)
        return jsonify(latest_documents), 200
    else:
        print("No se encontraron documentos.")
        return jsonify({'error': 'No se encontraron documentos.'}), 404
     
@kpi_metas_sanitarias_19_bp.route('/kpi_metas_PROPS_19', methods=['GET'])
def get_PROPS():

    collection = get_latest_version_documents("KPI_GOALS", "PROPS_KPI_METAS_19",True)
    try:
        # Obtener todos los documentos de Praps Primario
        documents = json_serializable_documents(list(collection.find()))
        return jsonify(documents), 200
    except PyMongoError as e:
        return jsonify({'error': f'Error al obtener los documentos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error inesperado: {str(e)}'}), 500

@kpi_metas_sanitarias_19_bp.route('/kpi_metas_objetivos_19', methods=['GET'])
def get_metas_objetivos():
	collection = get_latest_version_documents("KPI_GOALS", "METAS_Y_OBJETIVOS_METAS_19",True)
	try:
		# Obtener todos los documentos de Praps Primario
		documents = json_serializable_documents(list(collection.find()))
		return jsonify(documents), 200
	except PyMongoError as e:
		return jsonify({'error': f'Error al obtener los documentos: {str(e)}'}), 500
	except Exception as e:
		return jsonify({'error': f'Error inesperado: {str(e)}'}), 500
@kpi_metas_sanitarias_19_bp.route('/get_kpi_by_id_metas_19', methods=['GET'])
def get_kpi_by_id():
    id = request.args.get('id')
    collection = get_latest_version_documents("KPI_GOALS", "PROPS_KPI_METAS_19", True)
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