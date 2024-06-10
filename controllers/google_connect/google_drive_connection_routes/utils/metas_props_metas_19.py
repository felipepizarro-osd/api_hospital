from datetime import datetime
from controllers.google_connect.google_drive_connection_routes.utils.files_drive_utils import get_latest_version_documents


def procesar_PROPS_metas_19(lista_json):
    kpi_documentos = []
        # Obtener los documentos más recientes de la colección
    documentos_kpi = get_latest_version_documents("KPI_METAS_SANITARIAS_19", "Metas_Sanitarias_19", False)
    for elemento in lista_json:
        kpi_name = elemento.get("kpi_Name")
        if not kpi_name:
            continue  # Saltar documentos sin kpi_Name



        valor = None
        peso_especifico = None
        meta = None

        for doc in documentos_kpi:
            if doc.get("nombre") == kpi_name:
                valor = doc.get("Valor")
                peso_especifico = doc.get("peso_especifico")
                meta = elemento.get("goal")

                break

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
            "meta": meta,
            "peso_especifico": peso_especifico,
            "numerador": numeradores,
            "denominador": denominadores,
            "id": elemento.get("_id"),
            "Valor": valor
        }
        
        kpi_documentos.append(kpi_documento)

    return kpi_documentos

def procesar_METAS_METAS19(lista_json):
    kpi_documentos = []
        # Obtener los documentos más recientes de la colección
    documentos_kpi = get_latest_version_documents("KPI_METAS_SANITARIAS_19", "Metas_Sanitarias_19", False)

    for elemento in lista_json:
        kpi_name = elemento.get("kpi_Name")
        if not kpi_name:
            continue  # Saltar documentos sin kpi_Name


        fecha_calculo = None
        valor_actual = None
        for doc in documentos_kpi:
            if doc.get("nombre") == kpi_name:
                fecha_calculo = doc.get("fecha_de_calculo")
                valor_actual = doc.get("Valor")
                break

        kpi_documento = {
            "kpi_name": kpi_name,
            "programa": elemento.get("program"),
            "categoria": elemento.get("component"),
            "procedencia": elemento.get("Verification_file"),
            "Valor esperado": elemento.get("goal"),
            "Valor actual": valor_actual,
            "Fecha de calculo": fecha_calculo,
            "Fecha de creacion del documento": datetime.now().strftime('%Y-%m-%d'),
            "id": elemento.get("_id"),
            "peso_especifico": elemento.get("weight")
        }

        kpi_documentos.append(kpi_documento)

    return kpi_documentos