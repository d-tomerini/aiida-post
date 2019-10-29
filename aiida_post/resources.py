# -*- coding: utf-8 -*-
"""
Daniele Tomerini
Initial code march 2019

This module contains the general resources to be called 
by the main api
"""
# general imports
import json
from flask import request
from flask_restful import Resource, Api, reqparse

# aiida
from aiida.orm import load_node, Float
from aiida.orm import Dict, Str
from aiida.engine import launch, submit, run
from aiida.plugins import DataFactory, CalculationFactory, WorkflowFactory

# local imports
from aiida_post.submit.distributor import Distribute
from aiida_post.calculations.request import importJSON



class app_submit(Resource):

    def post(self, prop):
        """
        Route to manage the requests from ext
        Access is through a JSON file passed to the serveri
        containing the input required for calculation
        Data is handled and responded accordingly

        :input prop: is the quantity we required for calculation, passed as the endpoint
        """

        from aiida_post.tools.convert import request_to_dict
        HttpData = DataFactory('post.HttpData')
        reqdata = request_to_dict(request)
        print(('cao', reqdata))
        importJSON(Dict(dict=reqdata))
        res, wf = run.get_node(
            xx,
            request=Dict(dict=request.get_json()),
            predefined=Dict(dict=CALCULATION_OPTIONS),
            property=Str(prop),
        )
        if not wf.is_finished_ok:
            msg = 'Structure retrieval error. See node uuid={} for more specific report'.format(wf.uuid)
            return {
                'error': wf.exit_message,
                'message': msg,
                'stored_request': wf.inputs.request.get_dict(),
            }
        else:
            exwf = Distribute(wf, prop)
            msg = ' Successful retrieval of structure, {}, workflow at uuid {}'.format(
                exwf.inputs.structure.pk, exwf.pk
            )
            return {
                'error': wf.exit_message,
                'message': msg,
                'stored_request': wf.inputs.request.get_dict(),
            }
            # get to the actual calculation of the workflow


class app_check_existing(Resource):

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


class app_input(Resource):

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


class app_nodes(Resource):

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



class NewResource(Resource):
    """
    resource containing GET and POST methods. Description of each method
    follows:

    GET: returns id, ctime, and attributes of the latest created Dict.

    POST: creates a Dict object, stores it in the database,
    and returns its newly assigned id.

    """

    def get(self):
        from aiida.orm import QueryBuilder, Dict

        qb = QueryBuilder()
        qb.append(Dict,
                  project=['id', 'ctime', 'attributes'],
                  tag='pdata')
        qb.order_by({'pdata': {'ctime': "desc"}})
        result = qb.first()

        # Results are returned as a dictionary, datetime objects is
        # serialized as ISO 8601
        return dict(id=result[0],
                    ctime=result[1].isoformat(),
                    attributes=result[2])

    def post(self):
        from aiida.orm import Dict

        params = dict(property1="spam", property2="egg")
        paramsData = Dict(dict=params).store()

        return {'id': paramsData.pk}

