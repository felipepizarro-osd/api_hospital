from database import get_client
client = get_client()

def upload_file_parameters(file_name, date_expirity, drive_file_id):
    
    try:
        # Cambia esto según la configuración de tu MongoDB
        db = client['Data_Origin']  # Cambia 'nombre_de_tu_base_de_datos' al nombre de tu base de datos
        collection = db['expirity_dates']  # Cambia 'nombre_de_tu_coleccion' al nombre de tu colección
        
        # Crear el documento a insertar en la colección
        documento = {"nombre_archivo": file_name, "date_expirity": date_expirity, "drive_file_id": drive_file_id}
        
        # Insertar el documento en la colección
        result = collection.insert_one(documento)
        
        # Imprimir el ID del documento insertado
        print("ID del documento insertado:", result.inserted_id)
        
        # Cerrar la conexión con la base de datos
        client.close()
        
        return True
    except Exception as e:
        print("Error al guardar datos en MongoDB:", e)
        return False