
from google.cloud import secretmanager
from google.api_core import exceptions as google
import json
from dotenv import load_dotenv
import os
load_dotenv()
mongo_connection_string = os.getenv("MONGO_URL")

def load_credentials_from_json(file_path):
    with open(file_path, 'r') as file:
        credentials = json.load(file)
    return credentials

def create_secret(project_id, secret_id, secret_value):
    client = secretmanager.SecretManagerServiceClient()

    parent = f"projects/{project_id}"
    secret = client.create_secret(
        request={
            "parent": parent,
            "secret_id": secret_id,
            "secret": {"replication": {"automatic": {}}}
        }
    )

    version = client.add_secret_version(
        request={"parent": secret.name, "payload": {"data": secret_value.encode("UTF-8")}}
    )

    print(f"Added secret version: {version.name}")
    
def create_secret_with_credentials(project_id, secret_id, credentials):
    # Convert the credentials dictionary to a JSON string
    credentials_str = json.dumps(credentials)
    create_secret(project_id, secret_id, credentials_str)
    
def list_secrets(project_id: str) -> None:
    """
    List all secrets in the given project.
    """

    # Import the Secret Manager client library.
    from google.cloud import secretmanager

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the parent project.
    parent = f"projects/{project_id}"

    # List all secrets.
    for secret in client.list_secrets(request={"parent": parent}):
        print(f"Found secret: {secret.name}")
def get_secret(project_id: str, secret_id: str) -> secretmanager.GetSecretRequest:
    """
    Get information about the given secret. This only returns metadata about
    the secret container, not any secret material.
    """

    # Import the Secret Manager client library.
    from google.cloud import secretmanager

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret.
    name = client.secret_path(project_id, secret_id)

    # Get the secret.
    response = client.get_secret(request={"name": name})

    # Get the replication policy.
    if "automatic" in response.replication:
        replication = "AUTOMATIC"
    elif "user_managed" in response.replication:
        replication = "MANAGED"
    else:
        raise Exception(f"Unknown replication {response.replication}")
    access_response = client.access_secret_version(name=f'projects/{project_id}/secrets/{secret_id}/versions/latest')

    # Print data about the secret.
    print(f"Got secret {response.name} with replication policy {replication}")    
    print(f"Secret data: {access_response.payload.data.decode('UTF-8')}")
if __name__ == '__main__':
    #create_secret(project_id, secret_id)
    #list_secrets(project_id)
    # Example usage (replace with your actual file path)
    credentials_file_path = "/Users/felipepizarro/Documents/GitHub/HSJD_BI/controllers/google_connect/credentials.json"
    credentials_service_path =  "/Users/felipepizarro/Documents/GitHub/HSJD_BI/controllers/google_connect/google_drive_connection_routes/visualizacionkpis-24cb54e74f96.json"
    credentials_app_google = load_credentials_from_json(credentials_file_path)
    credentials_service = load_credentials_from_json(credentials_service_path)
    #create_secret_with_credentials(project_id, secret_id, credentials)
    #get_secret(project_id, secret_id)
    #create_secret_with_credentials(project_id, "mongodb_connection_string2", 'mongodb+srv://User1:HSJD2024@cluster0.9icvydo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0&tlsAllowInvalidCertificates=true')
    #create_secret_with_credentials(project_id, "google_service_account", credentials_service)
    #create_secret_with_credentials(project_id, "app_account", credentials_app_google)
    #list_secrets(project_id)
    #access_secret_version(project_id, "app_account")
    #access_secret_version(project_id, "google_service_account")
    #access_secret_version(project_id, "mongodb_connection_string2")