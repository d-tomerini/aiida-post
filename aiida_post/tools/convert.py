# -*- coding: utf-8 -*-
# General tools to handle the conversion between data types


def Request_To_Dictionary(req):
    """
    Receive a :Flask.request datatypes, and it process its content.
    The information is saved inside a dictionary, that can be used
    to save it into a node and use it as an initial link.
    More data could be added if needed
    :param req: the Flask.request object
    :returns : a dictionary of data
    """
    alldata = {}
    # environment properties
    alldata['environ'] = req.environ
    # arguments passed in the url request
    alldata['args'] = req.args.to_dict()
    # date
    alldata['date'] = req.date
    # values
    alldata['values'] = req.values
    # incoming json info
    alldata['json'] = req.get_json()

    return alldata
