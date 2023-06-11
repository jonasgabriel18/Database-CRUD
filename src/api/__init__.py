from flask import Flask, Blueprint
import os
import sys

directory = os.path.dirname(os.path.abspath("__file__"))
sys.path.append(os.path.dirname(os.path.dirname(directory)))

from src.api.client_routes import client_routes
from src.api.personal_routes import personal_routes

api_blueprint = Blueprint('api', __name__)

api_blueprint.register_blueprint(client_routes)
api_blueprint.register_blueprint(personal_routes)

template_dir = os.path.abspath('../templates')

app = Flask(__name__, template_folder=template_dir)
app.register_blueprint(api_blueprint)

if __name__ == '__main__':
    app.run(debug=True)