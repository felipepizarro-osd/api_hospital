from controllers.google_connect.google_drive_connection_routes.utils.files_drive_utils import get_latest_version_documents
from controllers.google_connect.Script_Data_Extraction.utils.process_store_utils import get_unique_collection_name
from database import get_client
from datetime import datetime
import re
client = get_client()
# Estructura de programas y componentes
programs_structure = {
    "programs": [
        {
            "program": "Programa apoyo a la gestion en el nivel primario",
            "components": [
                {
                    "component": "COMPONENTE 2: Apoyo al Programa de Salud Cardiovascular",
                    "Valor": 0,
                    "peso_relativo": 0.25
                },
                {
                    "component": "COMPONENTE 1: Mejoramiento de la APS",
                    "Valor": 0,
                    "peso_relativo": 0.25
                },
                {
                    "component": "COMPONENTE 3: Apoyo diagnóstico y tratamiento de patologías prevalentes",
                    "Valor": 0,
                    "peso_relativo": 0.25
                },
                {
                    "component": "COMPONENTE 4: Apoyo a las acciones de salud en el nivel primario de atención en establecimientos dependientes del servicio de salud",
                    "Valor": 0,
                    "peso_relativo": 0.25
                }
            ]
        },
        {
            "program": "Programa GES Odontologico",
            "components": [
                {
                    "component": "ATENCION DENTAL EN NINHOS",
                    "Valor": 0,
                    "peso_relativo": 0.32
                },
                {
                    "component": "ATENCION DENTAL EN EMBARAZADA",
                    "Valor": 0,
                    "peso_relativo": 0.32
                },
                {
                    "component": "ATENCION DENTAL DE URGENCIA",
                    "Valor": 0,
                    "peso_relativo": 0.04
                },
                {
                    "component": "ATENCION ODONTOLOGICA ADULTOS",
                    "Valor": 0,
                    "peso_relativo": 0.32
                }
            ]
        },
        {
            "program": "Programa Odontológico Integral",
            "components": [
                {
                    "component": "Programa Odontológico Integral",
                    "Valor": 0,
                    "peso_relativo": 0.3
                },
                {
                    "component": "MÁS SONRISAS PARA CHILE",
                    "Valor": 0,
                    "peso_relativo": 0.3
                },
                {
                    "component": "ATENCIÓN ODONTOLÓGICA INTEGRAL A ESTUDIANTES QUE CURSEN ENSEÑANZA MEDIA Y/O SU EQUIVALENTE",
                    "Valor": 0,
                    "peso_relativo": 0.2
                },
                {
                    "component": "ATENCIÓN ODONTOLÓGICA DOMICILIARIA A PERSONAS CON DEPENDENCIA SEVERA",
                    "Valor": 0,
                    "peso_relativo": 0.2
                }
            ]
        }
    ]
}
# Función para validar el formato del JSON
def validar_json(json_data):
    # Verificar si el campo 'formula' no contiene espacios
    if 'formula' in json_data and ' ' in json_data['formula']:
        return False, 'La fórmula no debe contener espacios.'

    # Verificar si la fórmula contiene el carácter '/'
    if '/' not in json_data['formula']:
        return False, 'La fórmula debe contener el carácter "/".'
    
    # Verificar si los numeradores y denominadores están correctamente referenciados
    numeradores = [num['Name'] for num in json_data['formula'][0]['numerator']]
    denominadores = [den['Name'] for den in json_data['formula'][0]['denominator']]
    for num in numeradores:
        if num not in json_data['formula'][0]['formula']:
            return False, f'El numerador "{num}" no está correctamente referenciado en la fórmula.'
    for den in denominadores:
        if den not in json_data['formula'][0]['formula']:
            return False, f'El denominador "{den}" no está correctamente referenciado en la fórmula.'

    return True, None
def corregir_y_validar_json(json_data):
    # Eliminar espacios en blanco en la fórmula
    if 'formula' in json_data['formula'][0]:
        formula = json_data['formula'][0]['formula'].replace(' ', '')

    # Verificar si la fórmula contiene el carácter '/'
    if '/' not in formula:
        return False, 'La fórmula debe contener el carácter "/".', json_data
    
    # Separar la fórmula en numerador y denominador
    partes_formula = formula.split('/')
    if len(partes_formula) != 2:
        return False, 'La fórmula debe contener exactamente un carácter "/".', json_data

    numerador, denominador = partes_formula

    # Agregar paréntesis si hay operaciones en el numerador o denominador
    if '+' in numerador or '-' in numerador or '*' in numerador:
        numerador = f'({numerador})'
    if '+' in denominador or '-' in denominador or '*' in denominador:
        denominador = f'({denominador})'

    # Reconstruir la fórmula
    formula_corregida = f'{numerador}/{denominador}'
    json_data['formula'][0]['formula'] = formula_corregida

    # Obtener los nombres de los numeradores y denominadores de la fórmula
    formula_numeradores = [num['Name'].replace(' ', '') for num in json_data['formula'][0]['numerator']]
    formula_denominadores = [den['Name'].replace(' ', '') for den in json_data['formula'][0]['denominator']]

    # Verificar si los numeradores y denominadores están correctamente referenciados
    for num in formula_numeradores:
        if num not in formula_corregida:
            return False, f'El numerador "{num}" no está correctamente referenciado en la fórmula.', json_data
    for den in formula_denominadores:
        if den not in formula_corregida:
            return False, f'El denominador "{den}" no está correctamente referenciado en la fórmula.', json_data

    return True, None, json_data

def calculate_program_compliance(programa_decoded, documents):
    print(programa_decoded)
    print(documents)
    # Encuentra el programa solicitado
    programa = next((p for p in programs_structure["programs"] if p["program"] == programa_decoded), None)
    
    if not programa:
        return None, 'El programa solicitado no se encuentra en la estructura definida.'
    
    # Calcula el valor ponderado de cada componente
    for componente in programa["components"]:
        print("LOS COMPONENTES SON: ",componente)
        # Encuentra los indicadores que pertenecen a este componente
        indicadores = [doc for doc in documents if doc.get("Componente/programa") == componente["component"]]
        
        # Calcula el valor ponderado del componente
        valor_componente = 0
        for indicador in indicadores:
            print("LOS INDICADORES SON: ",indicador)
            valor = indicador.get("Valor")
            print("VALOR: ",valor)
            peso_especifico = indicador.get("peso_relativo", 0)
            print("PESO ESPECIFICO: ",peso_especifico)
            if isinstance(valor, str) and valor == "DIVISION POR CERO":
                continue
            try:
                valor = float(valor)
                valor_componente += valor * peso_especifico
            except ValueError:
                continue
        
        # Asigna el valor calculado al componente
        componente["Valor"] = valor_componente
    
    # Calcula el valor ponderado del programa
    valor_programa = sum(componente["Valor"] * componente["peso_relativo"] for componente in programa["components"])
    print("VALOR DEL PROGRAMA: ",valor_programa)
    result = {
        "program": programa_decoded,
        "valor_programa": valor_programa,
        "components": programa["components"]
    }
    print("RESULTADO =>  ",result)
    return result, None

def procesar_single_values(json_data):
    print("JSON DATA: ",json_data)
    datos_faltantes = []
    for elemento in json_data:
        for formula in elemento.get("formula", []):
            for num in formula.get("numerator", []):
                if num.get("source") is None or num.get("key") is None:
                    datos_faltantes.append({
                        "kpi_Name": elemento.get("kpi_Name"),
                        "program": elemento.get("program"),
                        "component": elemento.get("component"),
                        "campo_faltante": "Numerador",
                        "nombre": num.get("Name"),
                        "Value": None,
                        "Fecha": None,
                        "versions": []
                    })
            for denom in formula.get("denominator", []):
                if denom.get("source") is None or denom.get("key") is None:
                    datos_faltantes.append({
                        "kpi_Name": elemento.get("kpi_Name"),
                        "program": elemento.get("program"),
                        "component": elemento.get("component"),
                        "campo_faltante": "Denominador",
                        "nombre": denom.get("Name"),
                        "Value": None,
                        "Fecha": None,
                        "versions": []
                    })
    return datos_faltantes

def insertar_kpi_en_mongodb(kpi_documentos, collection_name):
    db = client["KPI_GOALS"]
    # Generar un nombre único para la colección
    unique_collection_name = get_unique_collection_name(client, db.name, collection_name)

    if kpi_documentos:
        collection = db[unique_collection_name]
        collection.insert_many(kpi_documentos)
        return True
    else:
        return False

def get_kpi_historical_data(database_name, collection_prefix, kpi_name):
    db = client[database_name]
    
    # Define el patrón para encontrar las colecciones
    collection_pattern = re.compile(rf'^{collection_prefix}_(\d{{4}}-\d{{2}}-\d{{2}})_v(\d+)$')
    
    # Encuentra las colecciones que coinciden con el patrón
    matching_collections = db.list_collection_names(filter={'name': {'$regex': collection_pattern}})
    
    kpi_historical_data = []

    for collection_name in matching_collections:
        collection = db[collection_name]
        
        # Buscar documentos con el KPI específico en la colección actual
        documents = collection.find({"nombre": kpi_name})
        
        for doc in documents:
            kpi_data = {
                "nombre": doc.get("nombre"),
                "procedencia": collection_name,
                "valor_esperado": None,
                "valor_actual": doc.get("Valor"),
                "porcentaje_cumplimiento": doc.get("Valor") * doc.get("peso_especifico")  # Inicialmente vacío, puede ser actualizado después
            }
            kpi_historical_data.append(kpi_data)
    
    return kpi_historical_data

def get_praps_historical_data(database_name, collection_prefix):
    db = client[database_name]

    # Define el patrón para encontrar las colecciones
    collection_pattern = re.compile(rf'^{collection_prefix}_(\d{{4}}-\d{{2}}-\d{{2}})_v(\d+)$')
    
    # Encuentra las colecciones que coinciden con el patrón
    matching_collections = db.list_collection_names(filter={'name': {'$regex': collection_pattern}})
    
    praps_historical_data = []

    for collection_name in matching_collections:
        collection = db[collection_name]
        
        # Buscar documentos de programas PRAPS en la colección actual
        documents = collection.find({"program": "PRAPS"})
        
        for doc in documents:
            praps_data = {
                "_id": str(doc.get("_id")),
                "fecha_calculo": doc.get("fecha_calculo").strftime("%a, %d %b %Y %H:%M:%S GMT") if doc.get("fecha_calculo") else None,
                "meta": doc.get("meta"),
                "meta_al_corte": doc.get("meta_al_corte"),
                "meta_anual": doc.get("meta_anual"),
                "program": doc.get("program"),
                "realizado": doc.get("realizado")
            }
            praps_historical_data.append(praps_data)
    
    return praps_historical_data

def get_Metas_historical_data(database_name, collection_prefix, program_name):
    db = client[database_name]

    # Define el patrón para encontrar las colecciones
    collection_pattern = re.compile(rf'^{collection_prefix}_(\d{{4}}-\d{{2}}-\d{{2}})_v(\d+)$')
    
    # Encuentra las colecciones que coinciden con el patrón
    matching_collections = db.list_collection_names(filter={'name': {'$regex': collection_pattern}})
    
    meta_historical_data = []

    for collection_name in matching_collections:
        collection = db[collection_name]
        
        # Buscar documentos de programas PRAPS en la colección actual
        documents = collection.find({"program": program_name})
        #print("DOCUMENTOS: ",documents)
        for doc in documents:
            print("DOC: ",doc.get("fecha_calculo"))
            metas_data = {
                "_id": str(doc.get("_id")),
                "fecha_calculo": doc.get("fecha_calculo").strftime("%a, %d %b %Y %H:%M:%S GMT") if doc.get("fecha_calculo") else None,
                "meta": doc.get("meta"),
                "meta_al_corte": doc.get("meta_al_corte"),
                "meta_anual": doc.get("meta_anual"),
                "program": doc.get("program"),
                "realizado": doc.get("realizado"),
                
            }
            meta_historical_data.append(metas_data)
    
    return meta_historical_data