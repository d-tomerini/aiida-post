"""
General variables used by the app
"""

# supported workchain. Will be changed to check the available endpoint in the definitions

CALCULATION = ['relax', 'scf', 'band_structure', 'band_gap']

# also will be superseded by something better, i.e. how to get
# information from structure and property databases

SUPPORTED_DATABASE = ['COD']

# list of the supported codes to use in the database
# for now, list is given by the nodes that are loaded in the database
# in the future it will probably be given as a list of "suggested to use"
# also, upf co not belong here
AVAILABLE_CODES = {'qe': 376, 'siesta': None, 'upf': 'efficiency'}
