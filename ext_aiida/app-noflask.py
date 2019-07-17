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

# aiida
from aiida import load_profile
from aiida.orm import Dict, Str
from aiida.engine import launch, submit, run
from time import sleep

# local imports
from other.group_initialize import Create_group, check_db
from submit.distributor import Distribute

import sys

"""
Route to manage the requests from ext
Access is through a JSON file passed to the server
containing the input required for calculation
Data is handled and responded accordingly
:input prop is the quantity we required for calculation
"""
# workfunction to process the incoming json dictionary
# this is always required
# here it needs a validation by 
prop = 'band_gap'
load_profile()
with open('config.json') as f:
        CALCULATION_OPTIONS = json.load(f)
with open(sys.argv[1]) as f:
    request = f.read()
f.close()

wf = run(
    ProcessInputs,
    request=Dict(dict=json.loads(request)),
    predefined=Dict(dict=CALCULATION_OPTIONS),
    property=Str(prop)
)


if not wf.is_finished_ok:
    msg = 'Structure retrieval error. See node uuid={} for more specific report'.format(wf.uuid)
    print (""" {
        'error': wf.exit_message,
        'message': msg,
        'stored_request': wf.inputs.request.get_dict()
    }""")
else:
    exwf = Distribute(wf, prop)
    msg = ' Successful retrieval of structure, saved as uuid={}'.format(exwf.uuid)
    print (""" {
        'error': wf.exit_message,
        'message': msg,
        'stored_request': wf.inputs.request.get_dict()
    }
    """)
    # get to the actual calculation of the workflow