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
import json
from flask import Flask, request
from flask_restful import Resource, Api, reqparse

# aiida
from aiida import load_profile
from aiida.orm import Dict, Str
from aiida.engine import launch

# local imports
from search.structural import find_structure
from check.input_wf import ProcessInputs
from utils.group_initialize import Create_group, check_db


APP = Flask(__name__)
api = Api(APP)


class Ext_submit(Resource):
    def post(self, prop):
        """
        Route to manage the requests from ext
        Access is through a JSON file passed to the server
        containing the input required for calculation
        Data is handled and responded accordingly

        :input prop is the quantity we required for calculation
        """
        # workfunction to process the incoming json dictionary
        myrequest, node = launch.run_get_node(
            ProcessInputs,
            request=Dict(dict=request.get_json()),
            predefined=Dict(dict=CALCULATION_OPTIONS),
            property=Str(prop),        
        )
        
        return 5


class Ext_check_existing(Resource):
    def get(self, prop):
        """
        check if there is any instance in the database
        related to the calculation required for a material
        returns any items that need to be checked
        : prop endpoint to the calculation prop
        : get queries define a projection for the property in the database
        """
        parser = reqparse.RequestParser()
        # This does not do what I want. Check it better
        parser.add_argument('id', type=int)
        args = parser.parse_args()
        Ext_Group = Create_group(groupname='ext')

        if prop not in CALCULATION_OPTIONS['calculation']:
            return {'message': 'Property {} not in supported properties: {}'.format(
                prop,
                " ,".join(CALCULATION_OPTIONS['calculation']),
                **args)
            }
        else:
            prop_group = Create_group(groupname=prop)
            print('options', args)  # debug

            structs = check_db('ext', **args)
            back = {}
            for i in structs:
                for i2 in i:
                    back.update(
                        {
                            str(i2.id): {
                                'class': i2.class_node_type,
                                'id': i2.id,
                                'uuid': i2.uuid,
                                'formula': i2.get_formula()
                            }
                        }
                    )
            return back


class Ext_input(Resource):
    def get(self, prop):
        """
        search of an input by ID that is known by the program
        returns property and/or status of the calculation
        """
        if prop not in CALCULATION_OPTIONS['calculation']:
            return {'message': 'property {} not supported. Recognised properties: {}'.format(
                prop,
                ", ".join(CALCULATION_OPTIONS['calculation']))
            }
        return {'message': 'work in progress here!'}


class Ext_nodes(Resource):
    def get(self, prop):
        """
        return a subset of nodes from the group ext
        additionally, it filters the request
        according to the data in the get method
        """
        if prop not in CALCULATION_OPTIONS['calculation']:
            return {
                'message': 'property {} not supported. Recognised properties: {}'.format(
                    prop,
                    ", ".join(CALCULATION_OPTIONS['calculation']))
            }
        return {'message': 'work in progress here!'}


api.add_resource(
    Ext_submit,
    '/ext/calculation/<string:prop>/submit/'
)

api.add_resource(
    Ext_check_existing,
    '/ext/calculation/<string:prop>/existing',
)

api.add_resource(
    Ext_input,
    '/ext/calculation/<string:prop>/check/',
)


if __name__ == '__main__':
    # aiida initialization
    load_profile()
    with open('config.json') as f:
        CALCULATION_OPTIONS = json.load(f)
    APP.run(host='127.0.0.1', port='2345', debug=True)
