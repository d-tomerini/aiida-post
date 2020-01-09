"""
Basic `workflow` to connect the inputs of the real, calculation workflow
to the entrypoint passed as information
"""
from __future__ import absolute_import
from aiida.engine import WorkChain
from aiida import orm


class ConnectRequestToWorkFlow(WorkChain):
    """
    Connect the request to the workflow
    It HAS to be easier to just hack the database,
    alternative is just to draw the link "by hand,
    as commented out in distributor
    """

    @classmethod
    def define(cls, spec):
        super().define(spec)
        #inputs
        spec.input('entrypoint', valid_type=orm.Str, help='The entrypoint of the calculation to call')
        spec.input('dictionary_inputs', valid_type=orm.Dict, help='Inputs of the workflow to launch')
        spec.input('workflow', valid_type=orm.ProcessNode, non_db=True)
        spec.output_namespace('output', dynamic=True)
        #outline
        spec.outline(cls.connect,)

    def connect(self):
        """
        This is a dummy workflow. 
        It detects the inputs of a workflow (not restored) and links them to the dictionary request
        that created it. This will allow the search for the dictionary that generated the workflow inputs.
        """
        from aiida.common.links import LinkType

        linktriples = self.inputs.workflow.get_incoming().all()
        i = 1
        outputs = {}
        for triple in linktriples:
            if triple.link_type == LinkType.INPUT_WORK:
                outputs[triple.link_label] = triple.node
                i += 1
        self.out('output', outputs)
