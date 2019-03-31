# -*- coding: utf-8 -*-
"""
Daniele Tomerini
Initial code march 2019

Initial proposal for an interface between Ginestra and Aiida
FLASK python app. 
Based on JSON interchange between a server accepting requests
and returning values and updates on the calculation
Endpoints  changes on property, with GET and POST requests
handling various tasks

Keywords for now are stored within a settings.json file.
Basic checks to help ensure consistency
"""
# general imports


import json
from flask import Flask,request
from flask_restful import Resource, Api

from aiida import load_dbenv, is_dbenv_loaded
# local imports
from search.structural import find_structure
from check.input import BackToGinestra

APP = Flask(__name__)
api = Api(APP)

class Ginestra_submit(Resource):
    def post(self, prop):
        """
        Route to manage the requests from ginestra
        Access is through a JSON file passed to the server
        containing the input required for calculation
        Data is handled and responded accordingly

        :property is the quantity we required for calculation
        """

        # initialize the answer to the request
        response = BackToGinestra()
        ### process options
        response.Check_Method(request)
        response.Add_Allowed(CALCULATION_OPTIONS)
        response.input['calculation'] = prop

        # some basic checks
        response.Check_Calculation()
        if response.No_HTML_Error():
            response.Check_Structure()

        ### processing input
        if response.No_HTML_Error():
            find_structure(response)
        
        ### back to answering the request

        # returns the input, the structure, the data, a message
        return response.Back(), response.status_code

class Ginestra_check_existing(Resource):
    def get(self, prop):
        """
        check if there is any instance in the database
        related to the calculation required for a material
        returns any items that need to be checked
        : prop endpoint to the calculation prop
        """
        if not prop in CALCULATION_OPTIONS['calculation']:
            return {'message': 'property {} not supported. Recognised properties: {}'.format(
                prop, 
                " ,".join(CALCULATION_OPTIONS['calculation']))
            }

class Ginestra_input(Resource):
    def get(self, prop):
        """
        search of an input by ID that is known by the program
        returns property and/or status of the calculation
        """
        return {'message': 'GET method not supported on '}

api.add_resource(
    Ginestra_submit,
    '/ginestra/<string:prop>/submit/',
)

api.add_resource(
    Ginestra_check_existing,
    '/ginestra/<string:prop>/existing/',
)

api.add_resource(
    Ginestra_input,
    '/ginestra/<string:prop>/input/',
)



if __name__ == '__main__':
    if not is_dbenv_loaded():
        load_dbenv()
    with open('config.json') as f:
        CALCULATION_OPTIONS = json.load(f)
    APP.run(host='127.0.0.1', port='2345', debug=True)
