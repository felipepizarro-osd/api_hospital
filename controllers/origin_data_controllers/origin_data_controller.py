from flask import Blueprint, jsonify, request
from controllers.google_connect.google_drive_connection_routes.utils.google_drive_utils import create_folder
from database import get_client

origin_data_bp = Blueprint('origin_data', __name__, url_prefix="")  

client = get_client()

@origin_data_bp.route('/insert_origin_data', methods=['POST'])
def insert_origin_data():
    data = request.get_json()
    name = data.get('name')
    folder = data.get('folder')
    sheets = data.get('sheets')
    print(data)
    if folder == "new":
        folder_id = create_folder(name)
    elif folder == "existing":
        folder_id = "1iLPx3NgHogw59h1VLIeagxk1MKLKbdAh"
    if not name or not folder_id or not sheets:
        return jsonify({'error': 'No se han especificado todos los datos necesarios'}), 400
    try:
        db = client['Data_Origin']
        collection = db['Files']
        new_data_source = {
            'name': name,
            'folder_id': folder_id,
            'sheets': sheets
        }
        collection.insert_one(new_data_source)
        return jsonify({'message': 'Origen de datos insertado correctamente'}), 200
    except Exception as e:
        print(f'Error al insertar el origen de datos: {str(e)}')
        return jsonify({'error': f'Error al insertar el origen de datos: {str(e)}'}), 500
    
@origin_data_bp.route('/delete_origin_data', methods=['DELETE'])
def delete_origin_data():
    name = request.args.get('name')
    if not name:
        return jsonify({'error': 'No se ha especificado el nombre del origen de datos'}), 400
    try:
        db = client['Data_Origin']
        collection = db['Files']
        result = collection.delete_one({'name': name})
        if result.deleted_count == 0:
            return jsonify({'error': 'No se encontró el origen de datos especificado'}), 404
        return jsonify({'message': 'Origen de datos eliminado correctamente'}), 200
    except Exception as e:
        print(f'Error al eliminar el origen de datos: {str(e)}')
        return jsonify({'error': f'Error al eliminar el origen de datos: {str(e)}'}), 500
@origin_data_bp.route('/modify_origin_data_sheets', methods=['PUT'])
def modify_origin_data_sheets():
    data = request.get_json()
    name = data.get('name')
    sheets_to_add = data.get('sheets_to_add', [])
    sheets_to_remove = data.get('sheets_to_remove', [])
    print(data)
    if not name:
        return jsonify({'error': 'No se ha especificado el nombre'}), 400
    
    try:
        db = client['Data_Origin']
        collection = db['Files']
        print(collection.name)
        # Encontrar el documento
        document = collection.find_one({'name': name})
        print(document)
        if not document:
            return jsonify({'error': 'No se encontró el origen de datos especificado'}), 404
        
        # Modificar las hojas
        current_sheets = document.get('sheets', [])
        for sheet in sheets_to_add:
            if sheet not in current_sheets:
                current_sheets.append(sheet)
        for sheet in sheets_to_remove:
            if sheet in current_sheets:
                current_sheets.remove(sheet)
        
        # Actualizar el documento
        collection.update_one({'name': name}, {'$set': {'sheets': current_sheets}})
        
        return jsonify({'message': 'Hojas modificadas correctamente'}), 200
    except Exception as e:
        print(f"Error al modificar las hojas del origen de datos: {e}")
        return jsonify({'error': 'Error al modificar las hojas del origen de datos'}), 500
@origin_data_bp.route('/modify_origin_data', methods=['PUT'])
def modify_origin_data():
    data = request.get_json()
    name = data.get('name')
    new_name = data.get('new_name')
    new_folder_id = data.get('new_folder_id')
    new_sheets = data.get('new_sheets')

    if not name:
        return jsonify({'error': 'No se ha especificado el nombre'}), 400

    try:
        db = client['Data_Origin']
        collection = db['Files']
        
        # Crear un diccionario con los campos a actualizar
        update_fields = {}
        if new_name:
            update_fields['file_name'] = new_name
        if new_folder_id:
            update_fields['folder_id'] = new_folder_id
        if new_sheets:
            update_fields['sheets'] = new_sheets
        
        if not update_fields:
            return jsonify({'error': 'No se ha especificado ningún campo para actualizar'}), 400
        
        # Actualizar el documento
        result = collection.update_one({'file_name': name}, {'$set': update_fields})
        
        if result.matched_count == 0:
            return jsonify({'error': 'No se encontró el origen de datos especificado'}), 404
        
        return jsonify({'message': 'Origen de datos modificado correctamente'}), 200
    except Exception as e:
        print(f"Error al modificar el origen de datos: {e}")
        return jsonify({'error': 'Error al modificar el origen de datos'}), 500
@origin_data_bp.route('/get_origin_data', methods=['GET'])
def get_origin_data():
    try:
        db = client['Data_Origin']
        collection = db['Files']
        
        # Obtener todos los documentos de la colección
        documents = list(collection.find({}))
        
        # Convertir ObjectId a string
        for document in documents:
            document['_id'] = str(document['_id'])
        
        return jsonify(documents), 200
    except Exception as e:
        print(f"Error al obtener los orígenes de datos: {e}")
        return jsonify({'error': 'Error al obtener los orígenes de datos'}), 500
