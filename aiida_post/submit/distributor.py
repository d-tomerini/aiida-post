# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from aiida.orm import load_node
from aiida.engine import submit, run
from aiida.plugins import WorkflowFactory
from aiida_post.common.threaded import submit_job


def Distribute(req, prop):
    """
    After the retrieval of the structure,
    we proceed with the distribution of the task
    according to the requested data
    : input req workfunction node
    : prop property to calculate
    """

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

        # upfamily = calcspecs['upf']
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
    calcnode = y.result_queue.get()  # aiida pk  # code pk
    return calcnode
