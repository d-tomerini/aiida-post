# -*- coding: utf-8 -*-
"""
Calcfunction to handle provenance of the request
takes the json input from the request
and turns it into a Dict
It process the input processing before further calculations
"""

from aiida.orm import StructureData, Dict, Str, Int
from aiida.engine import run, Process, WorkChain, ToContext, if_


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
        spec.output('html_code', valid_type=Int)
        spec.output('message', valid_type=Str)
        spec.outline(
            cls.check_dictionary,
            if_(cls.No_HTML_Error)(
                cls.find_structure,
            ),
            cls.run_results
        )

    def _init_inputs(self):
        """ Initialization of internal variables"""
        self.ctx.html_code = 200 # everything is ok
        self.ctx.html_message = ''

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

        a = self.inputs.property.value
        calcs = self.inputs.predefined.attributes['calculation']

        if a not in calcs:
            self.ctx.html_code = 400 # bad request
            self.ctx.html_message = 'Property type {} not supported. Recognized keywords: {}'.format(
                a,", ".join(calcs)
            )
            self.report(self.ctx.html_message)


    def run_results(self):
        """
        Final processing of the outputs
        """
        if not self.No_HTML_Error:
            self.report('Something went wrong in the retrival {}'.format(self.ctx.html_code))
        finalcode = Int(self.ctx.html_code)
        finalmessage = Str(self.ctx.html_message)
        finalcode.store()
        finalmessage.store()
        self.out('html_code', finalcode)
        self.out('message', finalmessage)
        
    def No_HTML_Error(self):
        """
        True if the HTML code is not an error status code
        """
        no_error_codes = (200, 201, 202, 203, 204)
        return self.ctx.html_code in no_error_codes

    def find_structure(self):
        """
        Expose the dictionary part about the query
        Try to get the structure according to the required method
        """
        if 'structure' not in self.inputs.request.attributes_keys():
            self.ctx.html_code = 400 # bad request
            self.ctx.html_message = 'No "structure" tag in json'
            self.report(self.ctx.html_message)