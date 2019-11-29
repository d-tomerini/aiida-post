# -*- coding: utf-8 -*-
"""
Daniele Tomerini
Initial code march 2019

This module contains the general resources to be called
by the main api
"""

from __future__ import absolute_import
from flask import request
from six.moves.urllib.parse import unquote  # pylint: disable=import-error

# aiida
from aiida.restapi.resources import BaseResource, ProcessNode

# local imports
from aiida_post.submit.distributor import Distribute


class submit(BaseResource):
    """
    Endpoint to submit AiiDA workflows
    """

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
        """
        from aiida.orm import Dict
        from aiida_post.tools.convert import Request_To_Dictionary

        # initialize response
        url = unquote(request.url)
        url_root = unquote(request.url_root)

        # This takes some additional info from the flask query, and store it into a node
        # not sure yet if it makes sense to store it.
        # but at least it can be returned after the request
        #HttpData = DataFactory('post.HttpData')

        reqdata = Request_To_Dictionary(request)
        node = Dict(dict=reqdata).store()

        response = Distribute(
            reqdata['json'],  # the actual json input of the request
            self.extended
        )

        request_content = dict(data=reqdata['json'], node=node.uuid)
        data = dict(
            method=request.method,
            url=url,
            url_root=url_root,
            path=request.path,
            id=None,
            query_string=request.query_string.decode('utf-8'),
            resource_type='submission of workflows',
            request_content=request_content,
            data=response
        )

        return self.utils.build_response(status=200, data=data)


class properties(BaseResource):
    """
    Endpoint to return a list of supported calculation properties
    """

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
    """
    endpoint to check the status of a workflow, together with its log messages
    """
    _parse_pk_uuid = 'uuid'  # Parse a uuid pattern in the URL path (not a pk)

    def get(self, node_id=None):
        """
        Returns the log file and the status of the workflow in progress
        """
        from aiida_post.common.formatter import format_wf

        # Unpack the URL
        path = unquote(request.path)
        url = unquote(request.url)
        url_root = unquote(request.url_root)

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
            resource_type='workflow status',
            data=data
        )

        return self.utils.build_response(status=200, data=data)


class workflow_inputs(BaseResource):
    """
    Endpoint to return the workflow input specification
    """

    def __init__(self, **kwargs):
        super(workflow_inputs, self).__init__(**kwargs)
        # Add the configuration file for my app
        # Taken almost verbatim from the configuration handling of BaseResource
        conf_keys = ('AVAILABLE_CODES', 'PROPERTY_MAPPING')
        self.extended = {k: kwargs[k] for k in conf_keys if k in kwargs}

    def get(self, node_id=None):
        """
        Returns all the possible inputs of a workflow as a schema
        """
        from aiida.plugins import WorkflowFactory
        from aiida_post.submit.distributor import Get_Namespace_Schema
        from aiida_post.common.threaded import get_builder

        # Unpack the URL
        path = unquote(request.path)
        url = unquote(request.url)
        url_root = unquote(request.url_root)

        available_properties = self.extended['PROPERTY_MAPPING']

        try:
            entry = available_properties[node_id]
        except:
            raise ValueError('<{}> is not in the list of available properties.'.format(node_id))

        WorkFlow = WorkflowFactory(entry)

        # creating the namespaces for the workflow, from the

        future = get_builder(WorkFlow)
        builder = future.result()

        schema = {}
        Get_Namespace_Schema(builder._port_namespace, schema)

        output = dict(workflow_input_schema=schema)

        data = dict(
            method=request.method,
            url=url,
            url_root=url_root,
            path=path,
            id=None,
            query_string=request.query_string.decode('utf-8'),
            resource_type='return workflow input schema',
            data=output
        )

        return self.utils.build_response(status=200, data=data)


# Additional endpoints to implement if useful


class existing(BaseResource):
    """
    Endpoint to query for existing resources types
    """

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
        Needs thinking on how to query for properties -- probably schema is best
        """
        raise ValueError('Endpoint not yet implemented')


class duplicates(BaseResource):
    """
    Endpoint to query for existing queries of the same type
    Probably I need to save a POST query and look for dictionary databases of the same type.
    Useful?
    """

    def get(self):
        """
        To implement
        """
        raise ValueError('Endpoint not yet implemented')


class app_nodes(BaseResource):
    """
    Endpoint to return all the already executed calculation of a specific kind
    Useful? To implement
    """

    def get(self):
        """
        To check if useful
        """
        raise ValueError('Endpoint not yet implemented')
