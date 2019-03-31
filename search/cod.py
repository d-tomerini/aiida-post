# -*- coding: utf-8 -*-

from aiida.tools.dbimporters.plugins.cod import CodDbImporter

def cod_check(cod_dict):
    """
    basic checks to ensure the consistency of the input
    returns a correct key:value to pass to the database search
    """
    importer = CodDbImporter()
    supported = importer.get_supported_keywords()
    # return supported keywords and unsupported keywords for the search
    # defaultdict append method create lists for duplicated k:v
    # keeps only one value if key is duplicated
    cod_rec = {}
    cod_unrec = {}
    for k, v in cod_dict.items():
        if k in supported:
            cod_rec.update({k:v})
        else:
            cod_unrec.update({k:v})
    return cod_rec, cod_unrec

def cod_search(cod_values):
    """ 
    performs a search of any CIF structure that is provided
    according to the data coming from the input JSON request
    returns a list of structures and an error code if there is 
    something wrong with things
    """
    
    importer = CodDbImporter()
    found = importer.query(**cod_values)
    return found # returned database object



