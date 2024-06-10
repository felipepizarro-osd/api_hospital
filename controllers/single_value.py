from flask import Blueprint, jsonify, request, Response
from database import get_database
from bson import json_util
from bson.objectid import ObjectId


single_value_bp = Blueprint('single_value', __name__, url_prefix="")

db = get_database()
single_value_collection = db["single_values"]


@single_value_bp.route('/single_values', methods=['GET'])
def get_all_single_values():
    results = []
    for sv in single_value_collection.find():
        results.append({
                       '_id': str(ObjectId(sv['_id'])),
                       'value_name': sv['value_name'],
                       'values': sv['values']}
                       )
    return jsonify(results), 200


@single_value_bp.route('/single_values/<single_value_id>', methods=['GET'])
def get_single_value_by_id(single_value_id):
    single_value_id = ObjectId(single_value_id)
    single_value = single_value_collection.find_one({"_id": single_value_id})
    if single_value is None:
        return jsonify({"message": f"single_value: {single_value} no fue encontrado"}), 404

    response = {'_id': str(ObjectId(single_value['_id'])),
                'value_name': single_value['value_name'],
                'values': single_value['values']}
    return jsonify(response), 200


@single_value_bp.route('/single_values', methods=['POST'])
def create_single_value():
    name = request.form.get('name')
    if name is None:
        return "Error: El parámetro 'name' es necesario en la solicitud.", 400

    new_single_value = {
        "value_name": name,
        "values": []
    }
    result = single_value_collection.insert_one(new_single_value)
    created_value = single_value_collection.find_one(
        {"_id": result.inserted_id})
    response = json_util.dumps(created_value)
    return Response(response, mimetype="application/json")


@single_value_bp.route('/single_values/<single_value_id>', methods=['DELETE'])
def delete_single_value_by_id(single_value_id):
    single_value_id = ObjectId(single_value_id)
    value = single_value_collection.find_one({"_id": single_value_id})
    if value is None:
        return jsonify({"message": f"single_value: {single_value_id} no fue encontrado"}), 404

    single_value_collection.delete_one({"_id": single_value_id})
    return jsonify({"message": f"single_value: {single_value_id} fue eliminado"}), 200


@single_value_bp.route('/single_values/<single_value_id>', methods=['POST'])
def insert_value_into_single_value_by_id(single_value_id):
    single_value_id = ObjectId(single_value_id)
    single_value = single_value_collection.find_one({"_id": single_value_id})

    # add type validation

    # validate any null field before insert
    if (request.form.get('value') is None or
            request.form.get('date') is None or
            request.form.get('expiration_date') is None):
        return jsonify({"message": "Ninguno de los campos puede ser nulo"}), 400

    new_embedded_value = {
        "value": float(request.form.get('value')),
        "date": request.form.get('date'),
        "expiration_date": request.form.get('expiration_date')
    }
    single_value['values'].append(new_embedded_value)

    updated_single_value = {'_id': str(ObjectId(single_value['_id'])),
                            'value_name': single_value['value_name'],
                            'values': single_value['values']}

    single_value_collection.update_one({"_id": single_value_id}, {
                                       "$set": {"values": single_value['values']}})

    return jsonify(updated_single_value), 200
