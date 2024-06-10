import os.path
import sys
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from datetime import datetime
import tempfile
from googleapiclient.http import MediaIoBaseDownload
import io
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google_connect.Script_Data_Extraction.Calculate_Data import CalculateData

SCOPES = ['https://www.googleapis.com/auth/drive']
credentials = 'controllers/google_connect/credential.json'
try:
	# Create a Google Drive service object
    service = build('drive', 'v3', credentials=credentials)
except Exception as e:
    print(f"Error al crear el servicio: {e}")
    service = None

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
def find_file_id_by_name(service, file_name):
    """Finds and returns the file ID for a given file name"""
    print(file_name)
    try:
        # Call the Drive v3 API to search for files with the given name
        results = service.files().list(
            pageSize=20,
            fields="nextPageToken, files(id, name)",
            q=f"name contains '{file_name}'",
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
def data_getter(file_name,service):
     # filename : Nombre del archivo que deseas buscar
    file_id = find_file_id_by_name(service, file_name)
    if file_id:
        print(f"El ID del archivo '{file_name}' es: {file_id}")
        #Descargar archivo
        file = download_file(service,file_id)
        
        # Read the file into a pandas DataFrame
        #df = pd.read_excel(file)
        #print(df.head())
        return file
def Calcular():

    REMA = tempfile.NamedTemporaryFile(delete=False) 
    REMA.write(data_getter('REMA',service))
    #CalculateData(REMA)
    REMP = tempfile.NamedTemporaryFile(delete=False)
    REMP.write(data_getter('REMP',service))
    POBLATION = tempfile.NamedTemporaryFile(delete=False)
    POBLATION.write(data_getter('Poblacion',service))
    # Ejemplo de uso: buscar el ID de un archivo por su nombre
    #Send to calculate the kpi values with this data 
    #CalculateData(REMA,REMP,POBLATION)
    try:
        sucess = CalculateData(REMA,REMP,POBLATION)

        REMA.close()
        REMP.close()
        POBLATION.close()
        if sucess:
            return True
        else:
            return False
    except Exception as e: 
        print("Error al calcular los datos")
        print(e)
        return False