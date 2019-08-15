# -*- coding: utf-8 -*-

from __future__ import absolute_import
from aiida.tools.dbimporters.plugins.cod import CodDbImporter
from aiida.engine import calcfunction
from aiida.orm import Dict, List
import six


@calcfunction
def cod_check(cod_dict):
    """
    Tries to infere which of the search keywords
    are actually valid
    :cod_dict input dictionary
    :output cod_rec valid keywords
    :output cod_unrec not valid keywords
    """
    importer = CodDbImporter()
    supported = importer.get_supported_keywords()
    # return supported keywords and unsupported keywords for the search
    # defaultdict append method create lists for duplicated k:v
    # keeps only one value if key is duplicated
    cod_rec = {}
    cod_unrec = {}
    for k, v in six.iteritems(cod_dict.get_dict()):
        if k in supported:
            cod_rec.update({k: v})
        else:
            cod_unrec.update({k: v})
    return Dict(dict={'valid': cod_rec, 'invalid': cod_unrec})


@calcfunction
def cod_query(cod_values):
    """
    performs a search of any CIF structure that is provided
    according to the data coming from the input JSON request
    returns a list of structures and an error code if there is
    something wrong with things
    """
    qlist = cod_values.get_dict()
    importer = CodDbImporter()
    found = importer.query(**qlist)
    found_list = found.fetch_all()
    x = [i.source['id'] for i in found_list]
    # returned list of retrieved structures

    return List(list=x)
