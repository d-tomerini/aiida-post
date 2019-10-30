# -*- coding: utf-8 -*-
"""
Daniele Tomerini
Initial code march 2019

Initialize the class inherited by AiidaApi, to include new endpoints
Add the endpoint definded into the resources
"""

from aiida.restapi.api import AiidaApi
from aiida_post.resources import NewResource,app_submit,app_check_existing,app_input

class InterfaceApi(AiidaApi):
    def __init__(self, app=None, **kwargs):
        """
        This init serves to add new endpoints to the basic AiiDA Api
        """
        
        super(InterfaceApi, self).__init__(app=app, **kwargs)

        self.add_resource(NewResource, '/new-endpoint/', strict_slashes=False)
        self.add_resource(app_submit, '/ext/calculation/<string:prop>/submit/')
        self.add_resource(app_check_existing, '/ext/calculation/<string:prop>/existing')
        self.add_resource(app_input, '/ext/calculation/<string:prop>/check/')

