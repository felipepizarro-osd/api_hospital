from flask import Flask
#from controllers.single_value import single_value_bp
#from controllers.kpi_goal import kpi_goal_bp
#from controllers.metas_sanitarias import metas_sanitarias_bp
#from controllers.kpi_calculator import kpi_calculator_bp
#from controllers.kpi_formulas import kpi_formulas_bp
from controllers.google_connect.google_drive_connection_routes.routes_calculation import drive_routes_bp
from controllers.Single_values_controllers.single_values_controller import singles_values_bp
from controllers.PRAPS_routes_controllers.praps_routes_controller import praps_routes_bp
from controllers.PRAPS_routes_controllers.kpi_praps import kpi_praps_routes_bp
from controllers.metas_sanitarias_19_routes.Clave_ref_metas_sanitarias_19_controller import metas_sanitarias_19_bp
from controllers.metas_sanitarias_19_routes.metas_19_kpi import kpi_metas_sanitarias_19_bp
from controllers.Clave_ref_metas_sanitarias_18_controllers.Clave_ref_metas_sanitarias_18_controller import metas_sanitarias_18_bp
from controllers.Clave_ref_metas_sanitarias_18_controllers.kpi_metas_18 import kpi_metas_sanitarias_18_bp
from controllers.Calculate_route.Calculate_controller import Maths_routes_bp
from controllers.origin_data_controllers.origin_data_controller import origin_data_bp
from controllers.login_routes.sign_in_controller import sign_in_bp

import sys
from dotenv import load_dotenv
from flask_cors import CORS
#from flasgger import Swagger

#load the variables from .env file
load_dotenv()

#set the environment variable
app = Flask(__name__)

CORS(resources={r"/*": {"origins": "http://localhost:3000"}})
#app.register_blueprint(single_value_bp)
#app.register_blueprint(kpi_goal_bp)
#app.register_blueprint(metas_sanitarias_bp)
#app.register_blueprint(kpi_calculator_bp)
#app.register_blueprint(kpi_formulas_bp)
app.register_blueprint(drive_routes_bp)
app.register_blueprint(singles_values_bp)
app.register_blueprint(praps_routes_bp)
app.register_blueprint(metas_sanitarias_19_bp)
app.register_blueprint(metas_sanitarias_18_bp)
app.register_blueprint(Maths_routes_bp)
app.register_blueprint(origin_data_bp)
app.register_blueprint(sign_in_bp)
app.register_blueprint(kpi_metas_sanitarias_19_bp)
app.register_blueprint(kpi_metas_sanitarias_18_bp)
app.register_blueprint(kpi_praps_routes_bp)
#swagger = Swagger(app, template_file='swagger_docs/swagger_doc.yaml', config=swagger_config)

if __name__ == '__main__':
    print(sys.path)
    app.run(host='0.0.0.0', port=4000, debug=True)
    


