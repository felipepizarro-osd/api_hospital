# HSJD Backend utility Python API ETL Pipeline 

Sistema API realizado para el sistema de monitoreo de KPI del Hospital San Juan de Dios de Vicuña.
Objetivos:
Desarrollo de sistema web para vision y apoyo a toma de desisones dentro de la institución.
Sistema API incluye:
  rutas de carga de Valores KPI
  rutas de Obtencion de valores y datos para mostrar en Frontend
  rutas de validacion y registro de usuarios
  rutas de carga de Archivos de Respaldo
  rutas de Actualización de calculos 
  rutas de carga de CLAVE-REFERENCIA
  rutas de administración de origenes
## Instalación

1. Clona este repositorio en tu máquina local:
   
```mkdir HSJD_BI; cd HSJD_BI;```

```git clone https://github.com/JeAntonioLopez/HSJD_BI.git```

PD: en caso de hacer git clone con HTTPS ingresar sus credenciales de github con un Personal token 
  PD_1 : Ingresar a su perfil en github.com entrar con su mail y contraseña
  PD_2 : Configurar el personal token en la seccion Setting ==> Developers Tools ==> generate personal token
  PD_3 : clonar el repositorio

3. Navega al directorio del proyecto:

```ls``` or  ```dir``` en el directorio en donde se clono el proyecto

Muestra total del directorio principal:

```.
├── README.md
├── Secret_manager
│   ├── Secret_Manager.py
│   ├── __pycache__
│   │   └── Secret_Manager.cpython-310.pyc
│   └── utils_secret_manager.py
├── __pycache__
│   ├── database.cpython-310.pyc
│   ├── database.cpython-311.pyc
│   ├── db.cpython-311.pyc
│   ├── product_model.cpython-311.pyc
│   └── products.cpython-311.pyc
├── app.py
├── config
│   └── routes.py
├── controllers
│   ├── Calculate_route
│   │   ├── Calculate_controller.py
│   │   └── __pycache__
│   │       └── Calculate_controller.cpython-310.pyc
│   ├── Clave_ref_metas_sanitarias_18_controllers
│   │   ├── Clave_ref_metas_sanitarias_18_controller.py
│   │   └── __pycache__
│   │       └── Clave_ref_metas_sanitarias_18_controller.cpython-310.pyc
│   ├── PRAPS_routes_controllers
│   │   ├── __pycache__
│   │   │   └── praps_routes_controller.cpython-310.pyc
│   │   └── praps_routes_controller.py
│   ├── Single_values_controllers
│   │   ├── __pycache__
│   │   │   └── single_values_controller.cpython-310.pyc
│   │   └── single_values_controller.py
│   ├── __pycache__
│   │   ├── calculated_kpis.cpython-311.pyc
│   │   ├── kpi_calculator.cpython-310.pyc
│   │   ├── kpi_calculator.cpython-311.pyc
│   │   ├── kpi_formulas.cpython-310.pyc
│   │   ├── kpi_formulas.cpython-311.pyc
│   │   ├── kpi_goal.cpython-310.pyc
│   │   ├── kpi_goal.cpython-311.pyc
│   │   ├── metas_sanitarias.cpython-310.pyc
│   │   ├── metas_sanitarias.cpython-311.pyc
│   │   ├── single_value.cpython-310.pyc
│   │   └── single_value.cpython-311.pyc
│   ├── calculated_kpis.py
│   ├── google_connect
│   │   ├── Script_Data_Extraction
│   │   │   ├── Calculate_Data.py
│   │   │   └── __pycache__
│   │   │       └── Calculate_Data.cpython-310.pyc
│   │   ├── __pycache__
│   │   │   ├── google_calc_file.cpython-310.pyc
│   │   │   └── google_file_recon.cpython-310.pyc
│   │   ├── credentials.json
│   │   ├── google_calc_file.py
│   │   ├── google_drive_conn.py
│   │   ├── google_drive_connection_routes
│   │   │   ├── __pycache__
│   │   │   │   └── routes_calculation.cpython-310.pyc
│   │   │   ├── routes_calculation.py
│   │   │   ├── utils
│   │   │   │   ├── __pycache__
│   │   │   │   │   ├── files_drive_utils.cpython-310.pyc
│   │   │   │   │   ├── google_drive_utils.cpython-310.pyc
│   │   │   │   │   └── json_utils.cpython-310.pyc
│   │   │   │   ├── files_drive_utils.py
│   │   │   │   ├── google_drive_utils.py
│   │   │   │   └── json_utils.py
│   │   │   └── visualizacionkpis-24cb54e74f96.json
│   │   └── google_file_recon.py
│   ├── kpi_calculator.py
│   ├── kpi_formulas.py
│   ├── kpi_goal.py
│   ├── metas_sanitarias_19_routes
│   │   ├── Clave_ref_metas_sanitarias_19_controller.py
│   │   └── __pycache__
│   │       └── Clave_ref_metas_sanitarias_19_controller.cpython-310.pyc
│   ├── origin_data_controllers
│   │   ├── __pycache__
│   │   │   └── origin_data_controller.cpython-310.pyc
│   │   └── origin_data_controller.py
│   └── single_value.py
├── database.py
├── modules.install.py
├── print_dot_env.py
├── requirement.txt
├── swagger_docs
│   └── swagger_doc.yaml
├── token.json
└── uploads
```

3. Instala los requerimientos del proyecto utilizando pip:


### Requerimientos

Asegúrate de tener instalados los siguientes módulos de Python antes de continuar:

- flasgger
- Flask
- Flask-RESTful
- google-api-core
- google-api-python-client
- google-auth
- google-auth-httplib2
- google-auth-oauthlib
- googleapis-common-protos
- pymongo
- python-dateutil==2.9.0.post0
- python-dotenv
- pandas
- google-cloud-secret-manager
- openpyxl

```pip install -r requirements.txt```

## Configuración

1. Crea un archivo `.env` en el directorio raíz del proyecto.
2. Agrega las siguientes variables de entorno en el archivo `.env`:
   
   `SERVICE_ACCOUNT_FILE="path_to/visualizacionkpis-24cb54e74f96.json"`
   
   `MONGO_URL="mongodb+srv://<user>:<password>:ClusterN&tlsAllowInvalidCertificates=true"`
   
   `PROJECT_ID = "project_id"`
   
   `CREDENTIALS = "path_to/credentials.json"`
   
   `MONGODB_URI=<URI_de_tu_base_de_datos_MongoDB>`
   
Reemplaza `<URI_de_tu_base_de_datos_MongoDB>` con la URI de conexión a tu base de datos MongoDB.

PD: En caso de no tener acceso a la base de datos probar liberar la IP 0.0.0.0 en security network de mongo atlas:
![image](https://github.com/JeAntonioLopez/HSJD_BI/assets/66143232/64e736d6-2e2c-41c7-899e-df5584f439ca)

y habilitar la ip por un tiempo prudente para el desarrollo requerido:

![Screenshot 2024-05-07 at 11 10 05 AM](https://github.com/JeAntonioLopez/HSJD_BI/assets/66143232/5e539f3b-f188-44ba-bd2f-419b28a0b926)

![image](https://github.com/JeAntonioLopez/HSJD_BI/assets/66143232/6fc9b2ae-fd80-4b12-9c2c-55a80e7eda36)


## Uso

1. Ejecuta la aplicación Flask:

```python app.py```

or 

```python3 app.py```

Logs:

<img width="1012" alt="image" src="https://github.com/JeAntonioLopez/HSJD_BI/assets/66143232/68a3099d-bca6-4ba7-abc2-301192d3e54e">


2. Abre tu navegador web y ve a `http://localhost:port` para ver la aplicación en funcionamiento.

   El port es el definido por el entorno asegurese que sea el correcto
   Consultar Documentación de la app API de la hecha en POSTMAN, ingresar en:
   https://universal-star-180168.postman.co/workspace/My-Workspace~9f962633-d9e7-41d8-8a3a-d61e2c34b024/collection/27712805-8638c2a3-0353-4ff7-a4b2-a3d835b95283?action=share&creator=27712805


## Contribuir

Si deseas contribuir a este proyecto, sigue estos pasos:

1. Realiza un fork del proyecto.
2. Crea una nueva rama (`git checkout -b feature/nueva-caracteristica`).
3. Realiza tus cambios y haz commit de ellos (`git commit -am 'Agrega una nueva característica'`).
4. Haz push de tu rama (`git push origin feature/nueva-caracteristica`).
5. Abre un Pull Request.

## Créditos

Este proyecto fue creado por Jean Lopez, Rocio Flores, Felipe Pizarro.

## Contacto

Si tienes preguntas, sugerencias o problemas, por favor contacta a Felipe Pizarro por correo electrónico: felipe.pizarro02@alumnos.ucn.cl .
