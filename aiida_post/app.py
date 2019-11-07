# -*- coding: utf-8 -*-
"""
Daniele Tomerini for the INTERSECT project

General click command to run the extended AiiDA REST API
This file heavily borrows from aiida.restapi.run_api
"""

from __future__ import absolute_import

import click
import json

from aiida.cmdline.utils import decorators
from aiida.cmdline.params.options import HOSTNAME, PORT

# configuration of the REST API and additional variables to set
# import aiida.restapi --> we can get the CONFIG file from there

import aiida_post
CONFIG_DIR = str(aiida_post.__path__[0]) + '/common/'


@click.command()
@HOSTNAME(default='127.0.0.1')
@PORT(default=5000)
@click.option(
    '-c',
    '--config-dir',
    'config',
    type=click.Path(exists=True),
    default=CONFIG_DIR,
    help='The path of the configuration directory'
)
@click.option(
    '--wsgi-profile',
    'wsgi_profile',
    is_flag=True,
    default=False,
    help='Flag to use WSGI profiler middleware for finding bottlenecks in web application'
)
@click.option('--hookup/--no-hookup', 'hookup', is_flag=True, default=True, help='to hookup app')
@click.option('--debug', 'debug', is_flag=True, default=False, help='run app in debug mode')
@decorators.with_dbenv()
def extendedrest(**kwargs):
    """
    Command line script to run an extended REST api of AiiDA
    """
    from aiida.restapi.api import App
    from aiida_post.api import InterfaceApi
    from aiida_post.run_api import run_api

    # Extend the passed parameter dictionary
    # Program name is just eye candy
    # catch_internal_server allows for printing the available endpoints
    # when the requested endpoint does not exist
    myargs = dict(
        prog_name='Interface-restapi',
        catch_internal_server=True,
    )
    kwargs.update(myargs)

    # Run the flask app; invoke the runner
    run_api(App, InterfaceApi, **kwargs)


if __name__ == '__main__':
    """
    Run the app accepting arguments.

    For example:

    verdi run app.py --host=127.0.0.2 --port=6000 --config-dir

    """

    extendedrest()
