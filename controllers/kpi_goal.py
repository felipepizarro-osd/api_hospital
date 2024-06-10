from flask import Blueprint, jsonify, request, Response
from database import get_database
from bson import json_util
from bson.objectid import ObjectId

kpi_goal_bp = Blueprint('kpi_goal', __name__, url_prefix="")

db = get_database()
kpi_goals_collection = db["kpi_goals"]


@kpi_goal_bp.route('/kpi_goals', methods=['GET'])
def get_all_kpi_goals():
    results = []
    for kg in kpi_goals_collection.find():
        results.append({
                       '_id': str(ObjectId(kg['_id'])),
                       'kpi_name': kg['kpi_name'],
                       'goals': kg['goals']}
                       )
    return jsonify(results), 200


@kpi_goal_bp.route('/kpi_goals/<kpi_goal_id>', methods=['GET'])
def get_kpi_goal_by_id(kpi_goal_id):
    kpi_goal_id = ObjectId(kpi_goal_id)
    kpi_goal = kpi_goals_collection.find_one({"_id": kpi_goal_id})
    if kpi_goal is None:
        return jsonify({"message": f"kpi_goal: {kpi_goal_id} no fue encontrado"}), 404

    response = {'_id': str(ObjectId(kpi_goal['_id'])),
                'kpi_name': kpi_goal['kpi_name'],
                'goals': kpi_goal['goals']}
    return jsonify(response), 200


@kpi_goal_bp.route('/kpi_goals', methods=['POST'])
def create_kpi_goal():
    name = request.form.get('name')
    if name is None:
        return "Error: El parámetro 'name' es necesario en la solicitud.", 400

    new_kpi_goal = {
        "kpi_name": name,
        "goals": []
    }
    result = kpi_goals_collection.insert_one(new_kpi_goal)
    created_goal = kpi_goals_collection.find_one({"_id": result.inserted_id})
    response = json_util.dumps(created_goal)
    return Response(response, mimetype="application/json")


@kpi_goal_bp.route('/kpi_goals/<kpi_goal_id>', methods=['DELETE'])
def delete_kpi_goal_by_id(kpi_goal_id):
    kpi_goal_id = ObjectId(kpi_goal_id)
    kpi_goal = kpi_goals_collection.find_one({"_id": kpi_goal_id})
    if kpi_goal is None:
        return jsonify({"message": f"kpi_goal: {kpi_goal_id} no fue encontrado"}), 404

    kpi_goals_collection.delete_one({"_id": kpi_goal_id})
    return jsonify({"message": f"kpi_goal: {kpi_goal_id} fue eliminado"}), 200


@kpi_goal_bp.route('/kpi_goals/<kpi_goal_id>', methods=['POST'])
def insert_goal_into_kpi_goal_by_id(kpi_goal_id):
    kpi_goal_id = ObjectId(kpi_goal_id)
    kpi_goal = kpi_goals_collection.find_one({"_id": kpi_goal_id})

    # add type validation

    # validate any null field before insert
    if (request.form.get('goal_value') is None or
            request.form.get('date') is None or
            request.form.get('expiration_date') is None):
        return jsonify({"message": "Ninguno de los campos puede ser nulo"}), 400

    new_embedded_goal = {
        "goal_value": float(request.form.get('goal_value')),
        "date": request.form.get('date'),
        "expiration_date": request.form.get('expiration_date')
    }
    kpi_goal['goals'].append(new_embedded_goal)

    updated_kpi_goal = {'_id': str(ObjectId(kpi_goal['_id'])),
                        'kpi_name': kpi_goal['kpi_name'],
                        'goals': kpi_goal['goals']}

    kpi_goals_collection.update_one(
        {"_id": kpi_goal_id}, {"$set": {"goals": kpi_goal['goals']}})

    return jsonify(updated_kpi_goal), 200
