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


class GSubmit(BaseResource):
    """
    Endpoint to submit AiiDA workflows
    """

    def __init__(self, **kwargs):
        super(GSubmit, self).__init__(**kwargs)
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
        #from aiida_post.tools.convert import Request_To_Dictionary

        # initialize response
        path = unquote(request.path)
        url = unquote(request.url)
        url_root = unquote(request.url_root)

        pathlist = self.utils.split_path(self.utils.strip_api_prefix(path))

        #reqdata = Request_To_Dictionary(request)
        content = request.get_json()
        node = Dict(dict=content).store()

        # whether I want to submit a workflow from the desired property, or from a known workflow entrypoint
        submission = pathlist[-1]
        required_keys = ['calculation', 'input']
        for key in required_keys:
            if key not in content:
                raise ValueError('Not found compulsory key <{}> is json'.format(key))
        prop = content['calculation']
        # simply assume the workflow is loaded from the property from the entrypoint

        if submission == 'workflow':
            # load the entrypoint directly
            entrypoint = prop
        else:
            # get the workflow associated with the property
            available_properties = self.extended['PROPERTY_MAPPING']
            if prop not in available_properties:
                raise ValueError('<{}> is not in the list of available properties.'.format(prop))
            entrypoint = available_properties[prop]

        # This takes some additional info from the flask query, and store it into a node
        # not sure yet if it makes sense to store it.
        # but at least it can be returned after the request
        #HttpData = DataFactory('post.HttpData')

        response = Distribute(content, entrypoint)

        request_content = dict(content, node=node.uuid)
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


class GProperties(BaseResource):
    """
    Endpoint to return a list of supported calculation properties
    """

    def __init__(self, **kwargs):
        super(GProperties, self).__init__(**kwargs)
        # Add the configuration file for my app
        # Taken almost verbatim from the configuration handling of BaseResource
        conf_keys = ('AVAILABLE_CODES', 'PROPERTY_MAPPING')
        self.extended = {k: kwargs[k] for k in conf_keys if k in kwargs}

    def get(self, node_id=None):
        """
        Returns a list of the properties that are available for calculation
        This is related to the entry points on aiida_post.workflow, that relate
        a keyword to the workflow in charge of the calculation.
        It might be interesting to trigger individual json file to see how this property
        is called inside a result node of the workflow, as we would not want to have a
        link with the specific name, but a general attribute/node type/name
        """
        from aiida.plugins import WorkflowFactory
        from aiida_post.common.formatter import pop_underscore
        # Unpack the URL
        path = unquote(request.path)
        url = unquote(request.url)
        url_root = unquote(request.url_root)

        pathlist = self.utils.split_path(self.utils.strip_api_prefix(path))

        if pathlist[-1] == 'properties':
            # just a request for the available properties connected to a workflow
            outdata = self.extended['PROPERTY_MAPPING']
            resource_type = 'Information about the properties available for calculation'
        else:
            available_properties = self.extended['PROPERTY_MAPPING']
            try:
                entry = available_properties[node_id]
            except:
                raise ValueError('<{}> is not in the list of available properties.'.format(node_id))

            workflow = WorkflowFactory(entry)
            schema = pathlist[-1]
            resource_type = 'Information about the workflow {}'.format(schema)
            # which part of the description do we want to print out?
            description = workflow.get_description()
            mydata = description['spec'][schema]
            if schema != 'outline':
                pop_underscore(mydata)
            outdata = {'workflow': workflow.get_name(), 'description': description['description'], str(schema): mydata}

        data = dict(
            method=request.method,
            url=url,
            url_root=url_root,
            path=request.path,
            id=None,
            query_string=request.query_string.decode('utf-8'),
            resource_type=resource_type,
            request_content=None,
            data=outdata
        )

        return self.utils.build_response(status=200, data=data)


class GStatus(ProcessNode):
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


class GWorkflows(BaseResource):
    """
    Endpoint to return the workflow input specification.
    This takes into account the workflow entry point, and not the property, as to be more general.
    It is a generalization of the endpoint properties
    """

    def __init__(self, **kwargs):
        super(GWorkflows, self).__init__(**kwargs)
        # Add the configuration file for my app
        # Taken almost verbatim from the configuration handling of BaseResource
        conf_keys = ('AVAILABLE_CODES', 'PROPERTY_MAPPING')
        self.extended = {k: kwargs[k] for k in conf_keys if k in kwargs}

    def get(self, entrypoint=None):
        """
        Returns all the possible inputs, outputs or outline of a workflow
        """
        from aiida.plugins import WorkflowFactory
        from aiida.plugins.entry_point import get_entry_point_names
        from aiida_post.common.formatter import pop_underscore

        # Unpack the URL
        path = unquote(request.path)
        url = unquote(request.url)
        url_root = unquote(request.url_root)

        pathlist = self.utils.split_path(self.utils.strip_api_prefix(path))

        if not entrypoint:
            # return a list of the available entry points for workflows
            outdata = get_entry_point_names('aiida.workflows')
            resource_type = 'List of all the available entrypoints for AiiDA workflows'
        else:
            schema = pathlist[-1]
            resource_type = 'Information about the workflow {}'.format(schema)
            workflow = WorkflowFactory(entrypoint)
            # which part of the description do we want to print out?
            description = workflow.get_description()
            mydata = description['spec'][schema]
            if schema != 'outline':
                pop_underscore(mydata)
            outdata = {'workflow': workflow.get_name(), 'description': description['description'], str(schema): mydata}

        data = dict(
            method=request.method,
            url=url,
            url_root=url_root,
            path=path,
            id=None,
            query_string=request.query_string.decode('utf-8'),
            resource_type=resource_type,
            data=outdata
        )

        return self.utils.build_response(status=200, data=data)


# Additional endpoints to implement if useful


class GExisting(BaseResource):
    """
    Endpoint to query for existing resources types
    """

    def __init__(self, **kwargs):
        super(GExisting, self).__init__(**kwargs)
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


class GDuplicates(BaseResource):
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


class GAppNodes(BaseResource):
    """
    Endpoint to return all the already executed calculation of a specific kind
    Useful? To implement
    """

    def get(self):
        """
        To check if useful
        """
        raise ValueError('Endpoint not yet implemented')
