from google.cloud import secretmanager
from dotenv import load_dotenv
import os
load_dotenv()

project_id = os.getenv("PROJECT_ID")
def access_secret_version(project_id, secret_id, version_id="latest"):
    client = secretmanager.SecretManagerServiceClient()

    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})

    payload = response.payload.data.decode("UTF-8")
    #print(f"Secret payload: {payload}")

    return payload
