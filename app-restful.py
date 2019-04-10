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
from flask import Flask, request
from flask_restful import Resource, Api, reqparse

from aiida import load_dbenv, is_dbenv_loaded
from aiida.orm import Node, StructureData, Dict, UpfData, ArrayData, CalculationNode, Group
from aiida.orm.querybuilder import QueryBuilder

# local imports
from search.structural import find_structure
from check.input import BackToGinestra
from aiida_related.group_initialize import Create_group


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
        # process options
        response.Check_Method(request)
        response.Add_Allowed(CALCULATION_OPTIONS)  
        response.input['calculation'] = prop

        # some basic checks
        response.Check_Calculation()
        if response.No_HTML_Error():
            response.Check_Structure()

        # processing input
        if response.No_HTML_Error():
            find_structure(response)
        
        # back to answering the request

        # returns the input, the structure, the data, a message
        return response.Back(), response.status_code

class Ginestra_check_existing(Resource):
    def get(self, prop):
        """
        check if there is any instance in the database
        related to the calculation required for a material
        returns any items that need to be checked
        : prop endpoint to the calculation prop
        : get queries define a projection for the property in the database
        """
        parser = reqparse.RequestParser()
        parser.add_argument('id',type=int)
        args = parser.parse_args()
        Ginestra_Group = Create_group(groupname='ginestra')

        if not prop in CALCULATION_OPTIONS['calculation']:
            return {'message': 'Retrieval of property {} not supported. Recognised properties: {}'.format(
                prop, 
                " ,".join(CALCULATION_OPTIONS['calculation']),
                **args)
            }
        else:
                prop_group = Create_group(groupname=prop)
                print( 'debug', args)    
                qb = QueryBuilder()
                # search 'ginestra'nodes in the query
                qb.append(
                    Group,
                    tag='tag1',
                    filters={'label': 'ginestra'}
                )
                if args['id']==None:
                    args = {}
                # finally, search in the GET query, if any
                qb = QueryBuilder()
                qb.append(
                    StructureData,
                    tag='tag1',
                    project=['*'],
                    filters=args
                )
                
                back = {}
                for i in qb.all():
                    for i2 in i:
                        back.update(
                            {str(i2.id):{
                                'class':i2.class_node_type,
                                'id':i2.id,
                                'uuid':i2.uuid,
                                'formula':i2.get_formula()
                                }
                            }
                        )
                return back


class Ginestra_input(Resource):
    def get(self, prop):
        """
        search of an input by ID that is known by the program
        returns property and/or status of the calculation
        """
        if not prop in CALCULATION_OPTIONS['calculation']:
            return {'message': 'property {} not supported. Recognised properties: {}'.format(
                prop, 
                ", ".join(CALCULATION_OPTIONS['calculation']))
            }
        return {'message':'work in progress here!'}


class Ginestra_nodes(Resource):
    def get(self, prop):
        """
        return a subset of nodes from the group ginestra
        additionally, it filters the request 
        according to the data in the get method
        """
        if not prop in CALCULATION_OPTIONS['calculation']:
            return {'message': 'property {} not supported. Recognised properties: {}'.format(
                prop, 
                ", ".join(CALCULATION_OPTIONS['calculation']))
            }
        return {'message':'work in progress here!'}


api.add_resource(
    Ginestra_submit,
    '/ginestra/<string:prop>/submit/'
)

api.add_resource(
    Ginestra_check_existing,
    '/ginestra/<string:prop>/existing',
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
