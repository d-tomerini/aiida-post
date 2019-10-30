# -*- coding: utf-8 -*-
"""
Daniele Tomerini
Initial code march 2019

Initial proposal for an interface between Ext and Aiida
FLASK python app.
Based on JSON interchange between a server accepting requests
and returning values and updates on the calculation
Endpoints  changes on property, with GET and POST requests
handling various tasks

Keywords for now are stored within a settings.json file.
Basic checks to help ensure consistency
"""
# general imports
import json

from aiida.restapi.api import AiidaApi, App
from aiida.restapi.run_api import run_api
from aiida.cmdline.utils import decorators
# end of the endpoint definitions
# start of the click resource to launch the script

from aiida.cmdline.params.options import HOSTNAME, PORT

import aiida.restapi.common as common
CONFIG_DIR = common.__path__[0]

import click
@click.command()
@HOSTNAME(default='127.0.0.1')
@PORT(default=5000)
@click.option(
    '-c',
    '--config-dir',
    type=click.Path(exists=True),
    default=CONFIG_DIR,
    help='the path of the configuration directory'
)
@click.option(
        '--debug', 
        'debug', 
        is_flag=True, 
        default=False, 
        help='run app in debug mode')
@click.option(
    '--wsgi-profile',
    'wsgi_profile',
    is_flag=True,
    default=False,
    help='to use WSGI profiler middleware for finding bottlenecks in web application'
)
@click.option(
        '--hookup/--no-hookup', 
        'hookup', 
        is_flag=True, 
        default=True, 
        help='to hookup app')

@decorators.with_dbenv()
def extendedrest(hostname, port, config_dir, debug, wsgi_profile, hookup):
    """ 
    command line script to run an extended REST api of AiiDA
    """
    from aiida_post.api import InterfaceApi
    # Construct parameter dictionary
    kwargs = dict(
        prog_name='verdi-restapi',
        hostname=hostname,
        port=port,
        config=config_dir,
        debug=debug,
        wsgi_profile=wsgi_profile,
        hookup=hookup,
    )

    # Invoke the runner
    run_api(App, InterfaceApi, **kwargs)


if __name__ == '__main__':
    """
    Run the app accepting arguments.

    Ex:
     python extended.py --host=127.0.0.2 --port=6000 --config-dir

    Defaults:
     address: 127.0.01:5000,
     config directory: <aiida_path>/aiida/restapi/common
    """

    with open('config.json') as f:
        CALCULATION_OPTIONS = json.load(f)
    extendedrest()
