# -*- coding: utf-8 -*-
"""
Daniele Tomerini
Initial code march 2019

General click command to run the extended AiiDA REST API

This file heavily borrows from aiida.restapi.run_api
"""


from __future__ import absolute_import
import click
import json
from aiida.cmdline.utils import decorators
from aiida.cmdline.params.options import HOSTNAME, PORT

import aiida.restapi
import aiida_post
CONFIG_DIR = str(aiida.restapi.__path__[0]) + '/common/'
APP_DIR = str(aiida_post.__path__[0]) + '/common/'


@click.command()
@HOSTNAME(default='127.0.0.1')
@PORT(default=5000)
@click.option(
    '-c',
    '--config-dir',
    'config',
    type=click.Path(exists=True),
    default=CONFIG_DIR,
    help='the path of the configuration directory'
)
@click.option('--debug', 'debug', is_flag=True, default=False, help='run app in debug mode')
@click.option(
    '--wsgi-profile',
    'wsgi_profile',
    is_flag=True,
    default=False,
    help='to use WSGI profiler middleware for finding bottlenecks in web application'
)
@click.option('--hookup/--no-hookup', 'hookup', is_flag=True, default=True, help='to hookup app')
@click.option(
    '--app-dir',
    '-a',
    type=click.Path(exists=True),
    default=APP_DIR,
    help='contains the configuration needed for aiida_post'
)
@decorators.with_dbenv()
def extendedrest(**kwargs):
    """
    command line script to run an extended REST api of AiiDA
    """
    from aiida_post.api import InterfaceApi
    from aiida.restapi.api import App
    from aiida.restapi.run_api import run_api

    # Construct parameter dictionary
    myargs = dict(
        prog_name='Interface-restapi',
        catch_internal_server=True,
    )

    # Invoke the runner
    run_api(App, InterfaceApi, **kwargs, **myargs)


if __name__ == '__main__':
    """
    Run the app accepting arguments.

    Ex:
     python extended.py --host=127.0.0.2 --port=6000 --config-dir

    Defaults:
     address: 127.0.01:5000,
     config directory: <aiida_path>/aiida/restapi/common
    """

    #    with open('config.json') as f:
    #        CALCULATION_OPTIONS = json.load(f)
    extendedrest()
