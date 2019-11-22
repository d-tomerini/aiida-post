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
from flask_restful import Resource, reqparse
from six.moves.urllib.parse import unquote  # pylint: disable=import-error

# aiida
from aiida.orm import Float, Dict, Str
from aiida.plugins import DataFactory, CalculationFactory, WorkflowFactory
from aiida.restapi.resources import BaseResource, ProcessNode

# local imports
from aiida_post.submit.distributor import Distribute


class submit(BaseResource):

    def __init__(self, **kwargs):
        super(submit, self).__init__(**kwargs)
        # Add the configuration file for my app
        # Taken almost verbatim from the configuration handling of BaseResource
        conf_keys = ('AVAILABLE_CODES', 'PROPERTY_MAPPING')
        self.extended = {k: kwargs[k] for k in conf_keys if k in kwargs}

    def post(self):
        """
        Route to manage the requests from the app
        Access is through a JSON file passed to the server containing the input required for calculation
        Data is handled and responded accordingly

        :param prop: the quantity we required for calculation, passed as the endpoint
        """
        from aiida.orm import Dict
        from aiida_post.tools.convert import Request_To_Dictionary

        # initialize response
        path = unquote(request.path)
        query_string = unquote(request.query_string.decode('utf-8'))
        url = unquote(request.url)
        url_root = unquote(request.url_root)

        # This takes some additional info from the flask query, and store it into a node
        # not sure yet if it makes sense to store it.
        # but at least it can be returned after the request
        HttpData = DataFactory('post.HttpData')

        reqdata = Request_To_Dictionary(request)
        node = Dict(dict=reqdata).store()

        response = Distribute(
            reqdata['json'],  # the actual json input of the request
            self.extended
        )

        data = dict(
            method=request.method,
            url=url,
            url_root=url_root,
            path=request.path,
            id=None,
            query_string=request.query_string.decode('utf-8'),
            resource_type='submission of workflows',
            request_content=reqdata['json'],
            data=response
        )

        return self.utils.build_response(status=200, data=data)


class existing(Resource):

    def __init__(self, **kwargs):
        super(existing, self).__init__(**kwargs)
        # Add the configuration file for my app
        # Taken almost verbatim from the configuration handling of BaseResource
        conf_keys = ('AVAILABLE_CODES', 'PROPERTY_MAPPING')
        self.extended = {k: kwargs[k] for k in conf_keys if k in kwargs}

    def get(self):
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


class duplicates(Resource):

    def get(self):
        """
        search of an input by ID that is known by the program
        returns property and/or status of the calculation
        This will probably go away to be integrated with the submit check
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

    def get(self):
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


class properties(BaseResource):

    def __init__(self, **kwargs):
        super(properties, self).__init__(**kwargs)
        # Add the configuration file for my app
        # Taken almost verbatim from the configuration handling of BaseResource
        conf_keys = ('AVAILABLE_CODES', 'PROPERTY_MAPPING')
        self.extended = {k: kwargs[k] for k in conf_keys if k in kwargs}

    def get(self):
        """
        Returns a list of the properties that are available for calculation
        This is related to the entry points on aiida_post.workflow, that relate
        a keyword to the workflow in charge of the calculation.
        It might be interesting to trigger individual json file to see how this property
        is called inside a result node of the workflow, as we would not want to have a
        link with the specific name, but a general attribute/node type/name
        """
        path = unquote(request.path)
        url = unquote(request.url)
        url_root = unquote(request.url_root)

        mapping = self.extended['PROPERTY_MAPPING']

        data = dict(
            method=request.method,
            url=url,
            url_root=url_root,
            path=request.path,
            id=None,
            query_string=request.query_string.decode('utf-8'),
            resource_type='Information about the properties available for calculation',
            request_content=None,
            data=mapping
        )

        return self.utils.build_response(status=200, data=data)


class status(ProcessNode):

    _parse_pk_uuid = 'uuid'  # Parse a uuid pattern in the URL path (not a pk)

    def get(self, id=None):
        """
        Returns the log file and the status of the workflow in progress
        """
        from aiida_post.common.formatter import format_wf

        # Unpack the URL
        path = unquote(request.path)
        url = unquote(request.url)
        url_root = unquote(request.url_root)

        (resource_type, page, node_id, query_type) = self.utils.parse_path(path, parse_pk_uuid=self.parse_pk_uuid)

        node = self._load_and_verify(node_id)

        data = self.trans.get_report(node)
        data.update(workflow=format_wf(node))

        data = dict(
            method=request.method,
            url=url,
            url_root=url_root,
            path=path,
            id=node_id,
            query_string=request.query_string.decode('utf-8'),
            resource_type=resource_type,
            data=data
        )

        return self.utils.build_response(status=200, data=data)
