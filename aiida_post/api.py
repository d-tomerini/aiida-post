# -*- coding: utf-8 -*-
"""
This class deals with the extension of the AiiDA REST api (v.4)
and defines the additional endpoints
"""
from __future__ import absolute_import

from aiida.restapi.api import AiidaApi
from aiida_post.resources import submit, existing, status, duplicates, properties


class InterfaceApi(AiidaApi):
    """
    Extension of the AiiDaApi, that is an extension of the Flask API
    """

    def __init__(self, app=None, **kwargs):
        """
        This init serves to add new endpoints to the basic AiiDA Api
        """

        super(InterfaceApi, self).__init__(app=app, prefix=kwargs['PREFIX'], catch_all_404s=True, **kwargs)

        # all AiiDA's endpoint, plus the following

        self.add_resource(submit, '/ginestra/submit/', strict_slashes=False, resource_class_kwargs=kwargs)
        self.add_resource(existing, '/ginestra/existing', strict_slashes=False, resource_class_kwargs=kwargs)
        self.add_resource(
            duplicates, '/ginestra/<string:prop>/check/', strict_slashes=False, resource_class_kwargs=kwargs
        )

        self.add_resource(
            status,
            '/ginestra/<string:id>/status/',
            '/ginestra/status/',
            strict_slashes=False,
            resource_class_kwargs=kwargs
        )

        self.add_resource(properties, '/ginestra/properties/', strict_slashes=False, resource_class_kwargs=kwargs)
