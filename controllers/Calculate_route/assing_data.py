from flask import jsonify
from controllers.google_connect.google_drive_connection_routes.utils.json_utils import insertar_kpi_en_mongodb
from controllers.google_connect.google_drive_connection_routes.utils.metas_props_metas_19 import procesar_PROPS_metas_19, procesar_METAS_METAS19
from controllers.google_connect.google_drive_connection_routes.utils.metas_props_metas_18 import procesar_PROPS_metas_18, procesar_METAS_METAS18
from controllers.google_connect.google_drive_connection_routes.utils.props_metas_praps import procesar_PROPS_PRAPS, procesar_METAS_PRAPS
from pymongo.errors import PyMongoError
from database import get_client
client = get_client()
def assing_metas_from_calculus():
    db = client["Clave_referencia"]
    collection_19 = db["Metas_Sanitarias_19"]
    collection_18 = db["Metas_Sanitarias_18"]
    collection_praps = db["Praps_Primario"]
    #print("ENTRO A ASIGNAR METAS")

    try:
        # Obtener todos los documentos de las colecciones
        documents_19 = list(collection_19.find())
        documents_18 = list(collection_18.find())
        documents_praps = list(collection_praps.find())

        # Procesar los documentos para Metas Sanitarias 19
        kpi_documentos_19 = procesar_PROPS_metas_19(documents_19)
        metas_praps_19 = procesar_METAS_METAS19(documents_19)

        # Procesar los documentos para Metas Sanitarias 18
        kpi_documentos_18 = procesar_PROPS_metas_18(documents_18)
        metas_praps_18 = procesar_METAS_METAS18(documents_18)

        # Procesar los documentos para Praps Primario
        kpi_documentos_praps = procesar_PROPS_PRAPS(documents_praps)
        metas_praps_praps = procesar_METAS_PRAPS(documents_praps)

        # Insertar los documentos procesados en las colecciones de KPI
        inserted_19 = (insertar_kpi_en_mongodb(kpi_documentos_19, "PROPS_KPI_METAS_19") and 
                       insertar_kpi_en_mongodb(metas_praps_19, "METAS_Y_OBJETIVOS_METAS_19"))

        inserted_18 = (insertar_kpi_en_mongodb(kpi_documentos_18, "PROPS_KPI_METAS_18") and 
                       insertar_kpi_en_mongodb(metas_praps_18, "METAS_Y_OBJETIVOS_METAS_18"))

        inserted_praps = (insertar_kpi_en_mongodb(kpi_documentos_praps, "PROPS_KPI_PRAPS") and 
                          insertar_kpi_en_mongodb(metas_praps_praps, "METAS_Y_OBJETIVOS_PRAPS"))

        if inserted_19 and inserted_18 and inserted_praps:
            return jsonify({'message': 'Metas asignadas correctamente'}), 200
        else:
            return jsonify({'error': 'Error al asignar metas'}), 500
    except PyMongoError as e:
        return jsonify({'error': f'Error al procesar los documentos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error inesperado: {str(e)}'}), 500