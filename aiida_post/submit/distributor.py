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

from pkg_resources import get_entry_map, load_entry_point

from aiida.orm import load_node
from aiida.plugins import WorkflowFactory
from aiida.plugins.entry_point import get_entry_point_names

from aiida.common.exceptions import MissingEntryPointError, MultipleEntryPointError, LoadingEntryPointError

from aiida_post.common.threaded import submit_job




def Distribute(req, prop):
    """
    After the retrieval of the structure, we proceed with the distribution of the task
    according to the requested data.
    : input req: a Dict node that contains info about the incoming request and the POST file
    : return response: a dictionary with the workflow info, error message and additional info
    """
    
    # prepare to return data containing eventual error messages and workchain properties
    response = {}
    error_message = None
    workflow = None
    # initial checks
    
    # check entry point
    available_properties = pkg_resources.get_entry_map('aiida_post', 'property_mapping')
    if prop not in available_properties:
        error_message = '<{}> is not in the list of available properties.'.format(prop)
        error_info = available_properties
    else:
        try:
            entry = load_entry_point('aiida_post', 'aiida_post.workflows', prop)
        except ImportError:
            error_message = 'Could not load entry point for property <{}>.'.format(prop)

        try:
            workflow =  WorkflowFactory(entry)
        except MissingEntryPointError:
            error_message = 'Entry point <{}> not found in aiida.workflows.'.format(prop)
        except MultipleEntryPointError:
            error_message = 'Multiple entry points for <{}> found in aiida.workflows.'.format(prop)
        except Exception as inst:
            error_message = inst
        
        calcspecs = req.inputs.predefined.dict.AVAILABLE_CODES
        structure = req.outputs.structure
        if prop == 'band_gap':
            # submit a bandgap workchain
            workflow = WorkflowFactory('post.BandGap')
            pwcode = calcspecs['qe']
            submit_kwargs = {
                'code': load_node(pwcode),
                'structure': structure
            }
    
        if prop == 'band_structure':
            workflow = WorkflowFactory('quantumespresso.pw.band_structure')
            pwcode = calcspecs['qe']
            submit_kwargs = {
                'code': load_node(pwcode),
                'structure': structure
            }
    
        if prop == 'structure.cod':
            workflow = WorkflowFactory('post.ProcessInputs')
            submit_kwargs = {
                    'incoming_request':hp,
                    'predefined':Dict(dict=self.extended),
                    'property_to_calculate': Str(prop)
                    }
            y = submit_job(workflow, **submit_kwargs)
        
        
    print()
    print('calcspecs', calcspecs, 'structure.pk', structure.pk)

    y = submit_job(workflow, **submit_kwargs)
    wf = y.result()

    return response

def Process_NameSpaces(namespace, req, error=None):
    from aiida.orm import load_node, Node, ArrayData, BandsData, Bool, Code, Dict, Float, FolderData, KpointsData
    from aiida.orm import XyData, TrajectoryData, SinglefileData, RemoteData, OrbitalData, List
    from  aiida.engine.processes.ports import PortNamespace
    """
    Process the request in order to create a dictionary of the right type of Nodes for the input of a workchain.
    :input namespace: created namespace for the worklow
    :input req: a dictionary for the workchain inputs. 
    :returns out: a dictionary with the AiiDA objects to run the calculation
    the value of a key is expected to contain a value to fill the AiiDA data type; 
    if instead it has to load an `aiida.orm.Node` from the database, it NEEDS to be a dictionary with one key with the 
    value 'NODE'.
    The subroutine runs recursively (for nested namespaces) in order to create the correct input
    """

    output = {}
    # If we decide Codes can be default, I need this check
    if 'Code' 
    for key, value in req.items():
        if key not in namespace:
            error = ' <{}> is not a valid input for the workflow'
            return None, error
        #check if it is a dictionary, and I should load the node
        valid = namespace.valid_type
        if isinstance(value, dict):
            if 'NODE' in value:
                try:
                    node = load_node(value('NODE'))
                except:
                    error = 'Problems loading node <{}> from the database'.format(value('NODE'))
                    return None, error
                if isinstance(node, valid):
                    output[key] = node
                else:
                    error = '<{}> is not a valid class for <{}>. Expected: {}.format(
                        node.__class,
                        key,
                        valid
                    )
                    return None, error
            else:
                if isinstance(namespace[key], PortNamespace):
                    # recursevily look for deeper namespaces
                    output[key], error = Process_NameSpaces(
                        namespace[key],
                        req[key],
                        error
                    )
                else:
                    # finally, process the individual values
                    # maybe we can do better?
                    if isinstance(Int, valid):
                        try:
                            output[key] = Int(int(value))
                        except:
                            error = 'Error while assigning integer <{}> to Int class.'.format(value)
                    elif isinstance(Float, valid):
                       try:
                            output[key] = Float(float(value))
                        except:
                            error = 'Error while assigning float <{}> to Float class.'.format(value)
                    elif isinstance(Bool, valid):
                       try:
                            output[key] = Bool(bool(value))
                        except:
                            error = 'Error while assigning boolean <{}> to Bool class.'.format(value)
                    elif isinstance(Dict, valid):
                       try:
                            output[key] = Dict(dict=bool(value))
                        except:
                            error = 'Error while assigning dict <{}> to Dict class.'.format(value)
                    elif isinstance(List, valid):
                       try:
                            output[key] = List(value)
                        except:
                            error = 'Error while assigning list <{}> to List class.'.format(value)
                    else:
                        # now trying to assign data that is going to be a Node...
                        othertypes = [
                            ArrayData,
                            BandsData,
                            Code,
                            FolderData,
                            KpointsData,
                            XyData,
                            TrajectoryData,
                            SinglefileData,
                            RemoteData,
                            OrbitalData
                        ]
                        for othertype in othertypes:
                            if isinstance(othertype, valid):
                                try:
                                    output[key] = load_node(value)
                                except:
                                    error = 'Error while loading datatype {} from node <{}>. '.format(
                                        othertype,
                                        value
                                    )
        if not error:
            # something bad happened during these assignments; go back one step at the time
            return None, error
    return output, error


def Recursively_Assign_Code(namespace, code, error=None):
    """
    Needed to pass the standard code down the workchain to where it is needed
    For the moment, we are going to assume that the code stays uniformly the same
    throught the workchain; if this is not the case, it is probably better to 
    implement some kind of validation dictionary for each of the workchains that we support
    """
    copy the code above
    recursively assign every instance of ``code`` to the standard one
