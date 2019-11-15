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
    """

    # initial checks
    # check entry point
    error_message = None
    try:
        workflow =  WorkflowFactory(prop)
    except MissingEntryPointError:
        error_message = 'Entry point <{}> not found in aiida.workflows'.format(prop)
    except MultipleEntryPointError:
        error_message = 'Multiple entry points for <{}> found in aiida.workflows'.format(prop)
    except LoadingEntryPointError:
        error_message = 'Unknown error while loading entry point <{}> for aiida.workflows'.format(prop)
    
    calcspecs = req.inputs.predefined.dict.AVAILABLE_CODES
    structure = req.outputs.structure
    if prop == 'band_gap':
        # submit a bandgap workchain
        workflow = WorkflowFactory('post.BandGap')
        pwcode = calcspecs['qe']
        params = {
            'code': load_node(pwcode),
            'structure': structure
        }

    if prop == 'band_structure':
        workflow = WorkflowFactory('quantumespresso.pw.band_structure')
        pwcode = calcspecs['qe']
        params = {
            'code': load_node(pwcode),
            'structure': structure
        }

    print()
    print('calcspecs', calcspecs, 'structure.pk', structure.pk)

    y = submit_job(workflow, **params)
    print(y)

    return y.result_queue.get() 
