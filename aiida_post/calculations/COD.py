"""
Set of utility functions to deal with the COD database queries
"""

from __future__ import absolute_import
from aiida.engine import calcfunction


@calcfunction
def cod_check(cod_dict):
    """
    Tries to infere which of the search keywords
    are actually valid
    :cod_dict input dictionary
    :output cod_rec valid keywords
    :output cod_unrec not valid keywords
    """
    from aiida.orm import Dict
    from aiida.tools.dbimporters.plugins.cod import CodDbImporter

    importer = CodDbImporter()
    supported = importer.get_supported_keywords()
    # return supported keywords and unsupported keywords for the search
    # defaultdict append method create lists for duplicated k:v
    # keeps only one value if key is duplicated
    cod_recognized = {}
    cod_unrecognized = {}
    for key, value in cod_dict.get_dict().items():
        if key in supported:
            cod_recognized.update({key: value})
        else:
            cod_unrecognized.update({key: value})
    return Dict(dict={'valid': cod_recognized, 'invalid': cod_unrecognized})


@calcfunction
def cod_find_and_store(query):
    """
    performs a search of any CIF structure that is provided
    according to the data coming from the input JSON request
    returns a dictionary of the of DataStructure UUID
    """
    from aiida.orm import List, Dict
    from aiida.tools.dbimporters.plugins.cod import CodDbImporter

    kwargs = query.dict.valid
    importer = CodDbImporter()
    allcifs = importer.query(**kwargs).fetch_all()
    allstructures = []
    wrongcifs = {}
    for structure in allcifs:
        cod_id = structure.source['id']
        try:
            node = structure.get_aiida_structure()
            node.source = structure.source
            node.store()
            allstructures.append(node.uuid)
        except Exception as e:
            wrongcifs[str(cod_id)] = 'returned exception: {}'.format(e)
    return Dict(dict=dict(aiida_structures=allstructures, excepted_cifs=wrongcifs))
