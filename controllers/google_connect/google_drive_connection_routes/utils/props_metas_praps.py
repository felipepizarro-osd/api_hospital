from datetime import datetime
from controllers.google_connect.google_drive_connection_routes.utils.files_drive_utils import get_latest_version_documents


def procesar_PROPS_PRAPS(lista_json):
    #print("LISTA JSON: ",lista_json)
    kpi_documentos = []
    documentos_kpi = get_latest_version_documents("KPI_PRAPS", "Praps", False)
    for elemento in lista_json:
        #print("ELEMENTO: ",elemento)
        kpi_name = elemento.get("kpi_Name")
        if not kpi_name:
            continue  # Saltar documentos sin kpi_Name

        # Obtener los documentos más recientes de la colección

        #print("DOCUMENTOS KPI: ",documentos_kpi)
        # Buscar el valor actual del KPI en los documentos más recientes
        peso_especifico = None
        peso_relativo = None

        for doc in documentos_kpi:
            #print("DOC: ",doc)
            if doc.get("nombre") == kpi_name:
                #print("VALOR ==>",doc.get("Valor"))
                valor = doc.get("Valor")
                peso_especifico = doc.get("peso_especifico")
                peso_relativo = doc.get("peso_relativo")
                break
                # Iterar sobre las fórmulas para obtener numerador y denominador
        #print("PESO RELATIVO: ",peso_relativo)
        #print("PESO ESPECIFICO: ",peso_especifico)
        numeradores = []
        denominadores = []
        for formula in elemento.get("formula", []):
            for numerador in formula.get("numerator", []):
                numeradores.append(numerador.get("Name"))
            for denominador in formula.get("denominator", []):
                denominadores.append(denominador.get("Name"))
        kpi_documento = {
            "kpi_name": kpi_name,
            "programa": elemento.get("program"),
            "categoria": elemento.get("component"),
            "procedencia":  elemento.get("Verification_file"),
            "peso_relativo": peso_relativo,
            "peso_especifico": peso_especifico,
            "numerador": numeradores,
            "denominador": denominadores,
            "id": elemento.get("_id"),
            "Valor": valor
        }
        
        kpi_documentos.append(kpi_documento)

    return kpi_documentos

def procesar_METAS_PRAPS(lista_json):
    #print("LISTA JSON: ",lista_json)
    kpi_documentos = []
    documentos_kpi = get_latest_version_documents("KPI_PRAPS", "Praps", False)
    for elemento in lista_json:
        #print("ELEMENTO: ",elemento)
        kpi_name = elemento.get("kpi_Name")
        if not kpi_name:
            continue  # Saltar documentos sin kpi_Name

        # Obtener los documentos más recientes de la colección

        #print("DOCUMENTOS KPI: ",documentos_kpi)
        # Buscar el valor actual del KPI en los documentos más recientes
        fecha_calculo = None
        valor_actual = None
        for doc in documentos_kpi:
            #print("DOC: ",doc)
            if doc.get("nombre") == kpi_name:
                #print("VALOR ==>",doc.get("Valor"))
                fecha_calculo = doc.get("fecha_de_calculo")
                valor_actual = doc.get("Valor")
                break

        kpi_documento = {
            "kpi_name": kpi_name,
            "programa": elemento.get("program"),
            "categoria": elemento.get("component"),
            "procedencia":  elemento.get("Verification_file"),
            "Valor esperado": None,
            "Valor actual": valor_actual,
            "Fecha de calculo": fecha_calculo,
            "Fecha de creacion del documento": datetime.now().strftime('%Y-%m-%d'),
            "id": elemento.get("_id"),
            
        }
        
        kpi_documentos.append(kpi_documento)

    return kpi_documentos