from voluptuous import Schema
s = Schema{
    Required('calculation'):str,
    Required('structure'):{
        Required('structure_type'):str
    }
}
