# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from aiida.orm import Dict
from aiida.engine import calcfunction


@calcfunction
def importJSON(req):
    """
    Calcfunction to process the received Flask request
    and convert it to AiiDA objects that can be used
    in the actual calculation/workflow loaded by the
    endpoint requested
    :param req : HttpRequest, a Dict
    """

    #myjson = check_dictionary(req.attributes['json'])
    print('ownownow')
    return Dict(dict=myjson)


def check_dictionary(dic):
    """
    Basic checks on the incoming request json
    'property' needs to be in the predefined workchain
    'structure' needs to be findable
    """

    # might be good to provide a schema, to look for required keywords
    # actually before and not adding exception one after the other

    # here it makes sense to expose a number of entry points
    print(('caocao', dic))
    return dic


def return_results(self):
    """
        Final processing of the outputs
        """

    self.out('structure', self.ctx.cif)


def check_structure_input(self):
    """
        Analyze the dictionary part about the query
        Try to get the structure according to the required method
        Proceed to the actual structure search
        """
    if 'structure' not in self.inputs.request.attributes_keys():
        self.report('No "structure" tag in json')
        return self.exit_codes.ERROR_MISSING_KEY
    if 'location' not in self.inputs.request.dict.structure:
        self.report('No "location" tag in json. ' 'I do not know where to search for the structure required')
        return self.exit_codes.ERROR_MISSING_KEY

    # assuming database search
    # duplicate code from above
    db = self.inputs.request.dict.structure['database']
    if 'query' not in self.inputs.request.dict.structure:
        self.report('No "query" tag in json')
        return self.exit_codes.ERROR_MISSING_KEY

    # here is another point where entry points
    # would make my life easier on definitions
    # loading calcfunction to look for structures
    # according to database

    if db in self.inputs.predefined.dict.supported_database:
        # cycle over the supported databases
        if db == 'COD':
            self.ctx.db = self.inputs.request.dict.structure['query']
            self._COD_search()
    else:
        self.report('Unrecognised database')
        return self.exit_codes.ERROR_WRONG_VALUE
