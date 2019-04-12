# -*- coding: utf-8 -*-
from aiida.orm.utils import load_node
import ext_workfunctions

def Distribute(response, prop):
    """
    Once a structure is available for calculation,
    this function distributes it to the
    right workfunction to obtain the data,
    returned as a dictionary of expected values
    """

    if prop == 'band_gap':
        # submit a bandgap workchain
        structure = load_node(response.id)
        code = load_node(response.allowed['qe'])
        upf = load_node(response.allowed['upf'])
        ext_workfunctions.bandgap(
            structure,  # aiida pk
            code,  # code pk
            upf # upf pk
        )
