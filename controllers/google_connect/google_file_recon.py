#this code is a function will return a specific file from google drive with a name that contains a specifics words
import io
import os.path
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import tempfile
from datetime import datetime
from database import get_client
#from Secret_manager.Secret_Manager import access_secret_version
import json
from dotenv import load_dotenv
load_dotenv()
# Script for calculate data from google drive files
#import Calculate_Data funcrion from Calculate_Data.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APP_ACCOUNT_FILE = os.getenv('CREDENTIALS')
print(APP_ACCOUNT_FILE)
client = get_client()
#from google_connect.Script_Data_Extraction.Calculate_Data import CalculateData
# If modifying these scopes, delete the file token.json.
# the scope is for access to REM values and spreadsheets and Poblation data of Vicuña uploaded in Google Drive
SCOPES = ["https://www.googleapis.com/auth/drive"]
def download_file(service,real_file_id):
  """Downloads a file
  Args:
      real_file_id: ID of the file to download
  Returns : IO object with location.

  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """
  try:
    # create drive api client
    file_id = real_file_id
    print('Download file')
    # pylint: disable=maybe-no-member
    request = service.files().get_media(fileId=file_id)
    file = io.BytesIO()
    downloader = MediaIoBaseDownload(file, request)
    done = False
    while done is False:
      status, done = downloader.next_chunk()
      print(f"Download {int(status.progress() * 100)}.")

  except HttpError as error:
    print(f"An error occurred: {error}")
    file = None

  return file.getvalue()

def authenticate():
    """Authenticates and returns Google Drive API service"""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            #secret_string = access_secret_version('app_id', "app_account")
            #secret_dict = json.loads(secret_string)
            flow = InstalledAppFlow.from_client_secrets_file(
                APP_ACCOUNT_FILE, scopes=SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    # Build and return the Drive v3 API service
    return build("drive", "v3", credentials=creds)
def find_file_id_by_name(service, file_name,folder_id):
    """Finds and returns the file ID for a given file name"""
    print(file_name)
    try:
        # Call the Drive v3 API to search for files with the given name
        query = f"'{folder_id}' in parents and name contains '{file_name}'"
        results = service.files().list(
            pageSize=20,
            fields="nextPageToken, files(id, name)",
            q=query,
            orderBy="modifiedTime desc",
        ).execute()
        print(results)
        # Extract the file ID from the results
        file_id = results['files'][0]['id']  # This gets the ID of the first file in the results
        print(file_id)
        
        file = service.files().get(fileId=file_id).execute()
        print(file)
        return file_id
    except HttpError as error:
        print(f"Ocurrió un error al buscar el archivo: {error}")
        return None

#this funcion search a file with the name and download to read from another script
def data_getter(file_name,service,folder_id):
     # filename : Nombre del archivo que deseas buscar
    file_id = find_file_id_by_name(service, file_name,folder_id)
    if file_id and validar_fecha_expiracion(file_id):
        print(f"El ID del archivo '{file_name}' es: {file_id}")
        #Descargar archivo
        file = download_file(service,file_id)
        
        # Read the file into a pandas DataFrame
        #df = pd.read_excel(file)
        #print(df.head())
        return file
def find_file_by_month(file_name, year, month, folder_id,service):
    """Finds and returns the file ID for a given file name and month"""
    print(f"Buscando archivo {file_name} en el mes {month} del año {year} en la carpeta con ID {folder_id}")
    try:
        #parsear a int el mes
        month = int(month)
        # Formatear el mes y el año en el formato 'YYYY-MM'
        month_str = f"{year}-{month:02d}"
        print(f"Mes formateado: {month_str}")
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
def data_getter_by_month(file_name,service,folder_id,month,year):
    print(f"Buscando archivo {file_name} en el mes {month} del año {year}")
    file_id = find_file_by_month(file_name,year,month,folder_id,service)
    if file_id and validar_fecha_expiracion(file_id):
        print(f"El ID del archivo '{file_name}' es: {file_id}")
        #Descargar archivo
        file = download_file(service,file_id)
        
        # Read the file into a pandas DataFrame
        #df = pd.read_excel(file)
        #print(df.head())
        return file


def share_file_with_service_account(file_id, service_account_email):
    """Shares a file with the service account.
    
    Args:
        file_id: ID of the file to share.
        service_account_email: Email of the service account.
    """
    try:
        service = authenticate()
        # Crear permiso de compartición
        permission = {
            'type': 'user',
            'role': 'reader',
            'emailAddress': service_account_email
        }

        # Asignar permiso al archivo
        service.permissions().create(
            fileId=file_id,
            body=permission,
            fields='id',
        ).execute()
    except HttpError as error:
        print(f"An error occurred: {error}")
#DEPRECATED
def validar_fecha_expiracion(document_id):
    try:
        db = client["Data_Origin"]
        db_collection = db["expirity_dates"]
        # Obtener el documento de la base de datos
        documento = db_collection.find_one({"drive_file_id": document_id})
        if documento:
            # Obtener la fecha de expiración del documento
            fecha_expiracion_str = documento.get("date_expirity")
            if fecha_expiracion_str:
                # Convertir la fecha de expiración a formato datetime
                fecha_expiracion = datetime.strptime(fecha_expiracion_str, "%Y-%m-%d").date()
                
                # Obtener la fecha actual
                fecha_actual = datetime.now().date()
                
                # Verificar si la fecha actual está dentro del rango de expiración
                if fecha_actual <= fecha_expiracion:
                    print("El documento no ha expirado.")
                    return True
                else:
                    return False
            else:
                print("El documento no tiene una fecha de expiración válida.")
                return False
        else:
            print("No se encontró el documento en la base de datos.")
            return False
    except Exception as e:
        print(f"Error al validar la fecha de expiración: {e}")
        return False