from flask import Blueprint, jsonify, request
from controllers.google_connect.Script_Data_Extraction.Calculate_Data import CalculateDataDinamic, CalculateDataDinamic_previousPeriod
from controllers.google_connect.Script_Data_Extraction.utils.process_store_utils import process_and_store_kpis_general_praps, process_and_store_kpis_general_metas
from controllers.Calculate_route.assing_data import assing_metas_from_calculus

Maths_routes_bp = Blueprint('Maths_routes', __name__, url_prefix="")

@Maths_routes_bp.route('/start_calculus2', methods=['GET', 'POST'])
def startCalculus2():
    #folder_id = '1iLPx3NgHogw59h1VLIeagxk1MKLKbdAh'
    try:
        # Realiza los cálculos
        success = CalculateDataDinamic()
        result = assing_metas_from_calculus()
        success18 = process_and_store_kpis_general_metas(True)
        success19 = process_and_store_kpis_general_metas()
        successpraps = process_and_store_kpis_general_praps()
        # Verifica si los cálculos fueron exitosos
        if success and result[1] == 200 and success18 and success19 and successpraps:
            return jsonify({'message': 'Cálculo hecho correctamente'}), 200
        else:
            return jsonify({'error': 'Error al iniciar el cálculo'}), 500
    except Exception as e:
        # Manejo de excepciones
        return jsonify({'error': f'Error al iniciar el cálculo: {str(e)}'}), 500
#TODO TEST FUNCTIONALITY
@Maths_routes_bp.route('/start_calculu_provious_period', methods=['GET', 'POST'])
def startCalculus_previos_period():
    month = request.args.get('month')
    year = request.args.get('year')
    #folder_id = '1iLPx3NgHogw59h1VLIeagxk1MKLKbdAh'
    try:
        # Realiza los cálculos
        success = CalculateDataDinamic_previousPeriod(month,year)
        result = assing_metas_from_calculus()
        # Verifica si los cálculos fueron exitosos
        if success and result[1] == 200:
            return jsonify({'message': 'Cálculo hecho correctamente'}), 200
        else:
            return jsonify({'error': 'Error al iniciar el cálculo'}), 500
    except Exception as e:
        # Manejo de excepciones
        return jsonify({'error': f'Error al iniciar el cálculo: {str(e)}'}), 500
@Maths_routes_bp.route('/process_and_store_kpis', methods=['GET', 'POST'])
def process_and_store_kpis_route():
    try:
        # Realiza los cálculos
        success18 = process_and_store_kpis_general_metas(True)
        success19 = process_and_store_kpis_general_metas()
        success = process_and_store_kpis_general_praps()
        if success and success18 and success19:
            return jsonify({'message': 'Cálculo hecho correctamente'}), 200
        else:
            return jsonify({'error': 'Error al interpretar el cálculo'}), 500
    except Exception as e:
        # Manejo de excepciones
        return jsonify({'error': f'Error al iniciar el cálculo: {str(e)}'}), 500