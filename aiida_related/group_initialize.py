# -*- coding: utf-8 -*-
"""
general functions and classes dealing with aiida
communication with the interface
"""

from aiida.orm.querybuilder import QueryBuilder
from aiida.orm import Group

def Create_group(groupname,**kwargs):
    """
    Check if a group exist in the database
    If it does not, it creates it
    This group will be used to select the nodes
    according to nodes that are marked relevant
    """
    g, was_created = Group.objects.get_or_create(label=groupname, **kwargs)
    print('group {} was created: {}'.format(groupname, was_created))

    return g

