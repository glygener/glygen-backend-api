import os
import datetime
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from flask_restx import Api, Resource, fields

from .protein import api as protein_api
from .glycan import api as glycan_api
from .auth import api as auth_api
from .data import api as data_api
from .globalsearch import api as globalsearch_api
from .pages import api as pages_api
from .seqmapping import api as seqmapping_api
from .motif import api as motif_api
from .publication import api as publication_api
from .site import api as site_api
from .idmapping import api as idmapping_api
from .typeahead import api as typeahead_api
from .log import api as log_api
from .video import api as video_api
from .supersearch import api as supersearch_api
from .event import api as event_api
from .misc import api as misc_api
from .job import api as job_api
from .usecases import api as usecases_api



def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.url_map.strict_slashes = False

    CORS(app, supports_credentials=True)
    #CORS(app)

    api = Api(app, version='1.0', title='GlyGen APIs', description='Documentation for the GlyGen APIs',)
        


    api.add_namespace(glycan_api)
    api.add_namespace(motif_api)
    api.add_namespace(protein_api)
    api.add_namespace(site_api)
    api.add_namespace(publication_api)
    api.add_namespace(usecases_api)
    api.add_namespace(idmapping_api)
    api.add_namespace(seqmapping_api)
    api.add_namespace(supersearch_api)
    api.add_namespace(globalsearch_api)
    api.add_namespace(data_api)
    api.add_namespace(pages_api)
    api.add_namespace(typeahead_api)
    api.add_namespace(auth_api)
    api.add_namespace(log_api)
    api.add_namespace(video_api)
    api.add_namespace(event_api)
    api.add_namespace(job_api)
    api.add_namespace(misc_api)


    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    if app.config["ENV"] == "production":
        app.config.from_pyfile('config.py', silent=True)
        settings = app.config.get('RESTFUL_JSON', {})
        settings.setdefault('indent', 2)
        #settings.setdefault('sort_keys', True)
        app.config['RESTFUL_JSON'] = settings
    else:
        app.config.from_pyfile('config.dev.py', silent=True)

    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = datetime.timedelta(days=30)
    app.config['PROPAGATE_EXCEPTIONS'] = True
    #app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.config['JSON_SORT_KEYS'] = False

    jwt = JWTManager(app)




    return app
