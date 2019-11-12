# -*- coding: utf-8 -*-
"""
Daniele Tomerini
Initial code march 2019

Initial proposal for an interface between Ext and Aiida
FLASK python app.
Based on JSON interchange between a server accepting requests
and returning values and updates on the calculation
Endpoints  changes on property, with GET and POST requests
handling various tasks

Keywords for now are stored within a settings.json file.
Basic checks to help ensure consistency
"""
# general imports
from __future__ import absolute_import
from __future__ import print_function
import json
from flask import Flask, request
from flask_restful import Resource, Api, reqparse

# aiida
from aiida import load_profile
from aiida.orm import load_node, Float
from aiida.orm import Dict, Str
from aiida.engine import launch, submit, run
from aiida.plugins import DataFactory, CalculationFactory, WorkflowFactory

# local imports
from aiida_post.submit.distributor import Distribute
from aiida_post.calculations.request import importJSON, importJSONNoFlask

APP = Flask(__name__)
api = Api(APP)


def post(dictprop):
    """
    Route to manage the requests from ext
    Access is through a JSON file passed to the serveri
    containing the input required for calculation
    Data is handled and responded accordingly
    :input prop: is the quantity we required for calculation, passed as the endpoint
    """
    from aiida_post.tools.convert import Request_To_Dictionary
    HttpData = DataFactory('post.HttpData')
    ProcessInputs = WorkflowFactory('post.ProcessInputs')
    # reqdata = request_to_dict(request)
    #

    dictprop['predefined'] = CALCULATION_OPTIONS
    importJSONNoFlask(Dict(dict=dictprop))

    #reqdata = Request_To_Dictionary(request)
    hp = HttpData(dict=dictprop)

    prop = dictprop['calculation']

    pk, wf = run.get_node(
        ProcessInputs,
        incoming_request=hp,#Dict(dict=dictprop),
        predefined=Dict(dict=CALCULATION_OPTIONS),
        property_to_calculate=Str(prop),
    )

    if not wf.is_finished_ok:
        msg = 'Structure retrieval error. See node uuid={} for more specific report'.format(wf.uuid)
        return {
            'error': wf.exit_message,
            'message': msg,
            'stored_request': wf.inputs.incoming_request.get_dict(),
        }
    else:

        exwf = Distribute(wf, prop)
        msg = ' Successful retrieval of structure, {}, workflow at uuid {}'.format(exwf.inputs.structure.pk, exwf.pk)
        return {
            'error': wf.exit_message,
            'message': msg,
            'stored_request': wf.inputs.incoming_request.get_dict(),
        }


        # get to the actual calculation of the workflow
def get(self, prop):
    """
    check if there is any instance in the database
    related to the calculation required for a material
    returns any items that need to be checked
    : prop endpoint to the calculation prop
    : get queries define a projection for the property in the database
    """
    from .other.group_initialize import check_db
    parser = reqparse.RequestParser()
    # This does not do what I want. Check it better
    parser.add_argument('id', type=int)
    args = parser.parse_args()
    Ext_Group = Create_group(groupname='ext')
    if prop not in CALCULATION_OPTIONS['calculation']:
        return {
            'message':
            'Property {} not in supported properties: {}'.format(
                prop, ' ,'.join(CALCULATION_OPTIONS['calculation']), **args
            )
        }
    else:
        prop_group = Create_group(groupname=prop)
        print(('options', args))  # debug
        structs = check_db('ext', **args)
        back = {}
        for i in structs:
            for i2 in i:
                back.update({
                    str(i2.id): {
                        'class': i2.class_node_type,
                        'id': i2.id,
                        'uuid': i2.uuid,
                        'formula': i2.get_formula(),
                    }
                })
        return back


def get(self, prop):
    """
    search of an input by ID that is known by the program
    returns property and/or status of the calculation
    """
    if prop not in CALCULATION_OPTIONS['calculation']:
        return {
            'message':
            'property {} not supported. Recognised properties: {}'.format(
                prop, ', '.join(CALCULATION_OPTIONS['calculation'])
            )
        }
    return {'message': 'work in progress here!'}


def get(self, prop):
    """
    return a subset of nodes from the group ext
    additionally, it filters the request
    according to the data in the get method
    """
    if prop not in CALCULATION_OPTIONS['calculation']:
        return {
            'message':
            'property {} not supported. Recognised properties: {}'.format(
                prop, ', '.join(CALCULATION_OPTIONS['calculation'])
            )
        }
    return {'message': 'work in progress here!'}


#api.add_resource(app_submit, '/ext/calculation/<string:prop>/submit/')

#api.add_resource(app_check_existing, '/ext/calculation/<string:prop>/existing')

#api.add_resource(app_input, '/ext/calculation/<string:prop>/check/')

import aiida_post
CONFIG_DIR = str(aiida_post.__path__[0]) + '/common/'

if __name__ == '__main__':
    # aiida initialization
    load_profile()
    with open(CONFIG_DIR + 'config.json') as f:
        CALCULATION_OPTIONS = json.load(f)
    # usage: two options
    # first one is the endpoint
    # second one is a file for post, when needed
    import sys
    address = sys.argv[1]
    postfile = sys.argv[2]

    print('ip address: {}'.format(address))
    print('POST file: {}'.format(postfile))

    with open(postfile, 'r') as ff:
        myfile = ff.read()
    ff.close()

    mydict = json.loads(myfile)

    print(mydict)

    if 'submit' in address:
        post(mydict)

    #APP.run(host='127.0.0.1', port='2345', debug=True)
