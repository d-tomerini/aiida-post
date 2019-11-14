# -*- coding: utf-8 -*-
"""
Daniele Tomerini
Initial code march 2019

This module contains the general resources to be called
by the main api
"""
from __future__ import absolute_import
from __future__ import print_function
from flask import request
from flask_restful import Resource, Api, reqparse

# aiida
from aiida.orm import load_node, Float, Dict, Str
from aiida.engine import submit, run
from aiida.plugins import DataFactory, CalculationFactory, WorkflowFactory
from aiida.restapi.resources import BaseResource

# local imports
from aiida_post.submit.distributor import Distribute
from aiida_post.calculations.request import importJSON
from aiida_post.common.threaded import submit_job, run_calculation
import asyncio

class submit(BaseResource):

    def __init__(self, **kwargs):
        super(submit, self).__init__(**kwargs)
        # Add the configuration file for my app
        # Taken almost verbatim from the configuration handling of BaseResource
        conf_keys = ('CALCULATION', 'SUPPORTED_DATABASE', 'AVAILABLE_CODES')
        self.extended = {k: kwargs[k] for k in conf_keys if k in kwargs}

    def post(self, prop):
        """
        Route to manage the requests from the app
        Access is through a JSON file passed to the server containing the input required for calculation
        Data is handled and responded accordingly

        :param prop: the quantity we required for calculation, passed as the endpoint
        """

        from aiida_post.tools.convert import Request_To_Dictionary
        HttpData = DataFactory('post.HttpData')
        reqdata = Request_To_Dictionary(request)
        hp = Dict(dict=reqdata)

        #a = Dict(dict=reqdata)
        #y = run_calculation(
        #    importJSON,
        #    Dict(dict=reqdata),
        #    Dict(dict=self.extended)
        #)
        #print(y)
        #hp = y.result_queue.get()
        
        
        #loop.run_until_complete(
        #        rrun_calculation(
        #            importJSON,
        #            a
        #        )
        #)
        #y = run_calculation(
        #    importJSON,
        #    a
        #)

        #print(y)
        #hp = y.result_queue.get()
        #thread = Thread(target=importJSON,args=(a.pk,))
        #importJSON(a)
        #thread.daemon = True
        #thread.start()
        xx = WorkflowFactory('post.ProcessInputs')
        print(xx)
        print('MUUUUU', self.extended)
        submit_kwargs = {
                'incoming_request':hp,
                'predefined':Dict(dict=self.extended),
                'property_to_calculate': Str(prop)
                }
        y = submit_job(xx, **submit_kwargs)
        print(y)
        wf = y.result_queue.get()

        #thread = Thread(target=submit_job,args=(hp),kwargs={submit_kwargs})
        #thread.daemon = True
        #thread.start()
        import time
        time.sleep(2)
        if not wf.is_finished_ok:
            print('Structure retrieval error. See node uuid={} for more specific report'.format(wf.uuid))
            return {
                'error': wf.exit_message,
                'message': msg,
                'stored_request': wf.inputs.request.get_dict(),
            }
        else:
            exwf = Distribute(wf, prop)
            print( ' Successful retrieval of structure, {}, workflow at uuid {}'.format(
                wf.inputs.structure.pk, exwf.pk
            ))
            return {
                'error': wf.exit_message,
                'message': msg,
                'stored_request': wf.inputs.request.get_dict(),
            }
            # get to the actual calculation of the workflow


class existing(Resource):

    def get(self, prop):
        """
        check if there is any instance in the database
        related to the calculation required for a material
        returns any items that need to be checked
        : prop endpoint to the calculation prop
        : get queries define a projection for the property in the database
        """
        from aiida_post.other.group_initialize import check_db

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


class input(Resource):

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


