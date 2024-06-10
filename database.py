import os
from pymongo import MongoClient
from dotenv import load_dotenv
from Secret_manager.Secret_Manager import access_secret_version
load_dotenv()
MONGODB_URI = os.getenv('MONGODB_URI')
MONGO_CLUSTER = os.getenv('MONGO_URL')
#connection_string = access_secret_version('app_id', "mongodb_connection_string2")

#connection_string = connection_string.strip('"')
#client = MongoClient(connection_string)
#print(f"Connection string: {connection_string}")
#print(MONGO_URL)
def get_database():
    client = MongoClient("mongodb+srv://felipe:198252021298@cluster0.sa4li7n.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0&tlsAllowInvalidCertificates=true")
    client.server_info()
    return client
def get_client():
    try:
        client = MongoClient(MONGO_CLUSTER)
        client.server_info()
        return client
    except Exception as e:
        print(f"Error al conectar a la base de datos: {str(e)}")
        return None
    
def get_user_database():
    client = MongoClient(MONGODB_URI)
    return client.get_database("Vicuna_KPIs_Users")
