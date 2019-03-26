# -*- coding: utf-8 -*-
# module to handle the input to the app
from flask import jsonify
class BackToGinestra():
    """
    Handles the data back to the Ginestra call.
    Reports back HTML response codes
    Data in dictionary form
    """
    def __init__(self):
        self.status_code = 200 # success code   
        self.message = None # message back to Ginestra
        self.input = None # input json
        self.allowed = None # allowed dictionary data, from settings.json
        self.instructure = {} # incoming structural request
        self.structure = None # dictionary structural output information
        self.back_to_server = {'data': {},
                               'calculation_status': None
                              } 
    def Set_Warning(self,message,code):
        """
        define a message and a code to return to the server
        :message string
        :code integer
        """
        self.message = message
        self.status_code = code      
    def Add_Allowed(self,calculations):
        self.allowed = calculations
    def Check_Method(self,req):
        """
        Initial data checks on parameters passed from Ginestra
        Data, in POST format, is a JSON
        :req incoming flask request
        """
        # format checks
        if (req.method != 'POST'):
            self.Set_Warning('Expecting a POST HTML method',405) # method not allowed
        # accepting only JSON
        if ( req.is_json):
            self.input = req.get_json()
        else:
            self.Set_Warning('Expecting json',400) # bad request
    def Check_Calculation(self):
        """
        Calculation checks.
        calculation tag needs to be there, and needs to be of the accepted type
        """
        if self.input.get("calculation") == None:
            self.Set_Warning('No "calculation" tag in json',400) # bad request
        else:
        # needs to be in the allowed calculations
            if (not self.input['calculation'] in (self.allowed['calculation'])):
                self.Set_Warning(
                    'Calculation type {} not supported. Accepted types: {}'.format(
                        self.input['calculation'],
                        ", ".join(self.allowed['calculation'])
                    ), 400) # bad request
    def Check_Structure(self):
        if self.status_code == 200:
            if self.input.get('structure') == None:
                self.Set_Warning('No "structure" tag in json',400) # bad request
            else:
                self.instructure = self.input['structure']
    def Data_Add(self,**kwargs):
        """
        Updates the data definition in the response
        Entries will be added to the dictionaries
        """
        if self.back_to_server['data'] == None:
            self.back_to_server['data'] = {}
        for key, value in kwargs.items():
            self.back_to_server['data'].update({key:value})
    def Structure_Add(self,**kwargs):
        """
        Updates the data definition in the response
        Entries will be added to the dictionaries
        """
        if self.structure == None:
            self.structure = {}
        for key, value in kwargs.items():
            self.structure.update({key:value})                     
    def Back(self):
        self.back_to_server.update(
            {
                'input':self.input,        
                'structure':self.structure,
                'message':self.message,
            #    'recognised_keywords':self.allowed
            }
        )
        return self.back_to_server
    def NoError(self):
        """
        True if the HTML code is not an error status code
        """
        no_error_codes = (200,201,202,203,204)
        return self.status_code in no_error_codes
