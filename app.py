# -*- coding: utf-8 -*-
"""
Daniele Tomerini
Initial code march 2019

Initial proposal for an interface between Ginestra and Aiida
FLASK python app. Based on JSON interchange between a server accepting requests
and returning values and updates on the calculation
Keywords for now are stored within a settings.json file.
Basic checks to help ensure consistency
"""
# general imports
import json
from flask import Flask, request, jsonify
from aiida import load_dbenv, is_dbenv_loaded
# local imports
from search.structural import find_structure
from check.input import BackToGinestra



APP = Flask(__name__)

@APP.route('/ginestra/<property>/submit/', methods=['POST'])
def get_ginestra_post_request(property):
    """
    Route to manage the requests from ginestra
    Access is through a JSON file passed to the server
    containing the input required for calculation
    Data is handled and responded accordingly

    :property is the quantity we required for calculation
    """

   # print calculation
### TODO ### process input data
    ### TODO ### according to calculation type, check that everything needed is there
    ### TODO ### check that there is no problem with data
    ### TODO ### identify what is the request structure. run query to get
    ### TODO ### is the structure with this options already running?
        ### TODO ### query aiida to get the status. Return status in the message
    ### TODO ### IF calculation not running. Check the workflow available
    ### TODO ### Run the workflow. Get the ID of the calculation.
             ### Monitor the status of the calculation on each request
        ### TODO ### If still running, return to wait. Calculation ok, but retry later
    ### TODO ### Calculation finished. Parse result. Tag database

    ### TODO tag result of the calculation
### END TODO

    # initialize the answer to the request
    response = BackToGinestra()
    ### process options
    response.Check_Method(request)
    response.Add_Allowed(CALCULATION_OPTIONS)
    response.input['calculation'] = property


    # some basic checks
    ### TODO
    response.Check_Calculation()
    if response.No_HTML_Error():
        response.Check_Structure()

    ### processing input

    if response.No_HTML_Error():
        find_structure(response)
        
    ### back to answering the request

    # returns the input, the structure, the data, a message
    return jsonify(response.Back()), response.status_code

@APP.route('/ginestra/', methods=['GET', 'HEAD', 'PUT', 'DELETE'])
def get_ginestra_notpost_request():
    """
    dealing with methods that are not allowed
    just return a warning
    """
    response = BackToGinestra()
    response.Set_Warning('Expecting a POST HTML method', 405) # method not allowed

    return jsonify(response.Back()), response.status_code

@APP.route('/ginestra/<property>/check_existing/')
def get_ginestra_check_existing(property):
    pass

@APP.route('/ginestra/<property>/input/')
def get_ginestra_input_by_id(property):
    pass

if __name__ == '__main__':
    if not is_dbenv_loaded():
        load_dbenv()
    with open('config.json') as f:
        CALCULATION_OPTIONS = json.load(f)
    APP.run(host='127.0.0.1', port='2345', debug=True)
