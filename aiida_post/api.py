# -*- coding: utf-8 -*-
"""
This class deals with the extension of the AiiDA REST api (v.4)
and defines the additional endpoints
"""

from __future__ import absolute_import
from aiida.restapi.api import AiidaApi
from aiida_post.resources import GSubmit, GExisting, GStatus, GDuplicates, GProperties, GWorkflows


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

        self.add_resource(
            GSubmit,
            # assume it is a property
            '/ginestra/submit/',
            # unless specified
            '/ginestra/submit/property',
            '/ginestra/submit/workflow',
            strict_slashes=False,
            resource_class_kwargs=kwargs
        )
        self.add_resource(existing, '/ginestra/existing', strict_slashes=False, resource_class_kwargs=kwargs)
        self.add_resource(
            GDuplicates,
            '/ginestra/duplicates/<string:prop>/check/',
            strict_slashes=False,
            resource_class_kwargs=kwargs
        )
        self.add_resource(
            GStatus, '/ginestra/status/<string:node_id>', strict_slashes=False, resource_class_kwargs=kwargs
        )
        self.add_resource(
            GProperties,
            '/ginestra/properties/',
            '/ginestra/properties/<string:node_id>/',
            '/ginestra/properties/<string:nodeS_id>/inputs/',
            '/ginestra/properties/<string:node_id>/outputs/',
            '/ginestra/properties/<string:node_id>/outline/',
            strict_slashes=False,
            resource_class_kwargs=kwargs
        )
        self.add_resource(
            GWorkflows,
            '/ginestra/workflows/',
            '/ginestra/workflows/<string:entrypoint>/inputs/',
            '/ginestra/workflows/<string:entrypoint>/outputs/',
            '/ginestra/workflows/<string:entrypoint>/outline/',
            strict_slashes=False,
            resource_class_kwargs=kwargs
        )
