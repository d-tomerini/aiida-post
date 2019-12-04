# -*- coding: utf-8 -*-
"""
This class deals with the extension of the AiiDA REST api (v.4)
and defines the additional endpoints
"""

from __future__ import absolute_import
from aiida.restapi.api import AiidaApi
from aiida_post.resources import GSubmit, GExisting, GStatus, \
     GDuplicates, GProperties, GWorkflows, GData


class InterfaceApi(AiidaApi):
    """
    Extension of the AiiDaApi, that is an extension of the Flask API
    """

    def __init__(self, app=None, **kwargs):
        """
        This init serves to add new endpoints to the basic AiiDA Api
        """

        super().__init__(app=app, prefix=kwargs['PREFIX'], catch_all_404s=True, **kwargs)

        # all AiiDA's endpoint, plus the following

        self.add_resource(
            GSubmit,
            # assume it is a property
            '/intersect/submit/',
            # unless specified
            '/intersect/submit/property',
            '/intersect/submit/workflow',
            strict_slashes=False,
            resource_class_kwargs=kwargs
        )

        self.add_resource(GExisting, '/intersect/existing', strict_slashes=False, resource_class_kwargs=kwargs)

        self.add_resource(
            GDuplicates,
            '/intersect/duplicates/<string:prop>/check/',
            strict_slashes=False,
            resource_class_kwargs=kwargs
        )

        self.add_resource(
            GStatus, '/intersect/status/<string:node_id>', strict_slashes=False, resource_class_kwargs=kwargs
        )

        self.add_resource(
            GProperties,
            '/intersect/properties/',
            '/intersect/properties/<string:node_id>/',
            '/intersect/properties/<string:node_id>/inputs/',
            '/intersect/properties/<string:node_id>/outputs/',
            '/intersect/properties/<string:node_id>/outline/',
            strict_slashes=False,
            resource_class_kwargs=kwargs
        )

        self.add_resource(
            GWorkflows,
            '/intersect/workflows/',
            '/intersect/workflows/<string:entrypoint>/inputs/',
            '/intersect/workflows/<string:entrypoint>/outputs/',
            '/intersect/workflows/<string:entrypoint>/outline/',
            strict_slashes=False,
            resource_class_kwargs=kwargs
        )

        self.add_resource(
            GData, '/intersect/derived_data/structuredata', strict_slashes=False, resource_class_kwargs=kwargs
        )
