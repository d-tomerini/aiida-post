# -*- coding: utf-8 -*-
from aiida.orm import load_node
from aiida.engine import launch
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
        wf = launch.submit(
            xx,
            structure=structure,  # aiida pk
            code=code,  # code pk
        )
    if prop == 'band_structure':
        # submit a bandgap workchain
        xx = WorkflowFactory('quantumespresso.pw.band_structure')
        calcspecs = req.inputs.predefined['aiida']
        structure = req.outputs.structure
        pwcode = calcspecs['qe']
        code = load_node(pwcode)
        # upfamily = calcspecs['upf']
        wf = launch.submit(
            xx,
            structure=structure,  # aiida pk
            code=code,  # code pk
        )
    
    return wf
