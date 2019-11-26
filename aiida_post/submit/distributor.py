# -*- coding: utf-8 -*-
"""
This module deals with the submission process.
This needs to be handled from a process in a separate thread from
Flask, and it is handled by the threaded fucnction, that spawn a new thread
and submit it from there. Since the submission job itself is a minimally
intensive process, it should not be a problem to have cuncurrent threads
"""

from __future__ import absolute_import
from __future__ import print_function

from aiida.plugins import WorkflowFactory
from aiida.common import exceptions
from aiida_post.common.threaded import get_builder, submit_builder


def Distribute(req, info):
    """
    After the retrieval of the structure, we proceed with the distribution of the task
    according to the requested data.
    : input req: a dictionary that contains info about the incoming request and the POST file
    : input info: a dictionary of CONFIG values that can be useful
    : return response: a dictionary with the workflow info, error message and additional info
    """
    from aiida_post.common.formatter import format_wf
    # prepare to return data containing eventual error messages and workchain properties
    response = {}
    error_info = ''
    wfinfo = None

    # this needs to be handled by schemas for future-proofness

    required_keys = ['calculation', 'input']
    for key in required_keys:
        if key not in req:
            raise ValueError('Not found compulsory key <{}> is json'.format(key))

    prop = req['calculation']

    # initial checks

    # check my property list
    available_properties = info['PROPERTY_MAPPING']

    if prop not in available_properties:
        raise ValueError('<{}> is not in the list of available properties.'.format(prop))

    entry = available_properties[prop]
    WorkFlow = WorkflowFactory(entry)

    # creating the namespaces for the workflow, from the
    future = get_builder(WorkFlow)
    builder = future.result()

    # standard code needs thinking
    #Assign_code(builder, req)
    # Assign ports to the workflow
    Process_NameSpaces(builder, req['input'])


    future = submit_builder(builder)
    workflow = future.result()
    wfinfo = format_wf(workflow)

    response.update(workflow=wfinfo, error=error_message, error_info=error_info)

    return response


def Process_NameSpaces(builder, req):
    """
    Process the request in order to create a dictionary of the right type of Nodes for the input of a workchain.
    :input namespace: created namespace for the worklow
    :input req: a dictionary for the workchain inputs.
    :returns out: a dictionary with the AiiDA objects to run the calculation
    the value of a key is expected to contain a value to fill the AiiDA data type;
    if instead it has to load an `aiida.orm.Node` from the database, it NEEDS to be a dictionary with one key with the
    value 'LOADNODE'.
    The subroutine runs recursively (for nested namespaces) in order to create the correct input
    """
    from aiida.orm import load_node, Node, ArrayData, Bool, Code, Dict, Float, Int, List
    from aiida.engine.processes.ports import PortNamespace

    namespace = builder._port_namespace
    # If we decide Codes can be default, I need something here to assign things
    for key, value in req.items():
        if key not in namespace:
            raise exceptions.InputValidationError(' <{}> is not a valid input for the workflow'.format(key))
        valid = namespace[key].valid_type
        #check if it is a dictionary, and I should load the node instead of taking the value
        if isinstance(value, dict):
            if 'LOADNODE' in value:
                node = load_node(value('LOADNODE'))
                if isinstance(node, valid):
                    builder[key] = node
                else:
                    raise exceptions.InputValidationError(
                        '<{}> is not a valid type: <{}>. Expected: {}'.format(node.__class, key, valid)
                    )
        if isinstance(namespace[key], PortNamespace):
            # recursevily look for deeper namespaces
            Process_NameSpaces(builder[key], req[key])
        else:
            # finally, process the individual values
            # maybe we can do better than dumb iteration?
            # first standard python types
            if isinstance(key, valid):
                builder[key] = value
            elif isinstance(Int(), valid):
                try:
                    builder[key] = Int(int(value))
                except:
                    raise exceptions.InputValidationError(
                        'Error while assigning integer <{}> to Int class.'.format(value)
                    )
            elif isinstance(Float(), valid):
                try:
                    builder[key] = Float(float(value))
                except:
                    raise exceptions.InputValidationError(
                        'Error while assigning float <{}> to Float class.'.format(value)
                    )
            elif isinstance(Bool(), valid):
                try:
                    builder[key] = Bool(bool(value))
                except:
                    raise exceptions.InputValidationError(
                        'Error while assigning boolean <{}> to Bool class.'.format(value)
                    )
            elif isinstance(Dict(), valid):
                try:
                    builder[key] = Dict(dict=value)
                except:
                    raise exceptions.InputValidationError(
                        'Error while assigning dict <{}> to Dict class.'.format(value)
                    )
            elif isinstance(List(), valid):
                try:
                    builder[key] = List(value)
                except:
                    raise exceptions.InputValidationError(
                        'Error while assigning list <{}> to List class.'.format(value)
                    )
            else:
                # now trying to assign data that I expect is going to be a Node...
                node = load_node(value)
                if isinstance(node, valid):
                    try:
                        builder[key] = node
                    except:
                        raise exceptions.InputValidationError(
                            'Error, expected {} of {} to be a node instance, but I cannot load <{}> .'.format(
                                value, key, node
                            )
                        )
                else:
                    raise exceptions.InputValidationError('Node {} is not of a valid type: {}'.format(node, valid))

    return


def Get_Namespace_Schema(namespace, schema):
    """
    Recursively process the namespace of a workflow in order to extract information about the
    input namespace, their type, if and what is  the defaul valuesif they're requested, and a help if it is available
    """
    from aiida.engine.processes.ports import PortNamespace

    for key, value in namespace.items():
        if isinstance(value, PortNamespace):
            # recursevily look for deeper namespaces
            schema[key] = {}
            Get_Namespace_Schema(value, schema[key])
        else:
            # Give all the values that might be interesting for the user.
            # name, type, has_default(), default, help
            default = None
            if value.has_default():
                default = value.default
            schema[key] = dict(
                valid_type=str(value.valid_type),
                is_required=value.required,
                has_default=value.has_default(),
                default=str(default),
                help_string=value.help
            )


# needs thinking
#def Assign_Code(builder, props):
#    """
#    Initialize the dictionary where to find the standard codes for the given workflow,
#    and assign it to the workflow builder if it has no key.
#    Maybe it is easier with a json schema?
#    : input builder: the process builder
#    : input props: the dictionary of keywords to be passed to the workflow
#    """
#    import json
#    SCHEMA_DIR = str(aiida_post.__path__[0]) + '/schemas/'
#
#    # get the name of the file to grep for the code
#    # these are stored under the process name in the 'schema' folder
#
#    name = builder._process_class.__name__
#    code_schema = SCHEMA_DIR + name + '.json'
#    with open(code_schema) as jsonfile:
#        codes = json.loads
#
#    Recursively_Assign_Code(
#        builder._port_namespace,
#        props,
#        codes
#    )
#
#    return
#
#
#
#def Recursively_Assign_Code(namespace, req, codes, error=None):
#    """
#    Needed to pass the standard code down the workchain to where it is needed
#    For the moment, we are going to assume that the code stays uniformly the same
#    throught the workchain; if this is not the case, it is probably better to
#    implement some kind of validation dictionary for each of the workchains that we support
#    """
#    # let's leave it for now
#    from aiida.orm import Code
#
#    for key, value in namespace.items():
#        # try to assign it only if REALLY necessary
#        if isinstance(namespace[key], Code):
#            if (key == 'code' and value.required and 'code' not in req and isinstance(namespace[key], Code)):
#
#
#
