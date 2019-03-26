# -*- coding: utf-8 -*-
"""
daniele tomerini
Initial code march 2019

Initial proposal for an interface between Ginestra and Aiida
FLASK python app. Based on JSON interchange between a server accepting requests 
and returning values and updates on the calculation
Keywords for now are stored within a settings.json file. 
Basic checks to help ensure consistency
"""

from flask import Flask, request, jsonify,render_template, Response
import json
import aiida

app = Flask(__name__)



@app.route('/ginestra/', methods=['GET','HEAD','POST','PUT','DELETE'])
def get_ginestra_request():
    from search.structural import find_structure
    from check.input import BackToGinestra
    """
    Route to manage the requests from ginestra
    Access is through a JSON file passed to the server
    containing the input required for calculation
    Data is handled and responded accordinglyt
    """


    # initialize the answer to the request
    response = BackToGinestra()
    ### process options

    response.Add_Allowed(calculation_options)

    # some basic checks
    response.Check_Method(request)
    response.Check_Calculation()
    if response.NoError():
        response.Check_Structure()

    ### processing input

    if response.NoError():
### TODO ### process input data
    ### TODO ### according to calculation type, check that everything needed is there
    ### TODO ### check that there is no problem with data
    ### TODO ### identify what is the request structure. run query to get
    ### TODO ### is the structure with this options already running? 
        ### TODO ### query aiida to get the status. Return status in the message
    ### TODO ### IF calculation not running. Check the workflow available
    ### TODO ### Run the workflow. Get the ID of the calculation. Monitor the status of the calculation on each request
        ### TODO ### If still running, return to wait. Calculation ok, but retry later
    ### TODO ### Calculation finished. Parse result. Tag database

    ### TODO tag result of the calculation 
        
        find_structure(response)
    
    
    ### back to answering the request

    # returns the input, the structure, the data, a message 
    return jsonify(response.Back()), response.status_code



if __name__ == '__main__':
    with open('config.json') as f:
        calculation_options = json.load(f)
    input_content = {}
    app.run(host= '127.0.0.1',port='2345',debug=True)



