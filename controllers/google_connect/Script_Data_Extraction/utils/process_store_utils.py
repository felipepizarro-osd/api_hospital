import pprint
from pymongo import MongoClient
from database import get_client
from datetime import datetime
from controllers.google_connect.google_drive_connection_routes.utils.files_drive_utils import get_latest_version_documents, json_serializable_documents
client = get_client()
def generate_collection_name(collection_name):
    # Genera un nombre de colección único con la fecha actual
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    return f"{collection_name}_{fecha_actual}"

def get_unique_collection_name(client, db_name, collection_name,recalculated=False, recalculation_month=None):
    # Genera un nombre de colección único y verifica si ya existe
    base_collection_name = generate_collection_name(collection_name)
    if recalculated and recalculation_month:
        base_collection_name = f"{base_collection_name}_recalculated_{recalculation_month}"

    new_collection_name = f"{base_collection_name}_v1"
    existing_collections = client[db_name].list_collection_names()
    version = 2
    while new_collection_name in existing_collections:
        new_collection_name = f"{base_collection_name}_v{version}"
        version += 1
    return new_collection_name
    
def process_and_store_kpis_general_metas1(ChangetoMeta18=False):
   #db_source = client.KPI_GOALS
    if ChangetoMeta18:
        collection_source = get_latest_version_documents("KPI_GOALS", "PROPS_KPI_METAS_18", True)
        print(collection_source)
    else:
        collection_source = get_latest_version_documents("KPI_GOALS", "PROPS_KPI_METAS_19", True)
        print(collection_source)
    db_target = client.GENERAL_PRAPS

    # Consulta para obtener los documentos de la colección
    kpis_cursor = collection_source.find()

    # Convertir el cursor a una lista
    kpis_json = list(kpis_cursor)

    # Inicialización de las estructuras
    programs_structure = {"programs": []}
    programas = {}

    # Organizar datos en programas
    for kpi in kpis_json:
        programa = kpi['programa']
        meta = kpi.get('meta')
        peso_especifico = kpi['peso_especifico']
        valor_kpi = kpi.get('Valor', 0)
        print(valor_kpi, "valor_kpi", kpi['kpi_name'], "kpi_name", programa, "programa", meta, "meta", peso_especifico, "peso_especifico")
        

        if valor_kpi == 'DIVISION POR CERO':
            valor_kpi = 0.0  # Manejar "DIVISION POR CERO" como 0

        # Estructura de programas
        if programa not in programas:
            programas[programa] = {
                'program': programa,
                'Valor': 0,
                'meta': meta,
                'peso_especifico': peso_especifico,
                'meta_anual': None,
                'meta_al_corte': None,
                'realizado': None,
                'indicators': []
            }

        programas[programa]['indicators'].append({
            'kpi_name': kpi['kpi_name'],
            'peso_especifico': peso_especifico,
            'valor_kpi': valor_kpi
        })

    # Convertir las estructuras a la forma solicitada
    programs_structure["programs"] = list(programas.values())

    # Calcular los valores de los programas
    for program in programs_structure['programs']:
        indicators = program['indicators']

        # Calcular el valor del programa
        valor_programa = sum(ind['valor_kpi'] * ind['peso_especifico'] for ind in indicators)
        program['Valor'] = valor_programa

    # Generar nombres de colecciones únicos y versionarlas
    if ChangetoMeta18:
        programs_collection_name = get_unique_collection_name(client, db_target.name, "GENERAL_PROGRAMS_METAS_18", recalculated=False)
    else:
        programs_collection_name = get_unique_collection_name(client, db_target.name, "GENERAL_PROGRAMS_METAS_19", recalculated=False)

    try:
        # Insertar los datos procesados en las colecciones de destino
        db_target[programs_collection_name].insert_many(programs_structure["programs"])
        return True
    except Exception as e:
        print(f"Error al insertar en la base de datos: {e}")
        return False
    
    
def process_and_store_kpis_general_praps1():
    collection_source = get_latest_version_documents("KPI_GOALS", "PROPS_KPI_PRAPS", True)
    db_target = client.GENERAL

    # Consulta para obtener los documentos de la colección
    kpis_cursor = collection_source.find()

    # Convertir el cursor a una lista
    kpis_json = list(kpis_cursor)

    # Inicialización de las estructuras
    programs_structure = {"total_realizado_todos_programas": 0, "programs": []}
    programs = {}
    components = {}

    # Organizar datos en programas y componentes
    for kpi in kpis_json:
        programa = kpi['programa']
        categoria = kpi['categoria']  # Si no hay categorías, este campo debería ser None o similar.
        peso_relativo = kpi['peso_relativo']
        peso_especifico = kpi['peso_especifico']
        valor_kpi = kpi.get('Valor', 0)

        if valor_kpi == 'DIVISION POR CERO':
            valor_kpi = 0.0  # Manejar "DIVISION POR CERO" como 0

        # Estructura de programas
        if programa not in programs:
            programs[programa] = {
                'program': programa,
                'Valor': 0,
                'meta': None,
                'meta_anual': None,
                'meta_al_corte': None,
                'realizado': 0,
                'components': {}
            }

        # Estructura de componentes
        if categoria not in programs[programa]['components']:
            programs[programa]['components'][categoria] = {
                'component': categoria,
                'peso_relativo': peso_relativo,
                'Valor': 0,
                'indicators': []
            }

        programs[programa]['components'][categoria]['indicators'].append({
            'kpi_name': kpi['kpi_name'],
            'peso_especifico': peso_especifico,
            'valor_kpi': valor_kpi,
            'realizado': valor_kpi * peso_especifico  # Calcular realizado como valor_kpi * peso_especifico
        })

    # Convertir las estructuras a la forma solicitada
    for programa, programa_data in programs.items():
        for categoria, component_data in programa_data['components'].items():
            # Calcular el valor del componente
            valor_componente = sum(ind['valor_kpi'] * ind['peso_especifico'] for ind in component_data['indicators'])
            component_data['Valor'] = valor_componente

            # Calcular el total realizado del componente
            realizado_componente = sum(ind['realizado'] for ind in component_data['indicators'])
            component_data['realizado'] = realizado_componente

        programs_structure["programs"].append({
            'program': programa,
            'meta': programa_data['meta'],
            'meta_anual': programa_data['meta_anual'],
            'meta_al_corte': programa_data['meta_al_corte'],
            'realizado': sum(comp['Valor'] * comp['peso_relativo'] for comp in programa_data['components'].values()),
            'components': list(programa_data['components'].values())
        })

    # Calcular el total de realizado para todos los programas
    total_realizado_todos_programas = sum(program['realizado'] for program in programs_structure["programs"])
    
    # Actualizar el valor de total_realizado_todos_programas en programs_structure
    programs_structure["total_realizado_todos_programas"] = total_realizado_todos_programas
    
    # Generar nombres de colecciones únicos y versionarlas
    programs_collection_name = get_unique_collection_name(client, db_target.name, "GENERAL_PROGRAMS_PRAPS", recalculated=False)
    print(programs_structure)
    try:
        # Insertar los datos procesados en las colecciones de destino
        db_target[programs_collection_name].insert_many(programs_structure["programs"])
        return True
    except Exception as e:
        print(f"Error al insertar en la base de datos: {e}")
        return False

def process_and_store_kpis_general_praps():
    collection_source = get_latest_version_documents("KPI_GOALS", "PROPS_KPI_PRAPS", True)
    db_target = client.GENERAL

    # Consulta para obtener los documentos de la colección
    kpis_cursor = collection_source.find()

    # Convertir el cursor a una lista
    kpis_json = list(kpis_cursor)

    # Inicialización de las estructuras
    programs_structure = {"total_realizado_todos_programas": 0, "programs": []}
    programs = {}
    components = {}

    # Organizar datos en programas y componentes
    for kpi in kpis_json:
        programa = kpi['programa']
        categoria = kpi['categoria']  # Si no hay categorías, este campo debería ser None o similar.
        peso_relativo = kpi['peso_relativo']
        peso_especifico = kpi['peso_especifico']
        valor_kpi = kpi.get('Valor', 0)

        if valor_kpi == 'DIVISION POR CERO':
            valor_kpi = 0.0  # Manejar "DIVISION POR CERO" como 0

        # Estructura de programas
        if programa not in programs:
            programs[programa] = {
                'program': programa,
                'Valor': 0,
                'meta': None,
                'meta_anual': None,
                'meta_al_corte': None,
                'realizado': 0,
                'components': {}
            }

        # Estructura de componentes
        if categoria not in programs[programa]['components']:
            programs[programa]['components'][categoria] = {
                'component': categoria,
                'peso_relativo': peso_relativo,
                'Valor': 0,
                'indicators': []
            }

        programs[programa]['components'][categoria]['indicators'].append({
            'kpi_name': kpi['kpi_name'],
            'peso_especifico': peso_especifico,
            'valor_kpi': valor_kpi,
            'realizado': valor_kpi * peso_especifico  # Calcular realizado como valor_kpi * peso_especifico
        })

    # Convertir las estructuras a la forma solicitada
    for programa, programa_data in programs.items():
        for categoria, component_data in programa_data['components'].items():
            # Calcular el valor del componente
            valor_componente = sum(ind['valor_kpi'] * ind['peso_especifico'] for ind in component_data['indicators'])
            component_data['Valor'] = valor_componente

            # Calcular el total realizado del componente
            realizado_componente = sum(ind['realizado'] for ind in component_data['indicators'])
            component_data['realizado'] = realizado_componente

        programs_structure["programs"].append({
            'program': programa,
            'meta': programa_data['meta'],
            'meta_anual': programa_data['meta_anual'],
            'meta_al_corte': programa_data['meta_al_corte'],
            'realizado': sum(comp['Valor'] * comp['peso_relativo'] for comp in programa_data['components'].values()),
            'components': list(programa_data['components'].values())
        })

    # Calcular el total de realizado para todos los programas
    total_realizado_todos_programas = sum(program['realizado'] for program in programs_structure["programs"])
    
    # Actualizar el valor de total_realizado_todos_programas en programs_structure
    programs_structure["total_realizado_todos_programas"] = total_realizado_todos_programas
    
    # Crear el resumen de todos los programas PRAPS
    resumen_praps = {
        'program': 'PRAPS',
        'meta': None,
        'meta_anual': None,
        'meta_al_corte': None,
        'realizado': total_realizado_todos_programas,
        'fecha_calculo': datetime.now()
    }

    # Añadir el resumen al principio de la estructura de programas
    programs_structure["programs"].insert(0, resumen_praps)
    
    # Generar nombres de colecciones únicos y versionarlas
    programs_collection_name = get_unique_collection_name(client, db_target.name, "GENERAL_PROGRAMS_PRAPS", recalculated=False)

    try:
        # Insertar los datos procesados en las colecciones de destino
        db_target[programs_collection_name].insert_many(programs_structure["programs"])
        return True
    except Exception as e:
        print(f"Error al insertar en la base de datos: {e}")
        return False

    
def process_and_store_kpis_general_metas(ChangetoMeta18=False):
    if ChangetoMeta18:
        collection_source = get_latest_version_documents("KPI_GOALS", "PROPS_KPI_METAS_18", True)
    else:
        collection_source = get_latest_version_documents("KPI_GOALS", "PROPS_KPI_METAS_19", True)

    db_target = client.GENERAL

    # Consulta para obtener los documentos de la colección
    kpis_cursor = collection_source.find()

    # Convertir el cursor a una lista
    kpis_json = list(kpis_cursor)

    # Inicialización de las estructuras
    programs_structure = {"programs": []}
    programas = {}

    # Organizar datos en programas
    for kpi in kpis_json:
        programa = kpi['programa']
        meta = kpi.get('meta')
        peso_especifico = kpi['peso_especifico']
        valor_kpi = kpi.get('Valor', 0)

        if valor_kpi == 'DIVISION POR CERO':
            valor_kpi = 0.0  # Manejar "DIVISION POR CERO" como 0

        # Estructura de programas
        if programa not in programas:
            programas[programa] = {
                'program': programa,
                'Valor': 0,
                'meta': meta,
                'meta_anual': None,
                'meta_al_corte': None,
                'realizado': 0,
                'indicators': [],
                'fecha_calculo': datetime.now()
            }

        programas[programa]['indicators'].append({
            'kpi_name': kpi['kpi_name'],
            'peso_especifico': peso_especifico,
            'valor_kpi': valor_kpi,
            'realizado': valor_kpi * peso_especifico  # Calcular realizado como valor_kpi * peso_especifico
        })

    # Convertir las estructuras a la forma solicitada
    programs_structure["programs"] = list(programas.values())

    # Calcular los valores de los programas
    for program in programs_structure['programs']:
        indicators = program['indicators']

        # Calcular el valor del programa
        valor_programa = sum(ind['valor_kpi'] * ind['peso_especifico'] for ind in indicators)
        program['Valor'] = valor_programa

        # Calcular el total realizado
        realizado_programa = sum(ind['realizado'] for ind in indicators)
        program['realizado'] = realizado_programa

    # Generar nombres de colecciones únicos y versionarlas
    if ChangetoMeta18:
        programs_collection_name = get_unique_collection_name(client, db_target.name, "GENERAL_PROGRAMS_METAS_18", recalculated=False)
    else:
        programs_collection_name = get_unique_collection_name(client, db_target.name, "GENERAL_PROGRAMS_METAS_19", recalculated=False)

    try:
        # Insertar los datos procesados en las colecciones de destino
        db_target[programs_collection_name].insert_many(programs_structure["programs"])
        return True
    except Exception as e:
        print(f"Error al insertar en la base de datos: {e}")
        return False