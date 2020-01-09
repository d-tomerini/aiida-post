# -*- coding: utf-8 -*-
"""
This module contains the general resources to be called by the main api
"""

from __future__ import absolute_import
from __future__ import print_function
from urllib.parse import unquote
from flask import request

from aiida.restapi.resources import BaseResource, ProcessNode
from aiida_post.submit.distributor import distribute


class GSubmit(BaseResource):
    """
    Endpoint to submit AiiDA workflows
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Add the configuration file for my app
        # Taken almost verbatim from the configuration handling of BaseResource
        conf_keys = ('AVAILABLE_CODES', 'PROPERTY_MAPPING', 'PROPERTY_OUTPUTS')
        self.extended = {k: kwargs[k] for k in conf_keys if k in kwargs}

    def post(self):
        """
        Route to manage the requests from the app
        Access is through a JSON file passed to the server containing the input required for calculation
        Data is handled and responded accordingly
        """
        from aiida_post.common.formatter import format_wf
        #from aiida_post.tools.convert import Request_To_Dictionary

        # initialize response
        path = unquote(request.path)
        url = unquote(request.url)
        url_root = unquote(request.url_root)
        query_string = request.query_string.decode('utf-8')

        #reqdata = Request_To_Dictionary(request)
        content = request.get_json()

        # whether I want to submit a workflow from the desired property, or from a known workflow entrypoint
        pathlist = self.utils.split_path(self.utils.strip_api_prefix(path))

        duplicates = request.args.get('search_duplicates')
        submission = request.args.get('submission_from', default='property')

        required_keys = ['calculation', 'input']
        for key in required_keys:
            if key not in content:
                raise ValueError('Not found compulsory key <{}> in json'.format(key))
        prop = content['calculation']
        # simply assume the workflow is loaded from the property from the entrypoint

        if submission == 'property':
            # get the workflow associated with the property
            available_properties = self.extended['PROPERTY_MAPPING']
            if prop not in available_properties:
                raise ValueError('<{}> is not in the list of available properties.'.format(prop))
            entrypoint = available_properties[prop]
        elif submission == 'workflow':
            # load the entrypoint directly
            entrypoint = prop
        else:
            raise ValueError('Workflow submission type not recognized: <{}>.'.format(submission))

        if duplicates:
            # check for nodes with the same `input` subdictionary, and return a list
            pass

        workflow, node = distribute(content, entrypoint)

        response = format_wf(workflow)

        request_content = dict(content, node=node.uuid)
        data = dict(
            method=request.method,
            url=url,
            url_root=url_root,
            path=request.path,
            id=None,
            query_string=query_string,
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
        super().__init__(**kwargs)
        # Add the configuration file for my app
        # Taken almost verbatim from the configuration handling of BaseResource
        conf_keys = ('AVAILABLE_CODES', 'PROPERTY_MAPPING', 'PROPERTY_OUTPUTS')
        self.extended = {k: kwargs[k] for k in conf_keys if k in kwargs}

    def get(self, entrypoint=None):
        """
        Returns a list of the properties that are available for calculation
        This is related to the entry points on aiida_post.workflow, that relate
        a keyword to the workflow in charge of the calculation.
        It might be interesting to trigger individual json file to see how this property
        is called inside a result node of the workflow, as we would not want to have a
        link with the specific name, but a general attribute/node type/name
        """
        from aiida.plugins import WorkflowFactory
        from aiida.orm import QueryBuilder
        from aiida_post.common.formatter import delete_key
        # Unpack the URL
        path = unquote(request.path)
        url = unquote(request.url)
        url_root = unquote(request.url_root)

        query_string = request.query_string.decode('utf-8')
        pathlist = self.utils.split_path(self.utils.strip_api_prefix(path))
        schema = pathlist[-1]
        (
            limit, offset, perpage, orderby, filters, download_format, download, filename, tree_in_limit,
            tree_out_limit, attributes, attributes_filter, extras, extras_filter, full_type
        ) = self.utils.parse_query_string(query_string)

        available_properties = self.extended['PROPERTY_MAPPING']
        if schema == 'properties':
            # just a request for the available properties connected to a workflow
            outdata = available_properties
            resource_type = 'Information about the properties available for calculation'
        elif schema == 'list':
            prop = available_properties[entrypoint]
            resource_type = 'List of nodes from the required entrypoint'
            workflowtype = WorkflowFactory(prop)
            qb = QueryBuilder().append(workflowtype, filters=filters, project=['uuid', 'attributes'])
            outdata = [dict(uuid=uuid, attributes=attr) for [uuid, attr] in qb.all()]
        else:
            try:
                entry = available_properties[entrypoint]
            except:
                raise ValueError('<{}> is not in the list of available properties.'.format(entrypoint))

            workflow = WorkflowFactory(entry)
            resource_type = 'Information about the workflow {}'.format(schema)
            # which part of the description do we want to print out?
            description = workflow.get_description()
            mydata = description['spec'][schema]
            # list of all calculations of this type
            if schema != 'outline':
                delete_key(mydata, '_', startswith=True)
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
        super().__init__(**kwargs)
        # Add the configuration file for my app
        # Taken almost verbatim from the configuration handling of BaseResource
        conf_keys = ('AVAILABLE_CODES', 'PROPERTY_MAPPING', 'PROPERTY_OUTPUTS')
        self.extended = {k: kwargs[k] for k in conf_keys if k in kwargs}

    def get(self, entrypoint=None):
        """
        Returns all the possible inputs, outputs or outline of a workflow
        """
        from aiida.plugins import WorkflowFactory
        from aiida.plugins.entry_point import get_entry_point_names
        from aiida_post.common.formatter import delete_key
        from aiida_post.common.formatter import delete_key_check_dict

        # Unpack the URL
        path = unquote(request.path)
        url = unquote(request.url)
        url_root = unquote(request.url_root)

        pathlist = self.utils.split_path(self.utils.strip_api_prefix(path))

        query_string = request.query_string.decode('utf-8')
        # all the query parsing that's needed from AiiDA REST
        # I probably need much less than this!
        (
            limit, offset, perpage, orderby, filters, download_format, download, filename, tree_in_limit,
            tree_out_limit, attributes, attributes_filter, extras, extras_filter, full_type
        ) = self.utils.parse_query_string(query_string)

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
                # remove keys that starts with '_'
                delete_key(mydata, '_', startswith=True)

            for key, value in filters.items():
                # filters are {key:{operator:value}}. I want key and value
                # value is a string to be compared

                for k, v in value.items():
                    delete_key_check_dict(mydata, key, str(v))

                #check if I should remove keys for better view

            outdata = {'workflow': workflow.get_name(), 'description': description['description'], str(schema): mydata}

        data = dict(
            method=request.method,
            url=url,
            url_root=url_root,
            path=path,
            id=None,
            query_string=query_string,
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
        super().__init__(**kwargs)
        # Add the configuration file for my app
        # Taken almost verbatim from the configuration handling of BaseResource
        conf_keys = ('AVAILABLE_CODES', 'PROPERTY_MAPPING', 'PROPERTY_OUTPUTS')
        self.extended = {k: kwargs[k] for k in conf_keys if k in kwargs}

    def get(self):
        """
        check if there is any instance in the database
        related to the calculation required for a material
        Needs thinking on how to query for properties -- probably schema is best
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


class GData(BaseResource):
    """
    Endpoint to return all the structuredata in the database, and query with formula
    """
    from  aiida.restapi.translator.nodes.node import NodeTranslator

    _translator_class = NodeTranslator
    _parse_pk_uuid = 'uuid'  # Parse a uuid pattern in the URL path (not a pk)

    def __init__(self, **kwargs):
        from aiida.restapi.common.utils import Utils

        super().__init__(**kwargs)
        # Add the configuration file for my app
        # Taken almost verbatim from the configuration handling of BaseResource
        conf_keys = ('AVAILABLE_CODES', 'PROPERTY_MAPPING', 'PROPERTY_OUTPUTS')
        self.extended = {k: kwargs[k] for k in conf_keys if k in kwargs}


    def get(self):
        """
        To check if useful
        """
        from aiida.orm import load_node

        # initialize response
        path = unquote(request.path)
        url = unquote(request.url)
        url_root = unquote(request.url_root)
        query_string = request.query_string.decode('utf-8')

        pathlist = self.utils.split_path(self.utils.strip_api_prefix(path))
        # all the query parsing that's needed from AiiDA REST
        # I probably need much less than this!
        (
            limit, offset, perpage, orderby, filters, download_format, download, filename, tree_in_limit,
            tree_out_limit, attributes, attributes_filter, extras, extras_filter, full_type
        ) = self.utils.parse_query_string(query_string)

        if not limit:
            limit = self.utils.limit_default
        if not offset:
            offset = 0
        # This is a hack SPECIFICALLY for structuredata types, and to search for
        # chemical formula

        filters.pop('chemical_formula', None)
        filters.pop('chemical_formula_type', None)
        full_type = 'data.structure.StructureData.|'

        self.trans.set_query(
            query_type='default',
            filters=filters,
            orders=orderby,
            download_format=download_format,
            download=download,
            filename=filename,
            attributes=attributes,
            attributes_filter=attributes_filter,
            extras=extras,
            extras_filter=extras_filter,
            full_type=full_type
        )

        ## Count results
        total_count = self.trans.get_total_count()
        self.trans.set_limit_offset(limit=limit, offset=offset)
        results = self.trans.get_results()
        if attributes_filter is not None and attributes:
            for node in results['nodes']:
                node['attributes'] = {}
                if not isinstance(attributes_filter, list):
                    attributes_filter = [attributes_filter]
                for attr in attributes_filter:
                    node['attributes'][str(attr)] = node['attributes.' + str(attr)]
                    del node['attributes.' + str(attr)]
        ## filter response

        chemical_formula = request.args.get('chemical_formula')

        if chemical_formula is not None:
            formula_type = request.args.get(
                'chemical_formula_type',
                default='hill_compact'
            )
            filtered_results = []
            # found = 0
            for res in results['nodes']:
                try:
                    node = load_node(res)
                    node_formula = node.get_formula(mode=formula_type)
                    if node_formula == formula:
                        filtered_results.append(res)
                        # found += 1
                        # if found > limit:
                        #     break
                except:
                    pass
        else:
            filtered_results = results['nodes']

        data = dict(
            method=request.method,
            url=url,
            url_root=url_root,
            path=path,
            id=None,
            query_string=request.query_string.decode('utf-8'),
            resource_type='structuredata search',
            data=dict(total_number_of_structures=total_count, nodes=filtered_results)
        )
        return self.utils.build_response(status=200, data=data)

        # Now I should prepare a query for the database, in order to retrieve all the possible
        # structuredata items in the database.
        # Call of a function to calculate the formula might be long
        # for this reason, I will select a slice according to limit, offset and perpage
