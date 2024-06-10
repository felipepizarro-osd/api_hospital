from database import get_user_database
from functools import wraps
from flask import Response, request, jsonify, g


import firebase_admin
from firebase_admin import credentials, auth

cred = credentials.Certificate('firebase_auth_credentials.json')
firebase_admin.initialize_app(cred)


user_db = get_user_database()
users_collection = user_db["Users"]


def test_middleware(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            user = request.authorization["username"]
            password = request.authorization["password"]
        except TypeError:
            return jsonify({"error": "Add basic auth"}), 401

        if user == 'admin' and password == '123':
            return func(*args, **kwargs)
        return jsonify({"message": "Authorization failed"}), 401

    return decorated_function


def sign_in_middleware(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):

        id_token = request.headers.get('Authorization').split(
            ' ').pop() if request.headers.get('Authorization') else None

        try:
            if id_token:
                g.decoded_token = auth.verify_id_token(id_token)

                # search user in database
                user = users_collection.find_one(
                    {"email": g.decoded_token["email"]})
                print(user)
                if user:
                    
                    g.user = {
                        "email": user["email"],
                        "permissions": user["permissions"],
                        "position": user["position"],
                        "status": user["status"]
                    }
                    return func(*args, **kwargs)
                return jsonify({"error": "User not found"}), 401
            else:
                return jsonify({"error": "Token is missing"}), 401
        except Exception as e:
            return jsonify({"error": str(e)}), 401
    return decorated_function
