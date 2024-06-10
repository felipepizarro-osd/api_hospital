from flask import Blueprint, jsonify, request, Response, g
from database import get_user_database
from bson import json_util
from bson.objectid import ObjectId
from pymongo import ASCENDING

from middlewares.middlewares import test_middleware, sign_in_middleware




sign_in_bp = Blueprint('sign_in', __name__, url_prefix="")

db = get_user_database()
user_collection = db["Users"]


@sign_in_bp.route('/sign_in', methods=['Post'])
@sign_in_middleware
def login():
    try:
        return jsonify({'message': 'Inicio de session exitoso', "user":g.user}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

