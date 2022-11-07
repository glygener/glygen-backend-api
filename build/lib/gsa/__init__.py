import os
import datetime
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from flask_restx import Api, Resource, fields

from .gsa import api as gsa_api





def create_app():
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, supports_credentials=True)
    #CORS(app)

    api = Api(app, version='1.0', title='GlyGen GSA APIs', description='Documentation for the GlyGen GSA APIs',)
    api.add_namespace(gsa_api)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    if app.config["ENV"] == "production":
        app.config.from_pyfile('config.prd.py', silent=True)
    else:
        app.config.from_pyfile('config.dev.py', silent=True)

    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = datetime.timedelta(days=30)

    jwt = JWTManager(app)



    from . import db

    from . import auth
    app.register_blueprint(auth.bp)

    from . import misc
    app.register_blueprint(misc.bp)

    app.add_url_rule('/', endpoint='index')



    return app
