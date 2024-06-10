from flask import Blueprint, jsonify, request, Response
from database import get_database
from bson import json_util
from bson.objectid import ObjectId
from pymongo import ASCENDING


kpi_formulas_bp = Blueprint('kpi_formulas', __name__, url_prefix="")

db = get_database()
kpi_formulas_collection = db["kpi_formulas"]


@kpi_formulas_bp.route('/kpi_formulas', methods=['GET'])
def get_all_kpi_formulas():
    results = []
    for ms in kpi_formulas_collection.find().sort([('type', ASCENDING), ('subtype', ASCENDING), ('kpi_number', ASCENDING)]):
        results.append({
            '_id': str(ms['_id']),  
            'kpi_name': ms['kpi_name'],
            'kpi_number': ms['kpi_number'],
            'weight': ms['weight'],
            'type': ms['type'],
            'subtype': ms['subtype'],
            'formula': ms['formula'],
        })    
        
    return jsonify(results), 200


@kpi_formulas_bp.route('/kpi_formulas/insert_test', methods=['POST'])
def insert_test_kpi_formulas():
    new_kpi_formula = {
        "kpi_name": "kpi de ejemplo",
        "kpi_number": 2,
        "type": "Programas APS",
        "weight": 1,
        "subtype": "Programa de ejemplo",
        "formula": "$sv:total de nacimientos$/$sv:poblacion vicuña$"
    }

    result = kpi_formulas_collection.insert_one(new_kpi_formula)

    if result.inserted_id:
        inserted_kpi_formula = kpi_formulas_collection.find_one(
            {"_id": result.inserted_id})
        response = {
            '_id': str(ObjectId(inserted_kpi_formula['_id'])),
            'kpi_name': inserted_kpi_formula['kpi_name'],
            'kpi_number': inserted_kpi_formula['kpi_number'],
            'type': inserted_kpi_formula['type'],
            "weight": insert_test_kpi_formulas['weight'],
            'subtype': inserted_kpi_formula['subtype'],
            'formula': inserted_kpi_formula['formula'],
        }
        return jsonify(response), 201
    else:
        return jsonify({"message": "Error al insertar la formula de kpi"}), 500


@kpi_formulas_bp.route('/kpi_formulas', methods=['POST'])
def create_kpi_formula():
    kpi_name = request.form.get('kpi_name')
    kpi_number = request.form.get('kpi_number')
    weight = request.form.get('weight')
    type = request.form.get('type')
    subtype = request.form.get('subtype')
    formula = request.form.get('formula')

    if not all([kpi_name, kpi_number, type, weight, subtype, formula]):
        return jsonify({"error": "Falta uno o más campos obligatorios."}), 400

    new_kpi_formula = {
        "kpi_name": kpi_name,
        "kpi_number": int(kpi_number),
        "weight": float(weight),
        "type": type,
        "subtype": subtype,
        "formula": formula,
    }

    result = kpi_formulas_collection.insert_one(new_kpi_formula)

    if result.inserted_id:
        inserted_kpi_formula = kpi_formulas_collection.find_one({"_id": result.inserted_id})
        response = {
            '_id': str(ObjectId(inserted_kpi_formula['_id'])),
            'kpi_name': inserted_kpi_formula['kpi_name'],
            'kpi_number': inserted_kpi_formula['kpi_number'],
            'type': inserted_kpi_formula['type'],
            'weight': inserted_kpi_formula['weight'],
            'subtype': inserted_kpi_formula['subtype'],
            'formula': inserted_kpi_formula['formula'],
        }
        return jsonify(response), 201
    else:
        return jsonify({"message": "Error al insertar la formula de kpi"}), 500



@kpi_formulas_bp.route('/kpi_formulas/<kpi_formula_id>', methods=['DELETE'])
def delete_kpi_formula_by_id(kpi_formula_id):
    kpi_formula_id = ObjectId(kpi_formula_id)
    kpi_formula = kpi_formulas_collection.find_one({"_id": kpi_formula_id})

    if kpi_formula is None:
        return jsonify({"message": f"kpi_formula: {kpi_formula_id} no fue encontrado"}), 404

    kpi_formulas_collection.delete_one({"_id": kpi_formula_id})
    return jsonify({"message": f"kpi_formula: {kpi_formula_id} fue eliminado"}), 200
