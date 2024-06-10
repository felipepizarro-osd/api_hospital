# print_env.py
import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener y imprimir las variables de entorno
service_account_file = os.getenv('SERVICE_ACCOUNT_FILE')

print(f"SERVICE_ACCOUNT_FILE: {service_account_file}")
