# -*- coding: utf-8 -*-
"""
Parsing the information from the json file
and return a Dict with processed data

Info about node numbers are converted into
nodes, so that they can be processed more easily later
"""

from __future__ import absolute_import
from aiida.orm import StructureData, Dict, Str, Int, List
from aiida.parsers import Parser


class ProcessJSON(Parser):
    """
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

    def parse(self, **kwargs):
        """
        Receive the json request
        Store the request
        Return a Dict of data
        """

        pass
