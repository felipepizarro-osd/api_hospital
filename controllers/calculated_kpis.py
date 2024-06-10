from flask import Blueprint, jsonify, request, Response
from bson.objectid import ObjectId
from datetime import datetime

from database import get_database

calculated_kpis_bp = Blueprint('calculated_kpis', __name__, url_prefix="")
db = get_database()

calculated_kpi_collection = db["calculated_kpi"]


@calculated_kpis_bp.route('/calculated_kpis/<kpi_type>', methods=['GET'])
def get_calculated_kpis_by_type(kpi_type):
    month_and_year = request.form.get('month_and_year')
    
    try:
        formatted_date = datetime.strptime(month_and_year, "%m/%Y").strftime("%m-%Y")
    except ValueError:
        return jsonify({"message": f"La fecha no es valida"}), 400

    results = []
    for ck in calculated_kpi_collection.find({"type":kpi_type, "month_and_year":month_and_year}):
        results.append({
        '_id': str(ObjectId(ck['_id'])),
        "type" : ck["type"],
        "subtype" : ck["subtype"],
        "month_and_year" : ck["month_and_year"],
        "version" : ck["version"],
        "number_of_kpis" : ck["number_of_kpis"],
        "kpis": ck["kpis"],
        "last_update": ck["last_update"]
    })    
        
    return jsonify(results), 200
    

    return jsonify({"message":"KPIs no encontrados"}),404


@calculated_kpis_bp.route('/calculated_kpis/<kpi_type>/<kpi_subtype>', methods=['GET'])
def get_calculated_kpis_by_type_and_subtype(kpi_type, kpi_subtype):
    month_and_year = request.form.get('month_and_year')
    print(f'/calculated_kpis/<{kpi_type}>/<{kpi_subtype}>')
    
    
    try:
        formatted_date = datetime.strptime(month_and_year, "%m/%Y").strftime("%m-%Y")
    except ValueError:
        return jsonify({"message": f"La fecha no es valida"}), 400

    result = calculated_kpi_collection.find_one({"type": kpi_type, "subtype": kpi_subtype, "month_and_year": month_and_year})
    
    print(result)
    if result:
        response = {
            '_id': str(ObjectId(result['_id'])),
            "type": result["type"],
            "subtype": result["subtype"],
            "month_and_year": result["month_and_year"],
            "version": result["version"],
            "number_of_kpis": result["number_of_kpis"],
            "kpis": result["kpis"],
            "last_update": result["last_update"]
        }
        
        return jsonify(response), 200

    return jsonify({"message": f"KPIs de '{kpi_type}: {kpi_subtype}' no encontrados para la fecha {month_and_year}"}), 404