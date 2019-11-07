# -*- coding: utf-8 -*-

from __future__ import absolute_import

from aiida.restapi.api import AiidaApi
from aiida_post.resources import submit, existing, input


class InterfaceApi(AiidaApi):
    """
    This class hanldes the extension of the
    AiidaApi class, in order to deal with nore endpoints
    """

    def __init__(self, app=None, **kwargs):
        """
        This init serves to add new endpoints to the basic AiiDA Api
        """

        super(InterfaceApi, self).__init__(app=app, prefix=kwargs['PREFIX'], catch_all_404s=True, **kwargs)

        # all AiiDA's endpoint, plus the following

        self.add_resource(
            submit,
            '/ginestra/<string:prop>/submit/',
            strict_slashes=False,
            resource_class_kwargs=kwargs
        )
        self.add_resource(
            existing,
            '/ginestra/<string:prop>/existing',
            strict_slashes=False,
            resource_class_kwargs=kwargs
        )
        self.add_resource(
            input, 
            '/ginestra/<string:prop>/check/', 
            strict_slashes=False, 
            resource_class_kwargs=kwargs
        )
