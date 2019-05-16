# -*- coding: utf-8 -*-
from aiida.engine import launch
from workfunctions.bandgap import PwBandGapWorkChain

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

        calcspecs = req.inputs.predefined['aiida']
        structure = req.outputs.structurenode
        codenode = calcspecs['qe']
        upfamily = calcspecs['upf']
        wf = launch.submit(
            PwBandGapWorkChain,
            structure=structure,  # aiida pk
            code=load_node(codenode),  # code pk
        )
        return wf

