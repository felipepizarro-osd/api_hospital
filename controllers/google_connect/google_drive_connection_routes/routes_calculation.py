import os.path
import sys
from flask import Blueprint, jsonify, request, redirect
from datetime import datetime, timedelta
from bson import ObjectId
from controllers.google_connect.google_drive_connection_routes.utils.google_drive_utils import upload_to_drive, list_files, list_files_sort, assing_date_expirity, get_web_content_link
from controllers.google_connect.google_drive_connection_routes.utils.files_drive_utils import json_serializable_documents
from database import get_client
from controllers.google_connect.google_drive_connection_routes.utils.mongo_data_utils import upload_file_parameters

#from flasgger import Swagger, swag_from
#Here will be the routes for the calculation of the data from the google drive
client = get_client()

drive_routes_bp = Blueprint('drive_routes', __name__, url_prefix="")
# Configurar Swagger
#swagger = Swagger(drive_routes_bp)
# If modifying these scopes, delete the file token.json.
# the scope is for access to REM values and spreadsheets and Poblation data of Vicuña uploaded in Google Drive
#for this case we will use the scope for access to the google drive with the service account
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')
#path for call a function from another folder like calculations
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Folder for uploaded files
UPLOAD_FOLDER = 'uploads'

# Setting a temp folder for the uploaded files
if not os.path.exists(UPLOAD_FOLDER):
	os.makedirs(UPLOAD_FOLDER)

#this function will list the files in the google drive service account
#PD: the google drive service account is the account that will be used for the connection to the google drive but is diferent account from the personal or organizational account is necessary share a directory with the service account mail for the connection and list the folder and files who service account can access and select the folder or directory in the personal or organizational account for the connection with the service account API
#PD: Dont forget share the folder Id with the development teams for the connection
@drive_routes_bp.route('/upload_file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No se ha enviado ningún archivo'}), 400
    file = request.files['file']
    file_name = request.form.get('file_name', 'Archivo sin nombre')
    default_expiry_date = assing_date_expirity(file_name)
    
    # Obtener la fecha de expiración del formulario o utilizar la fecha de expiración predeterminada
    date_expirity = request.form.get('date_expirity', default_expiry_date)
    #upload_file_parameters(file_name, date_expirity)
    # Verificar si el archivo no está vacío
    if file.filename == '':
        return jsonify({'error': 'No se ha seleccionado ningún archivo'}), 400
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    file_name_with_date = f"{current_date}_{file_name}"
    
    # Guardar el archivo en el sistema de archivos local
    file_path = os.path.join(UPLOAD_FOLDER, file_name_with_date)
    file.save(file_path)
    print(f'Archivo guardado en: {file_path}')
    print(f'Nombre del archivo: {file_name}')
    
    # Subir el archivo a Google Drive con el identificador de carpeta de cuenta personal u organizativa
    folder_id = '1iLPx3NgHogw59h1VLIeagxk1MKLKbdAh'
    drive_file_id = upload_to_drive(file_path, file_name_with_date, folder_id)
    try:
        upload_file_parameters(file_name, date_expirity,drive_file_id)
    except Exception as e:
        print("Error al guardar datos en MongoDB:", e)
        return False

    print(f'Archivo subido a Google Drive con ID: {drive_file_id}')
    
    # Eliminar el archivo del sistema de archivos local (solo para hacer una copia de seguridad mientras se carga el archivo a Google Drive)
    os.remove(file_path)
    
    # Si deseas listar los archivos en Google Drive, puedes descomentar la siguiente línea
    # print(list_files())
    
    # Respuesta para el frontend con el ID del archivo y el mensaje de que el archivo se ha subido a Google Drive
    return jsonify({'message': 'Archivo subido exitosamente a Google Drive', 'drive_file_id': drive_file_id}), 200
@drive_routes_bp.route('/<collection_name>/all', methods=['GET'])
def get_all_documents(collection_name):
    db = client["Clave_referencia"]
    if collection_name not in ['Metas_Sanitarias_19', 'Metas_Sanitarias_18', 'Praps_Primario']:
        return jsonify({'error': 'Colección no válida'}), 400

    collection = db[collection_name]
    documents = list(collection.find())
    result = json_serializable_documents(documents)

    return jsonify(result), 200
# Ruta para obtener un documento específico por ID
@drive_routes_bp.route('/GetDocument', methods=['GET'])
def get_document_by_id():
    id = request.args.get('id')
    collection_name = request.args.get('collection')
    db = client["Clave_referencia"]
    if collection_name not in ['Metas_Sanitarias_19', 'Metas_Sanitarias_18', 'Praps_Primario']:
        return jsonify({'error': 'Colección no válida'}), 400

    collection = db[collection_name]
    try:
        document = collection.find_one({"_id": ObjectId(id)})
        print(document)
        if document:
            result = json_serializable_documents(document)
            return jsonify(result), 200
        else:
            return jsonify({'error': 'Documento no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': f'Error al obtener el documento: {str(e)}'}), 500
@drive_routes_bp.route('/delete_document', methods=['DELETE'])
def delete_document():
    id = request.args.get('id')
    collection_name = request.args.get('collection')
    db = client["Clave_referencia"]
    if collection_name not in ['Metas_Sanitarias_19', 'Metas_Sanitarias_18', 'Praps_Primario']:
        return jsonify({'error': 'Colección no válida'}), 400

    collection = db[collection_name]
    try:
        result = collection.delete_one({"_id": ObjectId(id)})
        if result.deleted_count > 0:
            return jsonify({'message': 'Documento eliminado correctamente'}), 200
        else:
            return jsonify({'error': 'Documento no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': f'Error al eliminar el documento: {str(e)}'}), 500
    
@drive_routes_bp.route('/get_month_document', methods=['GET'])
def get_document_by_month():
    folder_id = '1iLPx3NgHogw59h1VLIeagxk1MKLKbdAh'
    #folder_id = request.args.get('folder_id')
    #if not folder_id:
    #    return jsonify({'error': 'Se requiere el parámetro folder_id'}), 400
    try:
        files_by_month = list_files_sort(folder_id)
        return jsonify(files_by_month)
    except Exception as e:
        return jsonify({'error': f'Error al obtener los archivos por mes: {str(e)}'}), 500
    
    
@drive_routes_bp.route('/get_file_download_by_id', methods=['GET'])
def get_file_download_by_id():
    file_id = request.args.get('file_id')
    if not file_id:
        return jsonify({'error': 'Se requiere el parámetro file_id'}), 400
    try:
        web_content_link = get_web_content_link(file_id)
        print(web_content_link)
        if not web_content_link:
            return jsonify({'error': 'No se pudo obtener el enlace de descarga del archivo'}), 500

    # Redirigir al usuario al enlace de descarga
        return redirect(web_content_link)
    except Exception as e:
        return jsonify({'error': f'Error al descargar el archivo: {str(e)}'}), 500
    
