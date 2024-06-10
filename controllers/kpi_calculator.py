from flask import Blueprint, jsonify, request, Response, abort

from database import get_database
from bson import json_util
from bson.objectid import ObjectId
from math import *
import pandas as pd
from datetime import datetime
from pymongo import ASCENDING

import time


kpi_calculator_bp = Blueprint('kpi_calculator', __name__, url_prefix="")

db = get_database()
single_value_collection = db["single_values"]
kpi_goals_collection = db["kpi_goals"]
kpi_formulas_collection = db["kpi_formulas"]
calculated_kpi_collection = db["calculated_kpi"]


df_list = []
df_list_names = []


### Google drive API
import os
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google.oauth2.service_account import Credentials


### Google Cloud API
creds = Credentials.from_service_account_file('visualizacionkpis-6ebee7f67482.json')


SCOPES = ['https://www.googleapis.com/auth/drive.readonly',
          'https://www.googleapis.com/auth/spreadsheets.readonly']


service_sheets = build('sheets', 'v4', credentials=creds)

REM_A_spreadsheet_id = None
REM_P_spreadsheet_id = None
Poblacion_Estimada_spreadsheet_id = None

single_values_list = None

get_parameter_count = 0

def read_single_cell_drive( document_type,sheet, cell, month_year_date):
    try:
        print(f"read_single_cell_drive({document_type},{sheet},{cell},{month_year_date})")
        document_spreadsheet_id = ''
        if document_type == 'REM-A':
            document_spreadsheet_id = REM_A_spreadsheet_id
        elif document_type == 'REM-P':
            document_spreadsheet_id = REM_P_spreadsheet_id
        elif document_type == 'Poblacion Estimada':
            document_spreadsheet_id = Poblacion_Estimada_spreadsheet_id
            

        
        if document_spreadsheet_id:
            print(f'Getting value from {document_type} {document_spreadsheet_id}')
            # Realizar una solicitud para leer el valor de la celda especificada
            cell_data = service_sheets.spreadsheets().values().get(spreadsheetId=document_spreadsheet_id,
                                                                   range=f"{sheet}!{cell}").execute()
            # Obtener el valor de la celda
            cell_value = cell_data.get('values', [])

            # Si la celda tiene un valor, retornarlo, de lo contrario, retornar None
            return cell_value[0][0] if cell_value else None

    except HttpError as error:
        print(f'Ocurrió un error: {error}')
        return None


def read_multiple_cell_drive( document_type, sheet, cell1, cell2, month_year_date):
    try:
        print(f"read_multiple_cell_drive({document_type, sheet, cell1, cell2, month_year_date})")
        document_spreadsheet_id = ''
        if document_type == 'REM-A':
            document_spreadsheet_id = REM_A_spreadsheet_id
        elif document_type == 'REM-P':
            document_spreadsheet_id = REM_P_spreadsheet_id
        elif document_type == 'Poblacion Estimada':
            document_spreadsheet_id = Poblacion_Estimada_spreadsheet_id
        

        if document_spreadsheet_id:
            print(f'Getting value from {document_spreadsheet_id}')
            # Realizar una solicitud para leer los valores del rango de celdas especificado
            range_name = f"{sheet}!{cell1}:{cell2}"
            cell_data = service_sheets.spreadsheets().values().get(spreadsheetId=document_spreadsheet_id,
                                                                   range=range_name).execute()
            # Obtener los valores de las celdas
            cell_values = cell_data.get('values', [])

            # Sumar los valores de las celdas en el rango
            suma = 0
            for row in cell_values:
                for cell_value in row:
                    if cell_value.isdigit():
                        suma += float(cell_value)

            return suma
        

    except HttpError as error:
        print(f'Ocurrió un error: {error}')
        return None


def searchDocument(document):
    print(f'Searching: {document}')
    try:
        service_drive = build('drive', 'v3', credentials=creds)

        directory_id = ''
       
  
        # if the document string contains "REM-A" directory = rem_A_directory_id, if it contains "REM-P" directory = rem_P_directory_id
        if "REM-A" in document:
            directory_id = '1KIJ9FyTq6_MBXaTzV4a9ybepKJwHts73'
        elif "REM-P" in document:
            directory_id = '1JCJwJhagHPbXGI8IiOKHpUOpPnEP3yQF'
        elif "Poblacion Estimada" in document:
            directory_id = '1oUR7gjU1SB-9gmgu5fp8C9R4t_NOlmR8'
        else:
            print("El documento no corresponde a REM-A ni REM-P.")
            return None

        results = service_drive.files().list(q=f"'{directory_id}' in parents",
                                             pageSize=5,
                                             fields='nextPageToken, files(id, name)').execute()

        items = results.get('files', [])

        if not items:
            print("No hay archivos en el directorio /REM.")
            return None

        for item in items:
            if item['name'] == document: ## searching the document
                print(f"document id: {item['id']}")
                return item['id']

        print(f"No se encontró el documento: {document}")
        return None

    except HttpError as error:
        print(f'Ocurrió un error: {error}')
        return None

def search_single_value(name, month_year_date):
    for sv in single_values_list:
        if sv['value_name'] == name:
            if len(sv['values']) == 0:
                return None
            for value_info in reversed(sv['values']):
                value_date = datetime.strptime(value_info['date'], "%d/%m/%Y")
                expiration_date = datetime.strptime(value_info['expiration_date'], "%d/%m/%Y")
                if value_date <= month_year_date <= expiration_date:
                    return value_info['value']
    return None


def get_parameter_value(parameter_atributes, month_and_year):
    # ADD DATE PARAMETER AND VERIFICATION
    month_year_date = datetime.strptime(month_and_year, "%m/%Y")

    if parameter_atributes[0] == "sv":
        
        #return search_single_value(parameter_atributes[1],month_year_date)
        
        # Reduce the amount of database queries by storing single values
        print(
            f"Single value, nombre: {parameter_atributes[1]}, ultimo campo: {parameter_atributes[-1]}, month_and_year: {month_and_year}")
        single_value = single_value_collection.find_one(
            {"value_name":  parameter_atributes[1]})
        print("\nValues list\n")
        print(single_value)
        # get a  value where the month an year is in the range [value date, value expiration date]
        if single_value is not None:
            if len(single_value['values']) == 0:
                return None
            for value_info in reversed(single_value['values']):
                value_date = datetime.strptime(value_info['date'], "%d/%m/%Y")
                expiration_date = datetime.strptime(
                    value_info['expiration_date'], "%d/%m/%Y")

                if value_date <= month_year_date <= expiration_date:
                    print(
                        f"Month and year {month_and_year} valido para: {value_info}")
                    return (value_info['value'])

            print(
                f"\n\n\nSingle value: {single_value['values'][-1]['value']}\n\n\n")
        return None
       
    elif parameter_atributes[0] == "sc":
        # $0 :1  :2    :3 :4     $
        # $sc:C14:REM-A:01:nombre$
        
        
        return (read_single_cell_drive( document_type=parameter_atributes[2], cell=parameter_atributes[1], sheet=parameter_atributes[3], month_year_date=month_year_date))
        

    elif parameter_atributes[0] == "mc":
        # $0 :1  :2  :3    :4 :      $
        # $mc:C14:D15:REM-A:01:nombre$
        
        
        return (read_multiple_cell_drive(document_type=parameter_atributes[3], cell1=parameter_atributes[1],
                                         cell2=parameter_atributes[2], sheet=parameter_atributes[4], month_year_date=month_year_date))

    return None


def calculate_formula(formula, month_and_year):
    print("\n\n\n Calculating formula for: "+formula+"\n\n\n")
    new_formula_for_eval = formula
    new_formula_for_detail = formula

    x1 = None
    x2 = None
    parameter_source_dict = {}

    print(f"\n\n\n{new_formula_for_eval}\n\n\n")

    for i in range(len(new_formula_for_eval)):
        if new_formula_for_eval[i] == '$':
            if x1 == None:
                x1 = i
            elif x2 == None:
                x2 = i
                subString = new_formula_for_eval[x1:x2+1]
                parameter_source_dict[subString] = None
                x1 = None
                x2 = None
    if (x1 != None):
        print("string incorrecto, falta un caracter $")

    print(f"\n\n\ndict:\n{parameter_source_dict}\n\n\n")

    index = 0
    new_dict_for_eval = {}
    new_dict_for_detail = {}
    parameters_detail = []
    message = ""
    for key, value in parameter_source_dict.items():
        subKey = key[1:-1]
        parameter_atributes = subKey.split(":")

        new_value = None
        try:
            global get_parameter_count
            get_parameter_count = get_parameter_count + 1
            new_value = float(get_parameter_value(
                parameter_atributes, month_and_year))
        except FileNotFoundError:
            message = f"Error: Archivo {parameter_atributes[-3]} {parameter_atributes[-2]} no encontrado"
        except TypeError:
            message = f"Error al calcular el KPI: 1 o mas valores es nulo"
        except ValueError:
            message = f"Error al calcular el KPI: 1 o mas valores es nulo"

        new_dict_for_eval["x"+str(index)] = new_value
        new_dict_for_detail[parameter_atributes[-1]] = new_value

        new_formula_for_eval = new_formula_for_eval.replace(
            key, "x"+str(index))
        new_formula_for_detail = new_formula_for_detail.replace(
            key, parameter_atributes[-1])

        source = ""
        if parameter_atributes[0] == "sv":
            source = f"Valor independiente"
        elif parameter_atributes[0] == "sc":
            source = f"Celda {parameter_atributes[1]}, {parameter_atributes[2]} {parameter_atributes[3]}"
        elif parameter_atributes[0] == "mc":
            source = f"Rango de celdas {parameter_atributes[1]}-{parameter_atributes[2]}, {parameter_atributes[3]} {parameter_atributes[4]}"

        parameters_detail.append(
            {"source": source, "name": parameter_atributes[-1], "parameter_value": new_value})
        index += 1

    print(new_dict_for_eval)
    print(new_formula_for_eval)
    print(new_dict_for_detail)
    print(parameters_detail)
    print(new_formula_for_detail)
    kpi_value = None

    try:
        kpi_value = eval(new_formula_for_eval, new_dict_for_eval)
        message = "KPI calculado con exito"
    except TypeError:
        if message == "":
            message = "Error al calcular el KPI: 1 o mas valores es nulo"
    except ZeroDivisionError:
        if message == "":
            message = "Error al calcular el KPI: division por 0"

    print(kpi_value)
    return kpi_value, new_formula_for_detail, parameters_detail, message




@kpi_calculator_bp.route('/kpi_calculator/<kpi_type>', methods=['POST'])
def calculate_kpis_by_type(kpi_type):
    # start time measurement
    start_time = time.time()
    kpi_count = 0

    if kpi_type != 'PRAPS' and kpi_type != 'Metas Sanitarias':
        return jsonify({"message": f"El tipo de KPI no es valido"}), 400
    try:
        month_and_year = request.form.get('month_and_year')
        formatted_date = datetime.strptime(
            month_and_year, "%m/%Y").strftime("%m-%Y")
    except ValueError:
        return jsonify({"message": f"La fecha no es valida"}), 400

    # Metas sanitarias BUSINESS RULE: They are measured every 3 months
    # we need to check that the month is either 1, 4, 7, or 10 (the start of each trimester).
    if kpi_type == 'Metas Sanitarias':
        month = int(formatted_date.split('-')[0])
        if month not in [1, 4, 7, 10]:
            return jsonify({"message": f"La fecha no es valida para calculo de Metas Sanitarias"}), 400

    # Spreadsheet instance
    REM_A_filename = "REM-A" + " " + formatted_date
    REM_P_filename = "REM-P" + " " + formatted_date
    Poblacion_Estimada_filename = "Poblacion Estimada" + " " + \
        datetime.strptime(month_and_year, "%m/%Y").strftime("%Y")
    print(
        f"filenames:  \n{REM_A_filename}\n{REM_P_filename}\n{Poblacion_Estimada_filename} ")

    global REM_A_spreadsheet_id
    global REM_P_spreadsheet_id
    global Poblacion_Estimada_spreadsheet_id

    REM_A_spreadsheet_id = searchDocument(REM_A_filename)
    REM_P_spreadsheet_id = searchDocument(REM_P_filename)
    Poblacion_Estimada_spreadsheet_id = searchDocument(
        Poblacion_Estimada_filename)
    if REM_A_spreadsheet_id is None:
        return jsonify({"message": f"El archivo {REM_A_filename} no fue encontrado en Google Drive"}), 404
    if REM_P_spreadsheet_id is None:
        return jsonify({"message": f"El archivo {REM_P_filename} no fue encontrado en Google Drive"}), 404
    if Poblacion_Estimada_spreadsheet_id is None:
        return jsonify({"message": f"El archivo {Poblacion_Estimada_filename} no fue encontrado en Google Drive"}), 404

    global single_values_list
    single_values_list = []
    for sv in single_value_collection.find():
        single_values_list.append({
            '_id': str(ObjectId(sv['_id'])),
            'value_name': sv['value_name'],
            'values': sv['values']}
        )

    distinct_subtypes = kpi_formulas_collection.distinct("subtype")
    for distinct_subtype in distinct_subtypes:
        print(distinct_subtype)
        results = []
        for kf in kpi_formulas_collection.find({"type": kpi_type, "subtype": distinct_subtype}).sort([('type', ASCENDING), ('subtype', ASCENDING), ('kpi_number', ASCENDING)]):
            formula = kf['formula']

            kpi_count = kpi_count + 1
            kpi_value, new_formula_for_detail, parameters_detail, message = calculate_formula(
                formula, month_and_year)

            results.append({
                "kpi_name": kf['kpi_name'],
                "kpi_number": kf['kpi_number'],
                "weight": kf['weight'],
                "formula": new_formula_for_detail,
                "parameters_detail": parameters_detail,
                "kpi_value": kpi_value,
                "message": message

            })
            print(f"\nEl kpi: {kf['kpi_name']}, n°{kf['kpi_number']} de {kf['type']}, {kf['subtype']}, tiene un valor de: {kpi_value}\n")

        if len(results) > 0:
            calculated_kpis = {
                "type": kpi_type,
                "subtype": distinct_subtype,
                "month_and_year": month_and_year,
                "version": 1,
                "number_of_kpis": len(results),
                "kpis": results,
                "last_update": datetime.utcnow()
            }

            # search in the calculated_kpi_collection by type and month_and_year
            existing_entry = calculated_kpi_collection.find_one(
                {"type": kpi_type, "subtype": distinct_subtype, "month_and_year": month_and_year})
            # if a collection already has both the same type and month_and_year override it and increase the version number by 1
            if existing_entry:
                calculated_kpis["version"] = existing_entry["version"] + 1
                calculated_kpi_collection.update_one(
                    {"_id": existing_entry["_id"]}, {"$set": calculated_kpis})
            else:
                calculated_kpi_collection.insert_one(calculated_kpis)

    # print time measurement results
    REM_A_spreadsheet_id = None
    REM_P_spreadsheet_id = None
    Poblacion_Estimada_spreadsheet_id = None

    single_values_list = None
    global get_parameter_count
    get_parameter_count_aux = get_parameter_count
    get_parameter_count = 0

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(
        f"Tiempo transcurrido: {elapsed_time} segundos, {kpi_count} KPIs calculados")
    
    return jsonify({"message":f"Numero de KPIs de {kpi_type} calculados: {kpi_count}, numero de valores usados para el calculo: {get_parameter_count_aux}"}), 200



@kpi_calculator_bp.route('/kpi_calculator/<kpi_type>/<kpi_subtype>', methods=['POST'])
def calculate_kpis_by_type_and_subtype(kpi_type,kpi_subtype):
    # start time measurement
    start_time = time.time()
    kpi_count = 0

    if kpi_type != 'PRAPS' and kpi_type != 'Metas Sanitarias':
        return jsonify({"message": f"El tipo de KPI no es valido"}), 400
    try:
        month_and_year = request.form.get('month_and_year')
        formatted_date = datetime.strptime(
            month_and_year, "%m/%Y").strftime("%m-%Y")
    except ValueError:
        return jsonify({"message": f"La fecha no es valida"}), 400

    # Metas sanitarias BUSINESS RULE: They are measured every 3 months
    # we need to check that the month is either 1, 4, 7, or 10 (the start of each trimester).
    if kpi_type == 'Metas Sanitarias':
        month = int(formatted_date.split('-')[0])
        if month not in [1, 4, 7, 10]:
            return jsonify({"message": f"La fecha no es valida para calculo de Metas Sanitarias"}), 400

    # Spreadsheet instance
    REM_A_filename = "REM-A" + " " + formatted_date
    REM_P_filename = "REM-P" + " " + formatted_date
    Poblacion_Estimada_filename = "Poblacion Estimada" + " " + \
        datetime.strptime(month_and_year, "%m/%Y").strftime("%Y")
    print(
        f"filenames:  \n{REM_A_filename}\n{REM_P_filename}\n{Poblacion_Estimada_filename} ")

    global REM_A_spreadsheet_id
    global REM_P_spreadsheet_id
    global Poblacion_Estimada_spreadsheet_id

    REM_A_spreadsheet_id = searchDocument(REM_A_filename)
    REM_P_spreadsheet_id = searchDocument(REM_P_filename)
    Poblacion_Estimada_spreadsheet_id = searchDocument(
        Poblacion_Estimada_filename)
    if REM_A_spreadsheet_id is None:
        return jsonify({"message": f"El archivo {REM_A_filename} no fue encontrado en Google Drive"}), 404
    if REM_P_spreadsheet_id is None:
        return jsonify({"message": f"El archivo {REM_P_filename} no fue encontrado en Google Drive"}), 404
    if Poblacion_Estimada_spreadsheet_id is None:
        return jsonify({"message": f"El archivo {Poblacion_Estimada_filename} no fue encontrado en Google Drive"}), 404

    global single_values_list
    single_values_list = []
    for sv in single_value_collection.find():
        single_values_list.append({
            '_id': str(ObjectId(sv['_id'])),
            'value_name': sv['value_name'],
            'values': sv['values']}
        )

    distinct_subtypes = [kpi_subtype]
    for distinct_subtype in distinct_subtypes:
        print(distinct_subtype)
        results = []
        for kf in kpi_formulas_collection.find({"type": kpi_type, "subtype": distinct_subtype}).sort([('type', ASCENDING), ('subtype', ASCENDING), ('kpi_number', ASCENDING)]):
            formula = kf['formula']

            kpi_count = kpi_count + 1
            kpi_value, new_formula_for_detail, parameters_detail, message = calculate_formula(
                formula, month_and_year)

            results.append({
                "kpi_name": kf['kpi_name'],
                "kpi_number": kf['kpi_number'],
                "weight": kf['weight'],
                "formula": new_formula_for_detail,
                "parameters_detail": parameters_detail,
                "kpi_value": kpi_value,
                "message": message

            })
            print(f"\nEl kpi: {kf['kpi_name']}, n°{kf['kpi_number']} de {kf['type']}, {kf['subtype']}, tiene un valor de: {kpi_value}\n")

        if len(results) > 0:
            calculated_kpis = {
                "type": kpi_type,
                "subtype": distinct_subtype,
                "month_and_year": month_and_year,
                "version": 1,
                "number_of_kpis": len(results),
                "kpis": results,
                "last_update": datetime.utcnow()
            }

            # search in the calculated_kpi_collection by type and month_and_year
            existing_entry = calculated_kpi_collection.find_one(
                {"type": kpi_type, "subtype": distinct_subtype, "month_and_year": month_and_year})
            # if a collection already has both the same type and month_and_year override it and increase the version number by 1
            if existing_entry:
                calculated_kpis["version"] = existing_entry["version"] + 1
                calculated_kpi_collection.update_one(
                    {"_id": existing_entry["_id"]}, {"$set": calculated_kpis})
            else:
                calculated_kpi_collection.insert_one(calculated_kpis)

    # print time measurement results
    REM_A_spreadsheet_id = None
    REM_P_spreadsheet_id = None
    Poblacion_Estimada_spreadsheet_id = None

    single_values_list = None
    global get_parameter_count
    get_parameter_count_aux = get_parameter_count
    get_parameter_count = 0

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(
        f"Tiempo transcurrido: {elapsed_time} segundos, {kpi_count} KPIs calculados")
    
    return jsonify({"message":f"Numero de KPIs de {kpi_type} calculados: {kpi_count}, numero de valores usados para el calculo: {get_parameter_count_aux}"}), 200
