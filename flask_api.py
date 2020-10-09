#!/usr/bin/env python
import os
import time
import subprocess
from shutil import move
from pathlib import Path
from flask_swagger import swagger
from flask_cors import CORS, cross_origin
from flask import Flask, request, abort, jsonify, render_template, send_from_directory
from api_utils import get_file_info, update_mbot_table, get_file_address, delete_run
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
from flask_restplus import Api, Resource, Namespace, fields, reqparse, apidoc


# description of application
description = '''This API endpoint accepts files sent after an MBOT completes
a run. It then will write the file to a MongoDB database.'''

# start application
flask_api = Flask(__name__, static_url_path='/api/')

# setup security
CORS(flask_api)

# helper functions for abort
@flask_api.errorhandler(403)
def handle_403(e):
	return jsonify(error=str(e)), 403

# ERROR HANDLERS
@flask_api.errorhandler(404)
def handle_404(e):
	return jsonify(error=str(e)), 404

@flask_api.errorhandler(406)
def handle_406(e):
	return jsonify(error=str(e)), 406

@flask_api.errorhandler(422)
def handle_422(e):
	return jsonify(error=str(e)), 422

@flask_api.errorhandler(500)
def handle_500(e):
	return jsonify(error=str(e)), 500

@flask_api.errorhandler(501)
def handle_501(e):
	return jsonify(error=str(e)), 501

# check file extension
def check_extension(filename, extension):
    '''Check if the correct extension has been given'''
    return filename.rsplit('.', 1)[1].lower() == extension

# CURRENTLY NOT NEEDED
# @apidoc.apidoc.add_app_template_global
# def swagger_static(filename):
#     return "./swaggerui/{0}".format(filename)

# description of application
api = Api(
	app=flask_api,
	endpoint='/api/',
	doc='/api/',
	version = '0.0.2',
	title = 'Michael\'s API',
	description = description
	)

# CURRENTLY NOT NEEDED
# @api.documentation
# def custom_ui():
#     return render_template("swagger-ui.html", title=api.title, specs_url="./swagger.json")

# NAMESPACE FOR LOG FILE UPLOAD
mbot_namespace = api.namespace('MBOT',
            description= 'Upload and pull down log files from MBOT',
            path='/', 
            ordered=True)

@mbot_namespace.route('/api/mbot/v1/log')
class api_mplevy(Resource):
    '''POST/GET LOG FILE'''

    # setup documentation
    logfile_payload = {'description': 'Post must be a .log file.',
                            'name': 'logfile',
                            'type': 'file',
                            'in': 'path'}
    botname_payload = {'description': 'Botname',
                            'name': 'name',
                            'type': 'string',
                            'in': 'query'}
    # setup parameters
    @mbot_namespace.doc(params={'logfile': logfile_payload, 
                                'name': botname_payload})
    # different responses
    @mbot_namespace.response(200, 'Succcess')
    @mbot_namespace.response(404, 'No log file name detected')
    @mbot_namespace.response(406, 'Unknown Request')
    @mbot_namespace.response(422, 'Incorrect file type')
    @cross_origin()

    def post(self):
        '''POST A LOG FILE'''
        # check if file is in the request
        if 'logfile' not in request.files:
            return abort(406, 'Unknown Request')
        if 'name' not in request.args:
            return abort(404, 'No name given')
        
        # pull the log file from the request
        file = request.files['logfile']
        
        # Check if filename is blank
        if file.filename == '':
            abort(404, description='No log file name detected')

        # check if this is the correct extension
        if file and check_extension(file.filename, 'log'):
            
            # Get all file names and paths
            file_info = get_file_info()
            
            # save log file
            file.save(file_info['log']['path'])
            
            # write pickle in log directory
            lcm_result = subprocess.Popen(
                ['lcm-export', file_info['log']['name'], '--lcmtypes', '/home/michaellevy/MBOT-RPI/python/', '-p'],
                cwd=file_info['log']['path'].parents[0])
            
            # check if pickle is written and then move it to correct directory
            for i in range(10):
                # if file appears move it
                pickle_flg = os.path.exists(str(file_info['pkl_initial']['path'].absolute()))
                if pickle_flg:
                    move(src=file_info['pkl_initial']['path'].absolute(), dst=file_info['pkl_final']['path'].absolute())
                    break
                
                # sleep for a second while we wait for lcm-export to finish
                time.sleep(1)

            # test if pickle was written
            r = update_mbot_table(request.args['name'], file_info)
            if r == 0:
                return jsonify({'runId': file_info['runId'],
                                'Results': file_info['result']})
            elif r == -1:
                return abort(422, 'INTERNAL SERVER ERROR!')
            elif r == -2:
                return abort(422, 'FAILED TO WRITE PICKLE!')
        else:
            abort(422, 'Incorrect file type')

    # setup get
    runId_payload = {'description': 'runId for specific file',
                            'name': 'runId',
                            'type': 'string',
                            'in': 'query'}
    type_payload = {'description': 'Request a "log" or "pkl" file.',
                            'name': 'type',
                            'type': 'string',
                            'in': 'query'}
    
    @mbot_namespace.doc(params={'runId': runId_payload,
                            'type': type_payload})
    @mbot_namespace.response(200, 'Succcess')
    @mbot_namespace.response(404, 'INCORRECT TYPE/RUN ID GIVEN')
    @mbot_namespace.response(406, 'Unknown Request')
    @mbot_namespace.response(500, 'INTERNAL SERVER ERROR')
    @cross_origin()
    def get(self):
        '''RETURN LOG FILE BACK'''
        if 'runId' not in request.args:
            abort(404, 'NO runId GIVEN!')
        elif 'type' not in request.args:
            abort(404, 'NO type GIVEN!')
        
        runId = int(request.args['runId'])

        # get path
        if request.args['type'] == 'log':
            file_path = get_file_address(runId, 'LOG PATH')
        elif request.args['type'] == 'pkl':
            file_path = get_file_address(runId, 'PICKLE PATH')
        else:
            abort(404, 'INCORRECT TYPE GIVEN MUST BE "log" or "pkl"')

        # type to send the file
        if not isinstance(file_path, int):
            try:
                return send_from_directory(str(file_path.parent), str(file_path.name), mimetype='application/octet-stream')
            except Exception as e:
                abort(500, 'INTERNALL ERROR: ' + str(e))
        else:
            abort(404, 'Incorrect runId Given! ' + str(runId))
    

    # delete
    delete_payload = {'description': 'Delete a Run',
                            'name': 'RunId',
                            'type': 'string',
                            'in': 'query'}
    
    @mbot_namespace.doc(params={'runId': delete_payload})
    @mbot_namespace.response(200, 'Succcess')
    @mbot_namespace.response(404, 'INCORRECT runId GIVEN')
    @cross_origin()
    def delete(self):
        '''DELETE A RUN'''
        # check if runId in argument
        if 'runId' not in request.args:
            abort(404, 'NO RUN ID GIVEN!')
        
        # find runId and write
        runId = int(request.args['runId'])
        if not delete_run(runId):
            return jsonify({'runId': runId, 'DeletionSuccess': True})
        else:
            return jsonify({'runId': runId, 'DeletionSuccess': False})

def main():
    flask_api.run(port=8505, debug=True)


if __name__ == "__main__":
    main()