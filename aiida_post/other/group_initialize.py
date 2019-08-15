# -*- coding: utf-8 -*-
"""
general functions and classes dealing with aiida
communication with the interface
"""

from __future__ import absolute_import
from __future__ import print_function
from aiida.orm.querybuilder import QueryBuilder
from aiida.orm import Group, StructureData


def Create_group(groupname, **kwargs):
    """
    Check if a group exist in the database
    If it does not, it creates it
    This group will be used to select the nodes
    according to nodes that are marked relevant
    """
    g, was_created = Group.objects.get_or_create(label=groupname, **kwargs)
    print(('group {} was created: {}'.format(groupname, was_created)))

    return g


def check_db(mygroup, **args):
    """
    Query the database for existing information
    Project the search on the query provided by the GET

    """
    qb = QueryBuilder()
    # search 'ext'nodes in the query
    qb.append(Group, tag='tag1', filters={'label': mygroup})
    if args['id'] is None:
        args = {}
    # finally, search in the GET query, if any
    qb = QueryBuilder()
    qb.append(StructureData, tag='tag1', project=['*'], filters=args)

    return qb.all()
