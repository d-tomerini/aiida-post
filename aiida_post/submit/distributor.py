# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from aiida.orm import load_node
from aiida.engine import submit
from aiida.plugins import WorkflowFactory


def Distribute(req, prop):
    """
    After the retrieval of the structure,
    we proceed with the distribution of the task
    according to the requested data
    : input req workfunction node
    : prop property to calculate
    """

    if prop == 'band_gap':
        # submit a bandgap workchain
        xx = WorkflowFactory('ext_aiida.BandGap')
        calcspecs = req.inputs.predefined['aiida']
        structure = req.outputs.structure
        pwcode = calcspecs['qe']
        code = load_node(pwcode)
        upfamily = calcspecs['upf']
        wf = submit(xx, structure=structure, code=code)  # aiida pk  # code pk
    if prop == 'band_structure':
        xx = WorkflowFactory('quantumespresso.pw.band_structure')
        calcspecs = req.inputs.predefined['aiida']
        structure = req.outputs.structure
        pwcode = calcspecs['qe']
        code = load_node(pwcode)
        print(('picc {}'.format(code)))
        # upfamily = calcspecs['upf']
        wf = submit(xx, structure=structure, code=code)  # aiida pk  # code pk

    return wf
