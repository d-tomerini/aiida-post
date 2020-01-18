# -*- coding: utf-8 -*-
"""
Workflow to import a number of structures in the database from the COD database
"""
from __future__ import absolute_import
from aiida.engine import WorkChain, if_
from aiida import orm


class CODImportWorkChain(WorkChain):
    """
    Workfunction to query the COD database
    Check for data according to a dictionary query, Import nodes, Clean them, Import them as needed
    """

    @classmethod
    def define(cls, spec):
        super().define(spec)
        spec.input(
            'codquery', valid_type=orm.Dict, required=True, help='A list of option to the query to the COD database'
        )
        spec.input(
            'strictcheck',
            valid_type=orm.Bool,
            default=orm.Bool(False),
            help='Whether we should strictly check COD_query keywords'
        )
        spec.output(
            'output',
            valid_type=orm.Dict,
            help='Dictionary containing a list of aiida structure and a list of COD ids that did not work'
        )
        spec.outline(
            cls.validate_COD_query,
            if_(cls.should_check_query)(cls.check_keywords), cls.find_structures_and_return
        )

        spec.exit_code(201, 'WRONG_COD_QUERY', message='The query contains invalid keywords')
        spec.exit_code(
            202, 'INVALID_COD_QUERY', message='After parsing for valid keywords, the query contains no valid keywords'
        )
        spec.exit_code(210, 'ERROR_NO_STRUCTURE', message='The query was unable to return a structure')

    def validate_COD_query(self):
        """
        Analyze the query dictionary for valid keywords
        """
        from aiida_post.calculations.COD import cod_check

        self.ctx.kwords = cod_check(self.inputs.codquery)
        self.ctx.valid_COD_keys = self.ctx.kwords.dict.valid
        self.ctx.invalid_COD_keys = self.ctx.kwords.dict.invalid

    def should_check_query(self):
        """
        If I should check the query in some way
        """
        return self.inputs.strictcheck

    def check_keywords(self):
        """
        check if there are invalid keywords, and if there are any valid keywords
        """
        if self.ctx.invalid_COD_keys != {}:
            self.report('The query contains invalid keys: {}'.format(self.ctx.invalid_COD_keys))
            return self.exit_codes.WRONG_COD_QUERY
        if self.ctx.valid_COD_keys == {}:
            self.report(
                'The query contains no valid value. Warning: this would trigger the download of the whole COD database'
            )
            self.report('set strictcheck to `True` if this is the desired outcome')
            return self.exit_codes.INVALID_COD_QUERY

    def find_structures_and_return(self):
        """
        Retrieval of the structure from the COD database
        """
        from aiida_post.calculations.COD import cod_find_and_store

        # query the database for structures
        structurelist = cod_find_and_store(self.ctx.kwords)
        converted = structurelist.attributes['aiida_structures']
        failed = structurelist.attributes['excepted_cifs']
        self.report('{} cif files could not be converted to AiiDA objects'.format(len(failed)))
        n_structures = len(converted)
        if n_structures == 0:
            self.report('No structure retrieved')
            return self.exit_codes.ERROR_NO_STRUCTURE
        if n_structures == 1:
            self.report('One structure satisfies the query')
        else:
            self.report('{} structures satisfies the query'.format(n_structures))

        self.out('output', structurelist)
