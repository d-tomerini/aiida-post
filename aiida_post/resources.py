# -*- coding: utf-8 -*-
"""
This module contains the general resources to be called by the main api
"""

from __future__ import absolute_import
from __future__ import print_function
from flask import request
from aiida.restapi.resources import BaseResource
from aiida_post.submit.distributor import distribute


def build_response(req, resource_type, data):
    """
    Create a standard response for the request, uniform for all the endpoints.
    :param req: Flask object containing the incoming request
    :param resource_type: string to describe the endpoint
    :data: dictionary of data to return
    :return: output dictionary of the request
    """
    from urllib.parse import unquote

    return dict(
        method=req.method,
        url=unquote(req.url),
        url_root=unquote(req.url_root),
        path=req.path,
        query_string=req.query_string.decode('utf-8'),
        resource_type=resource_type,
        data=data
    )


class GResource(BaseResource):
    """
    Generic resource class that loads also the local variables needed by the extended REST API.
    Variables are stored in the extended property of the class
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Add the configuration file for my app
        # Taken almost verbatim from the configuration handling of BaseResource
        conf_keys = ('AVAILABLE_CODES', 'PROPERTY_MAPPING', 'PROPERTY_OUTPUTS')
        self.extended = {k: kwargs[k] for k in conf_keys if k in kwargs}


class GSubmit(GResource):
    """
    Endpoint to submit AiiDA workflows
    """

    def post(self):
        """
        Route to manage the requests from the app
        Access is through a JSON file passed to the server containing the input required for calculation
        Data is handled and responded accordingly
        """
        from aiida_post.common.formatter import format_wf

        content = request.get_json()

        # whether I want to submit a workflow from the desired property, or from a known workflow entrypoint
        # pathlist = self.utils.split_path(self.utils.strip_api_prefix(path))

        duplicates = request.args.get('search_duplicates', default=False)
        submission = request.args.get('submission_from', default='property')

        required_keys = ['calculation', 'input']
        for key in required_keys:
            if key not in content:
                raise ValueError('Not found compulsory key <{}> in json input'.format(key))
        prop = content['calculation']
        # simply assume the workflow is loaded from the property from the entrypoint

        # allowed keys for the submission type
        from_submission = ['property', 'workflow']
        if submission not in from_submission:
            raise ValueError(
                'Submission type <{}> not recognized: accepted: {}.'.format(submission, ', '.join(from_submission))
            )

        if submission == 'property':
            # get the workflow associated with the property
            available_properties = self.extended['PROPERTY_MAPPING']
            if prop not in available_properties:
                raise ValueError('<{}> is not in the list of available properties.'.format(prop))
            entrypoint = available_properties[prop]
        elif submission == 'workflow':
            # load the entrypoint directly
            entrypoint = prop

        if duplicates:
            # check for nodes with the same `input` subdictionary, and return a list
            # decide how to implement
            pass

        workflow, node = distribute(content, entrypoint)

        data = build_response(request, resource_type='submission of workflows', data=format_wf(workflow))
        data['request_content'] = dict(content, node=node.uuid)

        return self.utils.build_response(status=200, data=data)


class GProperties(GResource):
    """
    Endpoint to return a list of supported calculation properties
    """

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
        from urllib.parse import unquote

        available_properties = self.extended['PROPERTY_MAPPING']
        property_outputs = self.extended['PROPERTY_OUTPUTS']

        pathlist = self.utils.split_path(unquote(request.path))
        schema = pathlist[-1]
        (
            limit, offset, perpage, orderby, filters, download_format, download, filename, tree_in_limit,
            tree_out_limit, attributes, attributes_filter, extras, extras_filter, full_type
        ) = self.utils.parse_query_string(request.query_string.decode('utf-8'))

        if schema == 'properties':
            # just a request for the available properties connected to a workflow
            out = available_properties
            resource_type = 'Information about the properties available for calculation'
        elif schema == 'list':
            if entrypoint not in available_properties:
                raise ValueError('<{}> is not in the list of the supported properties'.format(entrypoint))
            prop = available_properties[entrypoint]
            resource_type = 'List of nodes from the required entrypoint'
            workflowtype = WorkflowFactory(prop)
            query = QueryBuilder().append(workflowtype, filters=filters, project=['uuid', 'attributes'])
            out = [dict(uuid=uuid, attributes=attr) for [uuid, attr] in query.all()]
        elif schema == 'outputs':
            if entrypoint not in property_outputs:
                raise ValueError(
                    '<{}> does not have defined outputs in property outputs config file'.format(entrypoint)
                )
            outputs = property_outputs[entrypoint]
            prop = available_properties[entrypoint]
            if entrypoint not in available_properties:
                raise ValueError('<{}> is not in the list of the supported properties'.format(prop))
            workflow = WorkflowFactory(prop)
            resource_type = 'Property name, and its position with respect to the workflow outputs'
            out = dict(
                property_name=outputs.name,
                is_node=outputs.is_node,
                output_node_name=outputs.edge,
                property_location=outputs.project,
                workflow=workflow.get_name()
            )
        else:
            try:
                entry = available_properties[entrypoint]
            except:
                raise ValueError(
                    '<{}> is not in the list of available properties: {}.'.format(
                        entrypoint, ' ,'.join(list(available_properties.keys()))
                    )
                )

            workflow = WorkflowFactory(entry)
            resource_type = 'Information about the workflow {}'.format(schema)
            # which part of the description do we want to print out?
            description = workflow.get_description()
            mydata = description['spec'][schema]
            # list of all calculations of this type
            if schema != 'outline':
                delete_key(mydata, '_', startswith=True)
            out = {'workflow': workflow.get_name(), 'description': description['description'], str(schema): mydata}

        data = build_response(request, resource_type=resource_type, data=out)

        return self.utils.build_response(status=200, data=data)


class GStatus(GResource):
    """
    endpoint to check the status of a workflow, together with its log messages
    """
    _parse_pk_uuid = 'uuid'  # Parse a uuid pattern in the URL path (not a pk)

    from aiida.restapi.translator.nodes.process.process import ProcessTranslator
    _translator_class = ProcessTranslator

    def get(self, node_id=None):
        """
        Returns the log file and the status of the workflow in progress
        """
        from aiida_post.common.formatter import format_wf

        node = self._load_and_verify(node_id)

        out = self.trans.get_report(node)

        out.update(workflow=format_wf(node))

        data = build_response(request, resource_type='workflow status', data=out)

        return self.utils.build_response(status=200, data=data)


class GWorkflows(GResource):
    """
    Endpoint to return the workflow input specification.
    This takes into account the workflow entry point, and not the property, as to be more general.
    It is a generalization of the endpoint properties
    """

    def get(self, entrypoint=None):
        """
        Returns all the possible inputs, outputs or outline of a workflow
        """
        from urllib.parse import unquote
        from aiida.plugins import WorkflowFactory
        from aiida.plugins.entry_point import get_entry_point_names
        from aiida_post.common.formatter import delete_key, delete_key_check_dict

        # all the query parsing that's needed from AiiDA REST
        # I probably need much less than this!
        (
            limit, offset, perpage, orderby, filters, download_format, download, filename, tree_in_limit,
            tree_out_limit, attributes, attributes_filter, extras, extras_filter, full_type
        ) = self.utils.parse_query_string(request.query_string.decode('utf-8'))

        if not entrypoint:
            # return a list of the available entry points for workflows
            out = get_entry_point_names('aiida.workflows')
            resource_type = 'List of all the available entrypoints for AiiDA workflows'
        else:
            pathlist = self.utils.split_path(unquote(request.path))
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

                for innervalue in value.values():
                    delete_key_check_dict(mydata, key, str(innervalue))

                #check if I should remove keys for better view

            out = {'workflow': workflow.get_name(), 'description': description['description'], str(schema): mydata}

        data = build_response(request, resource_type=resource_type, data=out)

        return self.utils.build_response(status=200, data=data)


class GExisting(GResource):
    """
    Endpoint to query for existing resources types
    """

    from aiida.restapi.translator.nodes.node import NodeTranslator

    _translator_class = NodeTranslator
    _parse_pk_uuid = 'uuid'  # Parse a uuid pattern in the URL path (not a pk)

    def get(self, prop=None, node_id=None):
        """
        check if there is any instance in the database
        Needs thinking on how to query for properties -- probably schema is best
        """
        from aiida.plugins import WorkflowFactory
        from aiida.orm import QueryBuilder, Node

        if not prop:
            raise ValueError('Property not selected')
        if not node_id:
            raise ValueError('node not selected')
        available_properties = self.extended['PROPERTY_MAPPING']
        output_mapping = self.extended['PROPERTY_OUTPUTS']

        if prop not in available_properties:
            raise ValueError('<{}> is not in the list of available properties.'.format(prop))
        entry = available_properties[prop]
        workflow = WorkflowFactory(entry)
        mapping = output_mapping[prop]

        node = self._load_and_verify(node_id)

        # looks exactly for the required property with the query, as defined by PROPERTY_OUTPUTS
        qb = QueryBuilder().append(node.__class__, filters={
            'uuid': node.uuid
        }, tag='input').append(workflow, with_incoming='input', tag='wf', project='uuid').append(
            Node, with_incoming='wf', edge_filters={'label': mapping.edge}, project=mapping.project
        )
        properties = []
        for item in qb.all():
            properties.append(
                dict(property_name=mapping.name, property_value=item[1], workflow=item[0], is_node=mapping.is_node)
            )

        # look for all processes of the same class, to check if some are ongoing/excepted
        wfs = QueryBuilder().append(node.__class__, filters={
            'uuid': node.uuid
        }, tag='input').append(
            workflow,
            with_incoming='input',
            tag='wf',
            project=['uuid', 'attributes.process_state', 'attributes.exit_status']
        )
        workfunctions = []
        for item in wfs.all():
            workfunctions.append(dict(uuid=item[0], process_state=item[1], exit_status=item[2]))

        data = build_response(
            request,
            resource_type='properties connected with the node input',
            data=dict(workfunctions=workfunctions, properties=properties)
        )

        return self.utils.build_response(status=200, data=data)


class GData(GResource):
    """
    Endpoint to return all the structuredata in the database, and query with formula
    """
    from aiida.restapi.translator.nodes.node import NodeTranslator

    _translator_class = NodeTranslator
    _parse_pk_uuid = 'uuid'  # Parse a uuid pattern in the URL path (not a pk)

    def get(self):
        """
        To check if useful
        """
        from aiida.orm import load_node

        # all the query parsing that's needed from AiiDA REST
        # I probably need much less than this!
        (
            limit, offset, perpage, orderby, filters, download_format, download, filename, tree_in_limit,
            tree_out_limit, attributes, attributes_filter, extras, extras_filter, full_type
        ) = self.utils.parse_query_string(request.query_string.decode('utf-8'))

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
            formula_type = request.args.get('chemical_formula_type', default='hill_compact')
            filtered_results = []
            for res in results['nodes']:
                try:
                    node = load_node(res['uuid'])
                    node_formula = node.get_formula(mode=formula_type)
                    if node_formula == chemical_formula:
                        filtered_results.append(res)
                except:
                    pass
        else:
            filtered_results = results['nodes']

        data = build_response(
            request,
            resource_type='structuredata search',
            data=dict(total_number_of_structures=total_count, nodes=filtered_results)
        )

        return self.utils.build_response(status=200, data=data)


# Additional endpoints to implement if useful


class GAppNodes(GResource):
    """
    Endpoint to return all the already executed calculation of a specific kind
    Useful? To implement
    """

    def get(self):
        """
        To check if useful
        """
        raise ValueError('Endpoint not yet implemented')
