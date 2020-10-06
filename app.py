import os
from flask import Flask, request, abort, jsonify
from flask_swagger import swagger
from flask_cors import CORS, cross_origin
from file_name import gen_file_name
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
from flask_restplus import Api, Resource, Namespace, fields, reqparse


# description of application
description = '''This API endpoint accepts files sent after an MBOT completes
a run. It then will write the file to a MongoDB database.'''

# start application
flask_app = Flask(__name__, static_url_path='/v1/api/')
flask_app.config['UPLOAD_FOLDER'] = os.path.abspath('static/uploads')
flask_app.config['EXTENSION'] = 'txt'

# setup security
CORS(flask_app)

# helper functions for abort
@flask_app.errorhandler(403)
def handle_403(e):
	return jsonify(error=str(e)), 403

@flask_app.errorhandler(404)
def handle_404(e):
	return jsonify(error=str(e)), 404

@flask_app.errorhandler(406)
def handle_406(e):
	return jsonify(error=str(e)), 406

@flask_app.errorhandler(422)
def handle_422(e):
	return jsonify(error=str(e)), 422

@flask_app.errorhandler(500)
def handle_500(e):
	return jsonify(error=str(e)), 500

@flask_app.errorhandler(501)
def handle_501(e):
	return jsonify(error=str(e)), 501

# check file extension
def check_extension(filename, extension):
    '''Check if the correct extension has been given'''
    return filename.rsplit('.', 1)[1].lower() == extension

# description of application
api = Api(
	app=flask_app,
	endpoint='/MBOT/v1/api/',
	doc='/MBOT/v1/api-docs/',
	version = '0.0.1',
	title = 'MBOT API Endpoint',
	description = description
	)

# Separate namespace for MBOT
mbot_namespace = api.namespace('MBOT', description= 'Upload and pull down log files from MBOT')
@mbot_namespace.route('/v1/api/log')
class api_mplevy(Resource):
    '''API RESOURCE FOR MBOT'''
    # setup documentation
    logfile_payload = {}
    logfile_payload['description'] = 'Data type must be a .log file.'
    logfile_payload['name'] = 'logfile'
    logfile_payload['type'] = 'file'
    logfile_payload['in'] = 'path'
    @mbot_namespace.doc(params={'logfile': logfile_payload})
    @mbot_namespace.response(200, 'Succcess')
    @mbot_namespace.response(404, 'No log file name detected')
    @mbot_namespace.response(406, 'Unknown Request')
    @mbot_namespace.response(422, 'Incorrect file type')
    @cross_origin()

    # define file upload post
    # @mbot_namespace.doc(responses={200:'Success', 404:'No log file name detected'})
    def post(self):
        # check if file is in the request
        if 'logfile' not in request.files:
            return abort(406, 'Unknown Request')
        
        # pull the log file from the request
        file = request.files['logfile']
        
        # Check if filename is blank
        if file.filename == '':
            abort(404, description='No log file name detected')

        # check if this is the correct extension
        if file and check_extension(file.filename, flask_app.config['EXTENSION']):
            # set a unique file name
            file_name = gen_file_name(flask_app.config['EXTENSION'])
            # save the file to the uploads folder
            file.save(os.path.join(flask_app.config['UPLOAD_FOLDER'], file_name))
            return jsonify({'FILE NAME': file_name, 'success': True})
        else:
            abort(422, 'Incorrect file type')
    
    # def get(self):
        


def main():
    flask_app.run(host='localhost', port=8503, debug=False)


if __name__ == "__main__":
    main()