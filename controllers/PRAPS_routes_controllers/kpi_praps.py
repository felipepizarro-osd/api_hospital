from flask import Blueprint, jsonify, request
from bson import ObjectId
from pymongo.errors import PyMongoError
import json
from controllers.google_connect.google_drive_connection_routes.utils.files_drive_utils import get_latest_version_documents, json_serializable_documents
from urllib.parse import unquote
from controllers.google_connect.google_drive_connection_routes.utils.json_utils import validar_json, corregir_y_validar_json, calculate_program_compliance, procesar_single_values, insertar_kpi_en_mongodb, get_kpi_historical_data
from controllers.google_connect.google_drive_connection_routes.utils.props_metas_praps import procesar_PROPS_PRAPS, procesar_METAS_PRAPS

from database import get_client

kpi_praps_routes_bp = Blueprint('kpi_praps_routes', __name__, url_prefix="")

client = get_client()

@kpi_praps_routes_bp.route('/Kpi_Praps_Values', methods=['GET'])
def Kpi_Praps_Values():
	# Selecciona la base de datos KPI_PRAPS
		# Uso de la función
	latest_documents = get_latest_version_documents("KPI_PRAPS", "Praps",False)
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
#also get a specific component or program from praps for example like the program desarollo biosicosocial
@kpi_praps_routes_bp.route('/Kpi_Praps_Values_component', methods=['GET'])
def Kpi_Praps_Values_component():
    componente_programa_encoded = request.args.get('componente/programa')
    componente_programa_decoded = unquote(componente_programa_encoded)
    print("COMPONENTE:", componente_programa_decoded)
    if not componente_programa_decoded:
        return jsonify({'error': 'No se ha especificado el componente/programa'}), 400
    latest_collection = get_latest_version_documents('KPI_PRAPS', 'Praps',True)
    print(latest_collection)
    if latest_collection:  # noqa: E999, E999
        documents = list(latest_collection.find({'Componente/programa': componente_programa_decoded}))
        #print(documents)
        # Calcular el porcentaje de cumplimiento del componente

        try:
            for doc in documents:
                valor = doc.get("Valor")
                peso_relativo = doc.get("peso_relativo", 0)
                
                if valor == "DIVISION POR CERO":
                    porcentaje_cumplimiento = 0
                elif peso_relativo == 0:
                    porcentaje_cumplimiento = valor
                else:
                    porcentaje_cumplimiento = sum(d.get("Valor", 0) * d.get("peso_relativo", 0) for d in documents if d.get("peso_relativo", 0) > 0)

        except ZeroDivisionError:
            porcentaje_cumplimiento = 0   
     
        result = json_serializable_documents(documents)
        
        # Añadir el porcentaje de cumplimiento al resultado
        result.append({"porcentaje_cumplimiento": porcentaje_cumplimiento})
        
        return jsonify(result), 200
    else:
        print('No se encontró la colección más reciente.')
        return jsonify({'error': 'No se encontró el componente solicitado.'}), 404
@kpi_praps_routes_bp.route('/Kpi_Praps_Values_by_program', methods=['GET'])
def Kpi_Praps_Values_program():
    indicador_perteneciente_encoded = request.args.get('indicador_perteneciente')
    indicador_perteneciente_decoded = unquote(indicador_perteneciente_encoded)
    print("COMPONENTE:", indicador_perteneciente_decoded)
    if not indicador_perteneciente_decoded:
        return jsonify({'error': 'No se ha especificado el componente/programa'}), 400
    latest_collection = get_latest_version_documents('KPI_PRAPS', 'Praps',True)
    print(latest_collection)
    if latest_collection:  # noqa: E999, E999
        documents = list(latest_collection.find({'indicador_perteneciente': indicador_perteneciente_decoded}))
        #print(documents)
        resultado = json_serializable_documents(documents)
        try:
            result, error = calculate_program_compliance(indicador_perteneciente_decoded, documents)
            #print(result)   
        except Exception:
            return jsonify({'error': f'Error al calcular el cumplimiento del programa: {str(error)}'}), 500
        if result:
            resultado.append({'cumplimiento_programa': result})
            return jsonify(resultado), 200
        else:   
            porcentaje_cumplimiento = sum((0 if doc["Valor"] == "DIVISION POR CERO" else doc["Valor"]) * doc["peso_relativo"]for doc in documents if doc["peso_relativo"] > 0)
            resultado.append({"porcentaje_cumplimiento": porcentaje_cumplimiento})
            return jsonify(resultado), 200
    else:
        print('No se encontró la colección más reciente.')
        return jsonify({'error': 'No se encontró el componente solicitado.'}), 404
@kpi_praps_routes_bp.route('/kpi_praps_general', methods=['GET'])
def kpi_praps_general():
    latest_documents = get_latest_version_documents("GENERAL", "GENERAL_PROGRAMS_PRAPS",False)
    #return the latest documents registers
    if latest_documents:
        latest_documents = json_serializable_documents(latest_documents)
        return jsonify(latest_documents), 200
    else:
        print("No se encontraron documentos.")
        return jsonify({'error': 'No se encontraron documentos.'}), 404
     


@kpi_praps_routes_bp.route('/kpi_metas_PROPS_Praps', methods=['GET'])
def get_PROPS():

    collection = get_latest_version_documents("KPI_GOALS", "PROPS_KPI_PRAPS",True)
    try:
        # Obtener todos los documentos de Praps Primario
        documents = json_serializable_documents(list(collection.find()))
        return jsonify(documents), 200
    except PyMongoError as e:
        return jsonify({'error': f'Error al obtener los documentos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error inesperado: {str(e)}'}), 500

@kpi_praps_routes_bp.route('/kpi_metas_objetivos_Praps', methods=['GET'])
def get_metas_objetivos():
	collection = get_latest_version_documents("KPI_GOALS", "PROPS_KPI_PRAPS",True)
	try:
		# Obtener todos los documentos de Praps Primario
		documents = json_serializable_documents(list(collection.find()))
		return jsonify(documents), 200
	except PyMongoError as e:
		return jsonify({'error': f'Error al obtener los documentos: {str(e)}'}), 500
	except Exception as e:
		return jsonify({'error': f'Error inesperado: {str(e)}'}), 500
