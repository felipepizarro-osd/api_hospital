from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os 
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv
from Secret_manager.Secret_Manager import access_secret_version
from controllers.google_connect.google_file_recon import download_file
import json
from datetime import datetime, timedelta
from collections import defaultdict

load_dotenv()

# Define tus constantes como SCOPES y SERVICE_ACCOUNT_FILE
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')
#print(f"SERVICE_ACCOUNT_FILE: {service_account_file}")
#service_account_info = access_secret_version('sonic-silo-423120-r8', "google_service_account")
#service_account_info = json.loads(service_account_info)
credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)


def create_folder(folder_name):
    """Create a folder and prints the folder ID
    Returns : Folder Id

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    if SERVICE_ACCOUNT_FILE is None:
        raise ValueError("SERVICE_ACCOUNT_FILE environment variable is not set")
    
    #credentials = service_account.Credentials.from_service_account_info(
        #service_account_info, scopes=SCOPES)

    try:
        # create drive api client
        service = build("drive", "v3", credentials=credentials)
        file_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
        }

        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, fields="id").execute()
        print(f'Folder ID: "{file.get("id")}".')
        return file.get("id")

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None
    
def upload_to_drive(file_path, file_name, folder_id):
    """Insert new file.
    Returns : Id's of the file uploaded

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    if SERVICE_ACCOUNT_FILE is None:
        raise ValueError("SERVICE_ACCOUNT_FILE environment variable is not set")
    
    #credentials = service_account.Credentials.from_service_account_info(
        #SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    try:
        # create drive api client
        service = build("drive", "v3", credentials=credentials)
        
        # Metadata of the file to upload
        file_metadata = {
            'name': file_name,
            "parents": [folder_id]
        }

        media = MediaFileUpload(file_path, mimetype="application/vnd.ms-excel.sheet.macroenabled.12", resumable=True)
        # pylint: disable=maybe-no-member
        file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id, name")
            .execute()
        )
        print(f'File ID: {file.get("id")}')
        print(f'File Name: {file.get("name")}')
    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None

    return file.get("id")
def list_files():
  #credentials = service_account.Credentials.from_service_account_info(
	#	SERVICE_ACCOUNT_FILE, scopes=SCOPES)

	# Create a Google Drive service object
  drive_service = build('drive', 'v3', credentials=credentials)
  
  try:
    # Make a request to the Drive API
    results = drive_service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()

    # Extract the list of files from the results
    files = results.get('files', [])

    # Return the list of files
    if not files:
      return []
    else:
      return [(file["name"], file["id"]) for file in files]
  except Exception as e:
    print(f"Error al listar archivos: {e}")
    return []
def list_files_sort1(folder_id):
    drive_service = build('drive', 'v3', credentials=credentials)
    
    try:
        query = f"'{folder_id}' in parents"

        # Make a request to the Drive API
        results = drive_service.files().list(
            pageSize=100, fields="nextPageToken, files(id, name, createdTime)",q=query).execute()

        # Extract the list of files from the results
        files = results.get('files', [])

        if not files:
            return []
        
        # Group files by year and month
        files_by_month = defaultdict(list)
        for file in files:
            created_time = file.get("createdTime")
            if created_time:
                dt = datetime.strptime(created_time, '%Y-%m-%dT%H:%M:%S.%fZ')
                year_month = dt.strftime('%Y-%m')
                files_by_month[year_month].append((file["name"], file["id"]))

        return files_by_month
    except HttpError as e:
        print(f"Error al listar archivos: {e}")
        return {}
def list_files_sort(folder_id):
    drive_service = build('drive', 'v3', credentials=credentials)
    
    try:
        query = f"'{folder_id}' in parents"

        # Make a request to the Drive API
        results = drive_service.files().list(
            pageSize=100, fields="nextPageToken, files(id, name, createdTime)", q=query).execute()

        # Extract the list of files from the results
        files = results.get('files', [])

        if not files:
            return []
        
        # Group files by year and month
        files_by_date = defaultdict(list)
        for file in files:
            created_time = file.get("createdTime")
            if created_time:
                dt = datetime.strptime(created_time, '%Y-%m-%dT%H:%M:%S.%fZ')
                date_key = dt.strftime('%Y-%m-%d')
                files_by_date[date_key].append({"nombre": file["name"], "id": file["id"]})

        # Convert to the desired format
        sorted_files = [{"fecha": date, "docs": docs} for date, docs in files_by_date.items()]

        return sorted_files
    except HttpError as e:
        print(f"Error al listar archivos: {e}")
        return []
def find_file_by_month(file_name, year, month, folder_id):
    """Finds and returns the file ID for a given file name and month"""
    try:
        # create drive api client
        service = build("drive", "v3", credentials=credentials)
        # Formatear el mes y el año en el formato 'YYYY-MM'
        month_str = f"{year}-{month:02d}"
        # Construir la consulta para buscar archivos en el Drive
        query = f"'{folder_id}' in parents and name contains '{month_str}_{file_name}'"
        results = service.files().list(
            pageSize=20,
            fields="nextPageToken, files(id, name)",
            q=query,
            orderBy="modifiedTime desc",
        ).execute()

        if not results['files']:
            print(f"No se encontraron archivos con el nombre '{file_name}' en el mes {month_str}.")
            return None
        
        # Extraer el ID del primer archivo de los resultados
        file_id = results['files'][0]['id']
        print(f"File ID encontrado: {file_id}")
        return file_id
    except HttpError as error:
        print(f"Ocurrió un error al buscar el archivo: {error}")
        return None
def get_web_content_link(file_id):
    """Gets the webContentLink for a file.
    
    Args:
        file_id: ID of the file to get the link for.
    Returns:
        The webContentLink for the file, or None if it cannot be retrieved.
    """
    try:
        try :
            service = build("drive", "v3", credentials=credentials)
        except Exception as e:
            print("Error al autenticar ")
            print(e)
        # Obtener los metadatos del archivo
        file = service.files().get(fileId=file_id, fields='webContentLink').execute()

        # Retornar el webContentLink
        return file.get('webContentLink')
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None
def assing_date_expirity(file_name):
    # Establecer el valor predeterminado de la fecha de expiración
    default_expiry_date = None

    # Verificar el nombre del archivo para determinar la fecha de expiración predeterminada
    if 'REM_A' in file_name:
        # Si el nombre del archivo contiene 'REM_A', la fecha de expiración predeterminada será un mes más tarde que la fecha actual
        default_expiry_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    elif 'REM_P' in file_name:
        # Si el nombre del archivo contiene 'REM_P', la fecha de expiración predeterminada será tres meses más tarde que la fecha actual
        default_expiry_date = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
    else:
        # Para cualquier otro nombre de archivo, la fecha de expiración predeterminada será un año más tarde que la fecha actual
        default_expiry_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
    return default_expiry_date