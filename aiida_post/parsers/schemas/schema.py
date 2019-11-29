from __future__ import absolute_import
from voluptuous import Schema

s = Schema[Required('calculation'):str, Required('structure'):{Required('structure_type'): str},]
