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


def Distribute(request, entrypoint):
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
    wfinfo = None

    WorkFlow = WorkflowFactory(entrypoint)

    # creating the namespaces for the workflow, from the
    future = get_builder(WorkFlow)
    builder = future.result()

    # standard code needs thinking
    #Assign_code(builder, req)
    # Assign ports to the workflow
    Process_NameSpaces(builder, request['input'])

    future = submit_builder(builder)
    workflow = future.result()
    wfinfo = format_wf(workflow)

    response.update(workflow=wfinfo)

    return response


def Process_NameSpaces(builder, dictionary):
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
    from aiida.engine.processes.ports import PortNamespace

    namespace = builder._port_namespace
    # If we decide Codes can be default, I need something here to assign things

    for key, value in dictionary.items():
        if key not in namespace:
            raise exceptions.InputValidationError(' <{}> is not a valid input for the workflow'.format(key))
        valid = namespace[key].valid_type
        if isinstance(namespace[key], PortNamespace):
            if namespace[key].dynamic:
                # here I should probably consider also the possibility that itself contains other namespaces
                # for now I ignore the possibility
                if isinstance(value, list):
                    # convert elements in list, if it was indeed a list
                    builder[key] = [To_AiiDA_Type(item, valid) for item in iter(value)]
                elif isinstance(value, dict):
                    # it it was not iterable, it was probably a single value
                    builder[key] = {k: To_AiiDA_Type(v, valid) for k, v in value.items()}
                else:
                    raise exceptions.ValidationError('Dynamic namespace {} should be iterable'.format(key))
            else:
                # recursevily look for deeper namespaces
                Process_NameSpaces(builder[key], value)
        else:
            builder[key] = To_AiiDA_Type(value, valid)


def Get_Namespace_Schema(namespace, schema):
    """
    Recursively process the namespace of a workflow in order to extract information about the
    input namespace, their type, if and what is  the defaul values if they're requested, and a help if it is available
    """
    from aiida.engine.processes.ports import PortNamespace

    for key, value in namespace.items():
        if isinstance(value, PortNamespace):
            # recursevily look for deeper namespaces
            schema[key] = {}
            # if dynamic namespace, I just print that is dynamic, and fill it
            # problematic if a dynamic namespace contains other namespaces
            default = None
            if value.has_default():
                default = value.default
            if value.dynamic:
                schema[key] = dict(
                    valid_type=str(value.valid_type),
                    is_required=value.required,
                    has_default=value.has_default(),
                    default=str(default),
                    help_string='Dynamic namespace, can be a list of valid types. ' + value.help,
                )
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
                help_string=value.help,
            )


def To_AiiDA_Type(data, valid):
    """
    Function to take the value of a dictionary, and convert it to the expected type
    for the input namespace. It can be just converting the type, or trying to load a
    node with the required information
    """
    from aiida.orm.nodes.data.base import to_aiida_type
    from aiida import orm

    # Normal data, no conversion required
    if isinstance(data, valid):
        output = data
    # Data should be node type
    # Conversion to data, but check the type to see if we're looking for a node instead
    # Numeric or string could be node IDs, so I skip those checks
    if isinstance(data, dict):
        if 'LOADNODE' in data:
            node = orm.load_node(data['LOADNODE'])
            return node
        if 'CODELABEL' in data:
            node = orm.Code.get_from_string(data['CODELABEL'])
            return node
    if (
        isinstance(orm.Int(), valid) or isinstance(orm.Str(), valid) or
        (isinstance(orm.Float(), valid) and isinstance(data, float)) or
        (isinstance(orm.Bool(), valid) and isinstance(data, bool)) or
        (isinstance(orm.Dict(), valid) and isinstance(data, dict))
    ):
        output = to_aiida_type(data)
    elif isinstance(orm.List(), valid) and isinstance(data, list):
        # Automatic conversion does not work for list types
        # if value is not a list, we're probably trying to load a Node
        output = orm.List(list=data)
    else:
        # now trying to assign data that I expect is going to be a Node...
        node = orm.load_node(data)
        try:
            output = node
        except:
            raise exceptions.InputValidationError(
                'Error, expected {} to be a node instance, but I cannot load <{}> .'.format(data, node)
            )

    return output


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
