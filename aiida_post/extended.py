# -*- coding: utf-8 -*-
"""
Daniele Tomerini
Initial code march 2019

Initial proposal for an interface between Ext and Aiida
FLASK python app.
Based on JSON interchange between a server accepting requests
and returning values and updates on the calculation
Endpoints  changes on property, with GET and POST requests
handling various tasks

Keywords for now are stored within a settings.json file.
Basic checks to help ensure consistency
"""
# general imports
import json

from aiida.restapi.api import AiidaApi, App
from aiida.restapi.run_api import run_api
from aiida.cmdline.utils import decorators

class NewApi(AiidaApi):

    from aiida_post.resources import NewResource, app_submit, app_check_existing, app_input
    def __init__(self, app=None, **kwargs):
        """
        This init serves to add new endpoints to the basic AiiDA Api

        """
        super(NewApi, self).__init__(app=app, **kwargs)

        self.add_resource(
                NewResource, 
                '/new-endpoint/', 
                strict_slashes=False)
        self.add_resource(
                app_submit, 
                '/ext/calculation/<string:prop>/submit/',
                strict_slashes=False)
        self.add_resource(
                app_check_existing, 
                '/ext/calculation/<string:prop>/existing',
                strict_slashes=False)
        self.add_resource(app_input, 
                '/ext/calculation/<string:prop>/check/',
