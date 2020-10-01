import os
from flask import Flask, request, abort, jsonify
from flask_swagger import swagger
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
from flask_restplus import Api, Resource, Namespace, fields, reqparse


# description of application
description = ''' This is a simple description for my API docs '''

# flask application
flask_app = Flask(__name__, static_url_path='/v1/api/')


def check_extension(filename, extension):
    return filename.rsplit('.', 1)[1].lower() == extension

# description of 
api = Api(
	app=flask_app,
	endpoint='/v1/api/',
	doc='/v1/api-docs/',
	version = '0.3.2',
	title = 'Michael\'s API Endpoint for various Projects',
	description = description
	)

log_namespace = api.namespace('MBOT', description= 'API to upload a log file from an MBOT robot')

@log_namespace.route('/v1/api/log')
class api_mplevy(Resource):
    '''API RESOURCE FOR MPLEVY'''
    @log_namespace.doc(params={'log':'log file from an MBOT robot driving'})
    @log_namespace.response(200, 'Succcess')
    # @log_namespace.reponse(404, 'Not Found')

    def post(self):
        # check if file is in the request
        if 'log-file' not in request.files:
            return abort(406, 'Unknown Request')
        # pull the log file
        file = request.files['logfile']
        
        # Check if filename is blank
        if file.filename == '':
            return abort(422, 'No File Name Given')

        # check if this is the correct extension
        if file and check_extension(file.filename, '.txt'):
            # set a unique file name
            file.save(os.getcwd(), file.filename)
            return jsonify({'success': True, 'FILE NAME': file.filename})
        else: 
            abort(422, 'INCORRECT FILE TYPE')


def main():
    flask_app.run(port=8503, debug=True)


if __name__ == "__main__":
    main()