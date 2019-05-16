# -*- coding: utf-8 -*-
"""
Calcfunction to handle provenance of the request
takes the json input from the request
and turns it into a Dict
It process the input processing before further calculations
"""

from aiida.orm import StructureData, Dict, Str, Int, List
from aiida.engine import run, Process, WorkChain, ToContext

class ProcessInputs(WorkChain):
    """
    Workfunction to keep provenance of the request
    Handles the data back to the Ext call.
    Reports back HTML response codes
    Data in dictionary form
    :param req POST json
    :param property string, requested property from endpoint
    :param predefined dictionary of set values

    :return html_code for errors
    :return message for details
    :return structure is always needed to calculate properties
    :return clean_req dictionary of parsed request (looking for errors)
    """

    @classmethod
    def define(cls, spec):
        super(ProcessInputs, cls).define(spec)
        spec.input('request', valid_type=Dict)
        spec.input('predefined', valid_type=Dict)
        spec.input('property', valid_type=Str)
        #spec.output('html_code', valid_type=Int)
        #spec.output('message', valid_type=Str)
        spec.output('structure', valid_type=StructureData)
        spec.outline(
            cls.check_dictionary,
            cls.check_structure_input,
            cls.find_structure,
            cls.return_results,
        )
        spec.exit_code(
            400,
            'ERROR_NO_PROPERTY', 
            'No workflow defined for this property')
        spec.exit_code(
            401,
            'ERROR_MISSING_KEY', 
            'The key was required, and is not in the dictionary')
        spec.exit_code(
            402,
            'ERROR_WRONG_VALUE',
            'The value for the key is not one of the accepted options')
        spec.exit_code(
            403,
            'ERROR_NO_STRUCTURE',
            'It was impossible to obtain a StructureData file')
    
    
    def _init_inputs(self):
        """ Initialization of internal variables"""
        pass
    
    
    def check_dictionary(self):
        """
        Basic checks on the incoming request json
        'property' needs to be in the predefined workchain
        'structure' needs to be findable
        """
        self._init_inputs()
     
    
        # might be good to provide a schema, to look for required keywords 
        # actually before and not adding exception one after the other
    
        # here it makes sense to expose a number of entry points
        # so that every time I introduce a new workflow, I can automatically include it here
    
        v = self.inputs.property.value
        calcs = self.inputs.predefined.dict.calculation
        if v not in calcs:
            self.report(
                'WARNING. Property type {} not supported. '
                'Recognized keywords: {}'.format(v, ", ".join(calcs))
            )
            return self.exit_codes.ERROR_NO_PROPERTY
    
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
            self.report('No "location" tag in json. '
                'I do not know where to search for the structure required')
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
        
    
    def _COD_search(self):
        from .search.cod import cod_check
        from aiida.tools.dbimporters.plugins.cod import CodDbImporter
        """
        Deals with the retrieval of a structure
        from the COD database, according to the request dictionary
        Returns a database search object (array of arrays of structures)
        """
    
        kwords = cod_check(Dict(dict=self.ctx.db))
        self.ctx.db_valid = kwords.dict.valid
        self.ctx.db_invalid = kwords.dict.invalid
        
        # empty dictionary
        if not bool(self.ctx.db_valid):
            self.report('No valid keywords in search tag in json')
            return self.exit_codes.ERROR_MISSING_KEY
        # query the database for structures
        importer = CodDbImporter()
        self.ctx.allcifs = importer.query(**self.ctx.db_valid)
        self.ctx.n_structures = len(self.ctx.allcifs)
        if self.ctx.n_structures == 0:
            self.report('No structure retrived')
            return self.exit_codes.ERROR_NO_STRUCTURE
        else:
            s = self.ctx.allcifs[0].get_aiida_structure()
            s.store()
            self.ctx.cif = s
            if self.ctx.n_structures >= 2:
                self.report('{} structure satisfy the request'.format(self.ctx.n_structures))
                
    
    def find_structure(self):
        pass
    
