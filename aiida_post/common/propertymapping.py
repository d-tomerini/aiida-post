"""
map of the single property to an entry point name of a workflow
will have to contain where to look for properties, in order
"""

from __future__ import absolute_import
import collections

# supported workchain. Will be changed to check the available endpoint in the definitions

# also will be superseded by something better, i.e. how to get

# list of the supported codes to use in the database
# for now, list is given by the nodes that are loaded in the database
# in the future it will probably be given as a list of "suggested to use"
# also, upf co not belong here

AVAILABLE_CODES = {'qe': 667, 'siesta': 668, 'upf': 'efficiency'}

# map of properties to single workchain
# it should be interesting (necessary?) to also map WHERE to
# find this value / object (output name/location)
PROPERTY_MAPPING = {
    'structure.cod': 'post.CODImport',
    'relax.pw': 'quantumespresso.pw.relax',
    'relaxed_energy.pw': 'quantumespresso.pw.relax',
    'band_structure.pw': 'quantumespresso.pw.band_structure',
    'band_gap.pw': 'post.BandGap',
    'formation_energy.qe': 'defects.formation_energy.qe'
}

# for each of the properties, this tells us where to find the output
# a dictionary of properties; each entry is a list of lists
# first is an edge filter (name of the output)
# second is the desired attribute

PropMap = collections.namedtuple('PropMap', 'name, is_node, edge, project')
PROPERTY_OUTPUTS = {
    'structure.cod': PropMap('list_of_structures', False, 'output', 'attributes'),
    'relax.pw': PropMap('relaxed_structure', True, 'output_structure', 'uuid'),
    'relaxed_energy.pw': PropMap('final_relaxed_energy', False, 'output_parameters', 'attributes.energy'),
    'band_gap.pw': PropMap('band_gap', False, 'output_parameters', 'attributes.band_gap')
}
